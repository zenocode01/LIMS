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

## T-008 修复: Windows 脚本中文编码导致 GBK 乱码/解析风险
Resolution: 根因: setup.ps1/start.bat 以 UTF-8(无 BOM) 写中文，中文 Windows 的 cmd(GBK/CP936) 与 PowerShell 5.1(无 BOM 按 ANSI 读) 解析乱码——真机 start.bat 报「涓嶅瓨鍦」；且 UTF-8 中文字节被 GBK 当双字节字符解析，trail 字节可能吞掉后续 ASCII（引号/反斜杠），存在脚本语法被破坏的风险（setup.ps1 可能因此中途失败，venv 未建成）；修复: 两脚本整体重写为纯 ASCII 英文提示（保留 CRLF 与全部逻辑），start.bat 的 venv 缺失错误升级为输出实际检查路径 + setup 命令，便于自诊断；验证: LC_ALL=C grep 非 ASCII 字符为 0，file 确认 CRLF，pytest 36 全绿(TestCommand 真实执行)，ps1/bat 逐行人工审查(Push/Pop 配对、无 PS7 语法、bat 括号配对)；真机复验待用户 git pull 后重跑 setup.ps1
Status: done

- [x] setup.ps1/start.bat 重写为纯 ASCII（英文提示）+ CRLF；start.bat 错误信息输出实际检查路径与 setup 命令

## T-009 修复: setup.ps1 Split-Path -Parent -Parent 在 PS 5.1 非法
Resolution: 根因: setup.ps1 第 8 行 Split-Path $PSScriptRoot -Parent -Parent——Windows PowerShell 5.1 的 -Parent 是 switch 参数不可叠加（真机报 ParameterAlreadyBound/ParameterAlreadyBound,Microsoft.PowerShell.Commands.SplitPathCommand），PS7 中 -Parent 改为 int 需 -Parent 2，两种写法都错；修复: 改嵌套写法 Split-Path (Split-Path $PSScriptRoot -Parent) -Parent（PS 5.1 与 PS7 双兼容的标准 idiom）；验证: perl 替换保留 CRLF，file 确认 ASCII+CRLF，非 ASCII 扫描为 0，全脚本逐行人工审查（本机无 pwsh：#Requires/Get-Command/$LASTEXITCODE/Push-Pop 配对/原生命令 2>$null/bat if 块 %cd% 解析均过），pytest 36 全绿（TestCommand 真实执行）；真机复验待用户 git pull 后重跑 setup.ps1
Status: done

- [x] 第 8 行改为嵌套写法 Split-Path (Split-Path $PSScriptRoot -Parent) -Parent（PS 5.1/PS7 双兼容），CRLF/纯 ASCII 验证通过

## T-010 修复: setup.ps1 第8行丢失 $root 变量 (T-009 回归)
Resolution: 根因: T-009 用 perl -pi -e 's/.../$root = .../' 替换时，替换串（s/// 右侧）中的 $root 被 perl 当作 perl 变量展开成空字符串，导致第 8 行变成「 = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent」——丢失赋值左值。该写法 PowerShell 语法合法（被解析为调用名为 '=' 的命令），故 ParseFile 报 PARSE OK，但真机运行时报 "The term '=' is not recognized"；修复: 第 8 行恢复为 $root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent（改用 edit 工具精确子串替换，规避 perl 变量展开）；验证: 安装 pwsh 7.6.5（经 gitproxy 代理），复刻用户 E:\02-AREA\LIMS\LIMS 目录结构 + 假 python/node/npm 搭 mock 真跑——happy path 6 步全过 EXIT 0、无 Python 时干净报错 exit 1、venv 不存在时正确走 Creating venv 分支，路径解析 root/backend/frontend 全部正确，CRLF/纯 ASCII 验证通过，pytest 36 全绿（TestCommand 真实执行）；真机待用户 git pull 后重跑复验
Status: done

- [x] 第 8 行恢复 $root 前缀（perl 替换回归）；mock 环境真跑 setup.ps1 全分支验证（happy path 6 步 EXIT 0 / Python 缺失报错 / venv 不存在建分支）
