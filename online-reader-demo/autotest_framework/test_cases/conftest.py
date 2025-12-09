# autotest_framework/test_cases/conftest.py
import pytest
from playwright.sync_api import sync_playwright
import os
import allure

@pytest.fixture(scope="session")
def browser_context():
    """全局启动一次浏览器"""
    with sync_playwright() as p:
        # headless=False 可以看到浏览器动作，CI 环境改为 True
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        yield context
        browser.close()

@pytest.fixture(scope="function")
def page(browser_context):
    """每个测试用例都会获得一个新的 Tab 页"""
    page = browser_context.new_page()
    yield page
    page.close()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """失败自动截图并添加到 Allure 报告"""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        # 获取 page 对象
        page = item.funcargs.get("page")
        if page:
            # 截图
            png = page.screenshot()
            # 贴到报告里
            allure.attach(
                png, 
                name="失败截图", 
                attachment_type=allure.attachment_type.PNG
            )