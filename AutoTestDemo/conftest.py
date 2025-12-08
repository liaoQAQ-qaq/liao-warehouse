# conftest.py

import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="function")
def page_fixture():
    print("\n[Setup] 启动浏览器 (慢动作模式 + 录制)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage'],
            slow_mo=1000  # 【核心修改】每个动作慢 1000 毫秒 (即1秒)
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
        context.tracing.stop(path="trace.zip")
        context.close()
        browser.close()