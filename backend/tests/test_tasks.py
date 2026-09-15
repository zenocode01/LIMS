from conftest import auth_hdr

from test_entrusts import _mk_customer, _mk_entrust, _tok
from test_quotes import _mk_quote


def _mk_standard_with_items(client, h, items):
    """建一个含标准项目的标准，返回 standard_item 主键列表。"""
    r = client.post(
        "/api/standards",
        json={"std_no": "GB 9254-2028", "name": "骚扰限值", "items": items},
        headers=h,
    )
    assert r.status_code == 201
    return [i["id"] for i in r.json()["items"]]


def _quote_with_items(client, tok, cust, item_ids, names=None):
    """建挂标准项目引用的报价单。"""
    items = [
        {"standard_item_id": iid, "qty": 1, "unit_price": 1000}
        for iid in item_ids
    ]
    if names:
        for it, n in zip(items, names):
            it["item_name"] = n
    return _mk_quote(client, tok, cust, items=items)


def test_quote_item_standard_ref(client):
    tok = _tok(client, "biz")
    h_adm = auth_hdr(_tok(client, "admin"))
    cust = _mk_customer(client, tok)
    item_ids = _mk_standard_with_items(
        client, h_adm,
        [{"name": "辐射发射", "category": "EMI"}, {"name": "辐射抗扰度", "category": "EMS"}],
    )
    q = _quote_with_items(client, tok, cust, item_ids)
    # 名称自动回填
    assert [i["item_name"] for i in q["items"]] == ["辐射发射", "辐射抗扰度"]
    assert [i["standard_item_id"] for i in q["items"]] == item_ids
    # 无效标准项目 404
    r = client.post(
        "/api/quotations",
        json={"customer_id": cust, "items": [{"standard_item_id": 9999, "qty": 1}]},
        headers=auth_hdr(tok),
    )
    assert r.status_code == 404
    # 无名称无引用 422
    r = client.post(
        "/api/quotations",
        json={"customer_id": cust, "items": [{"qty": 1}]},
        headers=auth_hdr(tok),
    )
    assert r.status_code == 422


