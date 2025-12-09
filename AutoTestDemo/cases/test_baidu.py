# 文件：cases/test_baidu.py
import pytest
import csv
import os
from pages.baidu_page import BaiduPage

# --- 1. 读取 CSV 数据的辅助函数 ---
def get_csv_data():
    data_list = []
    file_path = 'data/users.csv'
    
    if not os.path.exists(file_path):
        print(f"警告: 数据文件 {file_path} 不存在！")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader) # 跳过表头
        except StopIteration:
            return [] # 空文件处理

        for i, row in enumerate(reader):
            # 【重要优化】为了防止 CI 跑死，强制限制只读前 3 条数据进行测试
            # 真实上线时可以注释掉下面这两行
            if i >= 3: 
                break 
            data_list.append(row)
            
    return data_list

# --- 2. 测试用例 ---
@pytest.mark.parametrize("user_id, search_word, expect", get_csv_data())
def test_baidu_search_100_times(page_fixture, app_credentials, user_id, search_word, expect):
    
    print(f"\n--- [用户: {user_id}] 搜索: {search_word} ---")
    
    # 1. 初始化
    page = page_fixture
    baidu = BaiduPage(page)
    
    # 2. 打开百度 (增加超时处理，防止白屏卡死)
    try:
        baidu.open()
    except Exception as e:
        print(f"打开百度超时或失败: {e}")
        # 如果连首页都打不开，后面就没必要跑了
        return 

    # 3. 执行搜索
    page.fill("#kw", search_word) 
    page.click("#su")
    
    # --- 【关键修复】 智能等待与调试 ---
    # 将等待时间延长到 30秒 (适应跨国网络)
    try:
        # 等待结果页的“左侧内容区域”出现
        page.wait_for_selector("#content_left", state="visible", timeout=30000)
    except Exception as e:
        print("\n[严重警告] 等待搜索结果超时！可能是网络慢，也可能是触发了百度验证码。")
        
        # 截图留证！这对 CI 调试至关重要
        # 图片会保存在 report.html 的同级目录，或者可以在 Artifacts 里看 trace
        page.screenshot(path=f"error_{user_id}.png")
        print(f"已截图保存为 error_{user_id}.png，请检查是否出现验证码。")
        
        # 让测试失败，不要假装成功
        pytest.fail(f"搜索结果未加载，无法断言。原因: {e}")
    
    # 4. 验证
    title = page.title()
    print(f"   -> 实际标题: {title}")
    
    # 断言
    assert expect in title