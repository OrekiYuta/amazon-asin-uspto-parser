import time
import traceback

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import NoSuchElementException

from selenium.webdriver.common.by import By

import logging
import parser_common


def fetch_uspto_co_jp(brand, driver, uspto_check_url):
    is_registered_flag = False

    retries = 0
    max_retries = 3
    while retries < max_retries:
        try:
            driver.get(uspto_check_url)

            time.sleep(2)
            # 进入商标查询页面
            link_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/center/table[1]/tbody/tr[2]/td/font/font/a')
                )
            )
            link_element.click()

            time.sleep(2)

            # 输入商标
            search_input = driver.find_element(By.XPATH, '/html/body/form/font/table[4]/tbody/tr[1]/td/input')
            search_input.send_keys(brand)

            # 点击查询按钮
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/form/font/table[4]/tbody/tr[4]/td/input[3]')
                )
            )

            search_button.click()
            time.sleep(2)
            break

        except Exception as e:
            parser_common.except_screenshot(driver)
            logging.error("加载查询品牌页面异常")
            logging.error(f'出现的异常信息：{str(e)}')
            logging.error(traceback.format_exc())
            time.sleep(1)
            retries += 1
            if retries > 3:
                break
            logging.info(f'查询品牌页面异常,第{retries}次重试...')

    try:

        # parser_common.fake_operation_scroll(driver)

        # 检查页面元素,查找结果
        flag_element = driver.find_element(By.XPATH, "//form[@action='/bin/showfield']")
        target_scope = flag_element.find_element(By.XPATH, './following-sibling::*[1]')

        if "Record" in target_scope.text:
            is_registered_flag = True

    except NoSuchElementException:
        logging.error(f'{brand},未找到查询结果,品牌未注册')
        logging.error(traceback.format_exc())
        pass

    return is_registered_flag
