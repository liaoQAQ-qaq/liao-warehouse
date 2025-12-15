# autotest_framework/pages/home_page.py

from playwright.sync_api import Page


class HomePage:
    """在线小说管理首页 PageObject

    这里只保留跟“上传小说”直接相关的操作：
    - 打开首页
    - 执行文件上传（input[type=file]）
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, url: str) -> None:
        print(f"🌍 正在打开页面: {url}")
        self.page.goto(url, wait_until="load", timeout=15_000)

    def upload_novel(self, file_path: str) -> None:
        """通过文件选择器上传小说文件"""
        # 这里假设前端页面上唯一的 input[type=file] 就是上传入口
        self.page.set_input_files('input[type="file"]', file_path)
