import logging
import time

import flet as ft
import pipeline
import os
import glob

flet_logger = logging.getLogger("flet_core")
# 设置日志级别为最高级别，即禁用所有日志输出
flet_logger.setLevel(logging.CRITICAL)


def main(page: ft.Page):
    page.title = "Amazon ASIN Parser"
    page.window_width = 600
    page.window_height = 600

    dialog_parser_finish = ft.AlertDialog(
        title=ft.Text("已完成!"),
    )

    dialog_parser_error = ft.AlertDialog(
        title=ft.Text("抓取太频繁,稍等一会再重试!"),
    )

    def start_amazon_asin_parser(e):
        start_amazon_asin_parser_button.disabled = True
        start_amazon_asin_parser_button.update()
        try:
            result = pipeline.pipeline()

            if result:
                page.dialog = dialog_parser_finish
                dialog_parser_finish.open = True
            else:
                page.dialog = dialog_parser_error
                dialog_parser_error.open = True
        except:
            pass
        finally:
            start_amazon_asin_parser_button.disabled = False
            start_amazon_asin_parser_button.update()
            page.update()

    def start_uspto_asin_enquiry(e):
        start_uspto_asin_enquiry_button.disabled = True
        start_uspto_asin_enquiry_button.update()

        try:
            result = pipeline.get_uspto_info()

            if result:
                page.dialog = dialog_parser_finish
                dialog_parser_finish.open = True
            else:
                page.dialog = dialog_parser_error
                dialog_parser_error.open = True
        except:
            pass
        finally:
            start_uspto_asin_enquiry_button.disabled = False
            start_uspto_asin_enquiry_button.update()
            page.update()

    def explorer_folder(folder_name):
        folder_path = os.path.join(os.getcwd(), folder_name)
        # 检查文件夹是否存在
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            # 文件夹存在，打开文件夹
            os.startfile(folder_path)

    def explorer_folder_input(e):
        folder_name = "商品ASIN"
        explorer_folder(folder_name)

    def explorer_folder_output_asin_result(e):
        folder_name = "不在售商品信息"
        explorer_folder(folder_name)

    def explorer_folder_output_uspto_result(e):
        folder_name = "未注册品牌信息"
        explorer_folder(folder_name)

    start_amazon_asin_parser_button = ft.ElevatedButton(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(value="查询不在售商品数据", size=22),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=ft.padding.all(15),
        ),
        on_click=start_amazon_asin_parser,
        disabled=False

    )

    start_uspto_asin_enquiry_button = ft.ElevatedButton(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(value="查询是否已注册品牌", size=22),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5, ),
            padding=ft.padding.all(15),
        ),
        on_click=start_uspto_asin_enquiry,
        disabled=False

    )

    logging_box = ft.ListView(spacing=3, padding=10, auto_scroll=True, height=300)

    def logbox_changed(line):
        logging_box.controls.append(ft.Text(f"{line}"))
        logging_box.update()

    def read_latest_log_file():
        latest_log_file = None
        latest_modified_time = None

        while True:
            log_files = glob.glob('log/*.log')
            if log_files:
                # 按文件修改时间进行排序，获取最新的文件
                new_latest_log_file = max(log_files, key=os.path.getmtime)
                new_latest_modified_time = os.path.getmtime(new_latest_log_file)

                # 检查是否有新的日志文件
                if latest_log_file != new_latest_log_file or latest_modified_time != new_latest_modified_time:
                    latest_log_file = new_latest_log_file
                    latest_modified_time = new_latest_modified_time
                    # print(f"最新的日志文件是：{latest_log_file}")

                    # 逐行读取日志文件内容
                    with open(latest_log_file, 'r') as file:
                        lines = file.readlines()
                        last_line = lines[-1].strip()

                        # 初始化日志，替换成提示语
                        last_line = last_line.replace("Session started:", "等待开始...")
                        if last_line:
                            # print(line)
                            logbox_changed(last_line)

                        # for line in file:
                        #     # print(latest_lines)  # 输出每行日志内容
                        #     logbox_changed(line)

            # 休眠一段时间后继续检查
            # time.sleep(1)

    page.add(ft.Column([
        ft.Row(
            controls=[
                ft.Text(value="打开文件夹:", size=16),
            ]
        ),
        ft.Row(
            controls=[
                ft.OutlinedButton(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(value="商品ASIN", size=16),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=5,
                        ),
                        padding=ft.padding.all(15),
                    ),
                    on_click=explorer_folder_input
                ),
                ft.OutlinedButton(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(value="不在售商品信息", size=16),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=5,
                        ),
                        padding=ft.padding.all(15),
                    ),
                    on_click=explorer_folder_output_asin_result
                ),
                ft.OutlinedButton(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(value="未注册品牌信息", size=16),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=5,
                        ),
                        padding=ft.padding.all(15),
                    ),
                    on_click=explorer_folder_output_uspto_result
                )

            ]
        ),
        ft.Row(
            controls=[
                ft.Text(value="操作:", size=16),
            ]
        ),
        ft.Row(
            controls=[
                start_amazon_asin_parser_button,
                start_uspto_asin_enquiry_button,
            ]

        ),

        logging_box
    ]))

    read_latest_log_file()


ft.app(target=main)
