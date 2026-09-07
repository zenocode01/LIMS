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

## T-004 编号规则定稿+设计文档更新
Resolution: 根因: 编号规则专题讨论定稿+范围变更；修复: 编号v2(样品业务线段/记录TR{层}-{模板号}段/工单任务合并/序列按日归零/历史不兼容旧号)+新增报价管理/记录模板库/历史导入(明细级)模块+权限矩阵/主流程/数据模型(22表)/里程碑同步；验证: 全文grep无残留旧引用,内部一致性重读通过
Status: done

- [ ] 编号体系v2(表单层级段/样品业务线段/记录模板号)+报价管理+记录模板库+历史导入(明细级)模块,更新设计规格

## T-005 P1-基础实现计划
Resolution: 根因: 设计已批准需拆实现计划；修复: P1-基础计划(8任务: 骨架/User+alembic/安全/登录/RBAC/编号v2/前端登录/compose部署)，自审修正6处(文件清单/cwd/conftest导入/接口签名/import位置/Dockerfile glob)；验证: 规格覆盖M1全部, 无占位符, 命名一致
Status: done

- [ ] writing-plans: 骨架/认证/RBAC/编号服务/前端登录/部署 8任务TDD计划

## T-006 P1-实现：基础底座
Resolution: 根因: P1 基础计划(T-005)已批准，基础底座未实现；修复: 按计划完成 8 任务——后端骨架(FastAPI+SQLAlchemy+Alembic 0001/0002)+bcrypt+JWT+登录/me+三角色 RBAC API 层强制+用户管理+幂等 seed+编号服务 v2 全格式，前端骨架(React19+Vite+antd 登录页/路由守卫/apiFetch)，部署(Dockerfile×2+compose+nginx+README)；偏差: 本机无 docker，冒烟改 uvicorn+vite 直跑(容器链路待 P2 补跑)，alembic upgrade 移到 api 容器运行时，TestCommand 用 python3；验证: 后端 pytest 23 全绿，前端 tsc+vite build 通过，冒烟 health/登录/静态页//api 代理 4 项全过
Status: done

- [x] Task1 后端骨架 + health + 测试基线
- [x] Task2 User 模型 + Alembic 0001
- [x] Task3 bcrypt 密码 + JWT
- [x] Task4 登录 + /me + 测试 conftest
- [x] Task5 RBAC + 用户管理 + seed
- [x] Task6 编号服务 v2 全格式
- [x] Task7 前端骨架 + 登录页
- [x] Task8 部署（docker compose + nginx）

## T-007 Windows 原生部署支持
Resolution: 根因: 目标 Windows 机器无法安装 Docker，现有 compose 链路不可用；修复: 后端 create_app(static_dir) 单进程托管前端 dist（/api 未命中 JSON 404/静态文件 FileResponse 直出/SPA 回退/is_relative_to 穿越守卫），新增 deploy/windows/setup.ps1(6 步幂等部署)+start.bat(双击启动)+.gitattributes(CRLF 强制)+README Windows 部署章节(含真机补跑清单)；附带: vite proxy 支持 LIMS_API_PROXY 环境变量覆盖；偏差: 实测 starlette 1.2 的 StaticFiles(html=True) 无 SPA 回退、GET-only catch-all 致未注册 API 非 GET 方法返 405，改用自写 catch-all + /api 全方法兜底路由；验证: pytest 36 全绿(存量 23+静态 13，.vibe/evidence 真实执行留痕)，npm run build 通过，8011 真 uvicorn 冒烟 5 项全过(首页/SPA 回退/静态文件/health/api 404)，file+check-attr 确认 CRLF 与 .gitattributes 生效；真 Windows 机补跑清单已随 README 交付(6 项待补跑)
Status: done

- [x] Task1 后端静态托管（config+main+test_static 13 用例，36 全绿）
- [x] Task2 Windows 脚本（setup.ps1 + start.bat + .gitattributes CRLF）
- [x] Task3 文档+冒烟（README Windows 章节 + 8011 冒烟 5 项 + vite proxy 可覆盖）
