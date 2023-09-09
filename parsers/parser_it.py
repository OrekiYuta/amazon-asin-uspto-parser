import logging
import traceback

from selenium.common import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import parsers.parser_common as parser_common


def get_product_info_it(asin_list, country_name, amazon_url, postal_code, driver):
    retries = 0
    max_retries = 3
    fail_flag = False
    while retries < max_retries:
        try:
            logging.info(f'打开 {country_name} 站点')
            driver.get(amazon_url)

            # 选择 Choose your location
            # 刚打开网页后,这里会出现验证码校验,给多点时间,或许之后提供人工输入
            logging.info(f'验证码校验处理-开始')
            # 如果出现验证码校验,尝试点击 "Try different image" 按钮,可能会跳过验证码校验
            captcha_jump = parser_common.captcha_jump(country_name, driver)
            if captcha_jump is False:
                fail_flag = True
                break

            logging.info(f'验证码校验处理-完成')

            time.sleep(1)
            logging.info(f'设置邮编-开始')

            try:
                choose_location_button = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.ID, 'nav-global-location-popover-link'))
                )
                choose_location_button.click()
            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException) as e:
                parser_common.except_screenshot(driver)
                logging.error(f'出现的异常信息：{str(e)}')
                logging.error(f'{country_name},重新点击设置邮编')
                driver.execute_script("arguments[0].click;", choose_location_button)
                pass

            parser_common.except_screenshot(driver)
            postal_code_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'GLUXZipUpdateInput'))
            )
            postal_code_input.clear()
            postal_code_input.send_keys(postal_code)

            # 点击 Apply
            apply_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#GLUXZipUpdate > span > input'))
            )
            apply_button.click()
            logging.info(f'设置邮编-完成')

            # 等待页面加载
            time.sleep(1)
            break

        except Exception as e:
            parser_common.except_screenshot(driver)
            logging.error(f'当前名为{country_name}的 Excel 数据没能开始爬取数据')
            logging.error("可能是出现 amazon 验证码校验提示,等待一段时间再启动程序吧")
            logging.error(f'出现的异常信息：{str(e)}')
            # 捕获异常，并输出具体位置和报错信息
            logging.error(traceback.format_exc())
            time.sleep(3)
            retries += 1
            if retries > 3:
                return None
            logging.info(f'amazon 反爬虫导致未能正常采集数据,第{retries}次重试...')

    if fail_flag is True:
        return None
    else:
        return get_common_product_data_set_multi_tabs_it(asin_list, country_name, amazon_url, driver)


def get_common_product_data_set_multi_tabs_it(asin_list, country_name, amazon_url, driver):
    # 创建结果集合
    results = []
    logging.info(f'开始循环打开 {country_name} 商品')

    # 打开三个标签页
    driver.get('about:blank')
    driver.execute_script("window.open('', '_blank');")
    driver.execute_script("window.open('', '_blank');")

    # 打开三个标签页,轮换操作获取数据
    for i in range(0, len(asin_list), 3):
        # 获取所有标签页的句柄
        handles = driver.window_handles

        for j in range(3):
            if i + j < len(asin_list):
                driver.switch_to.window(handles[j])

                single_result = get_common_product_data_set_single_it(asin_list[i + j], country_name, amazon_url,
                                                                      driver)

                if single_result is not None:
                    results.append(single_result)

    return results


def get_common_product_data_set_single_it(asin, country_name, amazon_url, driver):
    # 打开商品详情链接
    product_url = f'{amazon_url}dp/{asin}'
    driver.get(product_url)

    logging.info(f'{country_name}-{asin} 开始数据采集')
    result = None
    try:
        # 等待页面加载完成
        WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.ID, "dp-container"))
        )
    except TimeoutException:
        # 该 asin 商品的页面失效
        # 弹出验证码校验
        parser_common.except_screenshot(driver)
        logging.warning(f'{country_name}-{asin}, amazon 反爬,尝试绕过')

        # 尝试点击验证码绕过
        captcha_asin = parser_common.captcha_jump(country_name, driver)
        if captcha_asin is False:
            logging.error(f'{country_name}-{asin}, 无法绕过, 如果频繁出现该信息, 请等待一段时间再运行')
            return None
        else:
            logging.info(f'{country_name}-{asin}, 已绕过检测')
            pass

    # 执行随机操作,防止检测
    # fake_operation(country_name, asin, driver, "twotabsearchtextbox")

    # 判断是否为不可售商品
    is_unavailable = False

    try:
        # 检查是否不可在当前区域售卖
        unavailable_element = driver.find_element(By.ID, "availability")

        # if unavailable_element:
        if "Non disponibile" in unavailable_element.text:
            is_unavailable = True
        elif "Currently unavailable" in unavailable_element.text:
            is_unavailable = True

    except NoSuchElementException:
        # 未找到 "Currently unavailable." 元素,表示商品可在当前区域售卖
        logging.error(f'{country_name}-{asin},未找到 "Currently unavailable." 元素,表示商品可在当前区域售卖')
        pass

    if is_unavailable:
        # 获取商品信息
        title_element = parser_common.find_element_safe(country_name, asin, driver, By.ID, 'productTitle')
        brand_element = parser_common.find_element_safe(country_name, asin, driver, By.ID, 'bylineInfo')
        rating_element = parser_common.find_element_safe(country_name, asin, driver, By.ID, 'acrPopover')
        rating_count_element = parser_common.find_element_safe(country_name, asin, driver, By.ID,
                                                               'acrCustomerReviewText')
        category_element = parser_common.find_element_safe(country_name, asin, driver, By.ID,
                                                           'wayfinding-breadcrumbs_feature_div')

        title = "未找到标题"
        brand = "未找到品牌"
        rating = "未找到评分"
        rating_count = "未找到评价数量"
        main_category = "未找到大分类"
        sub_category = "未找到小分类"

        if title_element is not None:
            title = title_element.text.strip()

        if brand_element is not None:
            brand = brand_element.text.strip()
            # 'Brand: WindMax' -> 'WindMax'
            brand = parser_common.amazon_brand_split(brand)
            # Marke: BITOM
            # Marca: Compatibile
            # 品牌：Dalinch
            # Marque: Laurier

        if rating_element is not None:
            rating = rating_element.text.strip()

        if rating_count_element is not None:
            rating_count = rating_count_element.text.strip()
            # '4 ratings' -> '4'
            rating_count = rating_count.replace('ratings', '').strip()
            rating_count = rating_count.replace('rating', '').strip()

        if category_element is not None:
            # 'Appliances\n›\nRanges, Ovens & Cooktops\n›\nCooktops'
            categories = category_element.text.split('\n') if category_element else []
            # Appliances
            main_category = categories[0].strip() if categories else ''
            # ›Ranges, Ovens & Cooktops›Cooktops
            sub_category = ''.join(categories[1:]) if len(categories) > 1 else ''

        # 获取商品链接
        product_link = driver.current_url

        # 返回商品信息
        result = (
            {
                'ASIN': asin,
                '标题': title,
                '品牌名称': brand,
                '评论星级': rating,
                '评论数量': rating_count,
                '大分类': main_category,
                '小分类': sub_category,
                '商品链接': product_link
            }
        )

    logging.info(f'{country_name}-{asin} 完成数据采集')
    # 等待一段时间,防止访问频率过高被封禁或出现人机校验
    time.sleep(1)

    return result
