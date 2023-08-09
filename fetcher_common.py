import time
import traceback

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import NoSuchElementException

from selenium.webdriver.common.by import By

import logging
import parser_common


def fetch_uspto_common(brand, driver, uspto_check_url):
    is_registered_flag = False

    europe_url = "https://branddb.wipo.int/en/quicksearch"

    retries = 0
    max_retries = 3
    while retries < max_retries:
        try:

            # driver.get("https://www.baidu.com")
            # driver.implicitly_wait(10)
            #
            # driver.execute_script("window.open('', '_blank');")
            # driver.execute_script("window.open('', '_blank');")
            # handles = driver.window_handles

            # driver.switch_to.window(handles[1])
            # driver.get(uspto_check_url)
            # time.sleep(2)

            driver.get(europe_url)
            driver.implicitly_wait(20)

            search_input = driver.find_element(By.XPATH, '/html/body/app-root/div/div/page-quicksearch/div/div['
                                                         '1]/w-edit-panel/div[1]/w-section/div['
                                                         '2]/w-slot/w-input-autocomplete/div/div[1]/input')
            search_input.clear()
            search_input.send_keys(brand)

            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/app-root/div/div/page-quicksearch/div/div[1]/w-edit-panel/div['
                               '1]/w-section/div[2]/w-slot/w-input-autocomplete/div/div[2]/f-facet/button')
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

        # 检查页面元素,查找结果
        flag_element = driver.find_element(By.XPATH, "/html/body/app-root/div/div/page-results/results/div/results"
                                                     "-info/div[3]/div")

        if "No" in flag_element.text.strip():
            is_registered_flag = False
        else:
            is_registered_flag = True

        # Get the current window handle
        # current_handle = driver.current_window_handle

        # Loop through all handles and close those that are not the current handle
        # for handle in handles:
        #     if handle != current_handle:
        #         driver.switch_to.window(handle)
        #         driver.close()
        #
        # # Switch back to the original tab (current_handle)
        # driver.switch_to.window(current_handle)

    except NoSuchElementException:
        logging.error(f'{brand},未找到查询结果,品牌未注册')
        logging.error(traceback.format_exc())
        pass

    return is_registered_flag
