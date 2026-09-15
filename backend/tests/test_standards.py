from conftest import auth_hdr

from test_quotes import _tok

STANDARD = {
    "std_no": "GB 9254-2028",
    "name": "信息技术设备的无线电骚扰限值和测量方法",
    "effective_date": "2028-11-01",
    "items": [
        {"name": "辐射发射", "category": "EMI", "method": "30m 开阔场", "criteria": "准峰值限值"},
        {"name": "辐射抗扰度", "category": "EMS", "method": "GB/T 17626.3", "criteria": "性能判据 A"},
    ],
}


def test_rbac(client):
    tok = _tok(client, "biz")
    h_adm = auth_hdr(_tok(client, "admin"))
    h = auth_hdr(tok)
    # 业务/工程师可查看
    s = client.post("/api/standards", json=STANDARD, headers=h_adm).json()
    assert client.get("/api/standards", headers=h).status_code == 200
    h_eng = auth_hdr(_tok(client, "eng"))
    assert client.get("/api/standards", headers=h_eng).status_code == 200
    assert client.get("/api/equipment", headers=h_eng).status_code == 200
    # 业务/工程师不可写（管理维护）
    assert client.post("/api/standards", json=STANDARD, headers=h).status_code == 403
    assert client.post("/api/equipment", json={"name": "频谱仪"}, headers=h).status_code == 403
    assert client.delete(f"/api/standards/{s['id']}", headers=h).status_code == 403
    # 未认证
    assert client.get("/api/standards").status_code == 401


def test_standard_crud_and_items(client):
    h_adm = auth_hdr(_tok(client, "admin"))
    r = client.post("/api/standards", json=STANDARD, headers=h_adm)
    assert r.status_code == 201
    s = r.json()
    assert s["std_no"] == "GB 9254-2028"
    assert s["item_count"] == 2
    assert [i["name"] for i in s["items"]] == ["辐射发射", "辐射抗扰度"]
    assert [i["category"] for i in s["items"]] == ["EMI", "EMS"]
    # 重复标准号 409
    assert client.post("/api/standards", json=STANDARD, headers=h_adm).status_code == 409
    # 更新: 项目整组替换
    s2 = dict(STANDARD, items=[{"name": "传导发射", "category": "EMI"}])
    r = client.put(f"/api/standards/{s['id']}", json=s2, headers=h_adm)
    assert r.status_code == 200
    assert [i["name"] for i in r.json()["items"]] == ["传导发射"]
    # 删除
    assert client.delete(f"/api/standards/{s['id']}", headers=h_adm).status_code == 204
    assert client.get(f"/api/standards/{s['id']}", headers=h_adm).status_code == 404


def test_standard_search(client):
    h_adm = auth_hdr(_tok(client, "admin"))
    client.post("/api/standards", json=STANDARD, headers=h_adm)
    h = auth_hdr(_tok(client, "biz"))
    assert len(client.get("/api/standards", params={"q": "9254"}, headers=h).json()) == 1
    assert len(client.get("/api/standards", params={"q": "无线电骚扰"}, headers=h).json()) == 1
    assert len(client.get("/api/standards", params={"q": "不存在"}, headers=h).json()) == 0


def test_equipment_numbering_and_crud(client):
    h_adm = auth_hdr(_tok(client, "admin"))
    e1 = client.post("/api/equipment", json={"name": "频谱分析仪", "model": "FSN5071A", "location": "屏蔽室 A"}, headers=h_adm).json()
    assert e1["code"] == "EQ-001"
    e2 = client.post("/api/equipment", json={"name": "信号发生器"}, headers=h_adm).json()
    assert e2["code"] == "EQ-002"
    # 更新（编号不变）
    r = client.put(f"/api/equipment/{e2['id']}", json={"name": "信号发生器", "model": "N5183B", "location": "暗室"}, headers=h_adm)
    assert r.json()["code"] == "EQ-002"
    assert r.json()["model"] == "N5183B"
    # 删除
    assert client.delete(f"/api/equipment/{e2['id']}", headers=h_adm).status_code == 204
    assert client.get("/api/equipment", headers=h_adm).json()[0]["code"] == "EQ-001"
