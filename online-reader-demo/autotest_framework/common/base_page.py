# autotest_framework/common/base_page.py
from playwright.sync_api import Page, Locator

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str):
        print(f"🌍 正在打开页面: {url}")
        self.page.goto(url)

    def find(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def click(self, selector: str):
        print(f"🖱️ 点击元素: {selector}")
        self.find(selector).click()

    def input_text(self, selector: str, text: str):
        print(f"⌨️ 输入文本: {text}")
        self.find(selector).fill(text)
        
    def get_text(self, selector: str) -> str:
        return self.find(selector).text_content()

    def wait_for_visible(self, selector: str):
        self.page.wait_for_selector(selector, state="visible")