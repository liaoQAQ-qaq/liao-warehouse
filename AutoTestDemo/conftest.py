# conftest.py

import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# 1. 加载本地 .env 文件
# 作用：如果你在本地运行，它会读取 .env 里的变量；
# 如果在 GitHub Actions 运行，没有 .env 文件它也不会报错，而是直接从系统环境变量(Secrets)里读
load_dotenv()

# 2. 新增：专门管理账号密码的 Fixture
@pytest.fixture(scope="session")
def app_credentials():
    """
    全局 Fixture：负责获取账号和密码
    """
    username = os.getenv("APP_USERNAME")
    password = os.getenv("APP_PASSWORD")

    # 可选：打印一下看看（生产环境别打印密码！）
    print(f"当前使用的账号是: {username}")
    
    if not username or not password:
        print("\n[警告] 未检测到环境变量 APP_USERNAME 或 APP_PASSWORD！")
    
    return {"username": username, "password": password}

# 3. 你原有的浏览器启动 Fixture (保持逻辑不变)
@pytest.fixture(scope="function")
def page_fixture():
    print("\n[Setup] 启动浏览器 (慢动作模式 + 录制)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage'],
            slow_mo=1000  # 每个动作慢 1000 毫秒
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir="videos/", # 确保视频保存在这里
            no_viewport=False
        )
        
        # 依然开启 trace，双重保险
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        page = context.new_page()
        
        yield page
        
        print("\n[Teardown] 保存录像和轨迹...")
        # 建议：为了防止覆盖，Trace 文件名最好加上时间戳或用例名，不过这里先保持原样
        context.tracing.stop(path="trace.zip")
        context.close()
        browser.close()