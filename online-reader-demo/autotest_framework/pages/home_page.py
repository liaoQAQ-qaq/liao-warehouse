# autotest_framework/pages/home_page.py
from autotest_framework.common.base_page import BasePage

class HomePage(BasePage):
    # --- 1. 定位器 (Locators) ---
    # 现代化 UI 后的 CSS 选择器
    UPLOAD_INPUT = "input[type='file']"
    NOVEL_CARD = ".novel-card"
    CARD_TITLE = ".card-info h3"
    DELETE_BTN = "button.btn-delete"
    READ_BTN = "button.btn-read"
    READER_MODAL = ".reader-modal"
    
    # --- 2. 业务动作 (Actions) ---
    
    def upload_novel(self, file_path: str):
        """上传小说业务"""
        # Playwright 处理文件上传非常优雅
        self.page.set_input_files(self.UPLOAD_INPUT, file_path)
        # 我们的 UI 选中文件后自动上传，所以不需要点上传按钮
        # 等待上传完成（可以用 loading 状态消失作为判断依据，这里简单等待卡片出现）
        self.page.wait_for_selector(self.NOVEL_CARD, timeout=5000)

    def get_novel_titles(self):
        """获取当前页面所有小说的标题"""
        # 等待至少一个元素或空状态出现
        self.page.wait_for_timeout(500) 
        titles = self.page.locator(self.CARD_TITLE).all_text_contents()
        return titles

    def delete_novel_by_title(self, title: str):
        """根据标题删除小说"""
        # 监听 dialog (浏览器原生的 confirm 弹窗)
        self.page.on("dialog", lambda dialog: dialog.accept())
        
        # 找到包含特定标题的卡片，然后在里面找删除按钮
        # XPath 威力：//div[contains(@class, 'novel-card')][.//h3[text()='标题']]//button[contains(@class, 'btn-delete')]
        # 这里用 Playwright 的链式查找更易读
        card = self.page.locator(self.NOVEL_CARD).filter(has_text=title)
        card.locator(self.DELETE_BTN).click()
        
        # 等待卡片消失
        self.page.wait_for_timeout(1000) # 等待动画结束