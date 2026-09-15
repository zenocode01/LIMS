# STATUS — 当前状态总览

> 由 zcode ticket status 自动生成，请勿手写。Agent 先读本文件即可了解全貌；细节按需再读对应文件。

## 关键状态
Phase: commit
Current Ticket: T-017
Domain: 实验室信息管理系统（LIMS），领域 EMC（电磁兼容）；P2 模块开发中——客户/报价/委托/样品（样品 S-EMC-日期-流水 状态机 已登记→在测→已返→…
TestCommand: cd backend && python3 -m pytest
BranchMode: auto
术语表: 19 条 (docs/UBIQUITOUS_LANGUAGE.md)

## 当前工单 T-017 (P2-样品管理（样品状态机+流转留痕）) [review]
## T-017 P2-样品管理（样品状态机+流转留痕）
Resolution: 实现: 样品模块（设计规格 §3/§5/§7 落地）——Sample 模型（编号 S-EMC-YYYYMMDD-流水 业务线伞类 按日归零；状态机 已登记→在测→已返→已报废，线性守卫 409）+ SampleEvent 流转留痕表（每次变更写 from/to/操作人/备注/时间，只增不删，倒序展示）；API /api/samples CRUD + transition（登记自动写首条留痕）；权限 §5 业务登记/流转、工程师查看（含留痕）、管理全量；alembic 0006；前端样品管理页（列表/详情/登记/流转+备注/留痕时间线）+ 侧边导航 + 委托详情样品区（聚合可视化）；tests 5 例，全量 pytest 56 绿；E2E 实测 登记→在测→已返→报废 全链 + 留痕备注 + 委托详情样品区 + 工程师只读
Depends: T-016
- [x] 后端: Sample + SampleEvent 留痕模型（S-EMC-YYYYMMDD-流水；已登记→在测→已返→已报废，每次变更留痕）
- [x] API: CRUD + transition（状态机守卫 409 + 留痕写入）；权限 §5 业务登记/流转、工程师查看、管理全量
- [x] alembic 0006_samples
- [x] 前端: 样品管理页（列表/详情/登记/流转+备注/留痕时间线）、导航、委托详情样品区
- [x] tests/test_samples.py（5 例：RBAC/编号+登记留痕/流转链+留痕倒序/非法迁移/过滤搜索）
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
- [x] **T-016** P2-委托管理（委托单状态机+从报价一键转入） — done  ✓已记录修复
- [ ] **T-017** P2-样品管理（样品状态机+流转留痕） — review  (depends: T-016)  ✓已记录修复

## 阻塞
(无)

<!-- GENERATED-BY-ZCODE -->