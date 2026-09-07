# 变更日志

## [未发布]

**修复: setup.ps1 第8行丢失 $root 变量**（T-010）：根因: T-009 用 perl -pi 替换时替换串中的 $root 被 perl 当变量展开成空，第 8 行退化为「 = Split-Path ...」（PowerShell 语法合法但运行时报 "term '=' not recognized"，ParseFile 抓不到）；修复: 第 8 行恢复 $root 前缀（改用 edit 精确替换）；验证: pwsh 7.6.5 mock 环境真跑——happy path 6 步全过 EXIT 0、Python 缺失干净报错 exit 1、venv 不存在正确走创建分支，路径解析 root/backend/frontend 均正确，CRLF/纯 ASCII 验证通过，pytest 36 全绿；真机待 git pull 后重跑复验

**修复: setup.ps1 Split-Path 参数在 PS 5.1 非法**（T-009）：根因: `Split-Path $PSScriptRoot -Parent -Parent` 中 -Parent 在 Windows PowerShell 5.1 是 switch 参数不可叠加（ParameterAlreadyBound，真机报错），PS7 则要求 -Parent 2；修复: 第 8 行改嵌套写法 `Split-Path (Split-Path $PSScriptRoot -Parent) -Parent`（5.1/7 双兼容）；验证: 替换后 CRLF/纯 ASCII 验证通过，全脚本逐行人工审查（无 pwsh 环境），pytest 36 全绿；真机待 git pull 后重跑复验

**修复: Windows 脚本中文编码 GBK 乱码**（T-008）：根因: setup.ps1/start.bat 含 UTF-8（无 BOM）中文，中文 Windows 的 cmd/PowerShell 5.1 按 ANSI/GBK 解析 → 输出乱码（真机报「涓嶅瓨鍦」），且 UTF-8 字节被当 GBK 双字节字符可能吞掉 ASCII 破坏语法；修复: 两脚本重写为纯 ASCII（英文提示，保留 CRLF），start.bat venv 缺失错误改为输出实际检查路径 + setup 命令；验证: 非 ASCII 字符扫描为 0 + CRLF 验证通过，pytest 36 全绿；Windows 真机待重跑 setup.ps1 复验

**Windows 原生部署支持**（T-007）：根因: 目标 Windows 机器无法安装 Docker，现有 compose 链路不可用；修复: 后端 create_app(static_dir) 单进程托管前端 dist（/api 未命中 JSON 404/静态文件直出/SPA 回退/穿越守卫），新增 deploy/windows/setup.ps1(6 步幂等部署)+start.bat(双击启动)+.gitattributes(CRLF 强制)+README Windows 部署章节(含真机补跑清单)；附带: vite proxy 支持 LIMS_API_PROXY 覆盖；偏差: 发现 starlette 1.2 html=True 无 SPA 回退+catch-all 致非 GET 未注册 API 返 405，增 /api 全方法兑底路由；验证: pytest 36 全绿(23+13)，npm build 通过，8011 真 uvicorn 冒烟 5 项全过，CRLF/check-attr 验证；真 Windows 机补跑清单已随 README 交付

**P1-实现：基础底座**（T-006）：根因: P1 基础计划已批准，需落地基础底座；修复: 后端骨架(FastAPI+SQLAlchemy+Alembic 0001/0002)+bcrypt 密码+JWT+登录/me+三角色 RBAC API 层强制+用户管理+幂等 seed+编号服务 v2 全格式(委托/报告/样品/任务等)+前端骨架(React19+Vite+antd 登录页/路由守卫/apiFetch Bearer)+部署(Dockerfile×2/compose/nginx/README)；偏差: 本机无 docker 冒烟改 uvicorn+vite 直跑(容器链路待补跑)、alembic upgrade 由构建期移到运行时、TestCommand 用 python3(本机无 python 别名)；验证: 后端 pytest 23 全绿, 前端 tsc+vite build 通过, 冒烟 health/登录/静态页//api 代理全过

**P1-基础实现计划**（T-005）：根因: 设计已批准需拆实现计划；修复: P1-基础计划(8任务: 骨架/User+alembic/安全/登录/RBAC/编号v2/前端登录/compose部署)，自审修正6处(文件清单/cwd/conftest导入/接口签名/import位置/Dockerfile glob)；验证: 规格覆盖M1全部, 无占位符, 命名一致



**编号规则定稿+设计文档更新**（T-004）：根因: 编号规则专题讨论定稿+范围变更；修复: 编号v2(样品业务线段/记录TR{层}-{模板号}段/工单任务合并/序列按日归零/历史不兼容旧号)+新增报价管理/记录模板库/历史导入(明细级)模块+权限矩阵/主流程/数据模型(22表)/里程碑同步；验证: 全文grep无残留旧引用,内部一致性重读通过



**设计文档自审修正**（T-003）：根因: 自审发现 5 处歧义/不一致；修复: 任务生成改为委托单确认时自动生成、委托单已出报告=全部报告签发、已完成=业务手动关闭、排程'排给自己的任务'、TestCommand 措辞；验证: 文档内部一致性重读通过



**LIMS MVP 设计规格**（T-002）：根因: 新项目无设计基线；修复: 完成 LIMS MVP 设计规格（领域模型/状态机/技术栈FastAPI+PG+React/10模块/权限矩阵/二级签发/审计设计），编号规则留专题占位；验证: 文档已评审关键决策（范围/方案A/权限/二级签发均获用户确认）



**初始化工单工作台骨架**（T-001）：根因: 新项目无基线；修复: zcode ticket init 铺骨架 + 填 Domain(LIMS/EMC) + 登记 6 条术语(EMC/EMI/ESD/测试委托单/样品/测试报告)；验证: zcode ticket validate 仅剩'无工单'一条(本单完成后消失)

