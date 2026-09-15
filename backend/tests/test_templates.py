from conftest import auth_hdr

from test_quotes import _tok

TPL = {
    "name": "辐射发射记录表",
    "form_level": 4,
    "category": "EMI",
    "fields": [
        {"field_name": "频率范围", "field_type": "text", "required": True},
        {"field_name": "峰值读数", "field_type": "number", "unit": "dBμV", "required": True, "criteria_expr": "<= limit"},
    ],
}


def test_rbac(client):
    tok = _tok(client, "biz")
    h_adm = auth_hdr(_tok(client, "admin"))
    t = client.post("/api/record-templates", json=TPL, headers=h_adm).json()
    # 业务/工程师可查看
    h = auth_hdr(tok)
    assert client.get("/api/record-templates", headers=h).status_code == 200
    h_eng = auth_hdr(_tok(client, "eng"))
    assert client.get(f"/api/record-templates/{t['id']}", headers=h_eng).status_code == 200
    # 不可写（管理维护）
    assert client.post("/api/record-templates", json=TPL, headers=h).status_code == 403
    assert client.put(f"/api/record-templates/{t['id']}", json=TPL, headers=h).status_code == 403
    assert client.delete(f"/api/record-templates/{t['id']}", headers=h).status_code == 403
    # 未认证
    assert client.get("/api/record-templates").status_code == 401


def test_numbering_and_fields(client):
    h_adm = auth_hdr(_tok(client, "admin"))
    t1 = client.post("/api/record-templates", json=TPL, headers=h_adm).json()
    assert t1["tpl_no"] == "001"
    assert t1["form_level_label"] == "纯记录表单"
    assert t1["field_count"] == 2
    assert [f["field_no"] for f in t1["fields"]] == [1, 2]
    assert t1["fields"][1]["unit"] == "dBμV"
    assert t1["fields"][1]["criteria_expr"] == "<= limit"
    assert t1["controlled"] == "draft"
    t2 = client.post("/api/record-templates", json={**TPL, "name": "传导发射记录表"}, headers=h_adm).json()
    assert t2["tpl_no"] == "002"


def test_update_fields_and_level(client):
    h_adm = auth_hdr(_tok(client, "admin"))
    t = client.post("/api/record-templates", json=TPL, headers=h_adm).json()
    # 层级越界 422
    assert client.post("/api/record-templates", json={**TPL, "form_level": 9}, headers=h_adm).status_code == 422
    # 更新: 字段整组替换 + 升版
    t2 = dict(TPL, form_level=3, version=2, fields=[{"field_name": "仅一项"}])
    r = client.put(f"/api/record-templates/{t['id']}", json=t2, headers=h_adm)
    assert r.status_code == 200
    body = r.json()
    assert body["version"] == 2
    assert body["form_level_label"] == "作业指导书"
    assert [f["field_name"] for f in body["fields"]] == ["仅一项"]
    # 删除
    assert client.delete(f"/api/record-templates/{t['id']}", headers=h_adm).status_code == 204
    assert client.get(f"/api/record-templates/{t['id']}", headers=h_adm).status_code == 404


def test_search(client):
    h_adm = auth_hdr(_tok(client, "admin"))
    client.post("/api/record-templates", json=TPL, headers=h_adm)
    h = auth_hdr(_tok(client, "biz"))
    assert len(client.get("/api/record-templates", params={"q": "001"}, headers=h).json()) == 1
    assert len(client.get("/api/record-templates", params={"q": "辐射发射记录"}, headers=h).json()) == 1
    assert len(client.get("/api/record-templates", params={"q": "没有"}, headers=h).json()) == 0
