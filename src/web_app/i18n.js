const SANTONI_LANGUAGE_KEY = "santoniDemoLanguage";

const SANTONI_TRANSLATIONS = [
  ["Language", "语言"],
  ["Switch language", "切换语言"],
  ["English", "英文"],
  ["Page links", "页面链接"],
  ["Quick actions", "快捷操作"],
  ["User Page", "用户页"],
  ["Developer", "开发者"],
  ["Developer Entry", "开发者入口"],
  ["Developer Workflow", "开发者流程"],
  ["Developer page", "开发者页面"],
  ["Project Docs", "项目文档"],
  ["Guide", "使用说明"],
  ["Back to Demo", "返回 Demo"],
  ["Service Cases", "服务案例"],
  ["Service Manager Console", "服务经理控制台"],
  ["Changelog", "版本记录"],
  ["Hermes", "Hermes"],
  ["Hermes Integration", "Hermes 接入"],
  ["Hermes Integration Console", "Hermes 接入控制台"],
  ["Runtime, memory, tool orchestration, and self-evolution contract for Athena.", "面向 Athena 的运行时、记忆、工具调度和自我进化契约。"],
  ["Mock contract only", "仅本地 Mock 契约"],
  ["This page does not connect to a real Hermes endpoint yet. It defines the local adapter contract, memory event objects, evidence loop, and development suggestions for human review.", "本页面尚未连接真实 Hermes endpoint，只定义本地 adapter 契约、记忆事件对象、证据闭环和供人工审核的开发建议。"],
  ["Boundary", "边界"],
  ["Hermes can become Athena runtime, memory, MCP/tool orchestration, and automation layer. Santoni Agent Core remains responsible for domain workflows, guardrails, adapter permissions, evidence logs, and KPI rules.", "Hermes 可以成为 Athena 的运行时、记忆、MCP/工具调度和自动化层。Santoni Agent Core 仍负责领域工作流、guardrails、adapter 权限、证据日志和 KPI 规则。"],
  ["Self-evolution Loop", "自我进化闭环"],
  ["Adapter Contract", "接口契约"],
  ["Athena Memory Events", "Athena 记忆事件"],
  ["Development Suggestions", "开发建议"],
  ["Proposal only", "仅建议"],
  ["Focus", "关注范围"],
  ["Evaluation", "评估"],
  ["All", "全部"],
  ["Refresh Suggestions", "刷新建议"],
  ["Tool Registry Candidates", "工具注册候选"],
  ["Open Hermes Integration Console", "打开 Hermes 接入控制台"],
  ["Local adapter contract for Athena runtime, memory, tool orchestration, development suggestions, evidence logs, and KPI checks.", "面向 Athena 运行时、记忆、工具调度、开发建议、证据日志和 KPI 检查的本地 adapter 契约。"],
  ["Hermes Adapter Contract", "Hermes Adapter 契约"],
  ["Hermes Memory Event Governance", "Hermes 记忆事件治理"],
  ["Adds governed Hermes memory-event fields: `scope`, `tenant_id`, `factory_id`, `source`, `retention_policy`, `sensitivity_level`, and `promotion_status`.", "为 Hermes memory event 新增治理字段：`scope`、`tenant_id`、`factory_id`、`source`、`retention_policy`、`sensitivity_level` 和 `promotion_status`。"],
  ["Updates current Athena memory events to separate product/domain memory from future tenant/session memory.", "更新当前 Athena memory events，区分 product/domain memory 与未来 tenant/session memory。"],
  ["Shows memory governance metadata in `/hermes.html` so future customer-account memory can remain isolated and reviewable.", "在 `/hermes.html` 展示记忆治理元数据，确保未来客户账户记忆可以隔离并接受审核。"],
  ["Tianpai Training Data Pack", "天派训练数据包"],
  ["Adds `docs/training/tianpai_training_pack_v0_1.json` and `docs/training/tianpai_training_summary_v0_1.md` as the first structured Tianpai training baseline.", "新增 `docs/training/tianpai_training_pack_v0_1.json` 和 `docs/training/tianpai_training_summary_v0_1.md`，作为第一版结构化天派训练基线。"],
  ["Structures Agnes VOC plus Melos-provided Tianpai IOT output, scrap, and fault exports into field maps, data-quality findings, aggregate KPI seeds, candidate training tasks, and Hermes tenant memory-event candidates.", "将 Agnes VOC 以及 Melos 提供的天派 IOT 产量、废品、故障导出整理为字段映射、数据质量发现、聚合 KPI 种子、候选训练任务和 Hermes tenant memory event 候选。"],
  ["Marks the current Tianpai data boundary: IOT records lack order_id and machine coverage is partial, so current training supports machine/style/shift analysis before full order-flow root cause.", "标记当前天派数据边界：IOT 记录缺少 order_id，机台联网覆盖也不完整，因此当前训练先支持机台、款式、班次分析，暂不支持完整订单流根因分析。"],
  ["Tianpai APS Workflow Fragment", "天派 APS 现场流程片段"],
  ["Adds the current APS-side Tianpai workflow fragment to the structured training pack as `SRC-TPI-APS-WORKFLOW-001`.", "将当前 APS 侧天派 workflow 片段作为 `SRC-TPI-APS-WORKFLOW-001` 加入结构化训练包。"],
  ["Records the onsite workflow spine as order intake -> ERP -> APS -> IOT -> production -> quality inspection -> garment delivery.", "记录现场 workflow 主线：接单 -> ERP -> APS -> IOT -> 生产 -> 质检 -> 成衣交付。"],
  ["Adds `DQ-TPI-005` to clarify that this fragment supports workflow understanding but cannot calculate APS delay, schedule adherence, capacity variance, or order-level root cause without detailed APS schedule rows.", "新增 `DQ-TPI-005`，明确该片段可以训练 workflow 理解，但没有 APS 明细排程行时，不能计算 APS 延误、排程达成、产能偏差或订单级 root cause。"],
  ["Tianpai Actual Onsite Workflow", "天派真实现场流程"],
  ["Adds `SRC-TPI-ONSITE-WORKFLOW-001` as the confirmed Tianpai workflow note for ERP work split, APS weaving scheduling, and physical production stages.", "新增 `SRC-TPI-ONSITE-WORKFLOW-001`，作为天派 ERP 分工、APS 织造排产和物理生产阶段的已确认 workflow 说明。"],
  ["Clarifies that ERP records order totals, split deliveries, and work split; APS only schedules Tianpai weaving; IOT currently does not participate in Tianpai's actual production workflow.", "明确 ERP 记录订单总数、分批交货和分工；APS 只负责天派织造排产；IOT 目前不参与天派实际生产流程。"],
  ["Expands the Tianpai process map from yarn picking through weaving greige, pre-treatment, dyeing, inspection/replenishment, cutting, sewing, packing, needle/metal detection, storage, and container loading.", "扩展天派工序地图：领纱线、织造白坯、预处理、染色、检验/补单、裁剪、缝制、包装、验针/金属检测、存储和装集装箱。"],
  ["Tianpai Training Governance", "天派训练治理"],
  ["Adds a training-governance layer for the Tianpai general-manager persona, answer format, KPI priority, recommendation scope, terminology policy, and automation boundary.", "新增天派训练治理层，记录总经理 persona、回答格式、KPI 优先级、建议范围、术语规则和自动化边界。"],
  ["Sets the current training answer format to management summary + reason/evidence + recommended action.", "将当前训练回答格式设为：管理层摘要 + 原因/证据 + 建议动作。"],
  ["Sets KPI priority to quality > cost > delivery, keeps weaving-process recommendations allowed, and requires Athena to state missing data instead of forcing root-cause conclusions.", "将 KPI 优先级设为质量 > 成本 > 交期；允许 Athena 针对织造工序提出建议，并要求数据不足时明确说明缺失数据，而不是强行给出根因结论。"],
  ["Adds `/hermes.html` as a structured Hermes Integration Console for Athena runtime, memory, tool orchestration, and self-evolution planning.", "新增 `/hermes.html`，作为结构化 Hermes 接入控制台，用于 Athena 运行时、记忆、工具调度和自我进化规划。"],
  ["Adds mock-backed Hermes APIs: `/api/hermes/template`, `/api/hermes/overview`, and `/api/hermes/suggest`.", "新增 mock 支撑的 Hermes API：`/api/hermes/template`、`/api/hermes/overview` 和 `/api/hermes/suggest`。"],
  ["Defines memory events, evolution candidates, development suggestions, tool registry candidates, evidence logs, KPI logs, and blocked actions without storing credentials or connecting to live Hermes.", "定义 memory events、evolution candidates、development suggestions、tool registry candidates、evidence logs、KPI logs 和 blocked actions，不保存凭据，也不连接真实 Hermes。"],
  ["Version History", "版本历史"],
  ["Version Rule", "版本规则"],
  ["Patch updates change the third number. New features change the second number. Major iterations change the first number.", "小修复更新第三位；新增功能更新第二位；大版本迭代更新第一位。"],
  ["PRD First-Screen Risk Alignment", "PRD 第一屏风险卡对齐"],
  ["Aligns the Production Management Priority Engine with Athena PRD v0.1: delivery-risk order, quality/replenishment risk, and labor effective-hour risk are now the three main first-screen cards.", "将 Production Management Priority Engine 与 Athena PRD v0.1 对齐：交付风险订单、质量/补单风险、人工有效工时风险现在是第一屏三张主卡。"],
  ["Changes the priority policy to delivery > quality > cost, treating cost as a consequence metric until real purchasing, labor, rework, and freight records are connected.", "将优先级策略改为交付 > 质量 > 成本；在真实采购、人工、返工和运费记录接入前，成本作为结果指标处理。"],
  ["Adds a labor effective-hour root-cause branch so Santoni Athena can drill down by team, manual intervention, service/setup/waiting/rework, and evidence.", "新增人工有效工时根因分支，让 Santoni Athena 可以按班组、人工干预、服务/调机/等待/返工和证据下钻。"],
  ["PRD Risk-Card Evidence Details", "PRD 风险卡证据详情"],
  ["Adds PRD-required risk levels to Production first-screen risk cards: red, yellow, or gray.", "为 Production 第一屏风险卡新增 PRD 要求的风险等级：红色、黄色或灰色。"],
  ["Shows 2-3 key evidence items on each card and moves full evidence, evidence level, and data gaps into an expandable detail area.", "每张卡默认显示 2-3 条关键证据，并将完整证据、证据等级和数据缺口放入可展开详情区。"],
  ["Links local follow-up items back to their source risk-card ID so the decision loop remains traceable.", "将本地跟进事项关联回来源风险卡 ID，保持决策闭环可追溯。"],
  ["PRD Follow-Up Status Lifecycle", "PRD 跟进状态生命周期"],
  ["Aligns Production local follow-up items with the PRD lifecycle: pending confirmation, assigned, waiting for evidence, confirmed, closed, and unable to process.", "将 Production 本地跟进事项与 PRD 生命周期对齐：待确认、已分配、等待证据、已确认、已关闭、无法处理。"],
  ["Adds matching Production Console controls for confirmation, evidence waiting, closure, and unable-to-process review.", "新增匹配的 Production Console 控件，用于确认、等待证据、关闭和无法处理复核。"],
  ["Keeps all follow-up review updates metadata-only and blocked from APS, IOT, real ticket systems, machine control, and Hermes memory promotion.", "所有跟进复核更新仍只写本地 metadata，并阻止写入 APS、IOT、真实工单系统、机台控制和 Hermes 记忆提升。"],
  ["PRD First-Screen Management Summary", "PRD 第一屏管理摘要"],
  ["Adds a bilingual 3-5 line management summary to `management_priority_brief.daily_brief`.", "为 `management_priority_brief.daily_brief` 新增双语 3-5 行管理摘要。"],
  ["Summarizes delivery, quality/replenishment, labor effective hours, and data boundary before the three risk cards.", "在三张风险卡之前摘要交付、质量/补单、人工有效工时和数据边界。"],
  ["Renders the summary on `/production.html` so the general manager can read the first-screen brief before drilling into risk cards.", "在 `/production.html` 展示摘要，让总经理先阅读第一屏简报，再下钻风险卡。"],
  ["PRD Permission Boundary", "PRD 权限边界"],
  ["Adds a structured `permission_boundary` object to the Production workflow.", "为 Production workflow 新增结构化 `permission_boundary` 对象。"],
  ["Shows the general manager final-confirmation boundary on `/production.html`, including allowed Athena support actions and blocked automation actions.", "在 `/production.html` 展示总经理最终确认边界，包括 Athena 可支持动作和被禁止的自动化动作。"],
  ["Explicitly blocks schedule modification, automatic service dispatch, .co/.cx upload, machine control, employee-performance scoring, forced conclusions with insufficient evidence, and replacement of the general manager decision.", "明确禁止自动修改排程、自动派发 Service、上传 .co/.cx、控制机台、员工绩效评分、证据不足时强行下结论，以及替代总经理决策。"],
  ["Permission Boundary", "权限边界"],
  ["Human Gate", "人工确认门"],
  ["Final confirmation owner", "最终确认人"],
  ["Allowed", "可以做"],
  ["Blocked", "不会做"],
  ["PRD MVP Demo Story", "PRD MVP 演示故事线"],
  ["Adds a structured `mvp_demo_story` object to the Production workflow based on PRD section 16.", "基于 PRD 第 16 节，为 Production workflow 新增结构化 `mvp_demo_story` 对象。"],
  ["Shows a three-minute management story on `/production.html`, connecting delivery risk to quality/replenishment, labor effective hours, and service/machine stoppage signals.", "在 `/production.html` 展示三分钟管理故事线，把交付风险连接到质量/补单、人工有效工时和服务/机台停机信号。"],
  ["Links the story to evidence, object references, local follow-up items, success criteria, data boundary, and the general manager final-confirmation rule.", "将故事线关联到证据、对象引用、本地跟进事项、成功标准、数据边界和总经理最终确认规则。"],
  ["MVP Demo Story", "MVP 演示故事线"],
  ["三分钟管理故事线", "三分钟管理故事线"],
  ["Within three minutes", "三分钟内应确认"],
  ["PRD MVP Success Check", "PRD MVP 成功标准检查"],
  ["Adds a structured `mvp_success_check` object to the Production workflow based on PRD section 17.", "基于 PRD 第 17 节，为 Production workflow 新增结构化 `mvp_success_check` 对象。"],
  ["Shows a PRD success-check panel on `/production.html` for top priorities, why they matter, evidence, next confirmation owner, and missing data visibility.", "在 `/production.html` 展示 PRD 成功标准检查，覆盖前三件事、为什么重要、证据、下一步确认负责人和缺失数据可见性。"],
  ["Reports current three-minute readiness as Level 1 mock evidence and keeps real ERP/APS/IOT, labor baseline, quality records, and GM VOC as remaining data boundaries.", "将当前三分钟可用性标记为 Level 1 mock 证据，并保留真实 ERP/APS/IOT、人工基线、质量记录和总经理 VOC 作为剩余数据边界。"],
  ["MVP Success Check", "MVP 成功标准检查"],
  ["PRD 成功标准检查", "PRD 成功标准检查"],
  ["Still Needs Real Data", "仍需真实数据证明"],
  ["Coverage", "覆盖率"],
  ["PRD Alignment Audit", "PRD 覆盖审计"],
  ["PRD 覆盖矩阵", "PRD 覆盖矩阵"],
  ["Sections 1-18", "第 1-18 节"],
  ["Adds a structured `prd_alignment_audit` object to the Production workflow.", "为 Production workflow 新增结构化 `prd_alignment_audit` 对象。"],
  ["Shows a PRD coverage matrix on `/production.html` mapping sections 1-18 to implemented objects, evidence refs, and remaining gaps.", "在 `/production.html` 显示 PRD 覆盖矩阵，把第 1-18 节映射到已实现对象、证据引用和剩余缺口。"],
  ["Separates local mock MVP coverage from live customer deployment readiness so Athena does not overclaim completion.", "区分本地 mock MVP 覆盖与真实客户部署就绪度，避免 Athena 过度宣称完成。"],
  ["Remaining Open Questions", "仍需确认的问题"],
  ["Tianpai APS/ERP Export Adapter", "天派 APS/ERP 导出 Adapter"],
  ["Adds a read-only `TianpaiApsErpExportAdapter` for external no-header CSV exports.", "新增只读 `TianpaiApsErpExportAdapter`，用于读取外部无表头 CSV 导出。"],
  ["Parses Produce_Order, Weaving_Part_Order, Planned_Task, Manual_Machine_Production, Style_Component, Style_Sku, and T_Machine_Info using the `表字段` DDL field order.", "按照 `表字段` DDL 字段顺序解析 Produce_Order、Weaving_Part_Order、Planned_Task、Manual_Machine_Production、Style_Component、Style_Sku 和 T_Machine_Info。"],
  ["Exposes `/api/production/tianpai-aps-export` with standard object counts, join quality, missing fields, unmatched records, capability boundaries, and blocked write actions without copying raw customer CSV files into the repo.", "新增 `/api/production/tianpai-aps-export`，输出标准对象数量、关联质量、缺失字段、未匹配记录、能力边界和禁止写入动作，并且不把客户原始 CSV 复制进 repo。"],
  ["Production Mock + Actual Snapshot", "Production Mock + 真实快照"],
  ["Adds an `actual_data_snapshot` object to the Production workflow based on the Tianpai APS/ERP export adapter.", "基于 Tianpai APS/ERP export adapter，为 Production workflow 新增 `actual_data_snapshot` 对象。"],
  ["Shows the current data source as Mock / Tianpai APS Export on `/production.html`.", "在 `/production.html` 显示当前数据源为 Mock / Tianpai APS Export。"],
  ["Adds actual-data KPIs for total orders, near-due orders, scheduled/unscheduled weaving part orders, plan completion, report completion, machine plan load, and machine/style cylinder-gauge mismatch candidates.", "新增真实数据 KPI：总订单数、临近交期订单、已排/未排织造部件单、计划完成率、报工完成率、机台计划负载，以及机台/款式筒径针距不匹配候选。"],
  ["Mock / Tianpai APS Export", "Mock / 天派 APS 导出"],
  ["当前数据源与真实快照", "当前数据源与真实快照"],
  ["Bilingual page language switch", "全站双语切换"],
  ["Adds a shared Chinese / English language toggle to every current web page.", "为当前所有 Web 页面新增共享中英文切换按钮。"],
  ["Persists the selected language in browser local storage so navigation keeps the same language.", "将语言选择保存在浏览器 local storage 中，页面跳转后保持同一语言。"],
  ["Translates page chrome, navigation, controls, guide text, and console labels without changing business data, credentials, mock records, evidence logs, or exported test logs.", "翻译页面框架、导航、控件、操作说明和控制台标签，不改变业务数据、凭据、mock 记录、证据日志或导出测试日志。"],
  ["Production Console Chinese display", "Production 控制台中文显示"],
  ["Sets `/production.html` to default Chinese display for customer and management review.", "将 `/production.html` 设置为默认中文显示，便于客户和管理层查看。"],
  ["Localizes API-driven Production status, workflow stages, resource-lens signals, garment output, optimization signals, service request candidates, KPI logs, and evidence logs.", "中文化 API 驱动的 Production 状态、工作流阶段、资源视角信号、成衣输出、优化信号、服务请求候选、KPI 日志和证据日志。"],
  ["Keeps the English language switch available without changing mock data, adapter contracts, or read-only Production API behavior.", "保留英文切换，不改变 mock 数据、adapter 契约或只读 Production API 行为。"],
  ["Production Site Flow Layout", "生产现场链路布局"],
  ["Replaces the abstract resource-lens grid on `/production.html` with a top-down order, scheduling, machine, and garment layout.", "将 `/production.html` 上抽象的资源视角网格改为自上而下的订单、排单、机器、成衣布局。"],
  ["Adds backlog, style count, material-risk linkage, scheduled and unscheduled order counts, capacity occupation, machine status, running rate, fault machines, yield, and defect-reason summary blocks.", "新增 backlog、款式数、物料风险关联、已排/未排订单、产能占用率、机器状态、开机率、故障机器、良品率和不良原因统计模块。"],
  ["Keeps 人机料法环测 evidence available, but presents it through production-flow language for customer and management review.", "保留人机料法环测证据，但用生产流程语言呈现，便于客户和管理层查看。"],
  ["APS / IOT Adapter Contract", "APS / IOT 接口契约"],
  ["Adds a read-only `/api/production/adapter-contract` endpoint based on APS and IOT page research.", "基于 APS 和 IOT 页面调研新增只读 `/api/production/adapter-contract` 接口。"],
  ["Documents APS/IOT source pages and field mapping for order, scheduling, machine execution, program evidence, and garment output objects.", "记录 APS/IOT 来源页面，以及订单、排单、机器执行、程序证据和成衣输出对象的字段映射。"],
  ["Updates the production mock snapshot and console metrics to use real-system-like fields such as backlog, remaining quantity, scheduled quantity, capacity occupation, .co/.cx program files, scrap quantity, and yield.", "更新 production mock 快照和控制台指标，使用更接近真实系统的 backlog、剩余数量、已排数量、产能占用、.co/.cx 程序文件、废弃数量和良品率字段。"],
  ["Corrects seamless machine program-file terminology to `.co` / `.cx` file extensions.", "将无缝机台程序文件术语更正为 `.co` / `.cx` 文件扩展名。"],
  ["Renames Production adapter contract fields to `co_file` / `cx_file`.", "将 Production adapter contract 字段改为 `co_file` / `cx_file`。"],
  ["Updates mock APS/IOT evidence, docs, UI localization, and tests so the program-file wording stays aligned with seamless machine practice.", "更新 mock APS/IOT 证据、文档、UI 本地化和测试，确保程序文件表述符合无缝机台实践。"],
  ["Keeps the developer changelog preview working with the shared language switch by avoiding global script variable collisions.", "避免全局脚本变量冲突，保证 developer 页 changelog preview 与共享语言切换一起正常工作。"],
  ["Santoni Athena", "Santoni Athena"],
  ["Read-only", "只读"],
  ["Ask why a KPI changed. Santoni Athena will trace root cause from structured mock APS/IOT data and evidence logs.", "对看板 KPI 提问原因，Santoni Athena 会从结构化 mock APS/IOT 数据和证据日志中追溯根因。"],
  ["Scrap Rate Analysis", "废弃率分析"],
  ["OEE Drilldown", "OEE 下钻"],
  ["Downtime Source", "停机来源"],
  ["Delivery Risk", "交付风险"],
  ["Machine Bottleneck", "机台瓶颈"],
  ["Data Gap", "数据缺口"],
  ["Executive Answer", "管理层回答"],
  ["Conclusion", "结论"],
  ["Reason/Evidence", "原因/证据"],
  ["Risk", "风险"],
  ["Recommendation", "建议"],
  ["Data Gaps", "数据缺口"],
  ["Example: why is scrap rate around 4%?", "例如：为什么废弃率是4%？"],
  ["Ask", "提问"],
  ["Select a question or type a dashboard KPI question.", "选择一个问题或直接输入看板指标问题。"],
  ["Santoni Athena Production Insight Naming", "Santoni Athena 生产洞察命名"],
  ["Renames the production KPI question panel from BI-style wording to Santoni Athena for customer-facing presentation.", "将生产 KPI 提问面板从 BI 风格表述改为面向客户展示的 Santoni Athena。"],
  ["Keeps the underlying read-only `/api/production/chatbi` contract for KPI root-cause analysis compatibility.", "保留底层只读 `/api/production/chatbi` 契约，以兼容 KPI 根因分析能力。"],
  ["Clarifies documentation that the current production snapshot is loaded from local static mock data, not dynamically scraped from APS or IOT web pages.", "文档中明确当前生产快照来自本地静态 mock 数据，不是从 APS 或 IOT 网页动态抓取。"],
  ["Production Order ID Workflow Spine", "生产订单号工作流主线"],
  ["Order Key", "订单主键"],
  ["The order number is the unique workflow key connecting order intake, ERP, APS, IOT, production, service candidates, and garment output.", "订单号是串联接单、ERP、APS、IOT、生产、服务候选和成衣输出的唯一工作流主键。"],
  ["Adds a visible Production Console note that 订单号 / order_id is the unique workflow key.", "在 Production Console 页面明确标注 订单号 / order_id 是唯一工作流主键。"],
  ["Adds `workflow_primary_key` to the Production template and overview API so future APS/IOT database integration preserves traceability.", "在 Production template 和 overview API 中新增 `workflow_primary_key`，确保未来 APS/IOT 数据库集成保留可追溯性。"],
  ["Clarifies that order_id joins order intake, ERP, APS, IOT, production/service candidates, and garment output records.", "明确 order_id 串联接单、ERP、APS、IOT、生产/服务候选和成衣输出记录。"],
  ["Santoni Athena Production Insight", "Santoni Athena 生产洞察"],
  ["Adds a read-only Santoni Athena panel on `/production.html` for KPI question-to-data root-cause analysis.", "在 `/production.html` 新增只读 Santoni Athena 面板，用于 KPI 问数和根因分析。"],
  ["Adds `/api/production/chatbi` to analyze scrap rate, OEE, downtime, material risk, order delay, and overall production snapshots from structured mock APS/IOT data.", "新增 `/api/production/chatbi`，基于结构化 mock APS/IOT 数据分析废弃率、OEE、停机、物料风险、订单延误和生产总览快照。"],
  ["Returns metric snapshots, ranked root causes, recommended actions, next drilldowns, and evidence references instead of free-form chatbot answers.", "返回指标快照、排序根因、建议动作、下一步下钻和证据引用，而不是自由聊天式回答。"],
  ["Keeps the agent read-only: it does not change schedules, upload `.co/.cx` files, control machines, write APS/IOT data, or auto-dispatch service requests.", "保持 Agent 只读：不改排程、不上传 `.co/.cx` 文件、不控制机台、不写入 APS/IOT 数据，也不自动派发服务请求。"],
  ["Design Intake Structuring Console naming", "Design Intake 结构化中台命名"],
  ["Renames the former Athena MVP page chrome to Design Intake Structuring Console so it is presented as a Design Agent data-structuring middleware testbench.", "将原 Athena MVP 页面框架改名为 Design Intake Structuring Console，使其明确呈现为 Design Agent 数据结构化中台测试台。"],
  ["Adds top-of-page guidance explaining current usage, mock output limits, future design-software/file-import role, and why it is not a manual design-exhaustion tool.", "在页面顶部新增说明，解释当前用法、mock 输出限制、未来接入设计软件/文件导入后的作用，以及为什么它不是手动设计穷举工具。"],
  ["Keeps the existing `/athena-mvp.html` URL and API paths for compatibility while narrowing navigation labels and project docs.", "为兼容性保留现有 `/athena-mvp.html` URL 和 API 路径，同时收窄导航标签和项目文档表述。"],
  ["Production", "生产"],
  ["Design Intake", "设计输入"],
  ["Athena MVP", "Athena MVP"],
  ["Loading", "加载中"],
  ["Connecting", "连接中"],
  ["Checking API", "检查 API"],
  ["Not run", "尚未运行"],
  ["Image", "图片"],
  ["Send", "发送"],
  ["Clear Memory", "清空记忆"],
  ["Export Test Log", "导出测试日志"],
  ["Try real platform", "尝试真实平台"],
  ["Platform username", "平台用户名"],
  ["Platform password", "平台密码"],
  ["Username", "用户名"],
  ["Password", "密码"],
  ["Describe a seamless running top with breathable zones for Decathlon...", "描述一款给迪卡侬使用的无缝跑步上衣，例如需要透气区域..."],
  ["Tell me who you are and what you need. Example: I am a designer... / My machine stopped...", "告诉我你的身份和需求。例如：我是设计师... / 我的机器停机了..."],
  ["Memory cleared. Start a new test conversation.", "记忆已清空。请开始新的测试对话。"],
  ["Tell me who you are and what you need: a knitting design brief, reference image, or machine service issue. I will route the request to the correct sub-agents.", "告诉我你的身份和需求：针织设计 brief、参考图片或机器服务问题。我会路由到对应的 sub-agent。"],
  ["Backend is not reachable. Please keep the local demo server running with: python scripts/run_web_demo.py", "后端服务未连接。请保持本地服务运行：python scripts/run_web_demo.py"],
  ["Credentials are sent only with this request and are not exported in test logs.", "凭据只随本次请求发送，不会导出到测试日志。"],
  ["Identity", "身份识别"],
  ["Main Agent Auto Routing", "Main Agent 自动路由"],
  ["Tell the agent who you are or what you need. It will infer whether to continue as Designer or Equipment Engineer.", "告诉 agent 你的身份或需求，它会判断继续进入 Designer 还是设备工程师流程。"],
  ["Role: Auto", "角色：自动"],
  ["Agent Model Progress", "Agent 模型进度"],
  ["Loading operating model...", "正在加载 operating model..."],
  ["Latest Changelog", "最新版本记录"],
  ["Loading changelog...", "正在加载版本记录..."],
  ["Lock-machine Activation Tool", "锁机激活工具"],
  ["Designer Workflow", "设计师流程"],
  ["Service Assist Workflow", "服务协助流程"],
  ["Main Agent", "Main Agent"],
  ["Santoni AI Service Assistant", "Santoni AI 服务助手"],
  ["AI Knitting Agent", "AI Knitting Agent"],
  ["Hello, I am Santoni AI Assistant", "您好，我是 Santoni AI 助手"],
  ["I can help clarify seamless knitting design requirements and assist with equipment service troubleshooting.", "我可以帮助梳理无缝针织设计需求，也可以协助排查设备服务问题。"],
  ["Design Request", "设计需求"],
  ["Equipment Issue", "设备故障"],
  ["Lock-machine Activation", "锁机激活"],
  ["Restart", "重新开始"],
  ["Please enter your request, for example: SM8 machine miss-pattern, serial number 9009452, fabric issue repeats on the same path.", "请输入您的需求，例如：SM8 机器错花，序列号 9009452，布面固定在同一路出现问题。"],
  ["Upload image", "上传图片"],
  ["Santoni Platform", "Santoni 平台"],
  ["Please enter platform account", "请输入平台账号"],
  ["This account and password are only used for this real platform request and will not be saved to local files.", "该账号密码仅用于本次真实平台请求，不会保存到本地文件。"],
  ["Use mock mode", "使用模拟模式"],
  ["Continue real test", "继续真实测试"],
  ["I am a designer and want to develop a seamless sports top. It needs breathability and quick dry. Please help clarify the design request first.", "我是设计师，想开发一款无缝运动上衣，需要透气快干，请先帮我梳理设计需求。"],
  ["I am a factory equipment engineer. The machine has a fault and I need online troubleshooting first.", "我是工厂设备工程师，机器出现故障，需要先在线排查。"],
  ["The machine has a lock-machine activation issue and I need help handling it.", "机器出现锁机激活相关问题，我需要协助处理。"],
  ["Athena MVP Workflow Console", "Athena MVP 工作流控制台"],
  ["Design Agent Data Layer", "Design Agent 数据层"],
  ["Design Intake Structuring Console", "设计输入结构化中台"],
  ["Design Input To Production Readiness", "从设计输入到量产准备"],
  ["Structured workflow template for Santoni knitting onsite digital workforce.", "面向 Santoni 针织现场数字员工的结构化工作流模板。"],
  ["Structured testbench for turning design files, design notes, Style3D/CLO assets, AI images, or technical packages into auditable data objects.", "用于把设计文件、设计说明、Style3D/CLO 资产、AI 图片或技术包整理成可审计数据对象的结构化测试台。"],
  ["Positioning guardrail", "定位边界"],
  ["Athena is not a generic natural-language design agent and not another Style3D. This demo converts Style3D/CLO/AI/image/TP/design-request inputs into SWS/Arachne engineering brief, manufacturability check, sampling feedback, revision suggestion, and production readiness evidence.", "Athena 不是泛自然语言设计 agent，也不是另一个 Style3D。本 demo 将 Style3D/CLO/AI/图片/TP/设计需求输入转化为 SWS/Arachne 工程 brief、可制造性检查、打样反馈、修订建议和量产准备证据。"],
  ["What this page is", "这个页面是什么"],
  ["This is a Design Agent data-structuring middleware test page. It checks whether design inputs can be normalized into structured objects for engineering, sampling, evidence logging, and future tool handoff. It is not the full Athena MVP, not a generic chatbot, not a Style3D replacement, and not a manual design-exhaustion tool.", "这是一个 Design Agent 数据结构化中台测试页，用来检查设计输入是否能被规范化为工程、打样、证据日志和未来工具交接可用的结构化对象。它不是完整 Athena MVP，不是泛聊天机器人，不是 Style3D 替代品，也不是手动设计穷举工具。"],
  ["How to use it now", "现在怎么用"],
  ["Paste or describe a design request, Style3D/CLO note, AI/reference image note, or technical package summary, then run the structuring test. The current output is deterministic mock data used to review whether the object schema, required fields, risk checks, evidence log, and SWS/Arachne handoff shape make sense.", "粘贴或描述设计需求、Style3D/CLO 说明、AI/参考图片说明或技术包摘要，然后运行结构化测试。当前输出是确定性的 mock 数据，用于评审对象 schema、必填字段、风险检查、证据日志和 SWS/Arachne 交接形态是否合理。"],
  ["Future role after design-software or file import", "接入设计软件或文件导入后的作用"],
  ["When real design files or design-software adapters are connected, this layer should parse imported assets into standard design_request, source_asset, engineering_brief_candidate, manufacturability_check, sampling_feedback, revision_suggestion, evidence_log, and KPI objects. Constraint discovery and training should be automated from real design, sampling, engineering, and production data rather than typed manually into this page.", "当接入真实设计文件或设计软件 adapter 后，这一层应把导入资产解析为标准 design_request、source_asset、engineering_brief_candidate、manufacturability_check、sampling_feedback、revision_suggestion、evidence_log 和 KPI 对象。约束发现和训练应来自真实设计、打样、工程和生产数据的自动化沉淀，而不是长期手动输入到这个页面。"],
  ["Input Object", "输入对象"],
  ["Load Example", "载入示例"],
  ["Source Type", "来源类型"],
  ["Customer / Project", "客户 / 项目"],
  ["Product Category", "产品品类"],
  ["Target User", "目标用户"],
  ["Use Case", "使用场景"],
  ["Functional Requirements", "功能需求"],
  ["Material Preferences", "材料偏好"],
  ["Constraints", "限制条件"],
  ["Source Assets", "来源资产"],
  ["Sampling Feedback", "打样反馈"],
  ["Defect Signals", "缺陷信号"],
  ["Run Workflow", "运行工作流"],
  ["Run Structuring Test", "运行结构化测试"],
  ["Export Evidence JSON", "导出证据 JSON"],
  ["Workflow Output", "工作流输出"],
  ["Structured Output", "结构化输出"],
  ["SWS/Arachne Engineering Brief", "SWS/Arachne 工程 Brief"],
  ["Engineering Brief Candidate", "工程 Brief 候选对象"],
  ["Manufacturability Check", "可制造性检查"],
  ["Sampling / Revision / Readiness", "打样 / 修订 / 准备度"],
  ["Tool Interfaces", "工具接口"],
  ["Evidence Log", "证据日志"],
  ["Athena Production Operations Console", "Athena 生产运营控制台"],
  ["Athena Production Operations", "Athena 生产运营"],
  ["Order To Garment Monitoring", "从订单到成衣监控"],
  ["Management dashboard for order intake, ERP, APS, IOT, production, service escalation, and garment output.", "面向管理层的驾驶舱，监控接单、ERP、APS、IOT、生产、服务升级和成衣输出。"],
  ["Read-only MVP", "只读 MVP"],
  ["This console uses local mock data and read-only adapter contracts. It does not log in to APS/IOT, upload .co/.cx files, release orders, control machines, or create real service tickets.", "本控制台使用本地 mock 数据和只读 adapter 契约，不登录 APS/IOT、不上传 .co/.cx 文件、不下发订单、不控制机台、不创建真实服务工单。"],
  ["Workflow Lane", "工作流泳道"],
  ["Refresh Mock Snapshot", "刷新 Mock 快照"],
  ["People / Machine / Material / Method / Environment / Measurement", "人 / 机 / 料 / 法 / 环 / 测"],
  ["Production Site Flow", "生产现场链路"],
  ["Garment Output", "成衣输出"],
  ["Optimization Signals", "优化信号"],
  ["Service Request Candidates", "服务请求候选"],
  ["APS / IOT Field Mapping", "APS / IOT 字段映射"],
  ["KPI Log", "KPI 日志"],
  ["Orders", "订单数"],
  ["Scheduled", "已排程"],
  ["Pending / Exception", "待排 / 异常"],
  ["Running Machines", "运行机台"],
  ["Running Rate", "运行率"],
  ["Average OEE", "平均 OEE"],
  ["Downtime", "停机时间"],
  ["Material Risks", "物料风险"],
  ["Labor Efficiency", "人工效率"],
  ["Quality Risks", "质量风险"],
  ["Service Candidates", "服务候选"],
  ["People", "人"],
  ["Machine", "机"],
  ["Material", "料"],
  ["Method", "法"],
  ["Environment", "环"],
  ["Measurement", "测"],
  ["Implemented Features", "已完成功能"],
  ["Planned Features", "计划功能"],
  ["Confirmed", "已确认"],
  ["Uncertain / Pending", "不确定 / 待确认"],
  ["Designer State Flow", "Designer 状态流"],
  ["Service State Flow", "Service 状态流"],
  ["Athena MVP Workflow State Flow", "Athena MVP 工作流状态流"],
  ["Design Intake Structuring State Flow", "设计输入结构化状态流"],
  ["Production Operations State Flow", "Production Operations 状态流"],
  ["Open Athena MVP Workflow Console", "打开 Athena MVP 工作流控制台"],
  ["Open Design Intake Structuring Console", "打开设计输入结构化中台"],
  ["Open Production Operations Console", "打开生产运营控制台"],
  ["Service Case Mock Structure", "Service Case Mock 结构"],
  ["Open Service Case Library", "打开 Service Case Library"],
  ["Next Decisions", "下一步决策"],
  ["Operation Guide", "操作说明"],
  ["Scope", "适用范围"],
  ["Out of Scope", "不适用范围"],
  ["How to Use", "使用方法"],
  ["Current Features", "当前功能"],
  ["Excel Import", "Excel 导入"],
  ["Testing Suggestions", "测试建议"],
  ["Designer: describe design goals in natural language to clarify intent, explore product-development briefs, and prepare future SWS direction.", "Designer：用自然语言描述设计目标，用于澄清设计意图、探索产品开发 brief，并准备未来 SWS 方向。"],
  ["Customer Equipment Engineer: describe equipment issues so the Agent can try online assistance before deciding whether dispatch or a service ticket is needed.", "Customer Equipment Engineer：描述设备问题，让 Agent 先尝试在线协助，再判断是否需要派工或生成服务工单。"],
  ["Service Manager Console: review and edit service case status, online steps, safety warnings, dispatch triggers, and future ticket payloads.", "Service Manager Console：查看和编辑 service case 状态、在线处理步骤、安全提醒、派工触发条件和未来工单 payload。"],
  ["Lock-machine activation: test controlled activation-password generation after machine lock, using mock or experimental real-platform connection.", "锁机激活：在受控流程下测试机器锁定后的激活密码生成，可使用 mock 或实验性真实平台连接。"],
  ["The current version does not connect to real SWS, APS, DPP, formal ticket systems, or customer equipment data.", "当前版本不连接真实 SWS、APS、DPP、正式工单系统或客户设备数据。"],
  ["Image upload currently keeps interface and mock-understanding results only; it does not perform real visual recognition.", "图片上传目前只保留接口和 mock 理解结果，不做真实视觉识别。"],
  ["Service cases extracted from Excel still need Santoni service-team review before they become formal customer-facing guidance.", "由 Excel 提炼的 service case 仍需要 Santoni 服务团队审核，不能直接作为正式客户维修指引。"],
  ["Safety risk, machine disassembly, electrical repair, downtime loss, or spare-part replacement decisions require human service confirmation.", "涉及安全风险、拆机、电气维修、停机损失或备件更换的判断，需要人工服务人员确认。"],
  ["Open the web demo home page, choose 总经理, Service Engineer, or Design Development first, then enter your request.", "打开 Web Demo 首页，先选择总经理、服务工程师或设计开发身份，再输入需求。"],
  ["Business users use the default home page; development and testing users can open /developer.html for full debug information.", "业务用户使用默认首页；开发和测试同事可以进入 /developer.html 查看完整调试信息。"],
  ["Designer tests can include product type, target user, use case, style, function, material, cost, or delivery constraints.", "Designer 测试可以输入产品类型、目标用户、使用场景、风格、功能、材料、成本或交期限制。"],
  ["Service tests can include machine model, serial number, symptom, alarm, production impact, attempted steps, and image evidence.", "Service 测试可以输入机型、序列号、故障现象、报警信息、生产影响、已尝试步骤和图片证据。"],
  ["When you need a fresh test round, click Clear Memory on the home page or developer page.", "需要重新开始一轮测试时，点击首页或开发者页面的 Clear Memory。"],
  ["After testing, export the JSON test log for development-side analysis.", "测试结束后导出 JSON 测试日志，供开发侧分析对话过程。"],
  ["For real-platform lock-machine activation tests, the customer page prompts for platform credentials only after detecting the task.", "测试锁机激活真实平台时，用户页只会在识别到任务后弹出平台账号密码输入框。"],
  ["Main Agent keeps natural-language Designer, Service, or Production scenario detection as a backend fallback.", "Main Agent 保留 Designer、Service 或 Production 自然语言场景识别作为后端兜底。"],
  ["Designer Agent asks follow-up questions before generating a plan too early.", "Designer Agent 会先追问设计意图，避免过早生成方案。"],
  ["Service Agent collects required ticket information and prioritizes safe online assistance.", "Service Agent 收集工单必要信息，并优先尝试安全在线协助。"],
  ["Service Case Online Assist Mock matches structured service cases and suggests next checks.", "Service Case Online Assist Mock 匹配结构化服务案例并给出下一步检查建议。"],
  ["Service Manager Console supports case status review, case knowledge editing, diff view, and future CRM / ticket payload preview.", "Service Manager Console 支持案例状态审核、案例知识编辑、diff 视图和未来 CRM / 工单 payload 预览。"],
  ["Production Operations Console monitors order, ERP, APS, IOT, production/service escalation, and garment output with KPI and evidence logs.", "Production Operations Console 用 KPI 和证据日志监控订单、ERP、APS、IOT、生产 / 服务升级和成衣输出。"],
  ["Hermes Integration Console defines Athena runtime, memory, tool orchestration, and development suggestion contracts without live Hermes writeback.", "Hermes 接入控制台定义 Athena 运行时、记忆、工具调度和开发建议契约，但尚无真实 Hermes 写回。"],
  ["All web pages provide a Chinese / English language switch.", "所有 Web 页面都提供中文 / 英文切换。"],
  ["Test logs can be exported and do not include uploaded image content or platform passwords.", "支持导出测试日志，日志不包含上传图片内容或平台密码。"],
  ["The current version supports converting local service Excel files into draft service cases for review.", "当前版本支持将本地服务 Excel 转换为待审核 draft service cases。"],
  ["The default output file is src/mock_data/service_cases.draft_import.json.", "默认输出文件是 src/mock_data/service_cases.draft_import.json。"],
  ["Imported cases appear in Service Case Library with draft_needs_review status.", "导入结果会显示在 Service Case Library，状态为 draft_needs_review。"],
  ["Draft cases do not enter customer-facing matching until Service Manager Console marks them approved.", "Draft cases 不会进入客户回答匹配，必须先在 Service Manager Console 标记为 approved。"],
  ["needs_changes and internal_only cases remain in review pages but do not enter customer-facing response logic.", "needs_changes 和 internal_only 会保留在审核页，但不会进入客户回答逻辑。"],
  ["Enter information in batches and observe whether the Agent keeps context.", "分批输入信息，观察 Agent 是否能保留上下文。"],
  ["Intentionally omit key fields and check whether the Agent asks follow-up questions instead of inventing results.", "故意缺少关键字段，观察 Agent 是否追问而不是编造结果。"],
  ["When testing Designer, focus on whether it understands intent, functional needs, user scenarios, and constraints.", "测试 Designer 时，重点观察是否理解意图、功能需求、用户场景和限制条件。"],
  ["When testing Service, focus on online assistance, dispatch conditions, and avoiding over-promising.", "测试 Service 时，重点观察在线协助、派工条件和避免过度承诺。"],
  ["When testing service cases, use keywords and machine models from Service Case Library as references.", "测试 service case 时，可以参考 Service Case Library 中的关键词和机型。"],
  ["Total Cases", "案例总数"],
  ["Implemented Mock", "已实现 Mock"],
  ["Needs Review", "需要审核"],
  ["Excel Drafts", "Excel 草稿"],
  ["Approved", "已批准"],
  ["Needs Changes", "需要修改"],
  ["Internal Only", "仅内部"],
  ["Online Solvable", "可在线解决"],
  ["Dispatch Likely", "可能派工"],
  ["P1 / P2 / P3", "P1 / P2 / P3"],
  ["Console Workflow Status", "控制台工作流状态"],
  ["Search case, model, symptom, part", "搜索案例、机型、症状、备件"],
  ["Review status", "审核状态"],
  ["Issue category", "问题类别"],
  ["All statuses", "全部状态"],
  ["All categories", "全部类别"],
  ["All resolution types", "全部处理类型"],
  ["Dispatch likely", "可能派工"],
  ["No matching service cases.", "没有匹配的服务案例。"],
  ["Approve", "批准"],
  ["Reset Draft", "重置草稿"],
  ["Review note", "审核备注"],
  ["Save Console Changes", "保存控制台修改"],
  ["Title", "标题"],
  ["Issue Category", "问题类别"],
  ["Severity", "严重度"],
  ["Machine Models", "机型"],
  ["Symptom Keywords", "症状关键词"],
  ["Alarm Codes", "报警代码"],
  ["Recommended Parts", "建议备件"],
  ["Online Resolution Steps", "在线处理步骤"],
  ["Safety Warnings", "安全提醒"],
  ["Dispatch Triggers", "派工触发条件"],
  ["Estimated Resolution Time", "预计解决时间"],
  ["Confidence Notes", "置信备注"],
  ["Diff View", "Diff 视图"],
  ["CRM / Ticket Handoff Payload Preview", "CRM / 工单交接 Payload 预览"],
  ["Source Serials / WO", "来源序列号 / 工单"],
  ["Symptoms / Alarms", "症状 / 报警"],
  ["Online Steps", "在线步骤"],
  ["Parts / Time", "备件 / 时间"],
  ["No confidence note yet.", "暂无置信备注。"],
  ["Service Manager Console unavailable. Please restart the demo server.", "Service Manager Console 不可用，请重启 demo server。"],
];

