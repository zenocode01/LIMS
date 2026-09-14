# CONTEXT — 当前状态与领域理解

> 本文件是工单工作台的状态中枢。**锚点行**（Phase: / Current Ticket: / Domain: / TestCommand: / BranchMode:）由脚本解析，必须格式正确。

## Status

Phase: commit
Current Ticket: T-014
Domain: 实验室信息管理系统（LIMS），领域 EMC（电磁兼容）；P2 模块开发中——客户/报价（状态机 草稿→发出→已落单→已转委托）

## 配置

TestCommand: cd backend && python3 -m pytest
BranchMode: auto

> - `TestCommand:` 验证阶段真实执行的测试命令（如 `pytest` / `npm test`）。留空则 `--green` 退回自证 flag。
> - `BranchMode:` `auto` = begin 自动开 `vibe/T-XXX` 分支、close 自动合并删除；`manual` = 关闭自动分支。

## 领域理解

（在此记录你对项目领域的理解。`Domain:` 锚点保留一行摘要，细节写在这里。新术语用 zcode ticket gloss add 记入 docs/UBIQUITOUS_LANGUAGE.md。）

- P2 业务主线（设计规格 §6）：建报价单（客户+标准项目+数量+报价）→ 发出 → 客户接受（已落单）→ 一键转委托单（继承客户/项目信息）→ 样品登记 → 确认委托（生成测试任务，里程碑3）。
- 报价权限（§5）：业务=创建/发出/落单，工程师=无权限，管理=查看。
- 报价编号：`Q-YYYYMMDD-流水`，按日归零（numbering.no_quote 已就绪）。
- 标准项目属标准库（里程碑3）；本期报价明细以项目名称文本承载，后续挂 standard_items 引用。
- UI 设计语言（T-013 定稿）：反传统 ERP——示波器波形签名、编号等宽字体、大圆角留白；动效参考 motion-web 技能（产品型克制派：完整组件状态、原生 CSS 微交互、尊重 prefers-reduced-motion）。

## 当前目标

T-014 P2-报价管理：报价单 CRUD + 状态机（草稿→发出→已落单→已取消；已转委托留给 T-015 委托模块）+ 明细行编辑 + 列表/详情；权限 业务写/管理读/工程师 403。转委托单入口本期占位（委托模块 T-015 落地后接通）。
