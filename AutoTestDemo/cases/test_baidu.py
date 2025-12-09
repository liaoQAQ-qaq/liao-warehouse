# 文件：cases/test_baidu.py
import pytest
import csv
from pages.baidu_page import BaiduPage

# --- 1. 读取 CSV 数据的辅助函数 ---
def get_csv_data():
    data_list = []
    # 注意：确保你的 CSV 文件路径正确
    with open('data/users.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过第一行表头
        for row in reader:
            data_list.append(row)
    return data_list
    # 返回格式: [['User_1', '自动化测试_1', '自动化测试_1'], ...]

# --- 2. 测试用例 ---
# 增加 app_credentials 参数，验证 Secrets 是否注入成功
@pytest.mark.parametrize("user_id, search_word, expect", get_csv_data())
def test_baidu_search_100_times(page_fixture, app_credentials, user_id, search_word, expect):
    
    print(f"\n--- [模拟用户: {user_id}] 正在搜索: {search_word} ---")
    
    # 验证 Secrets 是否生效 (调试用，生产环境请勿打印真实密码)
    # 如果你在 .env 或 GitHub Secrets 配置了，这里应该能打出来
    current_user = app_credentials.get("username", "Guest")
    print(f"   (当前执行测试的内部账号: {current_user})")

    # 1. 初始化
    page = page_fixture
    baidu = BaiduPage(page)
    
    # 2. 打开百度
    baidu.open()
    
    # 3. 执行搜索
    # 修正逻辑：这里直接使用 playwright 原生操作，或者使用 PO 对象的方法。
    # 为了演示修复 "断言失败" 的逻辑，我把关键步骤写在这里：
    
    # 输入搜索词 (修正了之前 keyword 变量报错的问题)
    page.fill("#kw", search_word) 
    page.click("#su")
    
    # --- 【关键修复】 显式等待 ---
    # 之前报错 AssertionError 是因为点击后还没加载完就检查标题
    # 现在强制等待 "搜索结果列表容器(content_left)" 出现
    try:
        page.wait_for_selector("#content_left", state="visible", timeout=10000)
    except Exception as e:
        print("警告: 搜索结果未加载或超时")
    
    # 4. 验证
    title = page.title()
    print(f"   -> 实际标题: {title}")
    
    # 断言：标题里应该包含我们搜的词
    assert expect in title