const translationPairs = new Map(SANTONI_TRANSLATIONS);
const reversePairs = new Map(SANTONI_TRANSLATIONS.map(([english, chinese]) => [chinese, english]));
let isApplyingLanguage = false;

function initialLanguage() {
  const saved = localStorage.getItem(SANTONI_LANGUAGE_KEY);
  if (saved === "zh" || saved === "en") return saved;
  return document.documentElement.lang?.toLowerCase().startsWith("zh") ? "zh" : "en";
}

let currentLanguage = initialLanguage();

function translateText(value, language = currentLanguage) {
  if (!value) return value;
  const trimmed = String(value).trim();
  if (!trimmed) return value;
  const leading = String(value).match(/^\s*/)?.[0] || "";
  const trailing = String(value).match(/\s*$/)?.[0] || "";
  const translated = language === "zh" ? translationPairs.get(trimmed) : reversePairs.get(trimmed);
  return translated ? `${leading}${translated}${trailing}` : value;
}

function translateNodeText(node, language) {
  const translated = translateText(node.nodeValue, language);
  if (translated !== node.nodeValue) node.nodeValue = translated;
}

function translateAttributes(element, language) {
  ["title", "placeholder", "aria-label", "data-prompt"].forEach((attribute) => {
    if (!element.hasAttribute(attribute)) return;
    const current = element.getAttribute(attribute);
    const translated = translateText(current, language);
    if (translated !== current) element.setAttribute(attribute, translated);
  });
}

