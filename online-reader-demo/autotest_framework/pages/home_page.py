import os
import re
from typing import List
from playwright.sync_api import Page, Locator, expect


class HomePage:
    def __init__(self, page: Page):
        self.page = page

    # ======== 建议你最终用 data-testid 固定住（最稳）========
    # 如果你前端有这些 testid，就把它们改成真实值
    LIST_ROW_TESTID = "[data-testid='novel-row']"
    LIST_TITLE_TESTID = "[data-testid='novel-title']"
    UPLOAD_INPUT_TESTID = "[data-testid='upload-input']"

    def open(self, url: str) -> None:
        print(f"🌍 正在打开页面: {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        # 等页面基本渲染完成（按需保留/调整）
        self.page.wait_for_load_state("networkidle", timeout=15_000)

    # -------------------------
    # 内部：获取“列表行”的 locator（有 testid 优先，否则 fallback）
    # -------------------------
    def _rows(self) -> Locator:
        # 1) 优先 data-testid
        rows = self.page.locator(self.LIST_ROW_TESTID)
        if rows.count() > 0:
            return rows

        # 2) fallback: table 行
        rows = self.page.locator("table tbody tr")
        if rows.count() > 0:
            return rows

        # 3) fallback: ul/li 列表
        rows = self.page.locator("ul li")
        return rows

    def locator_novel_row(self, title: str) -> Locator:
        # 精确过滤：行里包含 title 的那一行
        return self._rows().filter(has_text=title)

    # -------------------------
    # 上传
    # -------------------------
    def upload_novel(self, filename: str) -> None:
        abs_path = os.path.abspath(filename)

        # 1) 找 input[type=file]
        upload_input = self.page.locator(self.UPLOAD_INPUT_TESTID)
        if upload_input.count() == 0:
            upload_input = self.page.locator("input[type='file']")

        # 有些 UI 会把 input 隐藏，用 label / button 触发，这里兜底点一下“上传”按钮
        if upload_input.count() == 0:
            # fallback：尝试点击“上传/选择文件”
            for txt in ["上传", "选择文件", "Choose File", "Upload"]:
                btn = self.page.get_by_role("button", name=re.compile(txt, re.I))
                if btn.count() > 0:
                    btn.first.click()
                    break
            upload_input = self.page.locator("input[type='file']")

        expect(upload_input).to_have_count(1, timeout=5_000)
        upload_input.set_input_files(abs_path)

        # 有些页面需要再点一次“提交/上传”
        for txt in ["提交", "确认上传", "上传", "Submit", "Confirm", "OK"]:
            btn = self.page.get_by_role("button", name=re.compile(txt, re.I))
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                break

    # -------------------------
    # 读取标题列表
    # -------------------------
    def get_novel_titles(self) -> List[str]:
        titles = self.page.locator(self.LIST_TITLE_TESTID)
        if titles.count() > 0:
            return [t.strip() for t in titles.all_text_contents() if t.strip()]

        # fallback：从行里提取文本（可能会包含按钮文字，必要时你可以更精确化）
        rows = self._rows()
        texts = [t.strip() for t in rows.all_text_contents() if t.strip()]
        return texts

    # -------------------------
    # 删除：按标题删除
    # -------------------------
    def delete_novel_by_title(self, title: str) -> None:
        row = self.locator_novel_row(title).first
        expect(row).to_be_visible(timeout=10_000)

        # 1) 若是 window.confirm / alert，直接 accept
        self.page.once("dialog", lambda d: d.accept())

        # 2) 点击行内“删除”
        delete_btn = row.get_by_role("button", name=re.compile(r"(删除|delete|remove)", re.I))
        if delete_btn.count() == 0:
            delete_btn = row.locator("button:has-text('删除')")

        expect(delete_btn).to_have_count(1, timeout=5_000)
        delete_btn.first.click()

        # 3) 若是自定义弹窗（modal），点“确认/确定”
        for txt in ["确认", "确定", "Yes", "OK", "Confirm"]:
            confirm = self.page.get_by_role("button", name=re.compile(txt, re.I))
            if confirm.count() > 0 and confirm.first.is_visible():
                confirm.first.click()
                break
