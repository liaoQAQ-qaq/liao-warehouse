class BaiduPage:
    def __init__(self, page):
        self.page = page
        self.url = "https://www.baidu.com"
        # 页面元素定位器
        self.search_input = "#kw"
        self.search_button = "#su"

    def open(self):
        self.page.goto(self.url)

    def search(self, text):
        # force=True 强行输入，无视遮挡
        self.page.fill(self.search_input, text, force=True) 
        # 用回车键代替点击，更稳定
        self.page.keyboard.press("Enter")