function shouldSkipTextNode(node) {
  const parent = node.parentElement;
  if (!parent) return true;
  return ["SCRIPT", "STYLE", "TEXTAREA", "PRE", "CODE"].includes(parent.tagName);
}

function applyLanguage(language = currentLanguage) {
  isApplyingLanguage = true;
  currentLanguage = language;
  localStorage.setItem(SANTONI_LANGUAGE_KEY, language);
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";

  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  while (walker.nextNode()) {
    if (!shouldSkipTextNode(walker.currentNode)) textNodes.push(walker.currentNode);
  }
  textNodes.forEach((node) => translateNodeText(node, language));
  document.querySelectorAll("*").forEach((element) => translateAttributes(element, language));
  updateLanguageToggle();
  isApplyingLanguage = false;
}

function updateLanguageToggle() {
  const button = document.querySelector("#languageToggle");
  if (!button) return;
  const nextLanguage = currentLanguage === "zh" ? "EN" : "中文";
  button.setAttribute("aria-label", currentLanguage === "zh" ? "切换语言" : "Switch language");
  button.innerHTML = `<span>${currentLanguage === "zh" ? "中文" : "EN"}</span><strong>${nextLanguage}</strong>`;
}

function mountLanguageToggle() {
  if (document.querySelector("#languageToggle")) return;
  const button = document.createElement("button");
  button.id = "languageToggle";
  button.className = "language-toggle";
  button.type = "button";
  button.addEventListener("click", () => {
    const next = currentLanguage === "zh" ? "en" : "zh";
    applyLanguage(next);
    window.dispatchEvent(new CustomEvent("santoni:language-change", { detail: { language: next } }));
  });

  const preferredHost = document.querySelector(".topbar-actions") || document.querySelector(".user-nav");
  if (preferredHost) {
    preferredHost.append(button);
  } else {
    const header = document.querySelector(".changelog-header") || document.querySelector("header") || document.body;
    const wrap = document.createElement("div");
    wrap.className = "topbar-actions language-toggle-wrap";
    wrap.append(button);
    header.append(wrap);
  }
  updateLanguageToggle();
}

