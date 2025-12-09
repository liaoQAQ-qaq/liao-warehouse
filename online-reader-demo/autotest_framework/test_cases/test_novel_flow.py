# autotest_framework/test_cases/test_novel_flow.py
import os
import allure
import pytest
from autotest_framework.pages.home_page import HomePage

# 准备测试数据
TEST_FILE_NAME = "enterprise_test.txt"
TEST_CONTENT = "这是一个企业级框架自动化测试生成的文本。"

@pytest.fixture(scope="function")
def prepare_file():
    """生成临时测试文件，测完自动删除"""
    with open(TEST_FILE_NAME, "w", encoding="utf-8") as f:
        f.write(TEST_CONTENT)
    yield TEST_FILE_NAME
    if os.path.exists(TEST_FILE_NAME):
        os.remove(TEST_FILE_NAME)

@allure.feature("小说管理模块")
class TestNovelManagement:
    
    @allure.story("上传与删除流程")
    @allure.title("测试上传一本小说并成功显示")
    def test_upload_and_delete(self, page, prepare_file):
        # 1. 初始化页面
        home = HomePage(page)
        
        with allure.step("打开首页"):
            home.open("http://127.0.0.1:5173") # 确保这个地址是你前端的地址
            
        with allure.step(f"上传文件: {prepare_file}"):
            home.upload_novel(prepare_file)
            
        with allure.step("验证列表包含该文件"):
            titles = home.get_novel_titles()
            assert prepare_file in titles, f"上传失败，{prepare_file} 未在列表中: {titles}"
            
        with allure.step("删除该文件"):
            home.delete_novel_by_title(prepare_file)
            
        with allure.step("验证文件已消失"):
            titles_after_delete = home.get_novel_titles()
            assert prepare_file not in titles_after_delete, "删除失败，文件依然存在"