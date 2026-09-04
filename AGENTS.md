# AGENTS.md — 工单工作台协议入口
本仓库使用 zcode 工单工作台管理 AI Vibe Coding 工作流。任何 Coding Agent 接手本仓库前，先读完本文件。

## 这是什么
三层系统中，本文件是协议层入口。它定义了：
- 两个状态机（Agent 阶段机 + 工单生命周期机）
- 文件锚点约定（脚本解析的最小标记）
- 你的工作流职责

## 接手仓库：先看什么（省 token）
1. 先读 `STATUS.md`（单屏总览：Phase / Current Ticket / Domain / 当前工单全文 / 工单列表 / 术语表条数），或直接运行 `zcode ticket context`。
2. 需要细节时再按需读：`docs/UBIQUITOUS_LANGUAGE.md`（术语）、`docs/ADR/`（决策）、`docs/CONTEXT.md`（领域细节）、`tickets.md` 当前工单块（STATUS.md 已含）。
3. **不要一次性读完所有项目文档** —— 按需读取，节省上下文。

## 两个状态机

### Agent 阶段机（你当前的位置）
```
analyze → plan → implement → verify → review → commit → analyze
```

- `analyze`：理解领域，更新 `docs/CONTEXT.md` 的 `Domain:`，新术语用 `zcode ticket gloss add` 记录。
- `plan`：把工作拆成 `tickets.md` 中的工单（或用 `zcode ticket add`）。
- `implement`：实现工单内容。
- `verify`：运行验证产物（测试/脚本），确认绿。
- `review`：对照标准 + 规范自查。
- `commit`：提交并记录修复情况，然后 close 进入下个工单。

### 工单生命周期机（任务的持久状态）
```
backlog → in-progress → review → done
    ↑         ↑  ↖       ↓
    └─────────┴──── blocked → backlog
```

## 你的职责（严格）
1. **绝不手动改状态锚点**。用 `zcode ticket` 命令推进，脚本会校验合法性；状态命令会自动刷新 `STATUS.md`。
2. 开始干活前 `zcode ticket begin T-XXX`；完成修复后先 `zcode ticket resolve T-XXX <根因+修复+验证>` 记录修复情况，再 `zcode ticket close T-XXX`（close 强制要求 Resolution 非空）。
3. 阶段切换必须用 `zcode ticket phase <name>`，不要自己编辑 `Phase:`。
4. 提交前确保 `zcode ticket validate` 通过；pre-commit hook 会强制拦截：Phase 未到 verify/review/commit、当前工单还在 in-progress、STATUS.md 过期、Domain 已填但术语表为空。
5. 状态文件（`docs/CONTEXT.md`、`tickets.md`）的**内容**可以自由写，但**锚点行**（`Phase:`、`Status:`、`Current Ticket:`、`Domain:`、`Depends:`、`Resolution:`、`TestCommand:`、`BranchMode:`）必须格式正确。
6. `BranchMode: auto` 时，`begin` 自动切到 `vibe/T-XXX` 分支、`close` 自动合并回主分支——**不要手动改分支**，除非工作流出错。
7. 遇到领域术语（歧义、专有名词、命名约定）立即用 `zcode ticket gloss add <术语> <定义>` 记入 `docs/UBIQUITOUS_LANGUAGE.md`。
8. **close 自动收尾**（无需人工）：`CHANGELOG.md` 缺本工单号时自动从 Resolution 补录（版本自动 bump）；`tickets.md` / `STATUS.md` / `docs/CONTEXT.md` 锚点 / `.vibe/` / `CHANGELOG.md` 自动提交（`T-XXX 状态收尾`），工作区保持干净。
9. **人工同步**（随工单提交）：`README.md` / `AGENTS.md` / **术语表（本次引入的新术语 gloss add）** / 技能清单（ask-zcode / skills/README / marketplace.json）按本次变更同步——**不允许关单后文档未更新**。

