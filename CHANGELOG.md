# 变更日志

## [未发布]

**P3-标准库（标准+测试项目+设备简表）**（T-018）：新增标准库——标准用官方号（如 GB 9254-2028，不自定义编号）；测试项目含类别 EMI/EMS（属性字段不入编号）、方法、判据；设备简表 `EQ-NNN` 静态编号；权限按设计规格 §5（业务/工程师查看、管理维护）；前端标准库页双 Tab + 项目动态编辑器；pytest 60 全绿

**P2-样品管理（样品状态机+流转留痕）**（T-017）：新增样品模块——编号 `S-EMC-YYYYMMDD-流水`（业务线伞类，按日归零）；状态机 已登记→在测→已返→已报废，每次流转写入留痕表（操作人/备注/时间，倒序展示）；权限按设计规格 §5（业务登记/流转、工程师查看、管理全量）；前端样品管理页（留痕时间线）+ 委托详情样品区；pytest 56 全绿

**P2-委托管理（委托单状态机+从报价一键转入）**（T-016）：新增委托单模块——编号 `C-YYYYMMDD-流水`（按日归零）；状态机 草稿→已确认→测试中→已出报告→已完成，任意非终态可终止（管理，留操作人+原因）；已落单报价一键转委托（继承客户+明细摘要，报价置「已转委托」，防重转）；权限按设计规格 §5（业务建/编/确认、工程师查看、管理全量+终止）；前端委托管理页+报价页转委托接线+工作台入口；pytest 51 全绿

**修复: 登录页右侧卡片过大**（T-015）：根因: 登录卡片 max-width 400px + 大 padding + size=large 控件，整体偏大；修复: max-width 356px、padding 34/30/26、圆角 16、标题 19px、表单项距 18px、输入框/按钮降默认高度 32px、底部备注收窄，卡片高度约 -25%；验证: tsc+vite build 通过，重启 lims 服务后截图对比（ui-mock/real3-login.png）

**P2-报价管理（报价单状态机+明细）**（T-014）：根因: 主流程起点“建报价单”未落地，业务无法从客户走到委托；修复: ①后端——Quotation/QuotationItem 模型（明细=项目×数量×单价，金额读时计算）+状态机 草稿→发出→已落单→已转委托(终态,T-015 接通)/草稿|已发出→已取消（非法迁移 409）+/api/quotations CRUD+issue/finalize/cancel 动作端点（读=业务+管理, 写=业务, 工程师 403）+编号 Q-YYYYMMDD-流水（no_quote 按日归零）+名称/编号/客户名搜索+状态筛选+alembic 0004；②前端——报价列表页（状态 Tag 色板/搜索/状态筛选/新建）、详情 Drawer（明细表+状态动作按钮, 已落单显示禁用态“一键转委托单”占位）、建单/编辑弹窗（客户选择+动态明细行编辑器+合计实时计算）、侧栏报价管理+工作台“新建报价”动作卡激活；③动效层（motion-web 技能产品型克制派）——登录信号线 draw-on（pathLength 归一化+一次性入场）、工作台/列表 stagger 入场、hover/focus 过渡、prefers-reduced-motion 全量兑底；偏差: 明细项目当前文本承载（标准库里程碑3 后挂 standard_items 引用，模型已预留注释）；验证: pytest 45 全绿（新增 test_quotes 5 用例：RBAC/编号/状态机/非法迁移/仅草稿可编辑/搜索筛选），tsc+vite build 通过，真 uvicorn+dist Playwright 端到端（建单合计 11000/发出/落单/取消/筛选/工程师 403/admin 无新建）截图存档 ui-mock/real2-*.png；附带: 修复前端提交 payload 漏 customer_id 的 bug（E2E 422 捉出）；术语: 已落单/标准项目 入术语表

**P2-应用外壳+客户管理（首模块打样）**（T-013）：根因: P1 底座 UI 简陋（默认 antd 顶栏+一行占位），用户要求反传统 ERP、更直观易用；修复: ①设计方向定稿（用户确认）——示波器波形签名元素/电蓝#2458F5+示波青/离白底大圆角/编号等宽字体，静态设计稿 docs/测试&BUGS/ui-mock/；②前端重做——登录页（深蓝+示波网格+发光信号线+品牌区）、AppShell（浅色窄侧栏 Logo/菜单/即将上线位/用户卡+细顶栏 标题/脉动状态点/⌘K 搜索/铃铛）、工作台页（问候/大动作卡/概览示例数据/最近客户真实/待办示例）、客户管理页（列表+防抖搜索+建档/编辑弹窗+删除空态引导）、theme.ts+app.css token、favicon/标题、路由与角色守卫（工程师 /customers → 403 页）；③后端客户模块——Customer 模型+CU 静态编号（numbering 复用）+/api/customers CRUD（读=业务+管理, 写=业务, 工程师 403）+名称唯一+q 模糊搜索+limit+PATCH exclude_unset 支持清空字段+alembic 0003；验证: pytest 40 全绿（新增 test_customers 4 用例：RBAC/编号 CU-001→002/409/搜索/更新/清空/删除/404/未认证 401），tsc+vite build 通过，真 uvicorn+dist 端到端 Playwright 走通（登录/工作台/建客户/按编号搜索/编辑/工程师 403/admin 无新建按钮），截图存档 ui-mock/real-*.png；术语: 工作台/示例数据 入术语表

**Windows start/stop 服务脚本**（T-012）：根因: 需 Windows 服务化启停（原 start.bat 仅前台，无停止手段）；修复: start.bat 升级后台模式（start /MIN 最小化窗口 + 输出重定向 backend\lims.log + 启动后 netstat 端口状态检查），新增 stop.bat（netstat 找 PORT 监听 PID + taskkill /F 精准杀，按端口不误伤其他 python/node 程序）；附带: README Windows 章节同步（启停说明 + 端口变量一致性提醒）；验证: 两脚本纯 ASCII + CRLF，逐行审查批处理语法并修掉 if 块内 echo 含括号会提前闭合代码块的陷阱，netstat/findstr/taskkill 管道与 for /f tokens=5 解析核对；pytest 36 全绿；真机待 git pull 后双击 start/stop 复验

**修复: pip install backend 打包失败 + setup.ps1 静默吞错误**（T-011）：根因: ①backend/ 含 app/ 与 alembic/ 两个顶层目录，setuptools flat-layout 自动发现报 "Multiple top-level packages"，pip install 失败 → venv 未装任何依赖（alembic/bcrypt 缺失）；②setup.ps1 的 $ErrorActionPreference=Stop 对原生命令退出码无效，失败被静默吞掉误报 "Setup complete!"；修复: pyproject.toml 加 [tool.setuptools.packages.find] include=["app*"]（排除 alembic/tests），setup.ps1 每步原生命令后检查 $LASTEXITCODE 并 fail-fast 报 [ERROR]；验证: Linux 重建 venv 真跑 pip install 成功（import app.main 7 路由/子包/bcrypt/alembic 均可用，alembic upgrade+seed 通过），pwsh mock 验证 happy path 6 步 EXIT 0 + pip 失败停在 3/6 报 [ERROR] exit 1 不误报成功，CRLF/纯 ASCII 通过，pytest 36 全绿；真机待 git pull 后重跑复验

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

