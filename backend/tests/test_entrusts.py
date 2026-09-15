from conftest import auth_hdr

from test_quotes import ITEMS, _mk_customer, _mk_quote, _tok


def _mk_entrust(client, tok, cust, requirement=None):
    r = client.post(
        "/api/entrustments",
        json={"customer_id": cust, "requirement": requirement or "辐射发射 x1"},
        headers=auth_hdr(tok),
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_rbac(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    e = _mk_entrust(client, tok, cust)
    h_adm = auth_hdr(_tok(client, "admin"))
    # 工程师可看（设计规格 §5: 委托-工程师=查看）, 不可写
    h_eng = auth_hdr(_tok(client, "eng"))
    assert client.get("/api/entrustments", headers=h_eng).status_code == 200
    assert client.get(f"/api/entrustments/{e['id']}", headers=h_eng).status_code == 200
    assert client.post("/api/entrustments", json={"customer_id": cust}, headers=h_eng).status_code == 403
    assert client.post(f"/api/entrustments/{e['id']}/confirm", headers=h_eng).status_code == 403
    # 管理全量: 可建可终止
    assert client.post("/api/entrustments", json={"customer_id": cust}, headers=h_adm).status_code == 201
    assert client.post(f"/api/entrustments/{e['id']}/terminate", json={"reason": "x"}, headers=h_adm).status_code == 200
    # 未认证
    assert client.get("/api/entrustments").status_code == 401


def test_create_numbering(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    e1 = _mk_entrust(client, tok, cust)
    assert e1["code"].startswith("C-") and e1["code"].endswith("-001")
    assert e1["status"] == "draft"
    assert e1["status_label"] == "草稿"
    assert e1["customer_name"]
    e2 = _mk_entrust(client, tok, cust)
    assert e2["code"].endswith("-002")
    # 客户不存在 404
    assert client.post("/api/entrustments", json={"customer_id": 9999}, headers=auth_hdr(tok)).status_code == 404


def test_confirm_and_illegal_transition(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    e = _mk_entrust(client, tok, cust)
    r = client.post(f"/api/entrustments/{e['id']}/confirm", headers=auth_hdr(tok))
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "confirmed"
    assert body["confirmed_at"] is not None
    # 重复确认 409
    assert client.post(f"/api/entrustments/{e['id']}/confirm", headers=auth_hdr(tok)).status_code == 409
    # 已终止后不可再确认
    h_adm = auth_hdr(_tok(client, "admin"))
    client.post(f"/api/entrustments/{e['id']}/terminate", json={"reason": "客户撤单"}, headers=h_adm)
    assert client.post(f"/api/entrustments/{e['id']}/confirm", headers=auth_hdr(tok)).status_code == 409


def test_terminate_guard(client):
    tok = _tok(client, "biz")
    h_adm = auth_hdr(_tok(client, "admin"))
    cust = _mk_customer(client, tok)
    e = _mk_entrust(client, tok, cust)
    # 业务无权终止
    assert client.post(f"/api/entrustments/{e['id']}/terminate", json={}, headers=auth_hdr(tok)).status_code == 403
    r = client.post(f"/api/entrustments/{e['id']}/terminate", json={"reason": "客户撤单"}, headers=h_adm)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "terminated"
    assert body["terminated_by"] == "admin"
    assert body["terminated_reason"] == "客户撤单"
    # 终态不可再终止
    assert client.post(f"/api/entrustments/{e['id']}/terminate", json={}, headers=h_adm).status_code == 409


def test_from_quote(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    q = _mk_quote(client, tok, cust)
    # 草稿不可转
    assert client.post(f"/api/entrustments/from-quote/{q['id']}", headers=auth_hdr(tok)).status_code == 409
    client.post(f"/api/quotations/{q['id']}/issue", headers=auth_hdr(tok))
    client.post(f"/api/quotations/{q['id']}/finalize", headers=auth_hdr(tok))
    # 已落单可转
    r = client.post(f"/api/entrustments/from-quote/{q['id']}", headers=auth_hdr(tok))
    assert r.status_code == 201, r.text
    e = r.json()
    assert e["customer_id"] == cust
    assert e["source_quote_id"] == q["id"]
    assert e["source_quote_code"] == q["code"]
    assert "辐射发射 x2" in e["requirement"]  # 明细摘要继承
    # 报价单置已转委托
    assert client.get(f"/api/quotations/{q['id']}", headers=auth_hdr(tok)).json()["status"] == "converted"
    # 重复转 409
    assert client.post(f"/api/entrustments/from-quote/{q['id']}", headers=auth_hdr(tok)).status_code == 409


def test_list_search_filter(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok, name="委托搜索客户")
    e = _mk_entrust(client, tok, cust, requirement="REQ-ABC")
    h = auth_hdr(tok)
    assert any(x["id"] == e["id"] for x in client.get("/api/entrustments", headers=h).json())
    assert client.get("/api/entrustments", params={"q": "委托搜索客户"}, headers=h).json()[0]["id"] == e["id"]
    assert client.get("/api/entrustments", params={"q": e["code"][:8]}, headers=h).json()[0]["id"] == e["id"]
    assert len(client.get("/api/entrustments", params={"status": "confirmed"}, headers=h).json()) == 0
    client.post(f"/api/entrustments/{e['id']}/confirm", headers=h)
    assert client.get("/api/entrustments", params={"status": "confirmed"}, headers=h).json()[0]["id"] == e["id"]
