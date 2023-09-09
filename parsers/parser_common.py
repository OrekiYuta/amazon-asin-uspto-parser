import logging
import traceback
from datetime import datetime
import os
from selenium.common import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import secrets


def get_common_product_data_set_multi_tabs(asin_list, country_name, amazon_url, driver):
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

                single_result = get_common_product_data_set_single(asin_list[i + j], country_name, amazon_url, driver)

                if single_result is not None:
                    results.append(single_result)

    return results


def get_common_product_data_set_single(asin, country_name, amazon_url, driver):
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
        except_screenshot(driver)
        logging.warning(f'{country_name}-{asin}, amazon 反爬,尝试绕过')

        # 尝试点击验证码绕过
        captcha_asin = captcha_jump(country_name, driver)
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
        if "Currently unavailable" in unavailable_element.text:
            is_unavailable = True

    except NoSuchElementException:
        # 未找到 "Currently unavailable." 元素,表示商品可在当前区域售卖
        logging.error(f'{country_name}-{asin},未找到 "Currently unavailable." 元素,表示商品可在当前区域售卖')
        pass

    if is_unavailable:
        # 获取商品信息
        title_element = find_element_safe(country_name, asin, driver, By.ID, 'productTitle')
        brand_element = find_element_safe(country_name, asin, driver, By.ID, 'bylineInfo')
        rating_element = find_element_safe(country_name, asin, driver, By.ID, 'acrPopover')
        rating_count_element = find_element_safe(country_name, asin, driver, By.ID, 'acrCustomerReviewText')
        category_element = find_element_safe(country_name, asin, driver, By.ID,
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
            # brand = brand.replace('Brand:', '').strip()
            brand = amazon_brand_split(brand)
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
    time.sleep(2)

    return result


def find_element_safe(country_name, asin, driver, by, value):
    try:
        element = driver.find_element(by, value)
        return element
    except NoSuchElementException:
        logging.info(f'{country_name}-{asin},页面不存在 {value} 元素')
        return None


def fake_operation(country_name, asin, driver, input_element):
    search_element = find_element_safe(country_name, asin, driver, By.ID, input_element)

    if search_element is not None:
        # 模拟输入操作
        search_element.clear()
        search_element.send_keys(secrets.token_hex(10))
        # 模拟随机滚动
        scroll_position = random.randint(0, 900)
        driver.execute_script("window.scrollTo(0, {});".format(scroll_position))
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, 0);")


def fake_operation_scroll(driver):
    # 模拟随机滚动
    scroll_position = random.randint(0, 900)
    driver.execute_script("window.scrollTo(0, {});".format(scroll_position))
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.execute_script("window.scrollTo(0, 0);")


def captcha_jump(country_name, driver):
    # 如果出现验证码校验,尝试点击 "Try different image" 按钮,可能会跳过验证码校验
    try:
        except_screenshot(driver)
        captcha_switch_button = WebDriverWait(driver, 12).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '/html/body/div/div[1]/div[3]/div/div/form/div[1]/div/div/div[2]/div/div[2]/a'))
        )

        captcha_switch_button.click()
        except_screenshot(driver)
        return True

    except TimeoutException as e:
        except_screenshot(driver)
        logging.error(f'{country_name},未找到验证码元素')
        logging.error(f'出现的异常信息：{str(e)}')
        logging.error(traceback.format_exc())
        return True

    except (NoSuchElementException, ElementClickInterceptedException) as e:
        except_screenshot(driver)
        logging.error(f'{country_name},未找到 "Try different image" 按钮')
        logging.error(f'{country_name},或者是 amazon 校验方式逻辑改变了')
        logging.error(f'出现的异常信息：{str(e)}')
        # 捕获异常，并输出具体位置和报错信息
        logging.error(traceback.format_exc())
        return False

    except Exception as e:
        except_screenshot(driver)
        logging.error(f'{country_name},验证码校验失败')
        logging.error(f'出现的异常信息：{str(e)}')
        # 捕获异常，并输出具体位置和报错信息
        logging.error(traceback.format_exc())
        return False


def except_screenshot(driver):
    # 创建截图保存目录
    screenshot_dir = os.path.join(os.getcwd(), '../log', 'img')
    os.makedirs(screenshot_dir, exist_ok=True)
    # 生成时间戳作为截图文件名
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    screenshot_path = os.path.join(screenshot_dir, f"{timestamp}.png")

    # 获取当前浏览器的截图并保存
    driver.save_screenshot(screenshot_path)


def amazon_brand_split(text):
    parts = text.split(":")

    if len(parts) > 1:
        return parts[-1].strip()

    parts = text.split("：")
    return parts[-1].strip()
