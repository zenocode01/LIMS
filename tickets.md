# 工单

工作拆解列表。每个工单一个块，格式：

```markdown
### T-XXX 工单标题
Status: backlog          # backlog / in-progress / review / done / blocked
Depends: T-00X           # 可选的依赖（多个用逗号分隔）
Resolution:              # 修复情况（根因+修复+验证），close 前用 zcode ticket resolve 填写
- [ ] 任务项 1
- [ ] 任务项 2
```

> 状态锚点行（`Status:` / `Depends:` / `Resolution:`）由脚本解析，**不要手动改**，用 `zcode ticket` 命令流转。
> 真实工单用 `## T-XXX` 开头（二级标题）；上面的示例用 `###` 仅为展示，不会被解析。

## 待办区
<!-- 在此补充工单 -->

## T-001 初始化工单工作台骨架
Resolution: 根因: 新项目无基线；修复: zcode ticket init 铺骨架 + 填 Domain(LIMS/EMC) + 登记 6 条术语(EMC/EMI/ESD/测试委托单/样品/测试报告)；验证: zcode ticket validate 仅剩'无工单'一条(本单完成后消失)
Status: done

- [ ] LIMS/EMC 项目基线：工单骨架、Domain、术语表

## T-002 LIMS MVP 设计规格
Resolution: 根因: 新项目无设计基线；修复: 完成 LIMS MVP 设计规格（领域模型/状态机/技术栈FastAPI+PG+React/10模块/权限矩阵/二级签发/审计设计），编号规则留专题占位；验证: 文档已评审关键决策（范围/方案A/权限/二级签发均获用户确认）
Status: done

- [ ] 领域模型/技术栈/模块/权限/报告流程设计文档；编号规则占位待专题

## T-003 设计文档自审修正
Resolution: 根因: 自审发现 5 处歧义/不一致；修复: 任务生成改为委托单确认时自动生成、委托单已出报告=全部报告签发、已完成=业务手动关闭、排程'排给自己的任务'、TestCommand 措辞；验证: 文档内部一致性重读通过
Status: done

- [ ] T-002 设计文档自审：任务生成时机/委托单状态触发/排程权限措辞等 5 处澄清
