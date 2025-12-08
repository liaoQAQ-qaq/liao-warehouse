from pages.baidu_page import BaiduPage

def test_search_python(page_fixture):
    # 1. 初始化
    page = page_fixture
    baidu = BaiduPage(page)
    
    # 2. 执行步骤
    print("正在打开百度...")
    baidu.open()
    
    print("正在搜索...")
    baidu.search("Python自动化")
    
    # 3. 验证结果 (等待页面加载出关键词)
    page.wait_for_selector("text=Python自动化")
    title = page.title()
    print(f"当前标题: {title}")
    
    assert "Python" in title