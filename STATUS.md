# STATUS — 当前状态总览

> 由 zcode ticket status 自动生成，请勿手写。Agent 先读本文件即可了解全貌；细节按需再读对应文件。

## 关键状态
Phase: commit
Current Ticket: T-016
Domain: 实验室信息管理系统（LIMS），领域 EMC（电磁兼容）；P2 模块开发中——客户/报价/委托（委托单 C-日期-流水 状态机 草稿→已确认→…→已终止，已落单…
TestCommand: cd backend && python3 -m pytest
BranchMode: auto
术语表: 18 条 (docs/UBIQUITOUS_LANGUAGE.md)

## 当前工单 T-016 (P2-委托管理（委托单状态机+从报价一键转入）) [review]
## T-016 P2-委托管理（委托单状态机+从报价一键转入）
Resolution: 实现: 委托单模块（设计规格 §3/§5/§7 落地）——模型 Entrustment（编号 C-YYYYMMDD-流水 按日归零；状态机 草稿→已确认→测试中→已出报告→已完成，任意非终态→已终止，非法迁移 409；testing/report_issued/completed 的自动触发留给任务/样品模块 M3/M4，钩子已留）；API /api/entrustments CRUD + confirm（业务/管理）+ terminate（仅管理，留操作人+原因）+ from-quote（已落单一键转入：继承客户+明细摘要，报价置已转委托，幂等防重转 409）；权限 §5 业务建/编/确认、工程师查看（可见客户名）、管理全量+终止；alembic 0005；前端委托管理页（列表/详情/新建/确认/终止+原因）+ 侧边导航（全角色可见）+ 报价页「一键转委托单」接线 + 工作台入口；tests 6 例，全量 pytest 51 绿
- [x] 后端: Entrustment 模型 + 状态机（草稿→已确认→测试中→已出报告→已完成；非终态可终止）
- [x] 编号 C-YYYYMMDD-流水（numbering.no_entrustment）
- [x] API: CRUD + confirm + terminate(管理) + from-quote（已落单一键转入，报价置已转委托）
- [x] 权限 §5: 业务建/编辑/确认, 工程师查看, 管理全量+终止
- [x] alembic 0005_entrustments
- [x] 前端: 委托管理页（列表+详情+新建+确认/终止）、侧边导航、报价页转委托接线、工作台入口
- [x] tests/test_entrusts.py（6 例：RBAC/编号/确认守卫/终止守卫/转委托/搜索过滤）
Status: review


## 工单
- [x] **T-001** 初始化工单工作台骨架 — done  ✓已记录修复
- [x] **T-002** LIMS MVP 设计规格 — done  ✓已记录修复
- [x] **T-003** 设计文档自审修正 — done  ✓已记录修复
- [x] **T-004** 编号规则定稿+设计文档更新 — done  ✓已记录修复
- [x] **T-005** P1-基础实现计划 — done  ✓已记录修复
- [x] **T-006** P1-实现：基础底座 — done  ✓已记录修复
- [x] **T-007** Windows 原生部署支持 — done  ✓已记录修复
- [x] **T-008** 修复: Windows 脚本中文编码导致 GBK 乱码/解析风险 — done  ✓已记录修复
- [x] **T-009** 修复: setup.ps1 Split-Path -Parent -Parent 在 PS 5.1 非法 — done  ✓已记录修复
- [x] **T-010** 修复: setup.ps1 第8行丢失 $root 变量 (T-009 回归) — done  ✓已记录修复
- [x] **T-011** 修复: pip install backend 打包失败 + setup.ps1 静默吞错误报成功 — done  ✓已记录修复
- [x] **T-012** Windows start/stop 服务脚本（后台启动 + 端口精准停止） — done  ✓已记录修复
- [x] **T-013** P2-应用外壳+客户管理（首模块打样） — done  ✓已记录修复
- [x] **T-014** P2-报价管理（报价单状态机+明细，首屏打样延续） — done  ✓已记录修复
- [x] **T-015** 修复: 登录页右侧卡片过大 — done  ✓已记录修复
- [ ] **T-016** P2-委托管理（委托单状态机+从报价一键转入） — review  ✓已记录修复
- [ ] **T-017** P2-样品管理（样品状态机+流转留痕） — backlog  (depends: T-016)

## 阻塞
(无)

<!-- GENERATED-BY-ZCODE -->