# STATUS — 当前状态总览

> 由 zcode ticket status 自动生成，请勿手写。Agent 先读本文件即可了解全貌；细节按需再读对应文件。

## 关键状态
Phase: commit
Current Ticket: T-020
Domain: 实验室信息管理系统（LIMS），领域 EMC（电磁兼容）；P3 模块开发中——标准库/记录模板/测试任务（确认委托按 项目×样品 自动生成, 打回重测）已落地，…
TestCommand: cd backend && python3 -m pytest
BranchMode: auto
术语表: 21 条 (docs/UBIQUITOUS_LANGUAGE.md)

## 当前工单 T-020 (P3-测试任务（确认委托自动生成+任务状态机）) [review]
## T-020 P3-测试任务（确认委托自动生成+任务状态机）
Resolution: 实现: 测试任务模块（设计规格 §3/§5/§7/§8 落地）——Task（编号 T-YYYYMMDD-流水; 状态机 未排程→已排程→测试中→完成, 打回重测=完成→测试中 仅管理且留原因, start 端点守卫仅 未排程/已排程 可开测）；确认委托钩子按 来源报价标准项目引用 × 样品 生成任务（类别 EMI/EMS 继承自项目, 无引用/无样品时 0 任务属合法）；开测钩子联动 样品 已登记→在测（system 留痕）+ 委托单 已确认→测试中；报价明细挂 standard_item_id（名称自动回填, 文本兜底, 迁移 0009 SQLite 方言兼容）；API start/complete=工程师/管理, retest=仅管理；前端任务页 + 报价明细标准项目选择器 + 委托确认任务数提示；tests 4 例, 全量 pytest 68 绿; E2E 全链路实测（建单挂项目→转委托→样品→确认生成 2 任务→开测→完成→打回留原因→再完成）
Depends: T-018, T-019
- [x] 报价明细挂标准项目引用（standard_item_id, 名称自动回填, 文本兜底保留）
- [x] Task 模型 + T-YYYYMMDD-流水 编号 + 状态机（未排程→已排程→测试中→完成; 完成→测试中=打回重测 管理触发留原因）
- [x] 确认委托钩子: 标准项目 × 样品 自动生成任务（类别继承）
- [x] 开测钩子: 样品 已登记→在测（留痕 system）+ 委托单 已确认→测试中
- [x] API: /api/tasks list/get/start(工程师/管理)/complete/retest(仅管理)
- [x] 前端: 测试任务页（列表/详情/开测/完成/打回+原因/状态类别筛选）、报价明细标准项目选择器、委托确认提示任务数
- [x] alembic 0009_tasks（SQLite 方言兼容）
- [x] tests/test_tasks.py（4 例）, 全量 68 绿; E2E 全链路实测
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
- [x] **T-017** P2-样品管理（样品状态机+流转留痕） — done  (depends: T-016)  ✓已记录修复
- [x] **T-018** P3-标准库（标准+测试项目+设备简表） — done  ✓已记录修复
- [x] **T-019** P3-记录模板库（模板+字段定义） — done  (depends: T-018)  ✓已记录修复
- [ ] **T-020** P3-测试任务（确认委托自动生成+任务状态机） — review  (depends: T-018, T-019)  ✓已记录修复
- [ ] **T-021** P3-排程日历（任务排程+日历视图） — backlog  (depends: T-020)

## 阻塞
(无)

<!-- GENERATED-BY-ZCODE -->