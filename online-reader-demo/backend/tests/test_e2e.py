import os
import pytest
from playwright.sync_api import Page, expect

# 这里的 URL 需要根据 CI 环境调整，通常 CI 里是 http://localhost:5173 (Vite 默认端口)
BASE_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

def test_upload_and_read_flow(page: Page):
    # 1. 创建一个临时的测试小说文件
    test_filename = "auto_test_novel.txt"
    test_content = "这是一个自动化测试生成的章节内容..."
    with open(test_filename, "w", encoding="utf-8") as f:
        f.write(test_content)

    try:
        # 2. 访问首页
        page.goto(BASE_URL)
        
        # 3. 验证标题存在
        expect(page.locator("h1")).to_contain_text("在线小说阅读器 Demo")

        # 4. 执行上传操作 (Playwright 处理文件上传非常简单)
        # 监听对话框 (alert)
        page.on("dialog", lambda dialog: dialog.accept())
        
        # 定位 input[type=file] 并设置文件
        page.locator("input[type='file']").set_input_files(test_filename)
        page.click("button:has-text('上传小说')")

        # 5. 验证列表里出现了这本小说 (需要稍作等待刷新)
        # 我们等待包含文件名的列表项出现
        expect(page.locator(f"li:has-text('{test_filename}')")).to_be_visible()

        # 6. 点击阅读
        page.locator(f"li:has-text('{test_filename}')").get_by_role("button", name="阅读").click()

        # 7. 验证阅读器内容是否正确
        expect(page.locator(".reader-section")).to_be_visible()
        expect(page.locator(".content-box")).to_contain_text(test_content)

    finally:
        # 清理测试文件
        if os.path.exists(test_filename):
            os.remove(test_filename)