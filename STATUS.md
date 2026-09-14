# STATUS — 当前状态总览

> 由 zcode ticket status 自动生成，请勿手写。Agent 先读本文件即可了解全貌；细节按需再读对应文件。

## 关键状态
Phase: commit
Current Ticket: T-014
Domain: 实验室信息管理系统（LIMS），领域 EMC（电磁兼容）；P2 模块开发中——客户/报价（状态机 草稿→发出→已落单→已转委托）
TestCommand: cd backend && python3 -m pytest
BranchMode: auto
术语表: 16 条 (docs/UBIQUITOUS_LANGUAGE.md)

## 当前工单 T-014 (P2-报价管理（报价单状态机+明细，首屏打样延续）) [review]
## T-014 P2-报价管理（报价单状态机+明细，首屏打样延续）
Resolution: 根因: 主流程起点建报价单未落地；修复: ①后端 Quotation/QuotationItem+状态机(草稿→发出→已落单→已转委托/取消, 非法迁移409)+/api/quotations CRUD+动作端点(RBAC: 读业务+管理, 写业务, 工程师403)+Q-YYYYMMDD流水编号+搜索/筛选+alembic 0004；②前端 报价列表页+详情Drawer+建单编辑弹窗(动态明细行+实时合计)+侧栏/工作台入口；③动效层 登录信号线draw-on/stagger入场/reduced-motion兜底；验证: pytest 45 全绿(test_quotes 5 用例), tsc+build 通过, Playwright 端到端全过(建单/发出/落单/取消/筛选/403/只读), 截图 real2-*.png; 附带修复 payload 漏 customer_id bug
Status: review

> 范围（2026-09-14）: 报价单 = 客户 + 明细行（项目名称×数量×单价），编号 Q-YYYYMMDD-流水（no_quote）。
> 状态机: 草稿 →（发出）已发出 →（客户接受=落单）已落单 →（转委托）已转委托（T-015 接通）；草稿/已发出 → 已取消。
> 权限（§5）: 业务=创建/编辑/发出/落单/取消, 管理=只读, 工程师=无权限（403）。
> 明细项目当前文本承载（标准库里程碑3 后挂 standard_items 引用）。
> 动效: 按 motion-web 技能产品型克制派——登录信号线 draw-on、卡片 stagger 入场、完整状态 token、reduced-motion 兜底。

- [x] 后端: Quotation/QuotationItem 模型 + 状态机迁移（非法迁移 409）+ /api/quotations CRUD+动作端点（RBAC）+ alembic 0004
- [x] 后端: pytest（RBAC/编号/状态机/搜索/编辑限制/管理只读）
- [x] 前端: 报价列表页（状态 Tag 色板/搜索/状态筛选/新建）+ 详情 Drawer（明细表+状态动作按钮）
- [x] 前端: 报价编辑弹窗（客户选择 + 动态明细行编辑器 + 合计实时计算）
- [x] 前端: 侧栏「报价管理」+ 工作台「新建报价」动作卡激活（工程师隐藏）
- [x] 动效层: 登录信号线 draw-on、工作台/列表 stagger 入场、hover/focus 状态补全、prefers-reduced-motion 关闭
- [x] 文档: CHANGELOG/README 同步 + 截图存档


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
- [ ] **T-014** P2-报价管理（报价单状态机+明细，首屏打样延续） — review  ✓已记录修复

## 阻塞
(无)

<!-- GENERATED-BY-ZCODE -->