# STATUS — 当前状态总览

> 由 zcode ticket status 自动生成，请勿手写。Agent 先读本文件即可了解全貌；细节按需再读对应文件。

## 关键状态
Phase: commit
Current Ticket: T-015
Domain: 实验室信息管理系统（LIMS），领域 EMC（电磁兼容）；P2 模块开发中——客户/报价（状态机 草稿→发出→已落单→已转委托）
TestCommand: cd backend && python3 -m pytest
BranchMode: auto
术语表: 16 条 (docs/UBIQUITOUS_LANGUAGE.md)

## 当前工单 T-015 (修复: 登录页右侧卡片过大) [review]
## T-015 修复: 登录页右侧卡片过大
Resolution: 根因: 登录卡片 max-width 400px + padding 44/40 + 大尺寸控件（size=large），整体偏大；修复: max-width 356px、padding 34/30/26、圆角 16、标题 19px、表单项距 18px、输入框/按钮降为默认高度（32px）、底部备注收窄，卡片整体高度约 -25%；验证: tsc+vite build 通过，重启 lims 服务后 Playwright 截图对比（real3-login.png）
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
- [ ] **T-015** 修复: 登录页右侧卡片过大 — review  ✓已记录修复

## 阻塞
(无)

<!-- GENERATED-BY-ZCODE -->