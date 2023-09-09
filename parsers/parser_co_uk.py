import logging
import traceback

from selenium.common import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import parsers.parser_common as parser_common


def get_product_info_co_uk(asin_list, country_name, amazon_url, postal_code, driver):
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
        return parser_common.get_common_product_data_set_multi_tabs(asin_list, country_name, amazon_url, driver)
