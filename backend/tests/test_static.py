"""静态托管（SPA 回退）测试 — T-007 Task 1。

不依赖 db fixture：health/静态路由不触库。
"""
from fastapi.testclient import TestClient

from app.main import create_app


def _make_dist(tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<html>LIMS SPA</html>", encoding="utf-8")
    (dist / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    (dist / "favicon.svg").write_text("<svg></svg>", encoding="utf-8")
    return dist


def test_root_serves_index(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/")
    assert r.status_code == 200
    assert "LIMS SPA" in r.text


def test_spa_fallback_for_client_route(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/dashboard")
    assert r.status_code == 200
    assert "LIMS SPA" in r.text


def test_deep_spa_fallback(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/samples/123/history")
    assert r.status_code == 200
    assert "LIMS SPA" in r.text


def test_static_file_served_with_type(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/assets/app.js")
    assert r.status_code == 200
    assert "javascript" in r.headers["content-type"]
    assert r.text == "console.log(1)"


def test_top_level_static_file(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/favicon.svg")
    assert r.status_code == 200
    assert "image/svg" in r.headers["content-type"]


def test_api_routes_unaffected(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_unknown_api_returns_json_404(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/api/nope")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/json")
    assert "LIMS SPA" not in r.text


def test_unknown_api_post_returns_404(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.post("/api/nope", json={})
    assert r.status_code == 404


def test_path_traversal_blocked(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/%2e%2e/%2e%2e/etc/passwd")
    assert "root:" not in r.text
    assert "LIMS SPA" in r.text  # 回退 index.html，不泄露系统文件


def test_pure_api_mode_unchanged():
    c = TestClient(create_app())
    assert c.get("/dashboard").status_code == 404
    assert c.get("/api/health").status_code == 200


def test_missing_dist_dir_falls_back_to_api_mode(tmp_path):
    c = TestClient(create_app(static_dir=str(tmp_path / "nope")))
    assert c.get("/dashboard").status_code == 404


def test_dist_without_index_falls_back_to_api_mode(tmp_path):
    (tmp_path / "d").mkdir()
    c = TestClient(create_app(static_dir=str(tmp_path / "d")))
    assert c.get("/").status_code == 404


def test_empty_full_path_is_index(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/")
    assert r.status_code == 200
    assert "LIMS SPA" in r.text
