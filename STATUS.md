# STATUS — 当前状态总览

> 由 zcode ticket status 自动生成，请勿手写。Agent 先读本文件即可了解全貌；细节按需再读对应文件。

## 关键状态
Phase: commit
Current Ticket: T-013
Domain: 实验室信息管理系统（LIMS），领域 EMC（电磁兼容）
TestCommand: cd backend && python3 -m pytest
BranchMode: auto
术语表: 14 条 (docs/UBIQUITOUS_LANGUAGE.md)

## 当前工单 T-013 (P2-应用外壳+客户管理（首模块打样）) [review]
## T-013 P2-应用外壳+客户管理（首模块打样）
Resolution: 根因: P1 底座 UI 简陋（默认 antd 顶栏+占位文字），用户要求反传统 ERP、更直观易用；修复: ①设计定稿（用户确认）——示波器波形签名/电蓝#2458F5+示波青/离白底大圆角/编号等宽字体，设计稿 docs/测试&BUGS/ui-mock/；②前端重做——登录页（深蓝+示波网格+发光信号线）、AppShell（浅色窄侧栏+细顶栏）、工作台页（问候/动作卡/示例数据/最近客户/待办）、客户管理页（列表+防抖搜索+建档编辑弹窗+删除）、theme.ts+app.css、路由角色守卫（工程师 /customers→403）；③后端客户模块——Customer 模型+CU 静态编号+/api/customers CRUD（读=业务+管理, 写=业务, 工程师403）+名称唯一+q搜索+limit+PATCH exclude_unset 支持清空+alembic 0003；验证: pytest 40 全绿（test_customers 4 用例），tsc+vite build 通过，真 uvicorn+dist Playwright 端到端全过（登录/建客户/搜索/编辑/工程师403/admin只读），截图 ui-mock/real-*.png
Status: review

> 设计方向（2026-09-14 用户确认）：反传统 ERP——角色工作台首页、浅色窄侧栏、大圆角卡片留白、
> 示波器波形为签名元素（登录页/Logo/顶栏脉动点）、编号等宽字体一等公民。
> 设计稿: docs/测试&BUGS/ui-mock/{login,workbench}.html|png
> 权限（设计规格 §5）: 客户 = 业务管理 / 工程师无权限 / 管理查看。

- [x] 后端 Customer: 模型 + CU 静态编号 + schema + /api/customers CRUD（RBAC: 读=业务+管理, 写=业务）
- [x] 后端: alembic 0003_customers 迁移 + pytest（RBAC/编号/搜索/增删改）
- [x] 前端: 主题 token（电蓝 #2458F5 / 示波青 / 离白底）+ antd ConfigProvider
- [x] 前端: 登录页重做（深蓝+示波网格+发光信号线+品牌区+白浮层表单）
- [x] 前端: AppShell 外壳（浅色窄侧栏 Logo/菜单/即将上线位/用户卡 + 细顶栏 标题/状态点/⌘K 搜索/铃铛）
- [x] 前端: 工作台页（问候/大动作卡/概览示例数据卡/最近客户(真实)/待办(示例)）
- [x] 前端: 客户管理页（列表+搜索+新建/编辑弹窗+删除, 角色差异: 管理只读, 工程师隐藏入口）
- [x] 前端: 路由与角色守卫（工程师访问 /customers → 403 提示页）


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
- [ ] **T-013** P2-应用外壳+客户管理（首模块打样） — review  ✓已记录修复

## 阻塞
(无)

<!-- GENERATED-BY-ZCODE -->