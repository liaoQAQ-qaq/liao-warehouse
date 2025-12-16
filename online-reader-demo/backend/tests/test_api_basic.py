# backend/tests/test_api_basic.py
from fastapi.testclient import TestClient
from backend.main import app  # 注意：根据你 main.py 里 app 的路径来改

client = TestClient(app)


def test_health_like():
    # 你现在没有健康检查，可以先用现有接口顶一下
    resp = client.get("/novels/")
    assert resp.status_code in (200, 422)  # 有参数校验也能接受


def test_upload_and_get_novel(tmp_path):
    # 准备一个临时文件
    file_path = tmp_path / "demo.txt"
    file_path.write_text("hello coverage", encoding="utf-8")

    # 1) 上传
    with file_path.open("rb") as f:
        resp = client.post("/upload/", files={"file": ("demo.txt", f, "text/plain")})

    assert resp.status_code == 200
    data = resp.json()
    novel_id = data["id"]

    # 2) 读列表，至少包含这本
    resp_list = client.get("/novels/")
    assert resp_list.status_code == 200
    ids = [item["id"] for item in resp_list.json()]
    assert novel_id in ids

    # 3) 读详情
    resp_detail = client.get(f"/novels/{novel_id}")
    assert resp_detail.status_code == 200
    assert resp_detail.json()["title"] == "demo.txt"
    
def test_upload_invalid_encoding_returns_422():
    # 模拟一个非 UTF-8 的“坏文件”
    bad_bytes = b"\xff\xfe\xfa\xfb"
    files = {"file": ("bad.bin", io.BytesIO(bad_bytes), "application/octet-stream")}

    resp = client.post("/upload/", files=files)
    assert resp.status_code == 422
    body = resp.json()
    assert isinstance(body.get("detail"), list)
    assert body["detail"][0]["loc"] == ["body", "file"]


def test_upload_empty_file_returns_422():
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
    resp = client.post("/upload/", files=files)
    assert resp.status_code == 422