def test_confirm_generates_tasks(client):
    tok = _tok(client, "biz")
    h_adm = auth_hdr(_tok(client, "admin"))
    cust = _mk_customer(client, tok)
    item_ids = _mk_standard_with_items(
        client, h_adm,
        [{"name": "辐射发射", "category": "EMI"}, {"name": "辐射抗扰度", "category": "EMS"}],
    )
    # 报价 → 落单 → 转委托
    q = _quote_with_items(client, tok, cust, item_ids)
    h = auth_hdr(tok)
    client.post(f"/api/quotations/{q['id']}/issue", headers=h)
    client.post(f"/api/quotations/{q['id']}/finalize", headers=h)
    e = client.post(f"/api/entrustments/from-quote/{q['id']}", headers=h).json()
    # 登记 2 个样品
    s1 = client.post("/api/samples", json={"entrustment_id": e["id"], "name_model": "样品 A"}, headers=h).json()
    s2 = client.post("/api/samples", json={"entrustment_id": e["id"], "name_model": "样品 B"}, headers=h).json()
    # 确认委托 → 2 项目 × 2 样品 = 4 任务
    r = client.post(f"/api/entrustments/{e['id']}/confirm", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["task_count"] == 4
    tasks = client.get("/api/tasks", headers=h).json()
    assert len(tasks) == 4
    assert all(t["status"] == "unscheduled" for t in tasks)
    assert t_code_seq(tasks)
    # 类别继承
    cats = sorted(t["category"] for t in tasks)
    assert cats == ["EMI", "EMI", "EMS", "EMS"]
    # 编号连续
    assert [t["code"][-3:] for t in sorted(tasks, key=lambda x: x["code"])] == ["001", "002", "003", "004"]
    # 样品矩阵: 每个样品 2 个任务
    assert sum(1 for t in tasks if t["sample_id"] == s1["id"]) == 2
    assert sum(1 for t in tasks if t["sample_id"] == s2["id"]) == 2


def t_code_seq(tasks):
    return all(len(t["code"]) > 0 for t in tasks)


def test_task_lifecycle_and_hooks(client):
    tok = _tok(client, "biz")
    h_adm = auth_hdr(_tok(client, "admin"))
    h_eng = auth_hdr(_tok(client, "eng"))
    cust = _mk_customer(client, tok)
    item_ids = _mk_standard_with_items(client, h_adm, [{"name": "辐射发射", "category": "EMI"}])
    q = _quote_with_items(client, tok, cust, item_ids)
    h = auth_hdr(tok)
    client.post(f"/api/quotations/{q['id']}/issue", headers=h)
    client.post(f"/api/quotations/{q['id']}/finalize", headers=h)
    e = client.post(f"/api/entrustments/from-quote/{q['id']}", headers=h).json()
    s = client.post("/api/samples", json={"entrustment_id": e["id"], "name_model": "样品 A"}, headers=h).json()
    client.post(f"/api/entrustments/{e['id']}/confirm", headers=h)
    task = client.get("/api/tasks", headers=h).json()[0]

    # 业务无权执行测试
    assert client.post(f"/api/tasks/{task['id']}/start", headers=h).status_code == 403
    # 工程师开测 → 样品在测（留痕）+ 委托单测试中
    r = client.post(f"/api/tasks/{task['id']}/start", headers=h_eng)
    assert r.status_code == 200
    assert r.json()["status"] == "testing"
    sample = client.get(f"/api/samples/{s['id']}", headers=h).json()
    assert sample["status"] == "in_test"
    assert any(ev["to_status"] == "in_test" and ev["operator"] == "system" for ev in sample["events"])
    entrust = client.get(f"/api/entrustments/{e['id']}", headers=h).json()
    assert entrust["status"] == "testing"
    # 完成
    r = client.post(f"/api/tasks/{task['id']}/complete", headers=h_eng)
    assert r.json()["status"] == "completed"
    assert r.json()["completed_at"] is not None
    # 已完成不可再开测（需打回）
    assert client.post(f"/api/tasks/{task['id']}/start", headers=h_eng).status_code == 409
    # 打回重测: 业务 403, 管理 200 留原因
    assert client.post(f"/api/tasks/{task['id']}/retest", json={"reason": "x"}, headers=h).status_code == 403
    r = client.post(f"/api/tasks/{task['id']}/retest", json={"reason": "数据存疑"}, headers=h_adm)
    body = r.json()
    assert body["status"] == "testing"
    assert body["retest_reason"] == "数据存疑"
    assert body["completed_at"] is None
    # 非终态非法: 未排程不可直接完成
    assert client.post(f"/api/tasks/{task['id']}/retest", json={}, headers=h_adm).status_code == 409


def test_task_list_filters(client):
    tok = _tok(client, "biz")
    h_adm = auth_hdr(_tok(client, "admin"))
    cust = _mk_customer(client, tok)
    item_ids = _mk_standard_with_items(client, h_adm, [{"name": "辐射发射", "category": "EMI"}])
    q = _quote_with_items(client, tok, cust, item_ids)
    h = auth_hdr(tok)
    client.post(f"/api/quotations/{q['id']}/issue", headers=h)
    client.post(f"/api/quotations/{q['id']}/finalize", headers=h)
    e = client.post(f"/api/entrustments/from-quote/{q['id']}", headers=h).json()
    client.post("/api/samples", json={"entrustment_id": e["id"], "name_model": "样品 A"}, headers=h)
    client.post(f"/api/entrustments/{e['id']}/confirm", headers=h)
    h_eng = auth_hdr(_tok(client, "eng"))
    # 工程师可查看任务（含客户上下文）
    assert client.get("/api/tasks", headers=h_eng).status_code == 200
    assert len(client.get("/api/tasks", params={"status": "unscheduled"}, headers=h).json()) == 1
    assert len(client.get("/api/tasks", params={"category": "EMI"}, headers=h).json()) == 1
    assert len(client.get("/api/tasks", params={"category": "EMS"}, headers=h).json()) == 0
    assert len(client.get("/api/tasks", params={"q": e["code"][:8]}, headers=h).json()) == 1
    assert len(client.get("/api/tasks", params={"q": "辐射发射"}, headers=h).json()) == 1
    assert len(client.get("/api/tasks", params={"entrustment_id": e["id"]}, headers=h).json()) == 1
