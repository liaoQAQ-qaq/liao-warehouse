# backend/tests/test_api_basic.py
import io
import uuid
from pathlib import Path
import shutil
from fastapi.testclient import TestClient

from backend.main import MAX_SQLITE_INT, app

client = TestClient(app)


def _upload_novel_via_api() -> tuple[int, str]:
    """通过 /upload/ 创建一条小说记录，返回 (id, title)。"""
    title = f"auto-test-{uuid.uuid4().hex}.txt"
    content = f"Hello from {title}".encode("utf-8")

    files = {
        "file": (title, io.BytesIO(content), "text/plain"),
    }

    resp = client.post("/upload/", files=files)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert isinstance(data["id"], int)
    assert data["id"] > 0
    assert data["title"] == title

    return data["id"], title


def test_upload_and_get_round_trip():
    """上传 → 通过 /novels/{id} 读取，验证数据闭环。"""
    novel_id, title = _upload_novel_via_api()

    resp = client.get(f"/novels/{novel_id}")
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["id"] == novel_id
    assert data["title"] == title
    # content 不强校验具体内容，只要有字符串即可
    assert isinstance(data["content"], str)
    assert data["content"] != ""


def test_list_novels_contains_uploaded_one():
    """上传一条小说，/novels/ 列表中应该能看到。"""
    _, title = _upload_novel_via_api()

    resp = client.get("/novels/?skip=0&limit=50")
    assert resp.status_code == 200, resp.text

    items = resp.json()
    assert isinstance(items, list)
    titles = [item["title"] for item in items]
    assert title in titles


def test_get_novel_not_found_returns_404():
    """请求一个不存在的 id，应该返回 404。"""
    # 选一个很大的 id，理论上不存在，但在 SQLite 范围内
    resp = client.get("/novels/999999999")
    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "Novel not found"


def test_get_novel_invalid_id_too_small_returns_422():
    """id < 1 触发 _validate_novel_id 的下限分支。"""
    resp = client.get("/novels/0")
    assert resp.status_code == 422
    body = resp.json()
    assert "detail" in body


def test_get_novel_invalid_id_too_big_returns_422():
    """id > MAX_SQLITE_INT 触发 _validate_novel_id 的上限分支。"""
    too_big = MAX_SQLITE_INT + 1
    resp = client.get(f"/novels/{too_big}")
    assert resp.status_code == 422
    body = resp.json()
    assert "detail" in body


def test_delete_novel_success_and_then_404():
    """删除成功后，再次获取应返回 404。"""
    novel_id, _ = _upload_novel_via_api()

    resp = client.delete(f"/novels/{novel_id}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["detail"] == "Deleted successfully"

    # 再查一次应该 404
    resp2 = client.get(f"/novels/{novel_id}")
    assert resp2.status_code == 404
    assert resp2.json()["detail"] == "Novel not found"


def test_delete_novel_invalid_id_range_returns_422():
    """删除时传入非法 id，同样触发 _validate_novel_id。"""
    resp = client.delete("/novels/0")
    assert resp.status_code == 422
    body = resp.json()
    assert "detail" in body
def test_main_import_fallback_mode(tmp_path):
    """
    模拟 Docker 镜像里的运行方式:
    - main.py 和 models.py 都在同一目录
    - 以顶层模块 `main` 导入
    -> `from .models import ...` 会失败，触发 fallback: `from models import ...`
    """

    project_root = Path(__file__).resolve().parents[2]
    backend_dir = project_root / "backend"

    # 把 main.py / models.py 拷贝到临时目录，模拟 /app/main.py 和 /app/models.py
    shutil.copy(backend_dir / "main.py", tmp_path / "main.py")
    shutil.copy(backend_dir / "models.py", tmp_path / "models.py")

    # 临时把该目录插入 sys.path，确保 `import main` / `import models` 能找到
    sys.path.insert(0, str(tmp_path))
    try:
        # 第一次导入 main：会先尝试 from .models 导入，
        # 因为模块名是 "main"，没有上级包，relative import 会抛 ImportError，
        # 然后走到 fallback 的 `from models import ...` 分支
        main = importlib.import_module("main")

        # 如果 fallback 成功，main 里应该有 app 对象
        assert hasattr(main, "app"), "fallback 导入失败，main.app 不存在"
    finally:
        # 清理现场，避免污染后续测试
        sys.path.pop(0)
        sys.modules.pop("main", None)
        sys.modules.pop("models", None)