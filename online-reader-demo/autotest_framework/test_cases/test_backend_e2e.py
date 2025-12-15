# autotest_framework/test_cases/test_backend_e2e.py
import os
import re
import allure
from playwright.sync_api import Page, expect


FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:5173")


def _first_existing(locator_candidates):
    """返回第一个 count() > 0 的 locator；都不存在则返回最后一个"""
    last = None
    for loc in locator_candidates:
        last = loc
        try:
            if loc.count() > 0:
                return loc
        except Exception:
            # 某些 locator 在页面未 ready 时可能抛错，先忽略
            pass
    return last


@allure.feature("E2E")
@allure.story("Upload -> Read -> (Optional) Delete")
@allure.title("test_upload_and_read_flow")
def test_upload_and_read_flow(page: Page, tmp_path):
    # 1) 准备上传文件（UTF-8）
    filename = "enterprise_test.txt"
    file_path = tmp_path / filename
    file_path.write_text(
        "在线小说阅读器 Demo\n\nHello from E2E.\n这是一段用于 UI 测试的内容。\n",
        encoding="utf-8",
    )

    with allure.step("打开前端首页并等待渲染完成"):
        page.goto(FRONTEND_BASE_URL, wait_until="domcontentloaded")

        # 等根节点（Vue 常见 #app，React 常见 #root）
        root = page.locator("#app, #root")
        expect(root).to_be_visible(timeout=15000)

        # 标题：优先 data-testid，其次回退 h1（避免你这次的报错）
        title = _first_existing(
            [
                page.locator("[data-testid='app-title']"),
                page.locator("h1").first,
            ]
        )
        expect(title).to_be_visible(timeout=15000)
        # 文案别写死“完全相等”，用关键字更稳
        expect(title).to_contain_text(re.compile(r"在线小说阅读器|Online Reader", re.I))

    with allure.step("上传小说文件"):
        # 上传 input：优先 data-testid，否则回退 input[type=file]
        upload_input = _first_existing(
            [
                page.locator("[data-testid='upload-input']"),
                page.locator("input[type='file']").first,
            ]
        )
        expect(upload_input).to_be_visible(timeout=15000)
        upload_input.set_input_files(str(file_path))

        # 上传按钮：优先 data-testid，否则按按钮文本兜底
        upload_btn = _first_existing(
            [
                page.locator("[data-testid='upload-submit']"),
                page.get_by_role("button", name=re.compile(r"上传|提交|Upload|Submit", re.I)),
            ]
        )
        expect(upload_btn).to_be_visible(timeout=15000)
        upload_btn.click()

    with allure.step("在列表中找到刚上传的小说并进入详情页"):
        # 列表项：优先 data-testid，否则用文本匹配（通常会显示文件名/去后缀标题）
        # 你项目里如果展示的是 “enterprise_test” 而不是 “enterprise_test.txt”，这里也能匹配
        item = _first_existing(
            [
                page.locator("[data-testid='novel-item']").filter(
                    has_text=re.compile(r"enterprise_test", re.I)
                ),
                page.get_by_text(re.compile(r"enterprise_test", re.I)).first,
            ]
        )

        expect(item).to_be_visible(timeout=15000)
        item.click()

    with allure.step("校验详情页内容已加载"):
        # 内容区域：优先 data-testid，否则用通用元素兜底
        content = _first_existing(
            [
                page.locator("[data-testid='novel-content']"),
                page.locator("pre").first,
                page.locator("article").first,
                page.locator("textarea").first,
                page.locator("div").filter(has_text=re.compile(r"Hello from E2E", re.I)).first,
            ]
        )
        expect(content).to_be_visible(timeout=15000)
        # 至少能看到我们写入的关键内容
        expect(page.get_by_text(re.compile(r"Hello from E2E", re.I))).to_be_visible(timeout=15000)

    # 如果你的产品允许删除，这里顺手做一下（可选）
    with allure.step("（可选）删除该小说并确认删除成功"):
        delete_btn = _first_existing(
            [
                page.locator("[data-testid='delete-button']"),
                page.get_by_role("button", name=re.compile(r"删除|Delete", re.I)),
            ]
        )

        if delete_btn and delete_btn.count() > 0:
            delete_btn.click()

            # 如果有确认弹窗
            confirm_btn = page.get_by_role("button", name=re.compile(r"确认|确定|Yes|Confirm", re.I))
            if confirm_btn.count() > 0:
                confirm_btn.click()

            # 回到列表后确认看不到
            page.goto(FRONTEND_BASE_URL, wait_until="domcontentloaded")
            expect(page.locator("#app, #root")).to_be_visible(timeout=15000)
            expect(page.get_by_text(re.compile(r"enterprise_test", re.I))).to_have_count(0, timeout=15000)
