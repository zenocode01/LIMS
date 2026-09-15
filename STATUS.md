# STATUS — 当前状态总览

> 由 zcode ticket status 自动生成，请勿手写。Agent 先读本文件即可了解全貌；细节按需再读对应文件。

## 关键状态
Phase: commit
Current Ticket: T-019
Domain: 实验室信息管理系统（LIMS），领域 EMC（电磁兼容）；P3 模块开发中——标准库（官方号标准+EMI/EMS 测试项目+设备 EQ-NNN）已落地，接下来记…
TestCommand: cd backend && python3 -m pytest
BranchMode: auto
术语表: 19 条 (docs/UBIQUITOUS_LANGUAGE.md)

## 当前工单 T-019 (P3-记录模板库（模板+字段定义）) [review]
## T-019 P3-记录模板库（模板+字段定义）
Resolution: 实现: 记录模板库（设计规格 §5/§7/§8 落地）——RecordTemplate（模板号 3 位静态流水, 入记录编号第 2 段; 表单层级 1-4; 类别 EMI/EMS/通用; 受控 draft/controlled/obsolete; 版本）+ TemplateField（字段名/类型 text|number|date|select/单位/必填/判据表达式, field_no 自动排序）；API /api/record-templates CRUD（字段嵌套整组替换）；权限 §5 业务/工程师查看、管理维护/升版；alembic 0008；前端记录模板页（字段动态编辑器+受控标签+版本）；tests 4 例, 全量 pytest 64 绿; E2E 实测建模板 001（2 字段含必填/单位/判据/数值类型）+ 业务只读
Depends: T-018
- [x] 后端: RecordTemplate（3位静态模板号/表单层级1-4/类别/受控状态/版本）+ TemplateField（字段名/类型/单位/必填/判据表达式）
- [x] API: /api/record-templates CRUD（字段嵌套整组替换, field_no 自动编号）
- [x] 权限 §5: 业务/工程师查看, 管理维护/升版
- [x] alembic 0008_record_templates
- [x] 前端: 记录模板页（列表/详情/新建+字段动态编辑器/受控标签/版本）
- [x] tests/test_templates.py（4 例）, 全量 64 绿
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
- [ ] **T-019** P3-记录模板库（模板+字段定义） — review  (depends: T-018)  ✓已记录修复
- [ ] **T-020** P3-测试任务（确认委托自动生成+任务状态机） — backlog  (depends: T-018, T-019)
- [ ] **T-021** P3-排程日历（任务排程+日历视图） — backlog  (depends: T-020)

## 阻塞
(无)

<!-- GENERATED-BY-ZCODE -->