# CONTEXT — 当前状态与领域理解

> 本文件是工单工作台的状态中枢。**锚点行**（Phase: / Current Ticket: / Domain: / TestCommand: / BranchMode:）由脚本解析，必须格式正确。

## Status

Phase: commit
Current Ticket: T-004
Domain: 实验室信息管理系统（LIMS），领域 EMC（电磁兼容）

## 配置

TestCommand:
BranchMode: auto

> - `TestCommand:` 验证阶段真实执行的测试命令（如 `pytest` / `npm test`）。留空则 `--green` 退回自证 flag。
> - `BranchMode:` `auto` = begin 自动开 `vibe/T-XXX` 分支、close 自动合并删除；`manual` = 关闭自动分支。

## 领域理解

（在此记录你对项目领域的理解。`Domain:` 锚点保留一行摘要，细节写在这里。新术语用 zcode ticket gloss add 记入 docs/UBIQUITOUS_LANGUAGE.md。）

## 当前目标

（本次会话要完成什么。）
