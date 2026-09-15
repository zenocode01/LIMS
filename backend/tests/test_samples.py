from conftest import auth_hdr

from test_entrusts import _mk_customer, _mk_entrust, _tok


def _mk_sample(client, tok, entrust, name="路由器 RT-9"):
    r = client.post(
        "/api/samples",
        json={"entrustment_id": entrust["id"], "name_model": name, "appearance": "外壳完好"},
        headers=auth_hdr(tok),
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_rbac(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    e = _mk_entrust(client, tok, cust)
    s = _mk_sample(client, tok, e)
    # 工程师可看, 不可写
    h_eng = auth_hdr(_tok(client, "eng"))
    assert client.get("/api/samples", headers=h_eng).status_code == 200
    assert client.get(f"/api/samples/{s['id']}", headers=h_eng).status_code == 200
    assert client.post("/api/samples", json={"entrustment_id": e["id"], "name_model": "x"}, headers=h_eng).status_code == 403
    assert client.post(f"/api/samples/{s['id']}/transition", json={"to": "in_test"}, headers=h_eng).status_code == 403
    # 未认证
    assert client.get("/api/samples").status_code == 401


def test_numbering_and_event(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    e = _mk_entrust(client, tok, cust)
    s = _mk_sample(client, tok, e)
    assert s["code"].startswith("S-EMC-") and s["code"].endswith("-001")
    assert s["status"] == "registered"
    assert s["status_label"] == "已登记"
    assert s["entrustment_code"] == e["code"]
    # 登记留痕: from 空 → registered
    assert len(s["events"]) == 1
    assert s["events"][0]["from_status"] is None
    assert s["events"][0]["to_status"] == "registered"
    assert s["events"][0]["operator"] == "biz"
    # 委托单不存在 404
    assert client.post("/api/samples", json={"entrustment_id": 9999, "name_model": "x"}, headers=auth_hdr(tok)).status_code == 404


def test_transition_chain_and_trace(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    e = _mk_entrust(client, tok, cust)
    s = _mk_sample(client, tok, e)
    h = auth_hdr(tok)
    # 在测
    r = client.post(f"/api/samples/{s['id']}/transition", json={"to": "in_test", "note": "上架"}, headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "in_test"
    # 已返
    client.post(f"/api/samples/{s['id']}/transition", json={"to": "returned", "note": "样品寄回"}, headers=h)
    # 已报废
    r = client.post(f"/api/samples/{s['id']}/transition", json={"to": "disposed", "note": "老化报废"}, headers=h)
    body = r.json()
    assert body["status"] == "disposed"
    # 留痕倒序: 最新在头, 共 4 条（登记+3 次流转）
    assert [ev["to_status"] for ev in body["events"]] == ["disposed", "returned", "in_test", "registered"]
    assert body["events"][0]["note"] == "老化报废"
    # 终态不可再迁移
    assert client.post(f"/api/samples/{s['id']}/transition", json={"to": "in_test"}, headers=h).status_code == 409


def test_illegal_transition(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    e = _mk_entrust(client, tok, cust)
    s = _mk_sample(client, tok, e)
    h = auth_hdr(tok)
    # 已登记 不能直接到 已返
    assert client.post(f"/api/samples/{s['id']}/transition", json={"to": "returned"}, headers=h).status_code == 409
    # 非法状态值 409
    assert client.post(f"/api/samples/{s['id']}/transition", json={"to": "flying"}, headers=h).status_code == 409


def test_list_filter_search(client):
    tok = _tok(client, "biz")
    cust = _mk_customer(client, tok)
    e = _mk_entrust(client, tok, cust)
    s = _mk_sample(client, tok, e, name="搜索样机 X1")
    h = auth_hdr(tok)
    assert client.get("/api/samples", params={"q": "搜索样机"}, headers=h).json()[0]["id"] == s["id"]
    assert client.get("/api/samples", params={"q": e["code"][:8]}, headers=h).json()[0]["id"] == s["id"]
    assert client.get("/api/samples", params={"entrustment_id": e["id"]}, headers=h).json()[0]["id"] == s["id"]
    assert client.get("/api/samples", params={"status": "in_test"}, headers=h).json() == []