## 修复类工单流程（记录修复情况）
1. `zcode ticket add "修复: <问题>"` → `zcode ticket begin T-XXX`
2. analyze：定位根因，更新 `Domain:` 与领域理解
3. `zcode ticket phase plan` → `zcode ticket phase implement`：改代码/配置
4. `zcode ticket phase verify`：跑测试（配了 `TestCommand:` 会真实执行；否则 `--green`）
5. `zcode ticket transition T-XXX review`：实现完成，工单进 review
6. `zcode ticket resolve T-XXX "根因: ...；修复: ...；验证: ..."` ← 修复记录，close 前必须
7. 更新相关文档：`CHANGELOG.md` 条目必须含 `T-XXX`（否则 close 被拒）；README/AGENTS/技能清单按需同步
8. `zcode ticket phase review --green` → `zcode ticket phase commit --pass` → git commit
9. `zcode ticket close T-XXX`（校验 Resolution 非空 + 已提交 + CHANGELOG 已记录 → 合并分支 → Phase 复位）

## 常用命令

```
zcode ticket add [title]            # 交互式新增工单（自动编号 T-XXX）
zcode ticket begin <ticket>         # 拾取工单 → in-progress, Phase=analyze（依赖守卫 + 自动开分支）
zcode ticket phase <name> [flags]   # 推进阶段（守卫 + 验证证据留痕）
zcode ticket transition <t> <s>     # 流转工单状态
zcode ticket resolve <t> <note>     # 记录修复情况（根因+修复+验证）
zcode ticket close <ticket>         # review→done（校验 Resolution + 已提交 + 合并分支）
zcode ticket context [ticket]       # 按需上下文摘要（接手仓库先跑它）
zcode ticket gloss [term|add]       # 术语表：列出 / 查询 / 记录新词
zcode ticket status                 # 刷新 STATUS.md（状态命令会自动刷新）
zcode ticket validate               # 全量校验（含依赖环、术语表、STATUS 保鲜）
zcode ticket next                   # 建议下一步（可拾取/依赖未满足/进行中）
zcode ticket log                    # 倒序查看流转历史
zcode ticket projects / switch      # 多项目总览 / 切换
```

phase 的 flags：
- `--green` 验证绿（verify→review）
- `--red` 验证红（verify→implement）
- `--pass` 审查通过（review→commit）
- `--reject` 审查打回（review→implement）
- `--force` 跳过验证产物守卫

## 验证证据
- `docs/CONTEXT.md` 配了 `TestCommand:`（如 `pytest`）时，`zcode ticket phase verify` 会**真实执行**并记录退出码+输出到 `.vibe/evidence/`；`--green` 仅在测试真跑绿时放行，`--red` 仅在测试失败时放行。
- `TestCommand:` 留空则退回自证 flag（`--green`/`--red` 由 Agent 声明）。

## 文件锚点约定

| 文件 | 锚点 | 取值 |
|---|---|---|
| `docs/CONTEXT.md` | `Phase:` | analyze/plan/implement/verify/review/commit |
| `docs/CONTEXT.md` | `Current Ticket:` | T-XXX（空 = 无进行中工单） |
| `docs/CONTEXT.md` | `Domain:` | 领域理解摘要 |
| `docs/CONTEXT.md` | `TestCommand:` | 验证命令（可空） |
| `docs/CONTEXT.md` | `BranchMode:` | auto/manual |
| `tickets.md` | `## T-XXX 标题` | 工单块 |
| `tickets.md` | `Status:` | backlog/in-progress/review/done/blocked |
| `tickets.md` | `Depends:` | 依赖的工单 ID |
| `tickets.md` | `Resolution:` | 修复情况（根因+修复+验证），close 前必须 |
| `docs/UBIQUITOUS_LANGUAGE.md` | `## 术语` + `- **含义**：` | 词条（zcode ticket gloss add 管理） |

## 换 Agent 说明
本协议不绑定任何具体 Agent。若换工具（如 Claude Code），写 `CLAUDE.md` 镜像本文件并接上同款 hooks，`zcode ticket` CLI 后端不变。