function observeLanguageMutations() {
  const observer = new MutationObserver((mutations) => {
    if (isApplyingLanguage) return;
    mutations.forEach((mutation) => {
      if (mutation.type === "characterData" && !shouldSkipTextNode(mutation.target)) {
        translateNodeText(mutation.target, currentLanguage);
        return;
      }
      if (mutation.type === "attributes") {
        translateAttributes(mutation.target, currentLanguage);
        return;
      }
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === Node.TEXT_NODE && !shouldSkipTextNode(node)) {
          translateNodeText(node, currentLanguage);
        }
        if (node.nodeType === Node.ELEMENT_NODE) {
          translateAttributes(node, currentLanguage);
          node.querySelectorAll?.("*").forEach((element) => translateAttributes(element, currentLanguage));
          const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
          while (walker.nextNode()) {
            if (!shouldSkipTextNode(walker.currentNode)) translateNodeText(walker.currentNode, currentLanguage);
          }
        }
      });
    });
  });
  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ["title", "placeholder", "aria-label", "data-prompt"],
    characterData: true,
    childList: true,
    subtree: true,
  });
}

window.SantoniI18n = {
  getLanguage: () => currentLanguage,
  setLanguage: applyLanguage,
  translate: translateText,
};

document.addEventListener("DOMContentLoaded", () => {
  mountLanguageToggle();
  applyLanguage(currentLanguage);
  observeLanguageMutations();
});

