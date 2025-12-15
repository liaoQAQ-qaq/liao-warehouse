import os
import uuid
import allure
import pytest
from playwright.sync_api import expect

from autotest_framework.pages.home_page import HomePage

# 可通过 CI / 本地环境变量覆盖
UI_URL = os.getenv("UI_URL", "http://127.0.0.1:5173")

TEST_CONTENT = "这是一个企业级框架自动化测试生成的文本。"


@pytest.fixture(scope="function")
def prepare_file():
    """生成临时测试文件（唯一文件名），测完自动删除"""
    filename = f"enterprise_test_{uuid.uuid4().hex}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(TEST_CONTENT)

    yield filename

    if os.path.exists(filename):
        os.remove(filename)


@allure.feature("小说管理模块")
class TestNovelManagement:
    @allure.story("上传与删除流程")
    @allure.title("测试上传一本小说并成功显示，再删除成功")
    def test_upload_and_delete(self, page, prepare_file):
        home = HomePage(page)

        with allure.step("打开首页"):
            home.open(UI_URL)

        with allure.step(f"上传文件: {prepare_file}（等待 POST /upload 返回 200）"):
            with page.expect_response(
                lambda r: r.request.method == "POST" and "/upload" in r.url,
                timeout=15_000,
            ) as resp_info:
                home.upload_novel(prepare_file)

            resp = resp_info.value
            assert resp.status == 200, f"上传失败 status={resp.status}, body={resp.text()}"

        with allure.step("验证列表包含该文件（等待 UI 出现）"):
            expect(home.locator_novel_row(prepare_file)).to_have_count(1, timeout=10_000)
            titles = home.get_novel_titles()
            assert prepare_file in titles, f"上传失败，{prepare_file} 未在列表中: {titles}"

        with allure.step("删除该文件（等待 DELETE /novels/{id} 返回 200 + 等 DOM 消失）"):
            with page.expect_response(
                lambda r: r.request.method == "DELETE" and "/novels/" in r.url,
                timeout=15_000,
            ) as del_info:
                home.delete_novel_by_title(prepare_file)

            del_resp = del_info.value
            assert del_resp.status in (200, 204), f"删除失败 status={del_resp.status}, body={del_resp.text()}"

            # 等该行彻底从列表消失（比 sleep 稳）
            expect(home.locator_novel_row(prepare_file)).to_have_count(0, timeout=15_000)

        with allure.step("最终验证文件已消失"):
            titles_after_delete = home.get_novel_titles()
            assert prepare_file not in titles_after_delete, f"删除失败，文件依然存在: {titles_after_delete}"
