# STATUS — 当前状态总览

> 由 zcode ticket status 自动生成，请勿手写。Agent 先读本文件即可了解全貌；细节按需再读对应文件。

## 关键状态
Phase: commit
Current Ticket: T-018
Domain: 实验室信息管理系统（LIMS），领域 EMC（电磁兼容）；P3 模块开发中——标准库（官方号标准+EMI/EMS 测试项目+设备 EQ-NNN）已落地，接下来记…
TestCommand: cd backend && python3 -m pytest
BranchMode: auto
术语表: 19 条 (docs/UBIQUITOUS_LANGUAGE.md)

## 当前工单 T-018 (P3-标准库（标准+测试项目+设备简表）) [review]
## T-018 P3-标准库（标准+测试项目+设备简表）
Resolution: 实现: 标准库模块（设计规格 §5/§7/§8 落地）——Standard（官方号唯一, 不自定义编号）+ StandardItem（名称/类别 EMI|EMS 属性字段/方法/判据, 类别不入编号）+ Equipment（EQ-NNN 静态编号 简表）；API /api/standards CRUD（项目嵌套整组替换, 重复标准号 409）+ /api/equipment CRUD；权限 §5 业务/工程师查看、管理维护；alembic 0007；前端标准库页（标准/设备双 Tab + 项目动态编辑器 + 类别标签）；tests 4 例, 全量 pytest 60 绿; E2E 实测入库 GB 9254-2028（EMI+EMS 双项目）+ 三角色权限验证
- [x] 后端: Standard/StandardItem/Equipment 模型（标准用官方号；项目=名称/类别EMI|EMS/方法/判据；设备 EQ-NNN 静态）
- [x] API: /api/standards CRUD（嵌套项目整组替换）+ /api/equipment CRUD（EQ 编号）
- [x] 权限 §5: 业务/工程师查看, 管理维护
- [x] alembic 0007_standards
- [x] 前端: 标准库页（标准/设备双 Tab, 项目动态编辑器, EMI/EMS 类别标签）
- [x] tests/test_standards.py（4 例）, 全量 60 绿
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
- [ ] **T-018** P3-标准库（标准+测试项目+设备简表） — review  ✓已记录修复
- [ ] **T-019** P3-记录模板库（模板+字段定义） — backlog  (depends: T-018)
- [ ] **T-020** P3-测试任务（确认委托自动生成+任务状态机） — backlog  (depends: T-018, T-019)
- [ ] **T-021** P3-排程日历（任务排程+日历视图） — backlog  (depends: T-020)

## 阻塞
(无)

<!-- GENERATED-BY-ZCODE -->