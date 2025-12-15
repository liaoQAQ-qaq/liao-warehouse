# autotest_framework/test_cases/test_novel_flow.py

import os
import time
import uuid

import allure
import pytest
import requests
from playwright.sync_api import Page

from autotest_framework.pages.home_page import HomePage

# 后端 / 前端 URL（CI 里可以用环境变量覆盖）
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
UI_URL = os.getenv("UI_URL", "http://127.0.0.1:5173")


@pytest.fixture
def prepare_file(tmp_path):
    """为本次用例生成一个唯一的测试文件，避免与历史数据冲突"""
    filename = f"enterprise_test_{uuid.uuid4().hex}.txt"
    file_path = tmp_path / filename
    file_path.write_text(
        "这是一个企业级自动化测试框架的 E2E 测试文件。\n", encoding="utf-8"
    )
    # 返回「文件路径」和「文件名」两份信息
    return str(file_path), filename


@allure.feature("小说管理模块")
class TestNovelManagement:
    @allure.story("上传与删除流程")
    @allure.title("测试通过 UI 上传小说，再用 API 校验创建与删除")
    def test_upload_and_delete(self, page: Page, prepare_file):
        file_path, filename = prepare_file
        home = HomePage(page)

        # 1. 打开首页
        with allure.step("打开前端首页"):
            home.open(UI_URL)

        # 2. 通过 UI 上传文件，并等待 /upload 返回 200
        with allure.step(f"上传文件: {filename}（等待 POST /upload 返回 200）"):
            with page.expect_response(
                lambda r: r.request.method == "POST" and "/upload" in r.url,
                timeout=15_000,
            ) as resp_info:
                home.upload_novel(file_path)

            resp = resp_info.value
            assert resp.status == 200, (
                f"上传失败 status={resp.status}, body={resp.text()}"
            )

        # 3. 用后端 API 校验：小说已经创建
        with allure.step("调用 GET /novels/，验证小说已创建"):
            # 给后端一点时间写入数据库（非常保险的 0.5s 缓冲）
            time.sleep(0.5)

            r = requests.get(f"{API_URL}/novels/")
            assert r.status_code == 200, f"/novels/ 请求失败: {r.status_code}"

            novels = r.json()
            titles = [n["title"] for n in novels]
            assert (
                filename in titles
            ), f"/novels/ 返回中未找到 {filename}，当前列表: {titles}"

            # 找到刚才上传的那条记录的 id，用于后续删除
            novel_id = next(n["id"] for n in novels if n["title"] == filename)

        # 4. 直接通过 API 删除这本小说
        with allure.step(f"调用 DELETE /novels/{novel_id} 删除小说"):
            del_resp = requests.delete(f"{API_URL}/novels/{novel_id}")
            assert del_resp.status_code == 200, (
                f"删除失败 status={del_resp.status_code}, body={del_resp.text}"
            )

        # 5. 再次校验：小说已被删除
        with allure.step("再次调用 GET /novels/，验证小说已被删除"):
            time.sleep(0.2)
            r2 = requests.get(f"{API_URL}/novels/")
            assert r2.status_code == 200, f"/novels/ 请求失败: {r2.status_code}"

            titles_after = [n["title"] for n in r2.json()]
            assert (
                filename not in titles_after
            ), f"删除失败，{filename} 仍然存在: {titles_after}"
