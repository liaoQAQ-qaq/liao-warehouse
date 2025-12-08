# 文件：cases/test_baidu.py
import pytest
import csv
from pages.baidu_page import BaiduPage

# --- 1. 读取 CSV 数据的辅助函数 ---
def get_csv_data():
    data_list = []
    with open('data/users.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # 核心：跳过第一行表头 (user_id, search_word...)
        for row in reader:
            data_list.append(row) 
    return data_list
    # 返回格式: [['User_1', '自动化测试_1', '自动化测试_1'], ...]

# --- 2. 测试用例 ---
# ids 参数是为了让测试报告里显示的用例名字更好看
@pytest.mark.parametrize("user_id, search_word, expect", get_csv_data())
def test_baidu_search_100_times(page_fixture, user_id, search_word, expect):
    
    print(f"\n--- 当前模拟用户: {user_id} 正在搜索: {search_word} ---")
    
    # 1. 初始化页面
    page = page_fixture
    baidu = BaiduPage(page)
    
    # 2. 打开百度
    baidu.open()
    
    # 3. 搜索 (数据驱动)
    baidu.search(search_word)
    
    # 4. 验证
    # 稍微给一点点时间等待页面刷新 (实际项目中推荐用 wait_for_selector)
    page.wait_for_timeout(1000) 
    
    title = page.title()
    print(f"实际标题: {title}")
    
    # 断言：标题里应该包含我们搜的词
    assert expect in title