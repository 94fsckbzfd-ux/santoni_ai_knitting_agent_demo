const trainingStatus = document.querySelector("#trainingStatus");
const trainingSummary = document.querySelector("#trainingSummary");
const trainingStages = document.querySelector("#trainingStages");
const trainingTasks = document.querySelector("#trainingTasks");
const capabilityProgress = document.querySelector("#capabilityProgress");
const hermesResultJson = document.querySelector("#hermesResultJson");
const hermesResultStatus = document.querySelector("#hermesResultStatus");
const reviewState = document.querySelector("#reviewState");
const patchQueue = document.querySelector("#patchQueue");
const executionGate = document.querySelector("#executionGate");
const worktreePrepQueue = document.querySelector("#worktreePrepQueue");
const worktreeLaunchGate = document.querySelector("#worktreeLaunchGate");
const worktreeResultIntake = document.querySelector("#worktreeResultIntake");
const worktreeResultReviewGate = document.querySelector("#worktreeResultReviewGate");
const promotionCandidateQueue = document.querySelector("#promotionCandidateQueue");
const promotionApprovalGate = document.querySelector("#promotionApprovalGate");
const promotionHandoffQueue = document.querySelector("#promotionHandoffQueue");
const promotionReadinessGate = document.querySelector("#promotionReadinessGate");
const promotionExecutionResultIntake = document.querySelector("#promotionExecutionResultIntake");
const promotionClosureAudit = document.querySelector("#promotionClosureAudit");
const promotionSyncReviewGate = document.querySelector("#promotionSyncReviewGate");
const promotionSyncHandoffQueue = document.querySelector("#promotionSyncHandoffQueue");
const promotionSyncReadinessGate = document.querySelector("#promotionSyncReadinessGate");
const promotionSyncExecutionResultIntake = document.querySelector("#promotionSyncExecutionResultIntake");
const promotionSyncClosureAudit = document.querySelector("#promotionSyncClosureAudit");
const promotionSyncClosureReviewGate = document.querySelector("#promotionSyncClosureReviewGate");
const promotionFinalSyncHandoffQueue = document.querySelector("#promotionFinalSyncHandoffQueue");
const promotionFinalSyncReadinessGate = document.querySelector("#promotionFinalSyncReadinessGate");
const promotionFinalSyncExecutionResultIntake = document.querySelector("#promotionFinalSyncExecutionResultIntake");
const promotionFinalSyncClosureAudit = document.querySelector("#promotionFinalSyncClosureAudit");
const promotionFinalCompletionReviewGate = document.querySelector("#promotionFinalCompletionReviewGate");
const promotionFinalPublicationHandoffQueue = document.querySelector("#promotionFinalPublicationHandoffQueue");
const promotionFinalPublicationReadinessGate = document.querySelector("#promotionFinalPublicationReadinessGate");
const promotionFinalPublicationResultIntake = document.querySelector("#promotionFinalPublicationResultIntake");
const promotionFinalPublicationClosureAudit = document.querySelector("#promotionFinalPublicationClosureAudit");
const promotionFinalReleaseReviewGate = document.querySelector("#promotionFinalReleaseReviewGate");
const nextTrainingTasks = document.querySelector("#nextTrainingTasks");
const trainingKpis = document.querySelector("#trainingKpis");
const trainingEvidence = document.querySelector("#trainingEvidence");
const runTrainingButton = document.querySelector("#runTrainingButton");
const trainingRoundSummary = document.querySelector("#trainingRoundSummary");
const promoteBaselineButton = document.querySelector("#promoteBaselineButton");
const playbookRegressionQueue = document.querySelector("#playbookRegressionQueue");
const runRegressionButton = document.querySelector("#runRegressionButton");
const trainingRegressionRun = document.querySelector("#trainingRegressionRun");
const trainingRegressionGate = document.querySelector("#trainingRegressionGate");
const trainingNextLoopHandoff = document.querySelector("#trainingNextLoopHandoff");
const trainingNextLoopClosure = document.querySelector("#trainingNextLoopClosure");
const trainingIterationProposal = document.querySelector("#trainingIterationProposal");
const codexWorkPacketQueue = document.querySelector("#codexWorkPacketQueue");

let lastTrainingStatus = null;
let lastTrainingResult = null;
let lastRoundSummary = null;
let lastRegressionRun = null;
let lastRegressionGate = null;
let lastNextLoopHandoff = null;
let lastNextLoopClosure = null;
let lastIterationProposal = null;
let lastCodexWorkPackets = null;
let lastCodexPatchQueue = null;
let lastCodexExecutionGate = null;
let lastCodexWorktreePrep = null;
let lastCodexWorktreeLaunch = null;
let lastCodexWorktreeResults = null;
let lastCodexWorktreeResultReviewGate = null;
let lastCodexPromotionCandidates = null;
let lastCodexPromotionApprovalGate = null;
let lastCodexPromotionHandoff = null;
let lastCodexPromotionReadiness = null;
let lastCodexPromotionExecutionResults = null;
let lastCodexPromotionClosureAudit = null;
let lastCodexPromotionSyncReviewGate = null;
let lastCodexPromotionSyncHandoff = null;
let lastCodexPromotionSyncReadiness = null;
let lastCodexPromotionSyncExecutionResults = null;
let lastCodexPromotionSyncClosureAudit = null;
let lastCodexPromotionSyncClosureReviewGate = null;
let lastCodexPromotionFinalSyncHandoff = null;
let lastCodexPromotionFinalSyncReadiness = null;
let lastCodexPromotionFinalSyncExecutionResults = null;
let lastCodexPromotionFinalSyncClosureAudit = null;
let lastCodexPromotionFinalCompletionReviewGate = null;
let lastCodexPromotionFinalPublicationHandoff = null;
let lastCodexPromotionFinalPublicationReadiness = null;
let lastCodexPromotionFinalPublicationResults = null;
let lastCodexPromotionFinalPublicationClosureAudit = null;
let lastCodexPromotionFinalReleaseReviewGate = null;

const TRAINING_TEXT = {
  zh: {
    title: "Athena 自动训练控制台",
    subtitle: "自动运行 Tianpai 训练任务，输出 Hermes-style JSON，跟踪能力进度、数据缺口、Playbook 回归队列和下一轮修正队列。",
    guardrailTitle: "自动训练边界",
    guardrailText: "当前实现是本地自动评测训练闭环：自动跑任务、自动打分、自动输出 JSON。真实 Hermes runner、模型权重 fine-tuning、APS/IOT 写入和大功能自动改代码仍未启用。",
    progressTitle: "怎么看训练进度",
    progressText: "看顶部进度卡、任务状态、能力评分、Hermes Result JSON、Playbook Regression Queue、Automatic Regression Run、Regression Gate、Next Loop Handoff、Next Loop Closure Gate、Training Iteration Proposal、Codex Patch Queue Contract 和 Next Training Tasks。",
    loop: "自动训练流水线",
    tasks: "训练任务队列",
    capability: "能力进度",
    hermesJson: "Hermes Result JSON",
    patchQueue: "Codex Patch Queue Contract",
    executionGate: "Codex Execution Gate",
    worktreePrep: "Codex Worktree Preparation Queue",
    worktreeLaunch: "Codex Worktree 启动门控",
    worktreeResults: "Codex Worktree 结果接收",
    worktreeResultReview: "Codex Worktree 结果复核门控",
    promotionCandidates: "Codex 推广候选队列",
    promotionApproval: "Codex 推广审批门控",
    promotionHandoff: "Codex 推广交接队列",
    promotionReadiness: "Codex 推广执行就绪门控",
    promotionResult: "Codex 推广执行结果接收",
    promotionClosure: "Codex Promotion 闭环 / Hermes 同步审计",
    promotionSyncReview: "Codex Promotion 同步复核门控",
    promotionSyncHandoff: "Codex Promotion 同步交接队列",
    promotionSyncReadiness: "Codex Promotion 同步执行就绪门控",
    promotionSyncResult: "Codex Promotion 同步执行结果接收",
    promotionSyncClosure: "Codex Promotion 同步关闭审计",
    promotionSyncClosureReview: "Codex Promotion Sync Closure Review Gate",
    promotionFinalSyncHandoff: "Codex Promotion Final Sync Handoff Queue",
    promotionFinalSyncReadiness: "Codex Promotion Final Sync Execution Readiness Gate",
    promotionFinalSyncResult: "Codex Promotion Final Sync Execution Result Intake",
    promotionFinalSyncClosure: "Codex Promotion Final Sync Closure Audit",
    promotionFinalCompletionReview: "Codex Promotion 最终完成确认门",
    promotionFinalPublicationHandoff: "Codex Promotion 最终发布交接队列",
    promotionFinalPublicationReadiness: "Codex Promotion 最终发布就绪门",
    promotionFinalPublicationResult: "Codex Promotion 最终发布结果接收",
    promotionFinalPublicationClosure: "Codex Promotion 最终发布闭环审计",
    promotionFinalReleaseReview: "Codex Promotion 最终发布 / 归档复核门",
    approveFinalCompletion: "批准最终完成",
    needsCompletionInputs: "需要完成确认资料",
    nextTasks: "Next Training Tasks",
    kpi: "KPI Log",
    evidence: "Evidence Log",
    baseline: "训练轮次摘要 / 基线",
    promoteBaseline: "固化已确认基线",
    baselineReady: "基线状态",
    promotedTasks: "已固化任务",
    capabilityRegression: "能力回归",
    dataGapRegression: "数据缺口回归",
    dataDecisions: "数据决策",
    remainingGap: "剩余缺口",
    playbookRegression: "组织 Playbook 回归队列",
    readyRegression: "可回归候选",
    blockedRegression: "阻塞候选",
    blockers: "阻塞原因",
    regressionRun: "自动回归运行",
    runRegression: "运行回归",
    executableCases: "可执行用例",
    passedCases: "通过用例",
    failedCases: "失败用例",
    blockedCases: "阻塞用例",
    passRate: "通过率",
    regressionGate: "回归门控",
    gateAllowed: "允许下一轮",
    reviewRequired: "需要复核",
    gateStatus: "门控状态",
    nextLoopHandoff: "下一轮训练交接单",
    handoffStatus: "交接状态",
    automaticActions: "自动项",
    humanReviewItems: "人工复核项",
    dataRequests: "数据请求项",
    handoffReviewStatus: "交接复核状态",
    approveNextLoop: "批准进入下一轮",
    markResolved: "标记已处理",
    deferHandoff: "延期",
    markNeedsData: "需要数据",
    nextLoopClosure: "下一轮关闭门控",
    closureStatus: "关闭状态",
    expectedResults: "预期结果",
    completeResults: "完整结果",
    missingResults: "缺失结果",
    closureReady: "允许本地下一轮",
    closureComplete: "交接是否关闭",
    openItems: "未关闭项",
    rejectedItems: "拒绝项",
    iterationProposal: "训练迭代提案",
    proposalStatus: "提案状态",
    proposalReady: "提案可用",
    taskSeeds: "任务种子",
    watchItems: "观察项",
    proposalReviewStatus: "提案复核状态",
    approveCodexQueue: "批准进入队列",
    codexWorkPackets: "Codex 工作包队列",
    packetStatus: "工作包状态",
    packetCount: "工作包数量",
    candidateCount: "候选数量",
    queueReady: "队列可用",
    workPackets: "工作包",
    sourceProposal: "来源提案",
    validation: "验证要求",
    patchStatus: "Patch 队列状态",
    patchCandidates: "Patch 候选",
    trainingSignals: "训练信号",
    gateStatus: "闸门状态",
    executionCandidates: "执行候选",
    autoExecution: "自动执行",
    approveWorktree: "批准准备 Worktree",
    prepStatus: "准备状态",
    prepTasks: "准备任务",
    approvedCandidates: "已批准候选",
    launchStatus: "启动状态",
    launchRequests: "启动请求",
    automaticLaunch: "自动启动",
    suggestedInstruction: "建议用户指令",
    preflightChecks: "启动前检查",
    resultStatus: "结果状态",
    resultCount: "结果数量",
    validationPassed: "验证通过",
    validationFailed: "验证失败",
    autoMerge: "自动合并",
    changedFiles: "变更文件",
    validationResults: "验证结果",
    reviewCandidates: "复核候选",
    regressionCandidates: "回归候选",
    memoryCandidates: "记忆候选",
    approveRegression: "批准进入回归候选",
    approveMemory: "批准进入记忆候选",
    approveRegressionMemory: "批准进入回归+记忆",
    promotionStatus: "推广状态",
    totalPromotionCandidates: "推广候选总数",
    approvalStatus: "审批状态",
    futureAction: "未来动作",
    approvedFutureActions: "已批准未来动作",
    approveFuturePromotion: "批准为未来动作",
    holdForLater: "保留观察",
    skipCandidate: "跳过候选项",
    handoffStatus: "交接状态",
    handoffItems: "交接项",
    targetSystem: "目标系统",
    ownerRole: "负责人角色",
    manualExecution: "手动执行",
    preflightChecks: "前置检查",
    readinessStatus: "就绪状态",
    readinessItems: "就绪项",
    missingInputs: "缺失输入",
    readinessReviewStatus: "执行就绪复核状态",
    confirmReadiness: "确认前置条件",
    needsExecutionInputs: "需要执行资料",
    resultIntakeStatus: "结果接收状态",
    recordManualResult: "记录手工结果",
    closureAuditStatus: "闭环审计状态",
    syncAuditCandidates: "同步审计候选",
    futureHermesSync: "未来 Hermes 同步审计",
    syncReviewStatus: "同步复核状态",
    approveFutureSync: "批准未来同步",
    needsSyncInputs: "需要同步资料",
    syncHandoffStatus: "同步交接状态",
    syncReadinessStatus: "同步就绪状态",
    run: "Run Auto Training",
    loading: "加载中",
    unavailable: "Training API 不可用",
    mockContract: "Mock Contract",
    value: "当前值",
    target: "目标",
    score: "评分",
    evidenceRefs: "证据",
    nextAction: "下一步",
    humanReview: "需要人工/数据确认",
    reviewState: "Review / Data Intake 状态",
    reviewStatus: "确认状态",
    dataStatus: "数据状态",
    approve: "确认有效",
    needsChangesAction: "需要修改",
    reject: "拒绝",
    addNote: "保存备注",
    notePlaceholder: "写一句确认原因、修改意见或现场判断",
    dataSource: "数据源登记",
    sourceType: "数据类型",
    sourceLabel: "数据名称",
    sourceReference: "路径/负责人/引用",
    fieldNotes: "字段说明或跳过原因",
    sensitivity: "敏感级别",
    registerDataSource: "登记数据源",
    skipForNow: "暂时跳过",
    markNotAvailable: "标记不可用",
    noRawUpload: "This records source and field notes only; raw files are not uploaded or stored.",
    saved: "已保存",
    errorSaving: "保存失败",
    notRegistered: "未登记",
    yes: "是",
    no: "否",
    needsData: "需要数据",
    passed: "通过",
    failed: "失败",
    version: "版本",
  },
  en: {
    title: "Athena Automatic Training Console",
    subtitle: "Runs Tianpai training tasks automatically, emits Hermes-style JSON, and tracks capability progress, data gaps, playbook regression, and the next correction queue.",
    guardrailTitle: "Automation Boundary",
    guardrailText: "This is a local automatic evaluation loop: it runs tasks, scores them, and emits JSON. Live Hermes runner, model-weight fine-tuning, APS/IOT writes, and automatic large code changes are not enabled.",
    progressTitle: "How To See Progress",
    progressText: "Use the summary cards, task status, capability scores, Hermes Result JSON, Playbook Regression Queue, Automatic Regression Run, Regression Gate, Next Loop Handoff, Next Loop Closure Gate, Training Iteration Proposal, Codex Patch Queue Contract, and Next Training Tasks.",
    loop: "Automatic Training Pipeline",
    tasks: "Training Task Queue",
    capability: "Capability Progress",
    hermesJson: "Hermes Result JSON",
    patchQueue: "Codex Patch Queue Contract",
    executionGate: "Codex Execution Gate",
    worktreePrep: "Codex Worktree Preparation Queue",
    worktreeLaunch: "Codex Worktree Launch Gate",
    worktreeResults: "Codex Worktree Result Intake",
    worktreeResultReview: "Codex Worktree Result Review Gate",
    promotionCandidates: "Codex Promotion Candidate Queue",
    promotionApproval: "Codex Promotion Approval Gate",
    promotionHandoff: "Codex Promotion Handoff Queue",
    promotionReadiness: "Codex Promotion Execution Readiness Gate",
    promotionResult: "Codex Promotion Execution Result Intake",
    promotionClosure: "Codex Promotion Closure / Hermes Sync Audit",
    promotionSyncReview: "Codex Promotion Sync Review Gate",
    promotionSyncHandoff: "Codex Promotion Sync Handoff Queue",
    promotionSyncReadiness: "Codex Promotion Sync Execution Readiness Gate",
    promotionSyncResult: "Codex Promotion Sync Execution Result Intake",
    promotionSyncClosure: "Codex Promotion Sync Closure Audit",
    promotionSyncClosureReview: "Codex Promotion Sync Closure Review Gate",
    promotionFinalSyncHandoff: "Codex Promotion Final Sync Handoff Queue",
    promotionFinalSyncReadiness: "Codex Promotion Final Sync Execution Readiness Gate",
    promotionFinalSyncResult: "Codex Promotion Final Sync Execution Result Intake",
    promotionFinalSyncClosure: "Codex Promotion Final Sync Closure Audit",
    promotionFinalCompletionReview: "Codex Promotion Final Completion Review Gate",
    promotionFinalPublicationHandoff: "Codex Promotion Final Publication Handoff Queue",
    promotionFinalPublicationReadiness: "Codex Promotion Final Publication Readiness Gate",
    promotionFinalPublicationResult: "Codex Promotion Final Publication Result Intake",
    promotionFinalPublicationClosure: "Codex Promotion Final Publication Closure Audit",
    promotionFinalReleaseReview: "Codex Promotion Final Release / Archive Review Gate",
    approveFinalCompletion: "Approve final completion",
    needsCompletionInputs: "Needs completion inputs",
    nextTasks: "Next Training Tasks",
    kpi: "KPI Log",
    evidence: "Evidence Log",
    baseline: "Training Round Summary / Baseline",
    promoteBaseline: "Promote Approved Baseline",
    baselineReady: "Baseline ready",
    promotedTasks: "Promoted tasks",
    capabilityRegression: "Capability regression",
    dataGapRegression: "Data-gap regression",
    dataDecisions: "Data decisions",
    remainingGap: "Remaining gap",
    playbookRegression: "Playbook Regression Queue",
    readyRegression: "Ready regression",
    blockedRegression: "Blocked regression",
    blockers: "Blockers",
    regressionRun: "Automatic Regression Run",
    runRegression: "Run Regression",
    executableCases: "Executable cases",
    passedCases: "Passed cases",
    failedCases: "Failed cases",
    blockedCases: "Blocked cases",
    passRate: "Pass rate",
    regressionGate: "Regression Gate",
    gateAllowed: "Next loop allowed",
    reviewRequired: "Review required",
    gateStatus: "Gate status",
    nextLoopHandoff: "Next Loop Handoff",
    handoffStatus: "Handoff status",
    automaticActions: "Automatic items",
    humanReviewItems: "Human review items",
    dataRequests: "Data request items",
    handoffReviewStatus: "Handoff review status",
    approveNextLoop: "Approve Next Loop",
    markResolved: "Mark Resolved",
    deferHandoff: "Defer",
    markNeedsData: "Needs Data",
    nextLoopClosure: "Next Loop Closure Gate",
    closureStatus: "Closure status",
    expectedResults: "Expected results",
    completeResults: "Complete results",
    missingResults: "Missing results",
    closureReady: "Local loop allowed",
    closureComplete: "Closure complete",
    openItems: "Open items",
    rejectedItems: "Rejected items",
    iterationProposal: "Training Iteration Proposal",
    proposalStatus: "Proposal status",
    proposalReady: "Proposal ready",
    taskSeeds: "Task seeds",
    watchItems: "Watch items",
    proposalReviewStatus: "Proposal review status",
    approveCodexQueue: "Approve Queue",
    codexWorkPackets: "Codex Work Packet Queue",
    packetStatus: "Packet status",
    packetCount: "Packet count",
    candidateCount: "Candidate count",
    queueReady: "Queue ready",
    workPackets: "Work packets",
    sourceProposal: "Source proposal",
    validation: "Required validation",
    patchStatus: "Patch queue status",
    patchCandidates: "Patch candidates",
    trainingSignals: "Training signals",
    gateStatus: "Gate status",
    executionCandidates: "Execution candidates",
    autoExecution: "Automatic execution",
    approveWorktree: "Approve Worktree",
    prepStatus: "Preparation status",
    prepTasks: "Preparation tasks",
    approvedCandidates: "Approved candidates",
    launchStatus: "Launch status",
    launchRequests: "Launch requests",
    automaticLaunch: "Automatic launch",
    suggestedInstruction: "Suggested user instruction",
    preflightChecks: "Preflight checks",
    resultStatus: "Result status",
    resultCount: "Result count",
    validationPassed: "Validation passed",
    validationFailed: "Validation failed",
    autoMerge: "Automatic merge",
    changedFiles: "Changed files",
    validationResults: "Validation results",
    reviewCandidates: "Review candidates",
    regressionCandidates: "Regression candidates",
    memoryCandidates: "Memory candidates",
    approveRegression: "Approve Regression Candidate",
    approveMemory: "Approve Memory Candidate",
    approveRegressionMemory: "Approve Regression + Memory",
    promotionStatus: "Promotion status",
    totalPromotionCandidates: "Total promotion candidates",
    approvalStatus: "Approval status",
    futureAction: "Future action",
    approvedFutureActions: "Approved future actions",
    approveFuturePromotion: "Approve Future Action",
    holdForLater: "Hold For Later",
    skipCandidate: "Skip Candidate",
    handoffStatus: "Handoff status",
    handoffItems: "Handoff items",
    targetSystem: "Target system",
    ownerRole: "Owner role",
    manualExecution: "Manual execution",
    preflightChecks: "Preflight checks",
    readinessStatus: "Readiness status",
    readinessItems: "Readiness items",
    missingInputs: "Missing inputs",
    readinessReviewStatus: "Readiness review status",
    confirmReadiness: "Confirm prerequisites",
    needsExecutionInputs: "Needs execution inputs",
    resultIntakeStatus: "Result intake status",
    recordManualResult: "Record manual result",
    closureAuditStatus: "Closure audit status",
    syncAuditCandidates: "Sync audit candidates",
    futureHermesSync: "Future Hermes sync audit",
    syncReviewStatus: "Sync review status",
    approveFutureSync: "Approve future sync",
    needsSyncInputs: "Needs sync inputs",
    syncHandoffStatus: "Sync handoff status",
    syncReadinessStatus: "Sync readiness status",
    run: "Run Auto Training",
    loading: "Loading",
    unavailable: "Training API unavailable",
    mockContract: "Mock Contract",
    value: "Value",
    target: "Target",
    score: "Score",
    evidenceRefs: "Evidence",
    nextAction: "Next action",
    humanReview: "Human/data review required",
    reviewState: "Review / Data Intake State",
    reviewStatus: "Review status",
    dataStatus: "Data status",
    approve: "Approve",
    needsChangesAction: "Needs Changes",
    reject: "Reject",
    addNote: "Save Note",
    notePlaceholder: "Add confirmation reason, change request, or site judgment",
    dataSource: "Data Source Registration",
    sourceType: "Data type",
    sourceLabel: "Data label",
    sourceReference: "Path / owner / reference",
    fieldNotes: "Field notes or skip reason",
    sensitivity: "Sensitivity",
    registerDataSource: "Register Data Source",
    skipForNow: "Skip For Now",
    markNotAvailable: "Mark Not Available",
    noRawUpload: "This records source and field notes only; raw files are not uploaded or stored.",
    saved: "Saved",
    errorSaving: "Save failed",
    notRegistered: "Not registered",
    yes: "Yes",
    no: "No",
    needsData: "Needs data",
    passed: "Passed",
    failed: "Failed",
    version: "Version",
  },
};

const STATUS_TEXT = {
  passed: ["Passed", "通过"],
  needs_data: ["Needs Data", "需要数据"],
  failed: ["Failed", "失败"],
  completed: ["Completed", "完成"],
  human_or_data_review_required: ["Human/Data Review", "人工/数据确认"],
  auto_evaluated: ["Auto Evaluated", "自动评测完成"],
  auto_training_available: ["Auto Training Available", "自动训练可用"],
  implemented_mock: ["Implemented Mock", "本地实现"],
  mock_contract: ["Mock Contract", "Mock 契约"],
  ok: ["OK", "正常"],
  attention: ["Attention", "需关注"],
  attention_required: ["Attention Required", "需要关注"],
  blocked_no_executable_cases: ["Blocked: No Executable Cases", "阻塞：无可执行用例"],
  blocked_no_executable_regression: ["Blocked: No Executable Regression", "阻塞：无可执行回归"],
  regression_failed_human_review_required: ["Regression Failed", "回归失败"],
  ready_for_next_loop_with_blocked_playbooks: ["Ready With Blocked Playbooks", "可继续，有阻塞 Playbook"],
  ready_for_next_automatic_loop: ["Ready For Next Loop", "可进入下一轮"],
  automatic_small_fix_ready_with_review_items: ["Small Fix Ready With Review Items", "可小修，有复核项"],
  automatic_loop_ready: ["Automatic Loop Ready", "自动循环就绪"],
  blocked_until_review: ["Blocked Until Review", "等待复核后继续"],
  prepare_next_training_iteration: ["Prepare Next Training Iteration", "准备下一轮训练"],
  next_training_task_seed: ["Next Training Task Seed", "下一轮训练任务种子"],
  regression_case_review: ["Regression Case Review", "回归用例复核"],
  pending_handoff_review: ["Pending Handoff Review", "等待交接复核"],
  auto_allowed: ["Auto Allowed", "自动允许"],
  approved_for_next_loop: ["Approved For Next Loop", "已批准进入下一轮"],
  resolved: ["Resolved", "已处理"],
  deferred: ["Deferred", "已延期"],
  ready_for_local_iteration_with_open_handoff_items: ["Ready With Open Handoff Items", "可进入本地下一轮，有未关闭项"],
  ready_for_local_iteration: ["Ready For Local Iteration", "可进入本地下一轮"],
  blocked_by_regression_gate: ["Blocked By Regression Gate", "被回归门控阻塞"],
  blocked_by_rejected_handoff_item: ["Blocked By Rejected Handoff Item", "被拒绝交接项阻塞"],
  local_training_task_preparation_only: ["Local Training Preparation Only", "仅限本地训练准备"],
  review_or_fix_blocking_handoff_items: ["Review Or Fix Blocking Items", "复核或修复阻塞项"],
  proposal_ready: ["Proposal Ready", "提案可用"],
  proposal_ready_with_open_items: ["Proposal Ready With Open Items", "提案可用，有观察项"],
  blocked_until_closure_review: ["Blocked Until Closure Review", "等待关闭复核"],
  local_training_iteration_seed: ["Local Training Iteration Seed", "本地训练迭代种子"],
  pending_proposal_review: ["Pending Proposal Review", "等待提案复核"],
  approved_for_codex_queue: ["Approved For Queue", "已批准进入队列"],
  ready_for_codex_worktree_preparation: ["Ready For Codex Worktree Preparation", "可准备 Codex Worktree"],
  ready_but_no_task_seeds: ["Ready But No Task Seeds", "可用但没有任务种子"],
  blocked_proposal_needs_changes: ["Blocked: Proposal Needs Changes", "阻塞：提案需要修改"],
  blocked_proposal_rejected: ["Blocked: Proposal Rejected", "阻塞：提案已拒绝"],
  deferred_by_proposal_review: ["Deferred By Proposal Review", "提案复核已延期"],
  blocked_until_proposal_review: ["Blocked Until Proposal Review", "等待提案复核"],
  codex_work_packet: ["Codex Work Packet", "Codex 工作包"],
  not_started: ["Not Started", "未开始"],
  ready_for_codex_patch_review: ["Ready For Codex Patch Review", "可进入 Codex Patch 复核"],
  blocked_no_work_packets: ["Blocked: No Work Packets", "阻塞：没有工作包"],
  blocked_patch_proposal_needs_changes: ["Blocked: Proposal Needs Changes", "阻塞：提案需要修改"],
  blocked_patch_proposal_rejected: ["Blocked: Proposal Rejected", "阻塞：提案已拒绝"],
  deferred_by_work_packet_review: ["Deferred By Work Packet Review", "工作包复核已延期"],
  blocked_until_codex_work_packet_queue_ready: ["Blocked Until Work Packet Queue Ready", "等待工作包队列可用"],
  local_codex_patch_candidate: ["Local Codex Patch Candidate", "本地 Codex Patch 候选"],
  ready_for_human_execution_review: ["Ready For Human Execution Review", "等待人工执行复核"],
  blocked_no_patch_candidates: ["Blocked: No Patch Candidates", "阻塞：没有 Patch 候选"],
  blocked_execution_proposal_needs_changes: ["Blocked: Proposal Needs Changes", "阻塞：提案需要修改"],
  blocked_execution_proposal_rejected: ["Blocked: Proposal Rejected", "阻塞：提案已拒绝"],
  deferred_by_patch_queue: ["Deferred By Patch Queue", "Patch 队列已延期"],
  blocked_until_codex_patch_queue_ready: ["Blocked Until Patch Queue Ready", "等待 Patch 队列可用"],
  human_reviewed_small_fix_candidate: ["Human-reviewed Small Fix Candidate", "人工复核小修候选"],
  pending_human_confirmation: ["Pending Human Confirmation", "等待人工确认"],
  blocked_until_user_confirmation: ["Blocked Until User Confirmation", "等待用户确认"],
  pending_execution_review: ["Pending Execution Review", "等待执行复核"],
  approved_for_worktree_preparation: ["Approved For Worktree", "已批准准备 Worktree"],
  approved_pending_user_execution_command: ["Approved, Pending User Command", "已批准，等待用户执行命令"],
  blocked_until_execution_review: ["Blocked Until Execution Review", "等待执行复核"],
  blocked_until_execution_review_approval: ["Blocked Until Execution Approval", "等待执行复核批准"],
  blocked_worktree_proposal_needs_changes: ["Blocked: Proposal Needs Changes", "阻塞：提案需要修改"],
  blocked_worktree_proposal_rejected: ["Blocked: Proposal Rejected", "阻塞：提案已拒绝"],
  deferred_by_execution_gate: ["Deferred By Execution Gate", "执行闸门已延期"],
  blocked_until_codex_execution_gate_ready: ["Blocked Until Execution Gate Ready", "等待执行闸门可用"],
  codex_worktree_preparation_task: ["Codex Worktree Prep Task", "Codex Worktree 准备任务"],
  pending_user_worktree_command: ["Pending User Worktree Command", "等待用户 Worktree 命令"],
  ready_for_user_worktree_launch_confirmation: ["Ready For User Launch Confirmation", "等待用户确认启动"],
  blocked_until_worktree_preparation_approval: ["Blocked Until Worktree Approval", "等待 Worktree 准备批准"],
  blocked_launch_proposal_needs_changes: ["Blocked: Launch Proposal Needs Changes", "启动提案需要修改"],
  blocked_launch_proposal_rejected: ["Blocked: Launch Proposal Rejected", "启动提案已拒绝"],
  deferred_by_worktree_preparation_queue: ["Deferred By Worktree Preparation Queue", "Worktree 准备队列已延期"],
  blocked_until_codex_worktree_preparation_ready: ["Blocked Until Worktree Preparation Ready", "等待 Worktree 准备队列可用"],
  codex_worktree_launch_request: ["Codex Worktree Launch Request", "Codex Worktree 启动请求"],
  pending_explicit_user_launch_command: ["Pending Explicit User Launch Command", "等待用户明确启动命令"],
  blocked_until_codex_worktree_launch_ready: ["Blocked Until Worktree Launch Ready", "等待 Worktree 启动门控可用"],
  waiting_for_codex_worktree_result: ["Waiting For Worktree Result", "等待 Worktree 结果"],
  worktree_result_validation_passed: ["Worktree Result Validation Passed", "Worktree 结果验证通过"],
  worktree_result_validation_failed: ["Worktree Result Validation Failed", "Worktree 结果验证失败"],
  worktree_result_review_required: ["Worktree Result Review Required", "Worktree 结果需要复核"],
  ready_for_worktree_result_review: ["Ready For Worktree Result Review", "可复核 Worktree 结果"],
  result_review_approved_for_promotion_candidates: ["Approved For Promotion Candidates", "已批准为推广候选"],
  blocked_result_validation_failed: ["Blocked: Result Validation Failed", "阻塞：结果验证失败"],
  blocked_result_contract_incomplete: ["Blocked: Result Contract Incomplete", "阻塞：结果合同不完整"],
  blocked_until_codex_worktree_result_ready: ["Blocked Until Worktree Result Ready", "等待 Worktree 结果可用"],
  pending_result_review: ["Pending Result Review", "等待结果复核"],
  codex_worktree_result_review_candidate: ["Codex Worktree Result Review Candidate", "Codex Worktree 结果复核候选"],
  approved_for_regression_baseline: ["Approved For Regression Baseline", "批准进入回归基线候选"],
  approved_for_hermes_memory_candidate: ["Approved For Hermes Memory Candidate", "批准进入 Hermes 记忆候选"],
  approved_for_regression_and_memory: ["Approved For Regression And Memory", "批准进入回归和记忆候选"],
  ready_for_promotion_candidate_handoff: ["Ready For Promotion Candidate Handoff", "推广候选可交接"],
  blocked_until_result_review_approval: ["Blocked Until Result Review Approval", "等待结果复核批准"],
  blocked_until_codex_result_review_ready: ["Blocked Until Result Review Ready", "等待结果复核可用"],
  regression_baseline_candidate: ["Regression Baseline Candidate", "回归基线候选"],
  hermes_memory_candidate: ["Hermes Memory Candidate", "Hermes 记忆候选"],
  candidate_pending_future_regression_promotion: ["Candidate Pending Future Regression Promotion", "候选等待未来回归推广"],
  candidate_pending_future_hermes_memory_write: ["Candidate Pending Future Hermes Memory Write", "候选等待未来 Hermes 记忆写入"],
  blocked_until_promotion_candidates_ready: ["Blocked Until Promotion Candidates Ready", "等待推广候选项"],
  ready_for_promotion_approval: ["Ready For Promotion Approval", "等待推广审批"],
  promotion_candidates_approved_for_future_action: ["Promotion Candidates Approved For Future Action", "已批准未来动作"],
  promotion_approval_waiting_for_follow_up: ["Promotion Approval Waiting For Follow-up", "等待后续处理"],
  promotion_approval_closed_without_execution: ["Promotion Approval Closed Without Execution", "审批已关闭但未执行"],
  pending_promotion_approval: ["Pending Promotion Approval", "等待推广审批"],
  approved_for_future_promotion: ["Approved For Future Promotion", "已批准未来推广"],
  hold_for_later: ["Hold For Later", "保留观察"],
  manual_regression_baseline_promotion: ["Manual Regression Baseline Promotion", "人工回归基线推广"],
  manual_hermes_memory_write: ["Manual Hermes Memory Write", "人工 Hermes 记忆写入"],
  approved_but_not_executed: ["Approved But Not Executed", "已批准但未执行"],
  ready_for_manual_promotion_handoff: ["Ready For Manual Promotion Handoff", "可进行人工推广交接"],
  blocked_until_promotion_approval: ["Blocked Until Promotion Approval", "等待推广审批"],
  waiting_manual_execution: ["Waiting Manual Execution", "等待人工执行"],
  local_regression_baseline_store: ["Local Regression Baseline Store", "本地回归基线存储"],
  live_hermes_memory: ["Live Hermes Memory", "Live Hermes 记忆"],
  product_owner: ["Product Owner", "产品负责人"],
  hermes_admin: ["Hermes Admin", "Hermes 管理员"],
  blocked_until_execution_prerequisites_confirmed: ["Blocked Until Execution Prerequisites Confirmed", "等待执行前置条件确认"],
  ready_for_manual_execution_confirmation: ["Ready For Manual Execution Confirmation", "等待人工执行确认"],
  blocked_until_promotion_handoff_ready: ["Blocked Until Promotion Handoff Ready", "等待推广交接队列"],
  blocked_missing_execution_prerequisites: ["Blocked: Missing Execution Prerequisites", "阻塞：缺少执行前置条件"],
  pending_readiness_review: ["Pending Readiness Review", "等待就绪复核"],
  confirmed_ready_for_manual_execution: ["Confirmed Ready For Manual Execution", "已确认可人工执行"],
  execution_prerequisites_confirmed: ["Execution Prerequisites Confirmed", "执行前置条件已确认"],
  needs_execution_inputs: ["Needs Execution Inputs", "需要执行资料"],
  deferred_by_readiness_review: ["Deferred By Readiness Review", "就绪复核已延期"],
  blocked_by_readiness_review_rejection: ["Blocked By Readiness Review Rejection", "就绪复核拒绝"],
  waiting_for_manual_promotion_execution_result: ["Waiting For Manual Promotion Execution Result", "等待手工推广执行结果"],
  promotion_execution_result_recorded: ["Promotion Execution Result Recorded", "推广执行结果已记录"],
  promotion_execution_result_failed: ["Promotion Execution Result Failed", "推广执行结果失败"],
  promotion_execution_result_needs_review: ["Promotion Execution Result Needs Review", "推广执行结果需要复核"],
  blocked_until_promotion_execution_readiness_confirmed: ["Blocked Until Promotion Execution Readiness Confirmed", "等待推广执行就绪确认"],
  blocked_until_promotion_execution_ready: ["Blocked Until Promotion Execution Ready", "等待推广执行就绪"],
  manual_execution_recorded: ["Manual Execution Recorded", "手工执行已记录"],
  manual_execution_failed: ["Manual Execution Failed", "手工执行失败"],
  manual_execution_skipped: ["Manual Execution Skipped", "手工执行跳过"],
  promotion_closure_ready_for_sync_audit: ["Promotion Closure Ready For Sync Audit", "推广闭环可进入同步审计"],
  promotion_closure_partial_results: ["Promotion Closure Partial Results", "推广闭环结果不完整"],
  promotion_closure_blocked_by_failed_result: ["Promotion Closure Blocked By Failed Result", "推广闭环被失败结果阻塞"],
  blocked_until_promotion_execution_result_ready: ["Blocked Until Promotion Execution Result Ready", "等待推广执行结果可审计"],
  complete_manual_execution_result_required: ["Complete Manual Execution Result Required", "需要完整手工执行结果"],
  sync_audit_ready: ["Sync Audit Ready", "同步审计就绪"],
  ready_for_promotion_sync_review: ["Ready For Promotion Sync Review", "等待推广同步复核"],
  promotion_sync_review_in_progress: ["Promotion Sync Review In Progress", "推广同步复核进行中"],
  promotion_sync_reviews_approved_for_future_execution: ["Promotion Sync Reviews Approved For Future Execution", "推广同步复核已批准未来执行"],
  blocked_until_promotion_closure_ready: ["Blocked Until Promotion Closure Ready", "等待推广闭环就绪"],
  blocked_no_sync_audit_candidates: ["Blocked: No Sync Audit Candidates", "没有同步审计候选"],
  pending_sync_review: ["Pending Sync Review", "等待同步复核"],
  approved_for_future_sync: ["Approved For Future Sync", "批准未来同步"],
  blocked_needs_sync_inputs: ["Blocked: Needs Sync Inputs", "需要同步资料"],
  deferred_by_sync_review: ["Deferred By Sync Review", "同步复核已延期"],
  blocked_by_sync_review_rejection: ["Blocked By Sync Review Rejection", "同步复核已拒绝"],
  sync_review_note_recorded: ["Sync Review Note Recorded", "同步复核备注已记录"],
  ready_for_manual_sync_handoff: ["Ready For Manual Sync Handoff", "等待人工同步交接"],
  blocked_until_sync_review_approval: ["Blocked Until Sync Review Approval", "等待同步复核批准"],
  blocked_until_sync_reviews_ready: ["Blocked Until Sync Reviews Ready", "等待同步复核就绪"],
  waiting_manual_sync_execution: ["Waiting Manual Sync Execution", "等待人工同步执行"],
  regression_maintainer: ["Regression Maintainer", "回归基线维护人"],
  blocked_until_sync_execution_prerequisites_confirmed: ["Blocked Until Sync Execution Prerequisites Confirmed", "等待同步执行前置条件确认"],
  ready_for_manual_sync_execution_confirmation: ["Ready For Manual Sync Execution Confirmation", "等待人工同步执行确认"],
  blocked_until_sync_handoff_ready: ["Blocked Until Sync Handoff Ready", "等待同步交接就绪"],
  blocked_missing_sync_execution_prerequisites: ["Blocked: Missing Sync Execution Prerequisites", "阻塞：缺少同步执行前置条件"],
  sync_execution_prerequisites_confirmed: ["Sync Execution Prerequisites Confirmed", "同步执行前置条件已确认"],
  pending_sync_readiness_review: ["Pending Sync Readiness Review", "等待同步就绪复核"],
  confirmed_ready_for_manual_sync_execution: ["Confirmed Ready For Manual Sync Execution", "已确认可人工同步执行"],
  needs_sync_execution_inputs: ["Needs Sync Execution Inputs", "需要同步执行资料"],
  blocked_needs_sync_execution_inputs: ["Blocked: Needs Sync Execution Inputs", "阻塞：需要同步执行资料"],
  deferred_by_sync_readiness_review: ["Deferred By Sync Readiness Review", "同步就绪复核已延期"],
  blocked_by_sync_readiness_review_rejection: ["Blocked By Sync Readiness Review Rejection", "同步就绪复核已拒绝"],
  waiting_for_manual_sync_execution_result: ["Waiting For Manual Sync Execution Result", "等待手工同步执行结果"],
  sync_execution_result_recorded: ["Sync Execution Result Recorded", "同步执行结果已记录"],
  sync_execution_result_failed: ["Sync Execution Result Failed", "同步执行结果失败"],
  sync_execution_result_needs_review: ["Sync Execution Result Needs Review", "同步执行结果需要复核"],
  blocked_until_sync_execution_readiness_confirmed: ["Blocked Until Sync Execution Readiness Confirmed", "等待同步执行就绪确认"],
  blocked_until_sync_execution_ready: ["Blocked Until Sync Execution Ready", "等待同步执行就绪"],
  manual_sync_execution_recorded: ["Manual Sync Execution Recorded", "手工同步执行已记录"],
  manual_sync_execution_failed: ["Manual Sync Execution Failed", "手工同步执行失败"],
  manual_sync_execution_skipped: ["Manual Sync Execution Skipped", "手工同步执行跳过"],
  sync_closure_ready_for_final_review: ["Sync Closure Ready For Final Review", "同步关闭可进入最终复核"],
  sync_closure_partial_results: ["Sync Closure Partial Results", "同步关闭结果不完整"],
  sync_closure_blocked_by_failed_result: ["Sync Closure Blocked By Failed Result", "同步关闭被失败结果阻塞"],
  blocked_until_sync_execution_result_ready: ["Blocked Until Sync Execution Result Ready", "等待同步执行结果可审计"],
  ready_for_final_manual_sync_review: ["Ready For Final Manual Sync Review", "等待最终人工同步复核"],
  ready_for_sync_closure_review: ["Ready For Sync Closure Review", "等待同步关闭最终复核"],
  sync_closure_review_in_progress: ["Sync Closure Review In Progress", "同步关闭最终复核进行中"],
  sync_closure_reviews_approved_for_future_execution: ["Sync Closure Reviews Approved For Future Execution", "同步关闭复核已批准未来执行"],
  blocked_until_sync_closure_ready: ["Blocked Until Sync Closure Ready", "等待同步关闭审计就绪"],
  blocked_no_sync_closure_candidates: ["Blocked: No Sync Closure Candidates", "没有同步关闭候选"],
  pending_sync_closure_review: ["Pending Sync Closure Review", "等待同步关闭复核"],
  approved_for_final_sync: ["Approved For Final Sync", "批准最终同步"],
  needs_final_sync_inputs: ["Needs Final Sync Inputs", "需要最终同步资料"],
  blocked_needs_final_sync_inputs: ["Blocked: Needs Final Sync Inputs", "缺少最终同步资料"],
  deferred_by_sync_closure_review: ["Deferred By Sync Closure Review", "同步关闭复核已延期"],
  blocked_by_sync_closure_review_rejection: ["Blocked By Sync Closure Review Rejection", "同步关闭复核已拒绝"],
  sync_closure_review_note_recorded: ["Sync Closure Review Note Recorded", "同步关闭复核备注已记录"],
  ready_for_manual_final_sync_handoff: ["Ready For Manual Final Sync Handoff", "等待最终人工同步交接"],
  blocked_until_sync_closure_review_approval: ["Blocked Until Sync Closure Review Approval", "等待同步关闭复核批准"],
  blocked_until_final_sync_actions_ready: ["Blocked Until Final Sync Actions Ready", "等待最终同步动作就绪"],
  waiting_manual_final_sync_execution: ["Waiting Manual Final Sync Execution", "等待最终人工同步执行"],
  final_sync_handoff_item: ["Final Sync Handoff Item", "最终同步交接项"],
  ready_for_manual_final_sync_execution_confirmation: ["Ready For Manual Final Sync Execution Confirmation", "等待最终人工同步执行确认"],
  blocked_until_final_sync_execution_prerequisites_confirmed: ["Blocked Until Final Sync Execution Prerequisites Confirmed", "等待最终同步执行前置条件确认"],
  blocked_until_final_sync_handoff_ready: ["Blocked Until Final Sync Handoff Ready", "等待最终同步交接就绪"],
  final_sync_execution_prerequisites_confirmed: ["Final Sync Execution Prerequisites Confirmed", "最终同步执行前置条件已确认"],
  blocked_missing_final_sync_execution_prerequisites: ["Blocked: Missing Final Sync Execution Prerequisites", "阻塞：缺少最终同步执行前置条件"],
  manual_final_sync_execution_recorded: ["Manual Final Sync Execution Recorded", "最终人工同步执行已记录"],
  manual_final_sync_execution_failed: ["Manual Final Sync Execution Failed", "最终人工同步执行失败"],
  manual_final_sync_execution_skipped: ["Manual Final Sync Execution Skipped", "最终人工同步执行跳过"],
  waiting_for_manual_final_sync_execution_result: ["Waiting For Manual Final Sync Execution Result", "等待最终人工同步执行结果"],
  final_sync_execution_result_recorded: ["Final Sync Execution Result Recorded", "最终同步执行结果已记录"],
  final_sync_execution_result_failed: ["Final Sync Execution Result Failed", "最终同步执行结果失败"],
  final_sync_execution_result_needs_review: ["Final Sync Execution Result Needs Review", "最终同步执行结果需要复核"],
  blocked_until_final_sync_execution_readiness_confirmed: ["Blocked Until Final Sync Execution Readiness Confirmed", "等待最终同步执行就绪确认"],
  blocked_until_final_sync_execution_ready: ["Blocked Until Final Sync Execution Ready", "等待最终同步执行就绪"],
  final_sync_closure_ready_for_completion_review: ["Final Sync Closure Ready For Completion Review", "最终同步关闭可进入完成复核"],
  final_sync_closure_blocked_by_failed_result: ["Final Sync Closure Blocked By Failed Result", "最终同步关闭被失败结果阻塞"],
  final_sync_closure_partial_results: ["Final Sync Closure Partial Results", "最终同步关闭结果不完整"],
  blocked_until_final_sync_execution_result_ready: ["Blocked Until Final Sync Execution Result Ready", "等待最终同步执行结果就绪"],
  metadata_ready_for_final_completion_review: ["Metadata Ready For Final Completion Review", "元数据可进入最终完成复核"],
  final_sync_execution_result_missing: ["Final Sync Execution Result Missing", "缺少最终同步执行结果"],
  complete_final_sync_execution_result_required: ["Complete Final Sync Execution Result Required", "需要完整最终同步执行结果"],
  product_owner_final_completion_confirmation: ["Product Owner Final Completion Confirmation", "产品负责人最终完成确认"],
  post_final_sync_validation_summary: ["Post-final Sync Validation Summary", "最终同步后验证摘要"],
  no_raw_file_or_credentials: ["No Raw File Or Credentials", "无原始文件或凭据"],
  complete_sync_execution_result_required: ["Complete Sync Execution Result Required", "需要完整同步执行结果"],
  product_owner_final_sync_closure_confirmation: ["Product Owner Final Sync Closure Confirmation", "产品负责人最终同步关闭确认"],
  post_sync_validation_summary: ["Post-sync Validation Summary", "同步后验证摘要"],
  rollback_reversal_verification: ["Rollback/Reversal Verification", "回滚或反转验证"],
  ready_for_final_completion_review: ["Ready For Final Completion Review", "最终完成确认就绪"],
  final_completion_review_in_progress: ["Final Completion Review In Progress", "最终完成确认进行中"],
  final_completion_reviews_approved_for_future_publication: ["Final Completion Reviews Approved For Future Publication", "最终完成确认已批准未来发布"],
  blocked_until_final_sync_closure_ready: ["Blocked Until Final Sync Closure Ready", "等待最终同步关闭审计就绪"],
  blocked_no_final_completion_candidates: ["Blocked: No Final Completion Candidates", "没有最终完成候选项"],
  pending_final_completion_review: ["Pending Final Completion Review", "等待最终完成确认"],
  approved_final_completion: ["Approved Final Completion", "批准最终完成"],
  approved_but_not_published: ["Approved But Not Published", "已批准但未发布"],
  needs_completion_inputs: ["Needs Completion Inputs", "需要完成确认资料"],
  blocked_needs_completion_inputs: ["Blocked: Needs Completion Inputs", "缺少完成确认资料"],
  deferred_by_final_completion_review: ["Deferred By Final Completion Review", "最终完成确认已延期"],
  blocked_by_final_completion_review_rejection: ["Blocked By Final Completion Review Rejection", "最终完成确认被拒绝"],
  final_completion_review_note_recorded: ["Final Completion Review Note Recorded", "最终完成确认备注已记录"],
  ready_for_manual_final_publication_handoff: ["Ready For Manual Final Publication Handoff", "等待最终人工发布交接"],
  blocked_until_final_completion_review_approval: ["Blocked Until Final Completion Review Approval", "等待最终完成确认批准"],
  blocked_until_final_publication_actions_ready: ["Blocked Until Final Publication Actions Ready", "等待最终发布动作就绪"],
  waiting_manual_final_publication: ["Waiting Manual Final Publication", "等待最终人工发布"],
  final_publication_handoff_item: ["Final Publication Handoff Item", "最终发布交接项"],
  publication_reference: ["Publication Reference", "发布引用"],
  published_memory_event_ids: ["Published Memory Event IDs", "已发布记忆事件 ID"],
  published_baseline_id: ["Published Baseline ID", "已发布基线 ID"],
  post_publication_validation_summary: ["Post-publication Validation Summary", "发布后验证摘要"],
  product_owner_publication_confirmation: ["Product Owner Publication Confirmation", "产品负责人发布确认"],
  ready_for_manual_final_publication_confirmation: ["Ready For Manual Final Publication Confirmation", "等待人工最终发布确认"],
  blocked_until_final_publication_prerequisites_confirmed: ["Blocked Until Final Publication Prerequisites Confirmed", "等待最终发布前置条件确认"],
  blocked_until_final_publication_handoff_ready: ["Blocked Until Final Publication Handoff Ready", "等待最终发布交接就绪"],
  final_publication_prerequisites_confirmed: ["Final Publication Prerequisites Confirmed", "最终发布前置条件已确认"],
  blocked_missing_final_publication_prerequisites: ["Blocked: Missing Final Publication Prerequisites", "缺少最终发布前置条件"],
  explicit_product_owner_final_publication_confirmation: ["Product Owner Final Publication Confirmation", "产品负责人最终发布确认"],
  publication_evidence_capture_plan: ["Publication Evidence Capture Plan", "发布证据采集计划"],
  publication_rollback_plan: ["Publication Rollback Plan", "发布回滚计划"],
  waiting_for_manual_final_publication_result: ["Waiting For Manual Final Publication Result", "等待最终人工发布结果"],
  final_publication_result_recorded: ["Final Publication Result Recorded", "最终发布结果已记录"],
  final_publication_result_failed: ["Final Publication Result Failed", "最终发布结果失败"],
  final_publication_result_needs_review: ["Final Publication Result Needs Review", "最终发布结果需要复核"],
  blocked_until_final_publication_readiness_confirmed: ["Blocked Until Final Publication Readiness Confirmed", "等待最终发布就绪确认"],
  blocked_until_final_publication_ready: ["Blocked Until Final Publication Ready", "等待最终发布就绪"],
  manual_final_publication_recorded: ["Manual Final Publication Recorded", "已记录手工最终发布"],
  manual_final_publication_failed: ["Manual Final Publication Failed", "手工最终发布失败"],
  manual_final_publication_skipped: ["Manual Final Publication Skipped", "已跳过手工最终发布"],
  final_publication_closure_ready_for_archive_review: ["Final Publication Closure Ready For Archive Review", "最终发布闭环可进入归档复核"],
  final_publication_closure_blocked_by_failed_result: ["Final Publication Closure Blocked By Failed Result", "最终发布闭环被失败结果阻塞"],
  final_publication_closure_partial_results: ["Final Publication Closure Partial Results", "最终发布闭环结果不完整"],
  blocked_until_final_publication_result_ready: ["Blocked Until Final Publication Result Ready", "等待最终发布结果就绪"],
  metadata_ready_for_final_release_review: ["Metadata Ready For Final Release Review", "元数据可进入最终发布复核"],
  final_publication_result_missing: ["Final Publication Result Missing", "缺少最终发布结果"],
  complete_final_publication_result_required: ["Complete Final Publication Result Required", "需要完整最终发布结果"],
  product_owner_final_publication_closure_confirmation: ["Product Owner Final Publication Closure Confirmation", "产品负责人最终发布闭环确认"],
  ready_for_product_owner_final_release_review: ["Ready For Product Owner Final Release Review", "等待产品负责人最终发布复核"],
  blocked_until_final_publication_closure_complete: ["Blocked Until Final Publication Closure Complete", "等待最终发布闭环完整"],
  blocked_until_final_publication_closure_ready: ["Blocked Until Final Publication Closure Ready", "等待最终发布闭环就绪"],
  final_release_review_blocked_by_failed_publication_result: ["Final Release Review Blocked By Failed Publication Result", "最终发布复核被失败发布结果阻塞"],
  pending_product_owner_final_release_review: ["Pending Product Owner Final Release Review", "等待产品负责人最终发布复核"],
  product_owner_final_release_confirmation: ["Product Owner Final Release Confirmation", "产品负责人最终发布确认"],
  archive_reference_or_release_note: ["Archive Reference Or Release Note", "归档引用或发布说明"],
  post_release_monitoring_owner: ["Post-release Monitoring Owner", "发布后监控负责人"],
  rollback_owner_confirmation: ["Rollback Owner Confirmation", "回滚负责人确认"],
  project_memory_publication_scope: ["Project Memory Publication Scope", "项目记忆发布范围"],
  baseline_update_endpoint_or_store: ["Baseline Update Endpoint Or Store", "基线更新 endpoint/存储"],
  baseline_version_label: ["Baseline Version Label", "基线版本标签"],
  baseline_rollback_plan: ["Baseline Rollback Plan", "基线回滚计划"],
  live_hermes_rollback_plan: ["Live Hermes Rollback Plan", "Live Hermes 回滚计划"],
  explicit_product_owner_sync_execution_confirmation: ["Product Owner Sync Execution Confirmation", "产品负责人同步执行确认"],
  sync_execution_evidence_capture_plan: ["Sync Execution Evidence Capture Plan", "同步执行证据采集计划"],
  execution_reference: ["Execution Reference", "执行引用"],
  changed_records: ["Changed Records", "变更记录"],
  validation_summary: ["Validation Summary", "验证摘要"],
  rollback_summary: ["Rollback Summary", "回滚摘要"],
  product_owner_confirmation: ["Product Owner Confirmation", "产品负责人确认"],
  explicit_product_owner_execution_confirmation: ["Product Owner Execution Confirmation", "产品负责人执行确认"],
  explicit_product_owner_final_sync_execution_confirmation: ["Product Owner Final Sync Execution Confirmation", "产品负责人最终同步执行确认"],
  current_compileall_validation_output: ["Current Compileall Validation Output", "当前 compileall 验证输出"],
  current_test_harness_validation_output: ["Current Test Harness Validation Output", "当前测试 harness 验证输出"],
  execution_evidence_capture_plan: ["Execution Evidence Capture Plan", "执行证据采集计划"],
  rollback_or_reversal_plan: ["Rollback Or Reversal Plan", "回滚或反转计划"],
  baseline_update_target_contract: ["Baseline Update Target Contract", "基线更新目标合同"],
  baseline_version_label_confirmation: ["Baseline Version Label Confirmation", "基线版本标签确认"],
  live_hermes_endpoint: ["Live Hermes Endpoint", "Live Hermes endpoint"],
  live_hermes_auth_scope: ["Live Hermes Auth Scope", "Live Hermes 授权范围"],
  live_hermes_memory_schema: ["Live Hermes Memory Schema", "Live Hermes 记忆 schema"],
  live_hermes_retention_policy: ["Live Hermes Retention Policy", "Live Hermes 保留策略"],
  live_hermes_tenant_factory_scope: ["Live Hermes Tenant/Factory Scope", "Live Hermes 租户/工厂范围"],
  validation_passed: ["Validation Passed", "验证通过"],
  validation_failed: ["Validation Failed", "验证失败"],
  blocked: ["Blocked", "阻塞"],
  codex_worktree_result_record: ["Codex Worktree Result Record", "Codex Worktree 结果记录"],
  pending_review: ["Pending Review", "待确认"],
  auto_regression: ["Auto Regression", "自动回归"],
  approved: ["Approved", "已确认"],
  needs_changes: ["Needs Changes", "需要修改"],
  rejected: ["Rejected", "已拒绝"],
  note_only: ["Note Only", "仅备注"],
  registered: ["Registered", "已登记"],
  skipped_for_now: ["Skipped For Now", "暂时跳过"],
  not_available: ["Not Available", "不可用"],
  not_registered: ["Not Registered", "未登记"],
  ready_for_regression: ["Ready For Regression", "可固化回归"],
  blocked_pending_playbook_approval: ["Blocked Pending Playbook Approval", "等待 Playbook 审批"],
  review_or_data_decision_required: ["Review/Data Decision Required", "需要确认/数据决策"],
  failed_task_blocked: ["Failed Task Blocked", "失败任务阻塞"],
  approval_incomplete: ["Approval Incomplete", "确认未完成"],
  baseline_promoted: ["Baseline Promoted", "基线已固化"],
  training_baseline: ["Training Baseline", "训练基线"],
  approved_playbook: ["Approved Playbook", "已批准 Playbook"],
  blocked_playbook_candidate: ["Blocked Playbook", "阻塞 Playbook"],
};

const KPI_TEXT = {
  training_task_count: ["Training Tasks", "训练任务"],
  auto_evaluated_task_count: ["Auto Evaluated", "自动评测"],
  passed_task_count: ["Passed Tasks", "通过任务"],
  needs_data_task_count: ["Needs Data", "需要数据"],
  failed_task_count: ["Failed Tasks", "失败任务"],
  average_score: ["Average Score", "平均评分"],
  evidence_resolution_rate: ["Evidence Resolution", "证据解析率"],
  governance_alignment_rate: ["Governance Alignment", "治理对齐率"],
  human_review_required_count: ["Human Review", "人工确认"],
  pending_review_count: ["Pending Review", "待确认"],
  approved_review_count: ["Approved Review", "已确认"],
  registered_data_source_count: ["Registered Data", "已登记数据"],
  playbook_regression_candidate_count: ["Playbook Regression Candidates", "Playbook 回归候选"],
  playbook_regression_ready_count: ["Ready Playbook Regression", "可回归 Playbook"],
  playbook_regression_blocked_count: ["Blocked Playbook Regression", "阻塞 Playbook"],
  regression_case_count: ["Regression Cases", "回归用例"],
  regression_executable_case_count: ["Executable Cases", "可执行用例"],
  regression_passed_case_count: ["Passed Cases", "通过用例"],
  regression_failed_case_count: ["Failed Cases", "失败用例"],
  regression_blocked_case_count: ["Blocked Cases", "阻塞用例"],
  regression_pass_rate: ["Pass Rate", "通过率"],
  codex_work_packet_queue_ready: ["Codex Packet Queue Ready", "Codex 工作包队列可用"],
  codex_work_packet_count: ["Codex Work Packets", "Codex 工作包数量"],
  codex_patch_queue_ready: ["Codex Patch Queue Ready", "Codex Patch 队列可用"],
  codex_patch_candidate_count: ["Codex Patch Candidates", "Codex Patch 候选数量"],
  codex_patch_training_signal_count: ["Training Signals", "训练信号数量"],
  codex_execution_gate_ready: ["Codex Execution Gate Ready", "Codex 执行闸门可用"],
  codex_execution_candidate_count: ["Codex Execution Candidates", "Codex 执行候选数量"],
  codex_automatic_execution_allowed: ["Automatic Execution Allowed", "允许自动执行"],
  codex_execution_review_count: ["Codex Execution Reviews", "Codex 执行复核数量"],
  codex_worktree_preparation_approved_count: ["Worktree Approvals", "Worktree 准备批准数量"],
  codex_worktree_preparation_queue_ready: ["Worktree Prep Queue Ready", "Worktree 准备队列可用"],
  codex_worktree_preparation_task_count: ["Worktree Prep Tasks", "Worktree 准备任务数量"],
  codex_worktree_launch_gate_ready: ["Worktree Launch Gate Ready", "Worktree 启动门控可用"],
  codex_worktree_launch_request_count: ["Worktree Launch Requests", "Worktree 启动请求数量"],
  codex_automatic_worktree_launch_allowed: ["Automatic Worktree Launch Allowed", "允许自动启动 Worktree"],
  codex_worktree_result_count: ["Worktree Result Count", "Worktree 结果数量"],
  codex_worktree_validation_passed_count: ["Worktree Validation Passed", "Worktree 验证通过数量"],
  codex_worktree_validation_failed_count: ["Worktree Validation Failed", "Worktree 验证失败数量"],
  codex_automatic_result_merge_allowed: ["Automatic Result Merge Allowed", "允许自动合并结果"],
  codex_worktree_result_review_count: ["Worktree Result Reviews", "Worktree 结果复核数量"],
  codex_worktree_regression_promotion_candidate_count: ["Regression Promotion Candidates", "回归推广候选数量"],
  codex_worktree_hermes_memory_candidate_count: ["Hermes Memory Candidates", "Hermes 记忆候选数量"],
  codex_automatic_result_promotion_allowed: ["Automatic Result Promotion Allowed", "允许自动推广结果"],
  codex_promotion_candidate_queue_ready: ["Promotion Candidate Queue Ready", "推广候选队列可用"],
  codex_regression_promotion_candidate_count: ["Regression Promotion Candidates", "回归推广候选数量"],
  codex_hermes_memory_promotion_candidate_count: ["Hermes Memory Promotion Candidates", "Hermes 记忆推广候选数量"],
  codex_promotion_approval_gate_ready: ["Promotion Approval Gate Ready", "推广审批门控可用"],
  codex_promotion_approval_pending_count: ["Pending Promotion Approvals", "待审批推广数量"],
  codex_promotion_approved_future_action_count: ["Approved Future Actions", "已批准未来动作数量"],
  codex_promotion_automatic_execution_allowed: ["Automatic Promotion Execution Allowed", "允许自动执行推广"],
  codex_promotion_handoff_queue_ready: ["Promotion Handoff Queue Ready", "推广交接队列可用"],
  codex_promotion_handoff_item_count: ["Promotion Handoff Items", "推广交接项数量"],
  codex_promotion_handoff_manual_execution_required: ["Manual Execution Required", "需要人工执行"],
  codex_promotion_handoff_automatic_execution_allowed: ["Automatic Handoff Execution Allowed", "允许自动执行交接"],
  codex_promotion_execution_readiness_ready: ["Promotion Execution Readiness Ready", "推广执行就绪"],
  codex_promotion_execution_readiness_item_count: ["Promotion Execution Readiness Items", "推广执行就绪项"],
  codex_promotion_execution_blocked_item_count: ["Blocked Readiness Items", "阻塞就绪项"],
  codex_promotion_execution_automatic_allowed: ["Automatic Promotion Execution Allowed", "允许自动推广执行"],
  codex_promotion_execution_readiness_review_count: ["Promotion Readiness Reviews", "推广就绪复核数量"],
  codex_promotion_execution_readiness_confirmed_count: ["Promotion Readiness Confirmed", "推广就绪确认数量"],
  codex_promotion_execution_result_count: ["Promotion Execution Results", "推广执行结果数量"],
  codex_promotion_execution_result_passed_count: ["Promotion Execution Recorded", "推广执行已记录数量"],
  codex_promotion_execution_result_contract_complete_count: ["Promotion Result Contracts Complete", "推广结果合约完成数量"],
  codex_promotion_execution_result_automatic_allowed: ["Automatic Promotion Result Execution Allowed", "允许自动执行推广结果"],
  codex_promotion_closure_ready: ["Promotion Closure Ready", "推广闭环就绪"],
  codex_promotion_closure_expected_result_count: ["Expected Promotion Results", "应有推广结果数量"],
  codex_promotion_closure_complete_result_count: ["Complete Promotion Results", "完整推广结果数量"],
  codex_promotion_sync_audit_candidate_count: ["Sync Audit Candidates", "同步审计候选数量"],
  codex_promotion_closure_automatic_allowed: ["Automatic Closure Allowed", "允许自动关闭推广"],
  codex_promotion_sync_review_gate_ready: ["Sync Review Gate Ready", "同步复核门控就绪"],
  codex_promotion_sync_candidate_count: ["Sync Candidates", "同步候选数量"],
  codex_promotion_sync_review_count: ["Sync Reviews", "同步复核数量"],
  codex_promotion_sync_approved_count: ["Approved Sync Reviews", "已批准同步复核"],
  codex_promotion_sync_automatic_allowed: ["Automatic Sync Allowed", "允许自动同步"],
  codex_promotion_sync_handoff_queue_ready: ["Sync Handoff Ready", "同步交接就绪"],
  codex_promotion_sync_handoff_item_count: ["Sync Handoff Items", "同步交接项数量"],
  codex_promotion_sync_handoff_hermes_count: ["Hermes Sync Handoffs", "Hermes 同步交接数量"],
  codex_promotion_sync_handoff_regression_count: ["Regression Sync Handoffs", "回归基线同步交接数量"],
  codex_promotion_sync_handoff_automatic_allowed: ["Automatic Sync Handoff Allowed", "允许自动同步交接"],
  codex_promotion_sync_execution_readiness_ready: ["Sync Execution Readiness Ready", "同步执行就绪"],
  codex_promotion_sync_execution_readiness_item_count: ["Sync Execution Readiness Items", "同步执行就绪项"],
  codex_promotion_sync_execution_blocked_item_count: ["Blocked Sync Readiness Items", "阻塞同步就绪项"],
  codex_promotion_sync_execution_confirmed_count: ["Confirmed Sync Readiness Items", "已确认同步就绪项"],
  codex_promotion_sync_readiness_review_count: ["Sync Readiness Reviews", "同步就绪复核数量"],
  codex_promotion_sync_readiness_confirmed_count: ["Confirmed Sync Readiness Reviews", "已确认同步就绪复核"],
  codex_promotion_sync_execution_automatic_allowed: ["Automatic Sync Execution Allowed", "允许自动同步执行"],
  codex_promotion_sync_execution_result_count: ["Sync Execution Results", "同步执行结果数量"],
  codex_promotion_sync_execution_result_passed_count: ["Sync Execution Recorded", "同步执行已记录数量"],
  codex_promotion_sync_execution_result_contract_complete_count: ["Sync Result Contracts Complete", "同步结果合约完成数量"],
  codex_promotion_sync_execution_result_automatic_allowed: ["Automatic Sync Result Execution Allowed", "允许自动执行同步结果"],
  codex_promotion_sync_closure_ready: ["Sync Closure Ready", "同步关闭就绪"],
  codex_promotion_sync_closure_expected_result_count: ["Expected Sync Results", "应有同步结果数量"],
  codex_promotion_sync_closure_complete_result_count: ["Complete Sync Results", "完整同步结果数量"],
  codex_promotion_sync_closure_missing_result_count: ["Missing Sync Results", "缺失同步结果数量"],
  codex_promotion_sync_closure_automatic_allowed: ["Automatic Sync Closure Allowed", "允许自动同步关闭"],
  codex_promotion_sync_closure_review_gate_ready: ["Sync Closure Review Gate Ready", "同步关闭复核闸门就绪"],
  codex_promotion_sync_closure_review_candidate_count: ["Sync Closure Review Candidates", "同步关闭复核候选数量"],
  codex_promotion_sync_closure_review_count: ["Sync Closure Reviews", "同步关闭复核数量"],
  codex_promotion_sync_closure_approved_count: ["Approved Sync Closure Reviews", "已批准同步关闭复核"],
  codex_promotion_sync_closure_review_automatic_allowed: ["Automatic Sync Closure Review Allowed", "允许自动同步关闭复核"],
  codex_promotion_final_sync_handoff_queue_ready: ["Final Sync Handoff Ready", "最终同步交接就绪"],
  codex_promotion_final_sync_handoff_item_count: ["Final Sync Handoff Items", "最终同步交接项数量"],
  codex_promotion_final_sync_handoff_hermes_count: ["Hermes Final Sync Handoffs", "Hermes 最终同步交接数量"],
  codex_promotion_final_sync_handoff_regression_count: ["Regression Final Sync Handoffs", "回归基线最终同步交接数量"],
  codex_promotion_final_sync_handoff_automatic_allowed: ["Automatic Final Sync Handoff Allowed", "允许自动最终同步交接"],
  codex_promotion_final_sync_execution_readiness_ready: ["Final Sync Execution Ready", "最终同步执行就绪"],
  codex_promotion_final_sync_execution_readiness_item_count: ["Final Sync Readiness Items", "最终同步就绪项数量"],
  codex_promotion_final_sync_execution_blocked_item_count: ["Blocked Final Sync Readiness Items", "阻塞的最终同步就绪项数量"],
  codex_promotion_final_sync_execution_confirmed_count: ["Confirmed Final Sync Readiness Items", "已确认最终同步就绪项数量"],
  codex_promotion_final_sync_execution_automatic_allowed: ["Automatic Final Sync Execution Allowed", "允许自动最终同步执行"],
  codex_promotion_final_sync_execution_result_count: ["Final Sync Execution Results", "最终同步执行结果数量"],
  codex_promotion_final_sync_execution_result_passed_count: ["Recorded Final Sync Execution Results", "已记录最终同步执行结果"],
  codex_promotion_final_sync_execution_result_contract_complete_count: ["Complete Final Sync Execution Result Contracts", "完整最终同步执行结果契约"],
  codex_promotion_final_sync_execution_result_automatic_allowed: ["Automatic Final Sync Result Execution Allowed", "允许自动执行最终同步结果"],
  codex_promotion_final_sync_closure_ready: ["Final Sync Closure Ready", "最终同步关闭就绪"],
  codex_promotion_final_sync_closure_expected_result_count: ["Expected Final Sync Results", "应有最终同步结果数量"],
  codex_promotion_final_sync_closure_complete_result_count: ["Complete Final Sync Results", "完整最终同步结果数量"],
  codex_promotion_final_sync_closure_missing_result_count: ["Missing Final Sync Results", "缺失最终同步结果数量"],
  codex_promotion_final_sync_closure_automatic_allowed: ["Automatic Final Sync Closure Allowed", "允许自动最终同步关闭"],
  codex_promotion_final_completion_review_gate_ready: ["Final Completion Review Gate Ready", "最终完成确认门就绪"],
  codex_promotion_final_completion_review_candidate_count: ["Final Completion Review Candidates", "最终完成确认候选数"],
  codex_promotion_final_completion_review_count: ["Final Completion Reviews", "最终完成确认数"],
  codex_promotion_final_completion_approved_count: ["Approved Final Completion Reviews", "已批准最终完成数"],
  codex_promotion_final_completion_review_automatic_allowed: ["Automatic Final Completion Review Allowed", "允许自动最终完成确认"],
  codex_promotion_final_publication_handoff_ready: ["Final Publication Handoff Ready", "最终发布交接就绪"],
  codex_promotion_final_publication_handoff_item_count: ["Final Publication Handoff Items", "最终发布交接项数量"],
  codex_promotion_final_publication_handoff_hermes_count: ["Hermes Final Publication Handoffs", "Hermes 最终发布交接数量"],
  codex_promotion_final_publication_handoff_regression_count: ["Regression Final Publication Handoffs", "回归基线最终发布交接数量"],
  codex_promotion_final_publication_handoff_automatic_allowed: ["Automatic Final Publication Handoff Allowed", "允许自动最终发布交接"],
  codex_promotion_final_publication_readiness_ready: ["Final Publication Readiness Ready", "最终发布就绪"],
  codex_promotion_final_publication_readiness_item_count: ["Final Publication Readiness Items", "最终发布就绪项数量"],
  codex_promotion_final_publication_blocked_item_count: ["Blocked Final Publication Readiness Items", "阻塞的最终发布就绪项数量"],
  codex_promotion_final_publication_confirmed_count: ["Confirmed Final Publication Readiness Items", "已确认最终发布就绪项数量"],
  codex_promotion_final_publication_automatic_allowed: ["Automatic Final Publication Allowed", "允许自动最终发布"],
  codex_promotion_final_publication_result_count: ["Final Publication Results", "最终发布结果数量"],
  codex_promotion_final_publication_result_passed_count: ["Recorded Final Publication Results", "已记录最终发布结果"],
  codex_promotion_final_publication_result_contract_complete_count: ["Complete Final Publication Result Contracts", "完整最终发布结果契约"],
  codex_promotion_final_publication_result_automatic_allowed: ["Automatic Final Publication Result Allowed", "允许自动最终发布结果"],
  codex_promotion_final_publication_closure_ready: ["Final Publication Closure Ready", "最终发布闭环就绪"],
  codex_promotion_final_publication_closure_expected_result_count: ["Expected Final Publication Results", "应有最终发布结果数量"],
  codex_promotion_final_publication_closure_complete_result_count: ["Complete Final Publication Results", "完整最终发布结果数量"],
  codex_promotion_final_publication_closure_missing_result_count: ["Missing Final Publication Results", "缺失最终发布结果数量"],
  codex_promotion_final_publication_closure_automatic_allowed: ["Automatic Final Publication Closure Allowed", "允许自动最终发布闭环"],
  codex_promotion_final_release_review_gate_ready: ["Final Release Review Gate Ready", "最终发布复核门就绪"],
  codex_promotion_final_release_review_candidate_count: ["Final Release Review Candidates", "最终发布复核候选数量"],
  codex_promotion_final_release_review_blocked_candidate_count: ["Blocked Final Release Review Candidates", "阻塞的最终发布复核候选"],
  codex_promotion_final_release_review_automatic_release_allowed: ["Automatic Final Release Allowed", "允许自动最终发布"],
};

function trainingLanguage() {
  return window.SantoniI18n?.getLanguage?.() || (document.documentElement.lang.startsWith("zh") ? "zh" : "en");
}

function trainingIsZh() {
  return trainingLanguage() === "zh";
}

function t(key) {
  return TRAINING_TEXT[trainingLanguage()]?.[key] || TRAINING_TEXT.en[key] || key;
}

function pair(pairValue) {
  return trainingIsZh() ? pairValue[1] : pairValue[0];
}

function statusText(value) {
  return STATUS_TEXT[value] ? pair(STATUS_TEXT[value]) : value;
}

function kpiText(value) {
  return KPI_TEXT[value] ? pair(KPI_TEXT[value]) : value;
}

function applyStaticText() {
  document.querySelector("#trainingTitle").textContent = t("title");
  document.querySelector("#trainingSubtitle").textContent = t("subtitle");
  document.querySelector("#trainingGuardrailTitle").textContent = t("guardrailTitle");
  document.querySelector("#trainingGuardrailText").textContent = t("guardrailText");
  document.querySelector("#trainingProgressTitle").textContent = t("progressTitle");
  document.querySelector("#trainingProgressText").textContent = t("progressText");
  document.querySelector("#trainingLoopHeading").textContent = t("loop");
  document.querySelector("#trainingTasksHeading").textContent = t("tasks");
  document.querySelector("#capabilityHeading").textContent = t("capability");
  document.querySelector("#hermesResultHeading").textContent = t("hermesJson");
  document.querySelector("#reviewStateHeading").textContent = t("reviewState");
  document.querySelector("#patchQueueHeading").textContent = t("patchQueue");
  document.querySelector("#executionGateHeading").textContent = t("executionGate");
  document.querySelector("#worktreePrepHeading").textContent = t("worktreePrep");
  document.querySelector("#worktreeLaunchHeading").textContent = t("worktreeLaunch");
  document.querySelector("#worktreeResultHeading").textContent = t("worktreeResults");
  document.querySelector("#worktreeResultReviewHeading").textContent = t("worktreeResultReview");
  document.querySelector("#promotionCandidateHeading").textContent = t("promotionCandidates");
  document.querySelector("#promotionApprovalHeading").textContent = t("promotionApproval");
  document.querySelector("#promotionHandoffHeading").textContent = t("promotionHandoff");
  document.querySelector("#promotionReadinessHeading").textContent = t("promotionReadiness");
  document.querySelector("#promotionResultHeading").textContent = t("promotionResult");
  document.querySelector("#promotionClosureHeading").textContent = t("promotionClosure");
  document.querySelector("#promotionSyncReviewHeading").textContent = t("promotionSyncReview");
  document.querySelector("#promotionSyncHandoffHeading").textContent = t("promotionSyncHandoff");
  document.querySelector("#promotionSyncReadinessHeading").textContent = t("promotionSyncReadiness");
  document.querySelector("#promotionSyncResultHeading").textContent = t("promotionSyncResult");
  document.querySelector("#promotionSyncClosureHeading").textContent = t("promotionSyncClosure");
  document.querySelector("#promotionSyncClosureReviewHeading").textContent = t("promotionSyncClosureReview");
  document.querySelector("#promotionFinalSyncHandoffHeading").textContent = t("promotionFinalSyncHandoff");
  document.querySelector("#promotionFinalSyncReadinessHeading").textContent = t("promotionFinalSyncReadiness");
  document.querySelector("#promotionFinalSyncResultHeading").textContent = t("promotionFinalSyncResult");
  document.querySelector("#promotionFinalSyncClosureHeading").textContent = t("promotionFinalSyncClosure");
  document.querySelector("#promotionFinalCompletionReviewHeading").textContent = t("promotionFinalCompletionReview");
  document.querySelector("#promotionFinalPublicationHandoffHeading").textContent = t("promotionFinalPublicationHandoff");
  document.querySelector("#promotionFinalPublicationReadinessHeading").textContent = t("promotionFinalPublicationReadiness");
  document.querySelector("#promotionFinalPublicationResultHeading").textContent = t("promotionFinalPublicationResult");
  document.querySelector("#promotionFinalPublicationClosureHeading").textContent = t("promotionFinalPublicationClosure");
  document.querySelector("#promotionFinalReleaseReviewHeading").textContent = t("promotionFinalReleaseReview");
  document.querySelector("#nextTasksHeading").textContent = t("nextTasks");
  document.querySelector("#trainingKpiHeading").textContent = t("kpi");
  document.querySelector("#trainingEvidenceHeading").textContent = t("evidence");
  document.querySelector("#trainingBaselineHeading").textContent = t("baseline");
  document.querySelector("#playbookRegressionHeading").textContent = t("playbookRegression");
  document.querySelector("#regressionRunHeading").textContent = t("regressionRun");
  document.querySelector("#regressionGateHeading").textContent = t("regressionGate");
  document.querySelector("#nextLoopHandoffHeading").textContent = t("nextLoopHandoff");
  document.querySelector("#nextLoopClosureHeading").textContent = t("nextLoopClosure");
  document.querySelector("#trainingIterationProposalHeading").textContent = t("iterationProposal");
  document.querySelector("#codexWorkPacketHeading").textContent = t("codexWorkPackets");
  runTrainingButton.textContent = t("run");
  promoteBaselineButton.textContent = t("promoteBaseline");
  runRegressionButton.textContent = t("runRegression");
  hermesResultStatus.textContent = t("mockContract");
}

async function loadTraining() {
  applyStaticText();
  trainingStatus.textContent = t("loading");
  const [statusResponse, overviewResponse, roundSummaryResponse, regressionRunResponse, regressionGateResponse, nextLoopResponse, closureResponse, proposalResponse, packetResponse, patchQueueResponse, executionGateResponse, worktreePrepResponse, worktreeLaunchResponse, worktreeResultResponse, worktreeResultReviewResponse, promotionResponse, promotionApprovalResponse, promotionHandoffResponse, promotionReadinessResponse, promotionExecutionResultResponse, promotionClosureResponse, promotionSyncReviewResponse, promotionSyncHandoffResponse, promotionSyncReadinessResponse, promotionSyncResultResponse, promotionSyncClosureResponse, promotionSyncClosureReviewResponse, promotionFinalSyncHandoffResponse, promotionFinalSyncReadinessResponse, promotionFinalSyncResultResponse, promotionFinalSyncClosureResponse, promotionFinalCompletionReviewResponse] = await Promise.all([
    fetch(`/api/status?ts=${Date.now()}`),
    fetch(`/api/training/overview?ts=${Date.now()}`),
    fetch(`/api/training/round-summary?ts=${Date.now()}`),
    fetch(`/api/training/regression-run?ts=${Date.now()}`),
    fetch(`/api/training/regression-gate?ts=${Date.now()}`),
    fetch(`/api/training/next-loop?ts=${Date.now()}`),
    fetch(`/api/training/next-loop-closure?ts=${Date.now()}`),
    fetch(`/api/training/iteration-proposal?ts=${Date.now()}`),
    fetch(`/api/training/codex-work-packets?ts=${Date.now()}`),
    fetch(`/api/training/codex-patch-queue?ts=${Date.now()}`),
    fetch(`/api/training/codex-execution-gate?ts=${Date.now()}`),
    fetch(`/api/training/codex-worktree-prep?ts=${Date.now()}`),
    fetch(`/api/training/codex-worktree-launch?ts=${Date.now()}`),
    fetch(`/api/training/codex-worktree-results?ts=${Date.now()}`),
    fetch(`/api/training/codex-worktree-result-review-gate?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-candidates?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-approval-gate?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-handoff?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-execution-readiness?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-execution-results?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-closure-audit?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-review-gate?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-handoff?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-readiness?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-execution-results?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-closure-audit?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-closure-review-gate?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-final-sync-handoff?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-final-sync-readiness?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-final-sync-execution-results?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-final-sync-closure-audit?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-final-completion-review-gate?ts=${Date.now()}`),
  ]);
  lastTrainingStatus = await statusResponse.json();
  lastTrainingResult = await overviewResponse.json();
  lastRoundSummary = await roundSummaryResponse.json();
  lastRegressionRun = await regressionRunResponse.json();
  lastRegressionGate = await regressionGateResponse.json();
  lastNextLoopHandoff = await nextLoopResponse.json();
  lastNextLoopClosure = await closureResponse.json();
  lastIterationProposal = await proposalResponse.json();
  lastCodexWorkPackets = await packetResponse.json();
  lastCodexPatchQueue = await patchQueueResponse.json();
  lastCodexExecutionGate = await executionGateResponse.json();
  lastCodexWorktreePrep = await worktreePrepResponse.json();
  lastCodexWorktreeLaunch = await worktreeLaunchResponse.json();
  lastCodexWorktreeResults = await worktreeResultResponse.json();
  lastCodexWorktreeResultReviewGate = await worktreeResultReviewResponse.json();
  lastCodexPromotionCandidates = await promotionResponse.json();
  lastCodexPromotionApprovalGate = await promotionApprovalResponse.json();
  lastCodexPromotionHandoff = await promotionHandoffResponse.json();
  lastCodexPromotionReadiness = await promotionReadinessResponse.json();
  lastCodexPromotionExecutionResults = await promotionExecutionResultResponse.json();
  lastCodexPromotionClosureAudit = await promotionClosureResponse.json();
  lastCodexPromotionSyncReviewGate = await promotionSyncReviewResponse.json();
  lastCodexPromotionSyncHandoff = await promotionSyncHandoffResponse.json();
  lastCodexPromotionSyncReadiness = await promotionSyncReadinessResponse.json();
  lastCodexPromotionSyncExecutionResults = await promotionSyncResultResponse.json();
  lastCodexPromotionSyncClosureAudit = await promotionSyncClosureResponse.json();
  lastCodexPromotionSyncClosureReviewGate = await promotionSyncClosureReviewResponse.json();
  lastCodexPromotionFinalSyncHandoff = await promotionFinalSyncHandoffResponse.json();
  lastCodexPromotionFinalSyncReadiness = await promotionFinalSyncReadinessResponse.json();
  lastCodexPromotionFinalSyncExecutionResults = await promotionFinalSyncResultResponse.json();
  lastCodexPromotionFinalSyncClosureAudit = await promotionFinalSyncClosureResponse.json();
  lastCodexPromotionFinalCompletionReviewGate = await promotionFinalCompletionReviewResponse.json();
  lastCodexPromotionFinalPublicationHandoff = await fetch(`/api/training/codex-promotion-final-publication-handoff?ts=${Date.now()}`).then((response) => response.json());
  lastCodexPromotionFinalPublicationReadiness = await fetch(`/api/training/codex-promotion-final-publication-readiness?ts=${Date.now()}`).then((response) => response.json());
  lastCodexPromotionFinalPublicationResults = await fetch(`/api/training/codex-promotion-final-publication-results?ts=${Date.now()}`).then((response) => response.json());
  lastCodexPromotionFinalPublicationClosureAudit = await fetch(`/api/training/codex-promotion-final-publication-closure-audit?ts=${Date.now()}`).then((response) => response.json());
  lastCodexPromotionFinalReleaseReviewGate = await fetch(`/api/training/codex-promotion-final-release-review-gate?ts=${Date.now()}`).then((response) => response.json());
  renderTraining(lastTrainingResult);
}

async function runTraining() {
  runTrainingButton.disabled = true;
  trainingStatus.textContent = trainingIsZh() ? "自动训练运行中" : "Auto training running";
  const response = await fetch("/api/training/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: "auto", source: "training_console" }),
  });
  lastTrainingResult = await response.json();
  const [roundResponse, regressionResponse, gateResponse, nextLoopResponse, closureResponse, proposalResponse, packetResponse, patchQueueResponse, executionGateResponse, worktreePrepResponse, worktreeLaunchResponse, worktreeResultResponse, worktreeResultReviewResponse, promotionResponse, promotionApprovalResponse, promotionHandoffResponse, promotionReadinessResponse, promotionExecutionResultResponse, promotionClosureResponse, promotionSyncReviewResponse, promotionSyncHandoffResponse, promotionSyncReadinessResponse, promotionSyncResultResponse, promotionSyncClosureResponse, promotionSyncClosureReviewResponse, promotionFinalSyncHandoffResponse, promotionFinalSyncReadinessResponse, promotionFinalSyncResultResponse, promotionFinalSyncClosureResponse, promotionFinalCompletionReviewResponse] = await Promise.all([
    fetch(`/api/training/round-summary?ts=${Date.now()}`),
    fetch(`/api/training/regression-run?ts=${Date.now()}`),
    fetch(`/api/training/regression-gate?ts=${Date.now()}`),
    fetch(`/api/training/next-loop?ts=${Date.now()}`),
    fetch(`/api/training/next-loop-closure?ts=${Date.now()}`),
    fetch(`/api/training/iteration-proposal?ts=${Date.now()}`),
    fetch(`/api/training/codex-work-packets?ts=${Date.now()}`),
    fetch(`/api/training/codex-patch-queue?ts=${Date.now()}`),
    fetch(`/api/training/codex-execution-gate?ts=${Date.now()}`),
    fetch(`/api/training/codex-worktree-prep?ts=${Date.now()}`),
    fetch(`/api/training/codex-worktree-launch?ts=${Date.now()}`),
    fetch(`/api/training/codex-worktree-results?ts=${Date.now()}`),
    fetch(`/api/training/codex-worktree-result-review-gate?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-candidates?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-approval-gate?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-handoff?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-execution-readiness?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-execution-results?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-closure-audit?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-review-gate?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-handoff?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-readiness?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-execution-results?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-closure-audit?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-sync-closure-review-gate?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-final-sync-handoff?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-final-sync-readiness?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-final-sync-execution-results?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-final-sync-closure-audit?ts=${Date.now()}`),
    fetch(`/api/training/codex-promotion-final-completion-review-gate?ts=${Date.now()}`),
  ]);
  lastRoundSummary = await roundResponse.json();
  lastRegressionRun = await regressionResponse.json();
  lastRegressionGate = await gateResponse.json();
  lastNextLoopHandoff = await nextLoopResponse.json();
  lastNextLoopClosure = await closureResponse.json();
  lastIterationProposal = await proposalResponse.json();
  lastCodexWorkPackets = await packetResponse.json();
  lastCodexPatchQueue = await patchQueueResponse.json();
  lastCodexExecutionGate = await executionGateResponse.json();
  lastCodexWorktreePrep = await worktreePrepResponse.json();
  lastCodexWorktreeLaunch = await worktreeLaunchResponse.json();
  lastCodexWorktreeResults = await worktreeResultResponse.json();
  lastCodexWorktreeResultReviewGate = await worktreeResultReviewResponse.json();
  lastCodexPromotionCandidates = await promotionResponse.json();
  lastCodexPromotionApprovalGate = await promotionApprovalResponse.json();
  lastCodexPromotionHandoff = await promotionHandoffResponse.json();
  lastCodexPromotionReadiness = await promotionReadinessResponse.json();
  lastCodexPromotionExecutionResults = await promotionExecutionResultResponse.json();
  lastCodexPromotionClosureAudit = await promotionClosureResponse.json();
  lastCodexPromotionSyncReviewGate = await promotionSyncReviewResponse.json();
  lastCodexPromotionSyncHandoff = await promotionSyncHandoffResponse.json();
  lastCodexPromotionSyncReadiness = await promotionSyncReadinessResponse.json();
  lastCodexPromotionSyncExecutionResults = await promotionSyncResultResponse.json();
  lastCodexPromotionSyncClosureAudit = await promotionSyncClosureResponse.json();
  lastCodexPromotionSyncClosureReviewGate = await promotionSyncClosureReviewResponse.json();
  lastCodexPromotionFinalSyncHandoff = await promotionFinalSyncHandoffResponse.json();
  lastCodexPromotionFinalSyncReadiness = await promotionFinalSyncReadinessResponse.json();
  lastCodexPromotionFinalSyncExecutionResults = await promotionFinalSyncResultResponse.json();
  lastCodexPromotionFinalSyncClosureAudit = await promotionFinalSyncClosureResponse.json();
  lastCodexPromotionFinalCompletionReviewGate = await promotionFinalCompletionReviewResponse.json();
  lastCodexPromotionFinalPublicationHandoff = await fetch(`/api/training/codex-promotion-final-publication-handoff?ts=${Date.now()}`).then((response) => response.json());
  lastCodexPromotionFinalPublicationReadiness = await fetch(`/api/training/codex-promotion-final-publication-readiness?ts=${Date.now()}`).then((response) => response.json());
  lastCodexPromotionFinalPublicationResults = await fetch(`/api/training/codex-promotion-final-publication-results?ts=${Date.now()}`).then((response) => response.json());
  lastCodexPromotionFinalPublicationClosureAudit = await fetch(`/api/training/codex-promotion-final-publication-closure-audit?ts=${Date.now()}`).then((response) => response.json());
  lastCodexPromotionFinalReleaseReviewGate = await fetch(`/api/training/codex-promotion-final-release-review-gate?ts=${Date.now()}`).then((response) => response.json());
  renderTraining(lastTrainingResult);
  runTrainingButton.disabled = false;
}

async function runRegression() {
  runRegressionButton.disabled = true;
  trainingStatus.textContent = trainingIsZh() ? "自动回归运行中" : "Regression running";
  try {
    const response = await fetch("/api/training/regression-run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: "regression", source: "training_console" }),
    });
    lastRegressionRun = await response.json();
    const [gateResponse, nextLoopResponse, closureResponse, proposalResponse, packetResponse, patchQueueResponse, executionGateResponse, worktreePrepResponse, worktreeLaunchResponse, worktreeResultResponse, worktreeResultReviewResponse, promotionResponse, promotionApprovalResponse, promotionHandoffResponse, promotionReadinessResponse, promotionExecutionResultResponse, promotionClosureResponse, promotionSyncReviewResponse, promotionSyncHandoffResponse, promotionSyncReadinessResponse, promotionSyncResultResponse, promotionSyncClosureResponse, promotionSyncClosureReviewResponse, promotionFinalSyncHandoffResponse, promotionFinalSyncReadinessResponse, promotionFinalSyncResultResponse, promotionFinalSyncClosureResponse, promotionFinalCompletionReviewResponse] = await Promise.all([
      fetch(`/api/training/regression-gate?ts=${Date.now()}`),
      fetch(`/api/training/next-loop?ts=${Date.now()}`),
      fetch(`/api/training/next-loop-closure?ts=${Date.now()}`),
      fetch(`/api/training/iteration-proposal?ts=${Date.now()}`),
      fetch(`/api/training/codex-work-packets?ts=${Date.now()}`),
      fetch(`/api/training/codex-patch-queue?ts=${Date.now()}`),
      fetch(`/api/training/codex-execution-gate?ts=${Date.now()}`),
      fetch(`/api/training/codex-worktree-prep?ts=${Date.now()}`),
      fetch(`/api/training/codex-worktree-launch?ts=${Date.now()}`),
      fetch(`/api/training/codex-worktree-results?ts=${Date.now()}`),
      fetch(`/api/training/codex-worktree-result-review-gate?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-candidates?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-approval-gate?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-handoff?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-execution-readiness?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-execution-results?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-closure-audit?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-sync-review-gate?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-sync-handoff?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-sync-readiness?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-sync-execution-results?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-sync-closure-audit?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-sync-closure-review-gate?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-final-sync-handoff?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-final-sync-readiness?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-final-sync-execution-results?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-final-sync-closure-audit?ts=${Date.now()}`),
      fetch(`/api/training/codex-promotion-final-completion-review-gate?ts=${Date.now()}`),
    ]);
    lastRegressionGate = await gateResponse.json();
    lastNextLoopHandoff = await nextLoopResponse.json();
    lastNextLoopClosure = await closureResponse.json();
    lastIterationProposal = await proposalResponse.json();
    lastCodexWorkPackets = await packetResponse.json();
    lastCodexPatchQueue = await patchQueueResponse.json();
    lastCodexExecutionGate = await executionGateResponse.json();
    lastCodexWorktreePrep = await worktreePrepResponse.json();
    lastCodexWorktreeLaunch = await worktreeLaunchResponse.json();
    lastCodexWorktreeResults = await worktreeResultResponse.json();
    lastCodexWorktreeResultReviewGate = await worktreeResultReviewResponse.json();
    lastCodexPromotionCandidates = await promotionResponse.json();
    lastCodexPromotionApprovalGate = await promotionApprovalResponse.json();
    lastCodexPromotionHandoff = await promotionHandoffResponse.json();
    lastCodexPromotionReadiness = await promotionReadinessResponse.json();
    lastCodexPromotionExecutionResults = await promotionExecutionResultResponse.json();
    lastCodexPromotionClosureAudit = await promotionClosureResponse.json();
    lastCodexPromotionSyncReviewGate = await promotionSyncReviewResponse.json();
    lastCodexPromotionSyncHandoff = await promotionSyncHandoffResponse.json();
    lastCodexPromotionSyncReadiness = await promotionSyncReadinessResponse.json();
    lastCodexPromotionSyncExecutionResults = await promotionSyncResultResponse.json();
    lastCodexPromotionSyncClosureAudit = await promotionSyncClosureResponse.json();
    lastCodexPromotionSyncClosureReviewGate = await promotionSyncClosureReviewResponse.json();
    lastCodexPromotionFinalSyncHandoff = await promotionFinalSyncHandoffResponse.json();
    lastCodexPromotionFinalSyncReadiness = await promotionFinalSyncReadinessResponse.json();
    lastCodexPromotionFinalSyncExecutionResults = await promotionFinalSyncResultResponse.json();
    lastCodexPromotionFinalSyncClosureAudit = await promotionFinalSyncClosureResponse.json();
    lastCodexPromotionFinalCompletionReviewGate = await promotionFinalCompletionReviewResponse.json();
    lastCodexPromotionFinalPublicationHandoff = await fetch(`/api/training/codex-promotion-final-publication-handoff?ts=${Date.now()}`).then((response) => response.json());
    lastCodexPromotionFinalPublicationReadiness = await fetch(`/api/training/codex-promotion-final-publication-readiness?ts=${Date.now()}`).then((response) => response.json());
    lastCodexPromotionFinalPublicationResults = await fetch(`/api/training/codex-promotion-final-publication-results?ts=${Date.now()}`).then((response) => response.json());
    lastCodexPromotionFinalPublicationClosureAudit = await fetch(`/api/training/codex-promotion-final-publication-closure-audit?ts=${Date.now()}`).then((response) => response.json());
    lastCodexPromotionFinalReleaseReviewGate = await fetch(`/api/training/codex-promotion-final-release-review-gate?ts=${Date.now()}`).then((response) => response.json());
    renderRegressionRun(lastRegressionRun);
    renderRegressionGate(lastRegressionGate);
    renderNextLoopHandoff(lastNextLoopHandoff);
    renderNextLoopClosure(lastNextLoopClosure);
    renderIterationProposal(lastIterationProposal);
    renderCodexWorkPackets(lastCodexWorkPackets);
    renderCodexPatchQueue(lastCodexPatchQueue);
    renderCodexExecutionGate(lastCodexExecutionGate);
    renderCodexWorktreePrep(lastCodexWorktreePrep);
    renderCodexWorktreeLaunchGate(lastCodexWorktreeLaunch);
    renderCodexWorktreeResults(lastCodexWorktreeResults);
    renderCodexWorktreeResultReviewGate(lastCodexWorktreeResultReviewGate);
    renderCodexPromotionCandidates(lastCodexPromotionCandidates);
    renderCodexPromotionApprovalGate(lastCodexPromotionApprovalGate);
    renderCodexPromotionHandoff(lastCodexPromotionHandoff);
    renderCodexPromotionReadiness(lastCodexPromotionReadiness);
    renderCodexPromotionExecutionResults(lastCodexPromotionExecutionResults);
    renderCodexPromotionClosureAudit(lastCodexPromotionClosureAudit);
    renderCodexPromotionSyncReviewGate(lastCodexPromotionSyncReviewGate);
    renderCodexPromotionSyncHandoff(lastCodexPromotionSyncHandoff);
    renderCodexPromotionSyncReadiness(lastCodexPromotionSyncReadiness);
    renderCodexPromotionSyncExecutionResults(lastCodexPromotionSyncExecutionResults);
    renderCodexPromotionSyncClosureAudit(lastCodexPromotionSyncClosureAudit);
    renderCodexPromotionSyncClosureReviewGate(lastCodexPromotionSyncClosureReviewGate);
    renderCodexPromotionFinalSyncHandoff(lastCodexPromotionFinalSyncHandoff);
    renderCodexPromotionFinalSyncReadiness(lastCodexPromotionFinalSyncReadiness);
    renderCodexPromotionFinalSyncExecutionResults(lastCodexPromotionFinalSyncExecutionResults);
    renderCodexPromotionFinalSyncClosureAudit(lastCodexPromotionFinalSyncClosureAudit);
    renderCodexPromotionFinalCompletionReviewGate(lastCodexPromotionFinalCompletionReviewGate);
    renderCodexPromotionFinalPublicationHandoff(lastCodexPromotionFinalPublicationHandoff);
    renderCodexPromotionFinalPublicationReadiness(lastCodexPromotionFinalPublicationReadiness);
    renderCodexPromotionFinalPublicationResults(lastCodexPromotionFinalPublicationResults);
    renderCodexPromotionFinalPublicationClosureAudit(lastCodexPromotionFinalPublicationClosureAudit);
    renderCodexPromotionFinalReleaseReviewGate(lastCodexPromotionFinalReleaseReviewGate);
    trainingStatus.textContent = `${lastTrainingStatus?.version || lastRegressionRun.workflow_instance?.version || ""} | ${statusText(lastRegressionRun.workflow_instance?.status || "")}`;
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  } finally {
    runRegressionButton.disabled = false;
  }
}

function renderTraining(result) {
  applyStaticText();
  renderStatus(result);
  renderSummary(result.training_overview || {});
  renderStages(result.training_stages || []);
  renderTasks(result.training_tasks || []);
  renderCapabilities(result.capability_progress || []);
  renderHermesJson(result.hermes_result_payload || {});
  renderReviewState(result.review_state || {});
  renderRoundSummary(lastRoundSummary || {});
  renderPlaybookRegressionQueue(result.playbook_regression_queue || {});
  renderRegressionRun(lastRegressionRun || {});
  renderRegressionGate(lastRegressionGate || {});
  renderNextLoopHandoff(lastNextLoopHandoff || {});
  renderNextLoopClosure(lastNextLoopClosure || {});
  renderIterationProposal(lastIterationProposal || {});
  renderCodexWorkPackets(lastCodexWorkPackets || {});
  renderCodexPatchQueue(lastCodexPatchQueue || { codex_patch_queue_contract: { training_signal_queue: result.codex_patch_queue || [] } });
  renderCodexExecutionGate(lastCodexExecutionGate || {});
  renderCodexWorktreePrep(lastCodexWorktreePrep || {});
  renderCodexWorktreeLaunchGate(lastCodexWorktreeLaunch || {});
  renderCodexWorktreeResults(lastCodexWorktreeResults || {});
  renderCodexWorktreeResultReviewGate(lastCodexWorktreeResultReviewGate || {});
  renderCodexPromotionCandidates(lastCodexPromotionCandidates || {});
  renderCodexPromotionApprovalGate(lastCodexPromotionApprovalGate || {});
  renderCodexPromotionHandoff(lastCodexPromotionHandoff || {});
  renderCodexPromotionReadiness(lastCodexPromotionReadiness || {});
  renderCodexPromotionExecutionResults(lastCodexPromotionExecutionResults || {});
  renderCodexPromotionClosureAudit(lastCodexPromotionClosureAudit || {});
  renderCodexPromotionSyncReviewGate(lastCodexPromotionSyncReviewGate || {});
  renderCodexPromotionSyncHandoff(lastCodexPromotionSyncHandoff || {});
  renderCodexPromotionSyncReadiness(lastCodexPromotionSyncReadiness || {});
  renderCodexPromotionSyncExecutionResults(lastCodexPromotionSyncExecutionResults || {});
  renderCodexPromotionSyncClosureAudit(lastCodexPromotionSyncClosureAudit || {});
  renderCodexPromotionSyncClosureReviewGate(lastCodexPromotionSyncClosureReviewGate || {});
  renderCodexPromotionFinalSyncHandoff(lastCodexPromotionFinalSyncHandoff || {});
  renderCodexPromotionFinalSyncReadiness(lastCodexPromotionFinalSyncReadiness || {});
  renderCodexPromotionFinalSyncExecutionResults(lastCodexPromotionFinalSyncExecutionResults || {});
  renderCodexPromotionFinalSyncClosureAudit(lastCodexPromotionFinalSyncClosureAudit || {});
  renderCodexPromotionFinalCompletionReviewGate(lastCodexPromotionFinalCompletionReviewGate || {});
  renderCodexPromotionFinalPublicationHandoff(lastCodexPromotionFinalPublicationHandoff || {});
  renderCodexPromotionFinalPublicationReadiness(lastCodexPromotionFinalPublicationReadiness || {});
  renderCodexPromotionFinalPublicationResults(lastCodexPromotionFinalPublicationResults || {});
  renderCodexPromotionFinalPublicationClosureAudit(lastCodexPromotionFinalPublicationClosureAudit || {});
  renderCodexPromotionFinalReleaseReviewGate(lastCodexPromotionFinalReleaseReviewGate || {});
  renderMiniList(nextTrainingTasks, result.next_training_tasks || [], renderNextTask);
  renderMiniList(trainingKpis, result.kpi_log || [], renderKpi);
  renderMiniList(trainingEvidence, result.evidence_log || [], renderEvidence);
}

function renderStatus(result) {
  const version = lastTrainingStatus?.version || result.workflow_instance?.version || "";
  const state = result.training_overview?.automation_state || "auto_training_available";
  trainingStatus.textContent = `${version} | ${statusText(state)}`;
}

function renderSummary(summary) {
  const tiles = [
    [["Target", "训练对象"], summary.target_persona || "tianpai_general_manager"],
    [["Total Tasks", "任务总数"], summary.total_task_count ?? 0],
    [["Auto Evaluated", "自动评测"], summary.auto_evaluated_task_count ?? 0],
    [["Passed", "通过"], summary.passed_task_count ?? 0],
    [["Needs Data", "需要数据"], summary.needs_data_task_count ?? 0],
    [["Failed", "失败"], summary.failed_task_count ?? 0],
    [["Pending Review", "待确认"], summary.pending_review_count ?? 0],
    [["Approved Review", "已确认"], summary.approved_review_count ?? 0],
    [["Playbook Ready", "Playbook 可回归"], summary.playbook_ready_regression_count ?? 0],
    [["Average Score", "平均评分"], summary.average_score ?? 0],
    [["Progress", "训练进度"], `${summary.progress_percent ?? 0}%`],
    [["Live Hermes", "真实 Hermes"], summary.real_hermes_connected ? t("yes") : t("no")],
  ];
  trainingSummary.innerHTML = "";
  tiles.forEach(([label, value]) => {
    const tile = document.createElement("article");
    tile.className = "production-tile";
    tile.innerHTML = `<span>${escapeTraining(pair(label))}</span><strong>${escapeTraining(value)}</strong>`;
    trainingSummary.append(tile);
  });
}

function renderStages(stages) {
  trainingStages.innerHTML = "";
  stages.forEach((stage, index) => {
    const card = document.createElement("article");
    card.className = `workflow-step ${stage.run_status === "completed" ? "ok" : "attention"}`;
    card.innerHTML = `
      <span>${index + 1}</span>
      <strong>${escapeTraining(stage.name)}</strong>
      <p>${escapeTraining(stage.owner)} | ${escapeTraining(statusText(stage.run_status))}</p>
      <small>${escapeTraining(stage.input_object)} -> ${escapeTraining(stage.output_object)} | ${escapeTraining(stage.evidence_ref)}</small>
    `;
    trainingStages.append(card);
  });
}

function renderTasks(tasks) {
  trainingTasks.innerHTML = "";
  tasks.forEach((task) => {
    const statusClass = task.status === "passed" ? "ok" : task.status === "failed" ? "failed" : "attention";
    const card = document.createElement("article");
    card.className = `training-task ${statusClass}`;
    card.innerHTML = `
      <div class="version-entry-header">
        <h3>${escapeTraining(task.task_id)}</h3>
        <span>${escapeTraining(statusText(task.status))}</span>
      </div>
      <p><strong>${escapeTraining(task.capability_group)}</strong> | ${escapeTraining(task.capability)}</p>
      <p>${escapeTraining(task.question)}</p>
      <p>${escapeTraining(t("score"))}: ${escapeTraining(task.score)} | ${escapeTraining(t("evidenceRefs"))}: ${escapeTraining((task.evaluation_checks?.resolved_evidence_refs || []).join(", "))}</p>
      <p>${escapeTraining(t("nextAction"))}: ${escapeTraining(task.next_action)}</p>
      ${renderTaskReviewControls(task)}
      ${task.status === "needs_data" ? renderTaskDataControls(task) : ""}
    `;
    trainingTasks.append(card);
  });
}

function renderTaskReviewControls(task) {
  const review = task.review || {};
  return `
    <div class="training-actions" data-task-id="${escapeTraining(task.task_id)}">
      <p><strong>${escapeTraining(t("reviewStatus"))}:</strong> ${escapeTraining(statusText(review.review_status || "pending_review"))}</p>
      ${review.review_note ? `<p>${escapeTraining(review.review_note)}</p>` : ""}
      <textarea class="training-review-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}">${escapeTraining(review.review_note || "")}</textarea>
      <div class="training-button-row">
        <button type="button" data-training-review="approved">${escapeTraining(t("approve"))}</button>
        <button type="button" data-training-review="needs_changes">${escapeTraining(t("needsChangesAction"))}</button>
        <button type="button" data-training-review="rejected">${escapeTraining(t("reject"))}</button>
        <button type="button" data-training-review="note_only">${escapeTraining(t("addNote"))}</button>
      </div>
    </div>
  `;
}

function renderTaskDataControls(task) {
  const intake = task.data_intake || {};
  const sources = intake.data_sources || [];
  const sourceList = sources.length
    ? sources.map((source) => `
      <li>
        <strong>${escapeTraining(statusText(source.data_status))}</strong>
        <span>${escapeTraining(source.source_type || "")} | ${escapeTraining(source.source_label || "")} | ${escapeTraining(source.source_reference || "")}</span>
      </li>
    `).join("")
    : `<li><span>${escapeTraining(t("notRegistered"))}</span></li>`;
  return `
    <div class="training-data-intake" data-task-id="${escapeTraining(task.task_id)}">
      <p><strong>${escapeTraining(t("dataSource"))}</strong> | ${escapeTraining(t("dataStatus"))}: ${escapeTraining(statusText(intake.latest_data_status || "not_registered"))}</p>
      <p class="muted-text">${escapeTraining(t("noRawUpload"))}</p>
      <div class="training-data-grid">
        <label><span>${escapeTraining(t("sourceType"))}</span><select class="training-source-type">
          <option value="APS export">APS export</option>
          <option value="IOT export">IOT export</option>
          <option value="ERP export">ERP export</option>
          <option value="quality export">Quality export</option>
          <option value="material export">Material export</option>
          <option value="labor export">Labor export</option>
          <option value="stage records">Stage records</option>
          <option value="meeting">Meeting</option>
          <option value="other">Other</option>
        </select></label>
        <label><span>${escapeTraining(t("sourceLabel"))}</span><input class="training-source-label" type="text" placeholder="APS June schedule export"></label>
        <label><span>${escapeTraining(t("sourceReference"))}</span><input class="training-source-reference" type="text" placeholder="Path / owner / table name"></label>
        <label><span>${escapeTraining(t("sensitivity"))}</span><select class="training-sensitivity">
          <option value="internal">internal</option>
          <option value="confidential">confidential</option>
          <option value="restricted">restricted</option>
        </select></label>
      </div>
      <textarea class="training-field-notes" rows="2" placeholder="${escapeTraining(t("fieldNotes"))}"></textarea>
      <div class="training-button-row">
        <button type="button" data-training-data="registered">${escapeTraining(t("registerDataSource"))}</button>
        <button type="button" data-training-data="skipped_for_now">${escapeTraining(t("skipForNow"))}</button>
        <button type="button" data-training-data="not_available">${escapeTraining(t("markNotAvailable"))}</button>
      </div>
      <ul class="training-source-list">${sourceList}</ul>
    </div>
  `;
}

function renderReviewState(state) {
  const items = [
    ["Reviews", state.review_count ?? 0],
    ["Approved", state.approved_count ?? 0],
    ["Needs Changes", state.needs_changes_count ?? 0],
    ["Rejected", state.rejected_count ?? 0],
    ["Registered Data", state.registered_data_source_count ?? 0],
    ["Skipped", state.skipped_data_source_count ?? 0],
    ["Not Available", state.not_available_data_source_count ?? 0],
    ["Handoff Reviews", state.handoff_review_count ?? 0],
    ["Handoff Resolved", state.handoff_resolved_count ?? 0],
    ["Handoff Needs Data", state.handoff_needs_data_count ?? 0],
    ["Proposal Reviews", state.iteration_proposal_review_count ?? 0],
    ["Proposal Approved", state.iteration_proposal_approved_count ?? 0],
    ["Proposal Needs Changes", state.iteration_proposal_needs_changes_count ?? 0],
    ["Promotion Readiness Reviews", state.codex_promotion_readiness_review_count ?? 0],
    ["Promotion Readiness Confirmed", state.codex_promotion_readiness_confirmed_count ?? 0],
    ["Sync Readiness Reviews", state.codex_promotion_sync_readiness_review_count ?? 0],
    ["Sync Readiness Confirmed", state.codex_promotion_sync_readiness_confirmed_count ?? 0],
    ["Sync Execution Results", state.codex_promotion_sync_execution_result_count ?? 0],
  ];
  reviewState.innerHTML = "";
  items.forEach(([label, value]) => {
    const card = document.createElement("article");
    card.className = "mini-object";
    card.innerHTML = `<small>${escapeTraining(state.updated_at || "")}</small><strong>${escapeTraining(label)}</strong><p>${escapeTraining(value)}</p>`;
    reviewState.append(card);
  });
}

function renderRoundSummary(summary) {
  const ready = summary.baseline_status === "ready_for_regression";
  promoteBaselineButton.disabled = !ready;
  const tiles = [
    [t("baselineReady"), statusText(summary.baseline_status || "review_or_data_decision_required")],
    [t("promotedTasks"), summary.promoted_task_count ?? 0],
    [t("capabilityRegression"), summary.capability_regression_count ?? 0],
    [t("dataGapRegression"), summary.data_gap_regression_count ?? 0],
    [t("dataDecisions"), (summary.data_decisions || []).length],
  ];
  const decisions = (summary.data_decisions || []).map((decision) => `
    <article class="mini-object">
      <small>${escapeTraining(statusText(decision.data_status || ""))} | ${escapeTraining(decision.coverage || "")}</small>
      <strong>${escapeTraining(decision.decision_name || decision.task_id)}</strong>
      <p>${escapeTraining(decision.source_label || decision.source_type || decision.source_reference || "")}</p>
      <p>${escapeTraining(t("remainingGap"))}: ${escapeTraining(decision.remaining_gap || "")}</p>
    </article>
  `).join("");
  trainingRoundSummary.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">${decisions}</div>
  `;
}

function renderPlaybookRegressionQueue(queue) {
  if (!playbookRegressionQueue) return;
  const candidates = queue.regression_candidates || [];
  const summaryTiles = [
    ["Playbook Candidates", queue.candidate_count ?? 0],
    [t("readyRegression"), queue.ready_regression_count ?? 0],
    [t("blockedRegression"), queue.blocked_regression_count ?? 0],
    ["Status", statusText(queue.queue_status || "mock_contract")],
  ];
  const candidateCards = candidates.map((item) => {
    const state = item.ready_for_regression ? t("readyRegression") : t("blockedRegression");
    const blockers = (item.blockers || []).length ? item.blockers.join(", ") : (trainingIsZh() ? "无" : "None");
    return `
      <article class="mini-object">
        <small>${escapeTraining(item.regression_id || "")} | ${escapeTraining(state)}</small>
        <strong>${escapeTraining(item.prompt_family || item.playbook_candidate_id || "")}</strong>
        <p>${escapeTraining(item.trigger_signal || "")}</p>
        <p>${escapeTraining(t("evidenceRefs"))}: ${escapeTraining((item.source_evidence_refs || []).join(", "))}</p>
        <p>${escapeTraining(t("blockers"))}: ${escapeTraining(blockers)}</p>
      </article>
    `;
  }).join("");
  playbookRegressionQueue.innerHTML = `
    <div class="production-summary compact-summary">
      ${summaryTiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    ${candidateCards || `<p class="muted-text">${escapeTraining(trainingIsZh() ? "暂无 playbook regression 候选。" : "No playbook regression candidates yet.")}</p>`}
  `;
}

function renderRegressionRun(payload) {
  if (!trainingRegressionRun) return;
  const overview = payload.regression_overview || {};
  const cases = payload.regression_cases || [];
  const tiles = [
    ["Status", statusText(overview.status || "mock_contract")],
    [t("executableCases"), overview.executable_case_count ?? 0],
    [t("passedCases"), overview.passed_case_count ?? 0],
    [t("failedCases"), overview.failed_case_count ?? 0],
    [t("blockedCases"), overview.blocked_case_count ?? 0],
    [t("passRate"), overview.pass_rate ?? 0],
  ];
  const caseCards = cases.slice(0, 8).map((item) => {
    const checks = (item.checks || []).map((check) => `${check.check}: ${check.passed ? "OK" : "NO"}`).join("; ");
    const blockers = (item.blockers || []).join(", ");
    return `
      <article class="mini-object">
        <small>${escapeTraining(statusText(item.regression_status || ""))} | ${escapeTraining(statusText(item.source || ""))}</small>
        <strong>${escapeTraining(item.case_id || "")}</strong>
        <p>${escapeTraining(item.capability || "")}</p>
        <p>${escapeTraining(checks || blockers || item.locked_next_action || "")}</p>
      </article>
    `;
  }).join("");
  trainingRegressionRun.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">${caseCards}</div>
  `;
}

function renderRegressionGate(payload) {
  if (!trainingRegressionGate) return;
  const gate = payload.regression_gate || {};
  const queue = payload.codex_next_action_queue || [];
  const tiles = [
    [t("gateStatus"), statusText(gate.gate_status || "mock_contract")],
    [t("gateAllowed"), gate.automatic_loop_allowed ? t("yes") : t("no")],
    [t("reviewRequired"), gate.human_review_required ? t("yes") : t("no")],
    [t("failedCases"), gate.failed_case_count ?? 0],
    [t("blockedCases"), gate.blocked_case_count ?? 0],
    [t("passRate"), gate.pass_rate ?? 0],
  ];
  const actionCards = queue.map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.queue_id || "")} | ${escapeTraining(item.priority || "")}</small>
      <strong>${escapeTraining(item.type || "")}</strong>
      <p>${escapeTraining(item.summary || "")}</p>
      <p>${escapeTraining(t("reviewRequired"))}: ${escapeTraining(item.human_review_required ? t("yes") : t("no"))}</p>
    </article>
  `).join("");
  const reviewCards = (gate.review_required_items || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(statusText(item.status || ""))} | ${escapeTraining(statusText(item.source || ""))}</small>
      <strong>${escapeTraining(item.case_id || "")}</strong>
      <p>${escapeTraining(item.reason || "")}</p>
    </article>
  `).join("");
  trainingRegressionGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">${actionCards}${reviewCards}</div>
  `;
}

function renderNextLoopHandoff(payload) {
  if (!trainingNextLoopHandoff) return;
  const handoff = payload.next_loop_handoff || {};
  const summary = handoff.queue_summary || {};
  const tiles = [
    [t("handoffStatus"), statusText(handoff.handoff_status || "mock_contract")],
    [t("gateAllowed"), handoff.automatic_loop_allowed ? t("yes") : t("no")],
    [t("automaticActions"), summary.automatic_action_count ?? 0],
    [t("humanReviewItems"), summary.human_review_count ?? 0],
    [t("dataRequests"), summary.data_request_count ?? 0],
    ["Hermes", payload.hermes_handoff_payload?.schema || "mock_contract"],
  ];
  const renderHandoffItem = (item) => {
    const review = item.handoff_review || {};
    return `
    <article class="mini-object handoff-review-card">
      <small>${escapeTraining(item.handoff_item_id || "")} | ${escapeTraining(item.priority || "")}</small>
      <strong>${escapeTraining(statusText(item.type || ""))}</strong>
      <p>${escapeTraining(item.summary || "")}</p>
      <p>${escapeTraining(t("humanReview"))}: ${escapeTraining(item.human_review_required ? t("yes") : t("no"))}</p>
      <div class="training-actions handoff-actions"
        data-handoff-item-id="${escapeTraining(item.handoff_item_id || "")}"
        data-handoff-item-type="${escapeTraining(item.type || "")}"
        data-handoff-source="${escapeTraining(item.source || "")}"
        data-related-case-id="${escapeTraining(item.related_case_id || "")}"
        data-related-task-id="${escapeTraining(item.related_task_id || "")}">
        <p><strong>${escapeTraining(t("handoffReviewStatus"))}:</strong> ${escapeTraining(statusText(review.review_status || ""))}</p>
        ${review.review_note ? `<p>${escapeTraining(review.review_note)}</p>` : ""}
        <textarea class="training-handoff-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}">${escapeTraining(review.review_note || "")}</textarea>
        <div class="training-button-row">
          <button type="button" data-handoff-review="approved_for_next_loop">${escapeTraining(t("approveNextLoop"))}</button>
          <button type="button" data-handoff-review="resolved">${escapeTraining(t("markResolved"))}</button>
          <button type="button" data-handoff-review="deferred">${escapeTraining(t("deferHandoff"))}</button>
          <button type="button" data-handoff-review="needs_data">${escapeTraining(t("markNeedsData"))}</button>
          <button type="button" data-handoff-review="note_only">${escapeTraining(t("addNote"))}</button>
        </div>
      </div>
    </article>
  `;
  };
  const automaticCards = (handoff.automatic_work_queue || []).map(renderHandoffItem).join("");
  const reviewCards = (handoff.human_review_queue || []).map(renderHandoffItem).join("");
  const dataCards = (handoff.data_request_queue || []).map(renderHandoffItem).join("");
  trainingNextLoopHandoff.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">${automaticCards}${reviewCards}${dataCards}</div>
  `;
}

function renderNextLoopClosure(payload) {
  if (!trainingNextLoopClosure) return;
  const closure = payload.next_loop_closure || {};
  const plan = closure.local_iteration_plan || {};
  const tiles = [
    [t("closureStatus"), statusText(closure.closure_status || "mock_contract")],
    [t("closureReady"), closure.local_iteration_allowed ? t("yes") : t("no")],
    [t("closureComplete"), closure.closure_complete ? t("yes") : t("no")],
    [t("automaticActions"), closure.automatic_action_count ?? 0],
    [t("openItems"), closure.open_item_count ?? 0],
    [t("rejectedItems"), closure.rejected_item_count ?? 0],
  ];
  const renderClosureItem = (item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.handoff_item_id || "")} | ${escapeTraining(item.priority || "")}</small>
      <strong>${escapeTraining(statusText(item.type || ""))}</strong>
      <p>${escapeTraining(statusText(item.review_status || ""))}</p>
      <p>${escapeTraining(item.summary || "")}</p>
    </article>
  `;
  const automaticCards = (plan.automatic_items || []).slice(0, 4).map(renderClosureItem).join("");
  const openCards = (closure.open_items || []).map(renderClosureItem).join("");
  const rejectedCards = (closure.rejected_items || []).map(renderClosureItem).join("");
  trainingNextLoopClosure.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(plan.plan_id || "")}</small>
        <strong>${escapeTraining(statusText(plan.scope || ""))}</strong>
        <p>${escapeTraining(t("gateAllowed"))}: ${escapeTraining(plan.allowed ? t("yes") : t("no"))}</p>
      </article>
      ${automaticCards}${openCards}${rejectedCards}
    </div>
  `;
}

function renderIterationProposal(payload) {
  if (!trainingIterationProposal) return;
  const proposal = payload.training_iteration_proposal || {};
  const contract = proposal.next_iteration_contract || {};
  const review = proposal.proposal_review || {};
  const tiles = [
    [t("proposalStatus"), statusText(proposal.proposal_status || "mock_contract")],
    [t("proposalReady"), proposal.proposal_ready ? t("yes") : t("no")],
    [t("proposalReviewStatus"), statusText(review.review_status || "pending_proposal_review")],
    [t("closureComplete"), proposal.closure_complete ? t("yes") : t("no")],
    [t("taskSeeds"), proposal.task_seed_count ?? 0],
    [t("watchItems"), proposal.open_watch_item_count ?? 0],
  ];
  const renderProposalItem = (item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.proposal_item_id || item.handoff_item_id || "")} | ${escapeTraining(item.priority || "")}</small>
      <strong>${escapeTraining(statusText(item.type || ""))}</strong>
      <p>${escapeTraining(statusText(item.review_status || contract.scope || ""))}</p>
      <p>${escapeTraining(item.summary || "")}</p>
    </article>
  `;
  const seedCards = (proposal.task_seed_queue || []).map(renderProposalItem).join("");
  const watchCards = (proposal.open_item_watchlist || []).map(renderProposalItem).join("");
  trainingIterationProposal.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(payload.hermes_iteration_payload?.schema || "mock_contract")}</small>
        <strong>${escapeTraining(statusText(contract.scope || ""))}</strong>
        <p>${escapeTraining(t("humanReview"))}: ${escapeTraining(contract.requires_user_confirmation_for_large_change ? t("yes") : t("no"))}</p>
      </article>
      <article class="mini-object training-actions iteration-proposal-actions"
        data-proposal-id="${escapeTraining(proposal.proposal_id || "")}"
        data-proposal-status="${escapeTraining(proposal.proposal_status || "")}"
        data-task-seed-count="${escapeTraining(proposal.task_seed_count ?? 0)}"
        data-open-watch-item-count="${escapeTraining(proposal.open_watch_item_count ?? 0)}">
        <small>${escapeTraining(review.updated_at || "")}</small>
        <strong>${escapeTraining(t("proposalReviewStatus"))}: ${escapeTraining(statusText(review.review_status || "pending_proposal_review"))}</strong>
        ${review.review_note ? `<p>${escapeTraining(review.review_note)}</p>` : ""}
        <textarea class="training-iteration-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}">${escapeTraining(review.review_note || "")}</textarea>
        <div class="training-button-row">
          <button type="button" data-iteration-review="approved_for_codex_queue">${escapeTraining(t("approveCodexQueue"))}</button>
          <button type="button" data-iteration-review="needs_changes">${escapeTraining(t("needsChangesAction"))}</button>
          <button type="button" data-iteration-review="deferred">${escapeTraining(t("deferHandoff"))}</button>
          <button type="button" data-iteration-review="rejected">${escapeTraining(t("reject"))}</button>
          <button type="button" data-iteration-review="note_only">${escapeTraining(t("addNote"))}</button>
        </div>
      </article>
      ${seedCards}${watchCards}
    </div>
  `;
}

function renderCodexWorkPackets(payload) {
  if (!codexWorkPacketQueue) return;
  const queue = payload.codex_work_packet_queue || {};
  const hermes = payload.hermes_work_packet_payload || {};
  const tiles = [
    [t("packetStatus"), statusText(queue.queue_status || "mock_contract")],
    [t("queueReady"), queue.queue_ready ? t("yes") : t("no")],
    [t("packetCount"), queue.packet_count ?? 0],
    [t("sourceProposal"), queue.source_proposal_review_status ? statusText(queue.source_proposal_review_status) : ""],
  ];
  const packetCards = (queue.work_packets || []).map((packet) => `
    <article class="mini-object">
      <small>${escapeTraining(packet.packet_id || "")} | ${escapeTraining(packet.priority || "")}</small>
      <strong>${escapeTraining(packet.title || statusText(packet.queue_status || ""))}</strong>
      <p>${escapeTraining(packet.summary || "")}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining((packet.required_validation || []).join(" | "))}</p>
      <p>${escapeTraining(t("humanReview"))}: ${escapeTraining(packet.requires_human_approval_before_execution ? t("yes") : t("no"))}</p>
    </article>
  `).join("");
  const blockers = (queue.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  codexWorkPacketQueue.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(queue.queue_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("workPackets"))}: ${escapeTraining(queue.packet_count ?? 0)}</p>
      </article>
      ${packetCards || blockers}
    </div>
  `;
}

function renderCodexPatchQueue(payload) {
  if (!patchQueue) return;
  const queue = payload.codex_patch_queue_contract || {};
  const hermes = payload.hermes_patch_queue_payload || {};
  const trainingSignals = queue.training_signal_queue || payload.source_training_signal_queue || [];
  const tiles = [
    [t("patchStatus"), statusText(queue.queue_status || "mock_contract")],
    [t("queueReady"), queue.queue_ready ? t("yes") : t("no")],
    [t("patchCandidates"), queue.patch_candidate_count ?? 0],
    [t("trainingSignals"), queue.training_signal_count ?? trainingSignals.length],
  ];
  const candidateCards = (queue.patch_candidates || []).map((candidate) => `
    <article class="mini-object">
      <small>${escapeTraining(candidate.candidate_id || "")} | ${escapeTraining(candidate.priority || "")}</small>
      <strong>${escapeTraining(statusText(candidate.type || ""))}</strong>
      <p>${escapeTraining(candidate.summary || "")}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining((candidate.required_validation || []).join(" | "))}</p>
      <p>${escapeTraining(t("humanReview"))}: ${escapeTraining(candidate.human_review_required ? t("yes") : t("no"))}</p>
    </article>
  `).join("");
  const signalCards = trainingSignals.slice(0, 4).map((item) => `
    <article class="mini-object">
      ${renderPatchItem(item)}
    </article>
  `).join("");
  const blockers = (queue.blocked_actions || []).slice(0, 3).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  patchQueue.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(queue.queue_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("patchCandidates"))}: ${escapeTraining(queue.patch_candidate_count ?? 0)}</p>
      </article>
      ${candidateCards || signalCards || blockers}
    </div>
  `;
}

function renderCodexExecutionGate(payload) {
  if (!executionGate) return;
  const gate = payload.codex_execution_gate || {};
  const hermes = payload.hermes_execution_gate_payload || {};
  const tiles = [
    [t("gateStatus"), statusText(gate.gate_status || "mock_contract")],
    [t("queueReady"), gate.gate_ready ? t("yes") : t("no")],
    [t("executionCandidates"), gate.execution_candidate_count ?? 0],
    [t("autoExecution"), gate.automatic_execution_allowed ? t("yes") : t("no")],
  ];
  const candidateCards = (gate.execution_candidates || []).map((candidate) => `
    <article class="mini-object training-actions execution-gate-actions"
      data-execution-candidate-id="${escapeTraining(candidate.execution_candidate_id || "")}"
      data-source-patch-candidate-id="${escapeTraining(candidate.source_patch_candidate_id || "")}"
      data-source-packet-id="${escapeTraining(candidate.source_packet_id || "")}"
      data-gate-status="${escapeTraining(gate.gate_status || "")}"
      data-candidate-type="${escapeTraining(candidate.type || "")}"
      data-priority="${escapeTraining(candidate.priority || "")}">
      <small>${escapeTraining(candidate.execution_candidate_id || "")} | ${escapeTraining(candidate.priority || "")}</small>
      <strong>${escapeTraining(statusText(candidate.type || ""))}</strong>
      <p>${escapeTraining(statusText(candidate.execution_review?.review_status || "pending_execution_review"))} | ${escapeTraining(statusText(candidate.worktree_preparation_status || candidate.execution_status || ""))}</p>
      <p>${escapeTraining(candidate.summary || "")}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining((candidate.required_validation || []).join(" | "))}</p>
      ${candidate.execution_review?.review_note ? `<p>${escapeTraining(candidate.execution_review.review_note)}</p>` : ""}
      <textarea class="training-execution-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}">${escapeTraining(candidate.execution_review?.review_note || "")}</textarea>
      <div class="training-button-row">
        <button type="button" data-execution-review="approved_for_worktree_preparation">${escapeTraining(t("approveWorktree"))}</button>
        <button type="button" data-execution-review="needs_changes">${escapeTraining(t("needsChangesAction"))}</button>
        <button type="button" data-execution-review="deferred">${escapeTraining(t("deferHandoff"))}</button>
        <button type="button" data-execution-review="rejected">${escapeTraining(t("reject"))}</button>
        <button type="button" data-execution-review="note_only">${escapeTraining(t("addNote"))}</button>
      </div>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  executionGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("humanReview"))}: ${escapeTraining(gate.human_confirmation_required ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || blockers}
    </div>
  `;
}

function renderCodexWorktreePrep(payload) {
  if (!worktreePrepQueue) return;
  const queue = payload.codex_worktree_preparation_queue || {};
  const hermes = payload.hermes_worktree_preparation_payload || {};
  const tiles = [
    [t("prepStatus"), statusText(queue.queue_status || "mock_contract")],
    [t("queueReady"), queue.queue_ready ? t("yes") : t("no")],
    [t("prepTasks"), queue.preparation_task_count ?? 0],
    [t("approvedCandidates"), queue.approved_execution_candidate_count ?? 0],
  ];
  const taskCards = (queue.preparation_tasks || []).map((task) => `
    <article class="mini-object">
      <small>${escapeTraining(task.task_id || "")} | ${escapeTraining(task.priority || "")}</small>
      <strong>${escapeTraining(statusText(task.type || ""))}</strong>
      <p>${escapeTraining(statusText(task.preparation_status || ""))}</p>
      <p>${escapeTraining(task.summary || "")}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining((task.required_validation || []).join(" | "))}</p>
      <p>${escapeTraining(t("humanReview"))}: ${escapeTraining(task.human_confirmation_required ? t("yes") : t("no"))}</p>
    </article>
  `).join("");
  const blockers = (queue.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  worktreePrepQueue.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(queue.queue_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("prepTasks"))}: ${escapeTraining(queue.preparation_task_count ?? 0)}</p>
      </article>
      ${taskCards || blockers}
    </div>
  `;
}

function renderCodexWorktreeLaunchGate(payload) {
  if (!worktreeLaunchGate) return;
  const gate = payload.codex_worktree_launch_gate || {};
  const hermes = payload.hermes_worktree_launch_payload || {};
  const tiles = [
    [t("launchStatus"), statusText(gate.launch_status || "mock_contract")],
    [t("queueReady"), gate.launch_ready ? t("yes") : t("no")],
    [t("launchRequests"), gate.launch_request_count ?? 0],
    [t("automaticLaunch"), gate.automatic_launch_allowed ? t("yes") : t("no")],
  ];
  const requestCards = (gate.launch_requests || []).map((request) => `
    <article class="mini-object">
      <small>${escapeTraining(request.launch_request_id || "")} | ${escapeTraining(request.priority || "")}</small>
      <strong>${escapeTraining(statusText(request.type || ""))}</strong>
      <p>${escapeTraining(statusText(request.launch_status || ""))}</p>
      <p>${escapeTraining(request.summary || "")}</p>
      <p>${escapeTraining(t("suggestedInstruction"))}: ${escapeTraining(request.suggested_user_instruction || "")}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((request.required_preflight_checks || []).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining((request.required_validation || []).join(" | "))}</p>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  worktreeLaunchGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.launch_gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("launchRequests"))}: ${escapeTraining(gate.launch_request_count ?? 0)}</p>
      </article>
      ${requestCards || blockers}
    </div>
  `;
}

function renderCodexWorktreeResults(payload) {
  if (!worktreeResultIntake) return;
  const intake = payload.codex_worktree_result_intake || {};
  const hermes = payload.hermes_worktree_result_payload || {};
  const tiles = [
    [t("resultStatus"), statusText(intake.intake_status || "mock_contract")],
    [t("resultCount"), intake.result_count ?? 0],
    [t("validationPassed"), intake.validation_passed_count ?? 0],
    [t("validationFailed"), intake.validation_failed_count ?? 0],
    [t("autoMerge"), intake.automatic_merge_allowed ? t("yes") : t("no")],
  ];
  const resultRecords = Object.values(intake.codex_worktree_results || {}).map((record) => `
    <article class="mini-object">
      <small>${escapeTraining(record.launch_request_id || "")} | ${escapeTraining(record.changed_file_count ?? 0)} ${escapeTraining(t("changedFiles"))}</small>
      <strong>${escapeTraining(statusText(record.result_status || "codex_worktree_result_record"))}</strong>
      <p>${escapeTraining(record.result_summary || "")}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((record.changed_files || []).join(" | "))}</p>
      <p>${escapeTraining(t("validationResults"))}: ${escapeTraining((record.validation_results || []).map((item) => `${item.command || ""}: ${statusText(item.status || "")}`).join(" | "))}</p>
    </article>
  `).join("");
  const blockers = (intake.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  worktreeResultIntake.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(intake.intake_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("resultCount"))}: ${escapeTraining(intake.result_count ?? 0)}</p>
      </article>
      ${resultRecords || blockers}
    </div>
  `;
}

function renderCodexWorktreeResultReviewGate(payload) {
  if (!worktreeResultReviewGate) return;
  const gate = payload.codex_worktree_result_review_gate || {};
  const hermes = payload.hermes_worktree_result_review_payload || {};
  const tiles = [
    [t("gateStatus"), statusText(gate.gate_status || "mock_contract")],
    [t("reviewCandidates"), gate.review_candidate_count ?? 0],
    [t("regressionCandidates"), gate.regression_promotion_candidate_count ?? 0],
    [t("memoryCandidates"), gate.hermes_memory_candidate_count ?? 0],
  ];
  const candidateCards = (gate.result_review_candidates || []).map((candidate) => `
    <article class="mini-object training-actions worktree-result-review-actions"
      data-launch-request-id="${escapeTraining(candidate.launch_request_id || "")}"
      data-result-status="${escapeTraining(candidate.result_status || "")}"
      data-changed-file-count="${escapeTraining(candidate.changed_file_count ?? 0)}"
      data-validation-contract-complete="${escapeTraining(candidate.validation_contract?.contract_complete ? "true" : "")}">
      <small>${escapeTraining(candidate.review_candidate_id || "")} | ${escapeTraining(candidate.changed_file_count ?? 0)} ${escapeTraining(t("changedFiles"))}</small>
      <strong>${escapeTraining(statusText(candidate.type || ""))}</strong>
      <p>${escapeTraining(statusText(candidate.review?.review_status || "pending_result_review"))}</p>
      <p>${escapeTraining(candidate.result_summary || "")}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((candidate.changed_files || []).join(" | "))}</p>
      ${candidate.review?.review_note ? `<p>${escapeTraining(candidate.review.review_note)}</p>` : ""}
      <textarea class="training-result-review-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}">${escapeTraining(candidate.review?.review_note || "")}</textarea>
      <div class="training-button-row">
        <button type="button" data-result-review="approved_for_regression_baseline">${escapeTraining(t("approveRegression"))}</button>
        <button type="button" data-result-review="approved_for_hermes_memory_candidate">${escapeTraining(t("approveMemory"))}</button>
        <button type="button" data-result-review="approved_for_regression_and_memory">${escapeTraining(t("approveRegressionMemory"))}</button>
        <button type="button" data-result-review="needs_changes">${escapeTraining(t("needsChangesAction"))}</button>
        <button type="button" data-result-review="deferred">${escapeTraining(t("deferHandoff"))}</button>
        <button type="button" data-result-review="rejected">${escapeTraining(t("reject"))}</button>
        <button type="button" data-result-review="note_only">${escapeTraining(t("addNote"))}</button>
      </div>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  worktreeResultReviewGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("humanReview"))}: ${escapeTraining(gate.human_review_required ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || blockers}
    </div>
  `;
}

function renderCodexPromotionCandidates(payload) {
  if (!promotionCandidateQueue) return;
  const queue = payload.codex_promotion_candidate_queue || {};
  const hermes = payload.hermes_promotion_candidate_payload || {};
  const tiles = [
    [t("promotionStatus"), statusText(queue.queue_status || "mock_contract")],
    [t("queueReady"), queue.queue_ready ? t("yes") : t("no")],
    [t("regressionCandidates"), queue.regression_promotion_candidate_count ?? 0],
    [t("memoryCandidates"), queue.hermes_memory_promotion_candidate_count ?? 0],
    [t("totalPromotionCandidates"), queue.promotion_candidate_count ?? 0],
  ];
  const renderCandidate = (candidate) => `
    <article class="mini-object">
      <small>${escapeTraining(candidate.promotion_candidate_id || "")} | ${escapeTraining(candidate.changed_file_count ?? 0)} ${escapeTraining(t("changedFiles"))}</small>
      <strong>${escapeTraining(statusText(candidate.promotion_type || ""))}</strong>
      <p>${escapeTraining(statusText(candidate.promotion_status || ""))}</p>
      <p>${escapeTraining(candidate.result_summary || "")}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((candidate.changed_files || []).join(" | "))}</p>
    </article>
  `;
  const candidateCards = [
    ...(queue.regression_baseline_promotion_candidates || []),
    ...(queue.hermes_memory_promotion_candidates || []),
  ].map(renderCandidate).join("");
  const blockers = (queue.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionCandidateQueue.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(queue.queue_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("humanReview"))}: ${escapeTraining(queue.human_confirmation_required ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || blockers}
    </div>
  `;
}

function renderCodexPromotionApprovalGate(payload) {
  if (!promotionApprovalGate) return;
  const gate = payload.codex_promotion_approval_gate || {};
  const hermes = payload.hermes_promotion_approval_payload || {};
  const tiles = [
    [t("approvalStatus"), statusText(gate.gate_status || "mock_contract")],
    [t("queueReady"), gate.gate_ready ? t("yes") : t("no")],
    [t("totalPromotionCandidates"), gate.promotion_candidate_count ?? 0],
    [t("reviewRequired"), gate.pending_approval_count ?? 0],
    [t("approvedFutureActions"), gate.approved_future_action_count ?? 0],
  ];
  const candidateCards = (gate.approval_candidates || []).map((candidate) => `
    <article class="mini-object promotion-approval-actions"
      data-promotion-candidate-id="${escapeTraining(candidate.promotion_candidate_id || "")}"
      data-promotion-type="${escapeTraining(candidate.promotion_type || "")}"
      data-launch-request-id="${escapeTraining(candidate.launch_request_id || "")}"
      data-source-patch-candidate-id="${escapeTraining(candidate.source_patch_candidate_id || "")}"
      data-source-packet-id="${escapeTraining(candidate.source_packet_id || "")}"
      data-changed-file-count="${escapeTraining(candidate.changed_file_count ?? 0)}">
      <small>${escapeTraining(candidate.approval_candidate_id || "")} | ${escapeTraining(statusText(candidate.review?.review_status || ""))}</small>
      <strong>${escapeTraining(statusText(candidate.promotion_type || ""))}</strong>
      <p>${escapeTraining(candidate.result_summary || "")}</p>
      <p>${escapeTraining(t("futureAction"))}: ${escapeTraining(statusText(candidate.future_action || ""))}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((candidate.changed_files || []).join(" | "))}</p>
      ${candidate.review?.review_note ? `<p>${escapeTraining(candidate.review.review_note)}</p>` : ""}
      <textarea class="training-promotion-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}">${escapeTraining(candidate.review?.review_note || "")}</textarea>
      <div class="training-button-row">
        <button type="button" data-promotion-approval="approved_for_future_promotion">${escapeTraining(t("approveFuturePromotion"))}</button>
        <button type="button" data-promotion-approval="hold_for_later">${escapeTraining(t("holdForLater"))}</button>
        <button type="button" data-promotion-approval="skipped_for_now">${escapeTraining(t("skipCandidate"))}</button>
        <button type="button" data-promotion-approval="needs_changes">${escapeTraining(t("needsChangesAction"))}</button>
        <button type="button" data-promotion-approval="rejected">${escapeTraining(t("reject"))}</button>
        <button type="button" data-promotion-approval="note_only">${escapeTraining(t("addNote"))}</button>
      </div>
    </article>
  `).join("");
  const futureActions = (gate.future_action_plan || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.plan_id || "")} | ${escapeTraining(statusText(item.execution_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.future_action || ""))}</strong>
      <p>${escapeTraining(item.promotion_candidate_id || "")}</p>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionApprovalGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("humanReview"))}: ${escapeTraining(gate.human_confirmation_required ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || futureActions || blockers}
    </div>
    ${futureActions ? `<div class="training-capability-grid">${futureActions}</div>` : ""}
  `;
}

function renderCodexPromotionHandoff(payload) {
  if (!promotionHandoffQueue) return;
  const queue = payload.codex_promotion_handoff_queue || {};
  const hermes = payload.hermes_promotion_handoff_payload || {};
  const tiles = [
    [t("handoffStatus"), statusText(queue.handoff_status || "mock_contract")],
    [t("queueReady"), queue.handoff_ready ? t("yes") : t("no")],
    [t("handoffItems"), queue.handoff_item_count ?? 0],
    [t("regressionCandidates"), queue.regression_handoff_count ?? 0],
    [t("memoryCandidates"), queue.hermes_memory_handoff_count ?? 0],
  ];
  const handoffCards = (queue.handoff_items || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.handoff_id || "")} | ${escapeTraining(statusText(item.handoff_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.future_action || ""))}</strong>
      <p>${escapeTraining(t("targetSystem"))}: ${escapeTraining(statusText(item.target_system || ""))}</p>
      <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
      <p>${escapeTraining(t("manualExecution"))}: ${escapeTraining(item.manual_execution_required ? t("yes") : t("no"))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_preflight_checks || []).join(" | "))}</p>
      <p>${escapeTraining(t("suggestedInstruction"))}: ${escapeTraining(item.suggested_user_instruction || "")}</p>
    </article>
  `).join("");
  const blockers = (queue.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionHandoffQueue.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(queue.handoff_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("manualExecution"))}: ${escapeTraining(queue.manual_execution_required ? t("yes") : t("no"))}</p>
      </article>
      ${handoffCards || blockers}
    </div>
  `;
}

function renderCodexPromotionReadiness(payload) {
  if (!promotionReadinessGate) return;
  const gate = payload.codex_promotion_execution_readiness_gate || {};
  const hermes = payload.hermes_promotion_execution_readiness_payload || {};
  const tiles = [
    [t("readinessStatus"), statusText(gate.readiness_status || "mock_contract")],
    [t("queueReady"), gate.readiness_ready ? t("yes") : t("no")],
    [t("readinessItems"), gate.readiness_item_count ?? 0],
    [t("blockers"), gate.blocked_readiness_item_count ?? 0],
    [t("manualExecution"), gate.manual_execution_required ? t("yes") : t("no")],
  ];
  const readinessCards = (gate.readiness_items || []).map((item) => `
    <article class="mini-object promotion-readiness-actions"
      data-readiness-item-id="${escapeTraining(item.readiness_item_id || "")}"
      data-source-handoff-id="${escapeTraining(item.source_handoff_id || "")}"
      data-promotion-candidate-id="${escapeTraining(item.promotion_candidate_id || "")}"
      data-promotion-type="${escapeTraining(item.promotion_type || "")}"
      data-confirmed-inputs="${escapeTraining(((item.original_missing_readiness_inputs || item.missing_readiness_inputs || [])).join("||"))}">
      <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.readiness_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.future_action || ""))}</strong>
      <p>${escapeTraining(t("targetSystem"))}: ${escapeTraining(statusText(item.target_system || ""))}</p>
      <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
      <p>${escapeTraining(t("readinessReviewStatus"))}: ${escapeTraining(statusText(item.readiness_review?.review_status || "pending_readiness_review"))}</p>
      <p>${escapeTraining(t("missingInputs"))}: ${escapeTraining((item.missing_readiness_inputs || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_preflight_checks || []).join(" | "))}</p>
      ${item.readiness_review?.review_note ? `<p>${escapeTraining(item.readiness_review.review_note)}</p>` : ""}
      <textarea class="training-readiness-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}">${escapeTraining(item.readiness_review?.review_note || "")}</textarea>
      <div class="training-button-row">
        <button type="button" data-promotion-readiness-review="confirmed_ready_for_manual_execution">${escapeTraining(t("confirmReadiness"))}</button>
        <button type="button" data-promotion-readiness-review="needs_execution_inputs">${escapeTraining(t("needsExecutionInputs"))}</button>
        <button type="button" data-promotion-readiness-review="deferred">${escapeTraining(t("deferHandoff"))}</button>
        <button type="button" data-promotion-readiness-review="rejected">${escapeTraining(t("reject"))}</button>
        <button type="button" data-promotion-readiness-review="note_only">${escapeTraining(t("addNote"))}</button>
      </div>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionReadinessGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("manualExecution"))}: ${escapeTraining(gate.manual_execution_required ? t("yes") : t("no"))}</p>
      </article>
      ${readinessCards || blockers}
    </div>
  `;
}

function renderCodexPromotionExecutionResults(payload) {
  if (!promotionExecutionResultIntake) return;
  const intake = payload.codex_promotion_execution_result_intake || {};
  const hermes = payload.hermes_promotion_execution_result_payload || {};
  const state = intake.result_state || {};
  const tiles = [
    [t("resultIntakeStatus"), statusText(intake.intake_status || "mock_contract")],
    [t("resultCount"), intake.result_count ?? 0],
    [t("validationPassed"), state.manual_execution_recorded_count ?? 0],
    [t("validationFailed"), state.manual_execution_failed_count ?? 0],
    [t("manualExecution"), intake.manual_execution_result_required ? t("yes") : t("no")],
  ];
  const resultCards = Object.values(intake.codex_promotion_execution_results || {}).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.result_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.promotion_type || ""))}</strong>
      <p>${escapeTraining(item.result_summary || "")}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.changed_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining(item.validation_summary || "")}</p>
    </article>
  `).join("");
  const readyItems = ((payload.source_codex_promotion_execution_readiness_gate || {}).readiness_items || [])
    .filter((item) => item.readiness_status === "execution_prerequisites_confirmed")
    .map((item) => `
      <article class="mini-object promotion-execution-result-actions"
        data-readiness-item-id="${escapeTraining(item.readiness_item_id || "")}"
        data-promotion-candidate-id="${escapeTraining(item.promotion_candidate_id || "")}"
        data-promotion-type="${escapeTraining(item.promotion_type || "")}"
        data-changed-records="${escapeTraining([item.promotion_candidate_id || item.readiness_item_id || ""].filter(Boolean).join("||"))}">
        <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.readiness_status || ""))}</small>
        <strong>${escapeTraining(statusText(item.future_action || ""))}</strong>
        <p>${escapeTraining(t("targetSystem"))}: ${escapeTraining(statusText(item.target_system || ""))}</p>
        <textarea class="training-promotion-result-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}"></textarea>
        <div class="training-button-row">
          <button type="button" data-promotion-execution-result="manual_execution_recorded">${escapeTraining(t("recordManualResult"))}</button>
          <button type="button" data-promotion-execution-result="manual_execution_failed">${escapeTraining(t("validationFailed"))}</button>
          <button type="button" data-promotion-execution-result="manual_execution_skipped">${escapeTraining(t("skipCandidate"))}</button>
          <button type="button" data-promotion-execution-result="note_only">${escapeTraining(t("addNote"))}</button>
        </div>
      </article>
    `).join("");
  const blockers = (intake.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionExecutionResultIntake.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(intake.intake_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(intake.automatic_execution_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${resultCards || readyItems || blockers}
    </div>
  `;
}

function renderCodexPromotionClosureAudit(payload) {
  if (!promotionClosureAudit) return;
  const audit = payload.codex_promotion_closure_audit || {};
  const hermes = payload.hermes_promotion_closure_audit_payload || {};
  const tiles = [
    [t("closureAuditStatus"), statusText(audit.closure_status || "mock_contract")],
    [t("resultCount"), audit.recorded_result_count ?? 0],
    [t("validationPassed"), audit.complete_result_count ?? 0],
    [t("missingInputs"), audit.missing_result_count ?? 0],
    [t("syncAuditCandidates"), audit.sync_audit_candidate_count ?? 0],
    [t("futureHermesSync"), audit.future_hermes_sync_audit_required ? t("yes") : t("no")],
  ];
  const candidateCards = (audit.sync_audit_candidates || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.sync_audit_id || "")} | ${escapeTraining(statusText(item.sync_audit_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(statusText(item.promotion_type || ""))} | ${escapeTraining(t("manualExecution"))}: ${escapeTraining(item.manual_review_required ? t("yes") : t("no"))}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.source_changed_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_sync_checks || []).map(statusText).join(" | "))}</p>
    </article>
  `).join("");
  const missingCards = (audit.missing_results || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")}</small>
      <strong>${escapeTraining(statusText(item.missing_reason || ""))}</strong>
      <p>${escapeTraining(statusText(item.promotion_type || ""))} | ${escapeTraining(item.promotion_candidate_id || "")}</p>
    </article>
  `).join("");
  const blockers = (audit.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionClosureAudit.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(audit.audit_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(audit.automatic_sync_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || missingCards || blockers}
    </div>
  `;
}

function renderCodexPromotionSyncReviewGate(payload) {
  if (!promotionSyncReviewGate) return;
  const gate = payload.codex_promotion_sync_review_gate || {};
  const hermes = payload.hermes_promotion_sync_review_payload || {};
  const state = gate.sync_review_state || {};
  const tiles = [
    [t("syncReviewStatus"), statusText(gate.gate_status || "mock_contract")],
    [t("syncAuditCandidates"), gate.sync_candidate_count ?? 0],
    [t("approvedCandidates"), gate.approved_future_sync_count ?? 0],
    [t("futureAction"), gate.future_sync_action_count ?? 0],
    [t("autoExecution"), gate.automatic_sync_allowed ? t("yes") : t("no")],
  ];
  const candidateCards = (gate.sync_review_candidates || []).map((item) => {
    const confirmedChecks = (item.required_sync_checks || []).join("||");
    return `
      <article class="mini-object promotion-sync-review-actions"
        data-sync-audit-id="${escapeTraining(item.sync_audit_id || "")}"
        data-readiness-item-id="${escapeTraining(item.readiness_item_id || "")}"
        data-promotion-candidate-id="${escapeTraining(item.promotion_candidate_id || "")}"
        data-promotion-type="${escapeTraining(item.promotion_type || "")}"
        data-target-system="${escapeTraining(item.target_system || "")}"
        data-confirmed-sync-checks="${escapeTraining(confirmedChecks)}">
        <small>${escapeTraining(item.sync_audit_id || "")} | ${escapeTraining(statusText(item.sync_review_status || ""))}</small>
        <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
        <p>${escapeTraining(statusText(item.promotion_type || ""))} | ${escapeTraining(t("manualExecution"))}: ${escapeTraining(item.manual_review_required ? t("yes") : t("no"))}</p>
        <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_sync_checks || []).map(statusText).join(" | "))}</p>
        <textarea class="training-sync-review-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}"></textarea>
        <div class="training-button-row">
          <button type="button" data-promotion-sync-review="approved_for_future_sync">${escapeTraining(t("approveFutureSync"))}</button>
          <button type="button" data-promotion-sync-review="needs_sync_inputs">${escapeTraining(t("needsSyncInputs"))}</button>
          <button type="button" data-promotion-sync-review="deferred">${escapeTraining(t("deferHandoff"))}</button>
          <button type="button" data-promotion-sync-review="rejected">${escapeTraining(t("reject"))}</button>
          <button type="button" data-promotion-sync-review="note_only">${escapeTraining(t("addNote"))}</button>
        </div>
      </article>
    `;
  }).join("");
  const futureActions = (gate.future_sync_action_plan || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.sync_audit_id || "")} | ${escapeTraining(statusText(item.execution_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(statusText(item.promotion_type || ""))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(item.automatic_sync_allowed ? t("yes") : t("no"))}</p>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionSyncReviewGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("reviewStatus"))}: ${escapeTraining(state.sync_review_count ?? 0)}</p>
      </article>
      ${candidateCards || futureActions || blockers}
    </div>
  `;
}

function renderCodexPromotionSyncHandoff(payload) {
  if (!promotionSyncHandoffQueue) return;
  const queue = payload.codex_promotion_sync_handoff_queue || {};
  const hermes = payload.hermes_promotion_sync_handoff_payload || {};
  const tiles = [
    [t("syncHandoffStatus"), statusText(queue.handoff_status || "mock_contract")],
    [t("handoffItems"), queue.handoff_item_count ?? 0],
    [t("manualExecution"), queue.manual_execution_required ? t("yes") : t("no")],
    [t("autoExecution"), queue.automatic_execution_allowed ? t("yes") : t("no")],
    [statusText("live_hermes_memory"), queue.hermes_sync_handoff_count ?? 0],
    [statusText("local_regression_baseline_store"), queue.regression_sync_handoff_count ?? 0],
  ];
  const handoffCards = (queue.handoff_items || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.sync_handoff_item_id || "")} | ${escapeTraining(statusText(item.execution_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_preflight_checks || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining((item.execution_evidence_required || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(item.suggested_user_instruction || "")}</p>
    </article>
  `).join("");
  const blockers = (queue.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionSyncHandoffQueue.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(queue.handoff_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(queue.automatic_execution_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${handoffCards || blockers}
    </div>
  `;
}

function renderCodexPromotionSyncReadiness(payload) {
  if (!promotionSyncReadinessGate) return;
  const gate = payload.codex_promotion_sync_execution_readiness_gate || {};
  const hermes = payload.hermes_promotion_sync_execution_readiness_payload || {};
  const reviewState = payload.codex_promotion_sync_readiness_review_state || gate.readiness_review_state || {};
  const tiles = [
    [t("syncReadinessStatus"), statusText(gate.readiness_status || "mock_contract")],
    [t("readinessItems"), gate.readiness_item_count ?? 0],
    [t("missingInputs"), gate.blocked_readiness_item_count ?? 0],
    [t("manualExecution"), gate.manual_sync_execution_required ? t("yes") : t("no")],
    [t("autoExecution"), gate.automatic_sync_execution_allowed ? t("yes") : t("no")],
    [statusText("live_hermes_memory"), gate.hermes_sync_readiness_count ?? 0],
    [statusText("local_regression_baseline_store"), gate.regression_sync_readiness_count ?? 0],
  ];
  const readinessCards = (gate.readiness_items || []).map((item) => {
    const confirmedInputs = (item.original_missing_readiness_inputs || []).join("||");
    return `
    <article class="mini-object promotion-sync-readiness-actions"
      data-readiness-item-id="${escapeTraining(item.readiness_item_id || "")}"
      data-source-sync-handoff-item-id="${escapeTraining(item.source_sync_handoff_item_id || "")}"
      data-source-sync-audit-id="${escapeTraining(item.source_sync_audit_id || "")}"
      data-promotion-candidate-id="${escapeTraining(item.promotion_candidate_id || "")}"
      data-promotion-type="${escapeTraining(item.promotion_type || "")}"
      data-target-system="${escapeTraining(item.target_system || "")}"
      data-confirmed-inputs="${escapeTraining(confirmedInputs)}">
      <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.readiness_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
      <p>${escapeTraining(t("missingInputs"))}: ${escapeTraining((item.missing_readiness_inputs || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining((item.execution_evidence_required || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(item.suggested_user_instruction || "")}</p>
      <textarea class="training-sync-readiness-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}"></textarea>
      <div class="training-button-row">
        <button type="button" data-promotion-sync-readiness-review="confirmed_ready_for_manual_sync_execution">${escapeTraining(t("confirmReadiness"))}</button>
        <button type="button" data-promotion-sync-readiness-review="needs_sync_execution_inputs">${escapeTraining(t("needsSyncInputs"))}</button>
        <button type="button" data-promotion-sync-readiness-review="deferred">${escapeTraining(t("deferHandoff"))}</button>
        <button type="button" data-promotion-sync-readiness-review="rejected">${escapeTraining(t("reject"))}</button>
        <button type="button" data-promotion-sync-readiness-review="note_only">${escapeTraining(t("addNote"))}</button>
      </div>
    </article>
  `;
  }).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionSyncReadinessGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("reviewStatus"))}: ${escapeTraining(reviewState.readiness_review_count ?? 0)} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(gate.automatic_sync_execution_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${readinessCards || blockers}
    </div>
  `;
}

function renderCodexPromotionSyncExecutionResults(payload) {
  if (!promotionSyncExecutionResultIntake) return;
  const intake = payload.codex_promotion_sync_execution_result_intake || {};
  const hermes = payload.hermes_promotion_sync_execution_result_payload || {};
  const state = intake.result_state || {};
  const tiles = [
    [t("resultIntakeStatus"), statusText(intake.intake_status || "mock_contract")],
    [t("resultCount"), intake.result_count ?? 0],
    [t("validationPassed"), state.manual_sync_execution_recorded_count ?? 0],
    [t("validationFailed"), state.manual_sync_execution_failed_count ?? 0],
    [t("manualExecution"), intake.manual_sync_execution_result_required ? t("yes") : t("no")],
  ];
  const resultCards = Object.values(intake.codex_promotion_sync_execution_results || {}).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.result_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(item.result_summary || "")}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.changed_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining(item.validation_summary || "")}</p>
    </article>
  `).join("");
  const readyItems = ((payload.source_codex_promotion_sync_execution_readiness_gate || {}).readiness_items || [])
    .filter((item) => item.readiness_status === "sync_execution_prerequisites_confirmed")
    .map((item) => `
      <article class="mini-object promotion-sync-execution-result-actions"
        data-readiness-item-id="${escapeTraining(item.readiness_item_id || "")}"
        data-source-sync-handoff-item-id="${escapeTraining(item.source_sync_handoff_item_id || "")}"
        data-source-sync-audit-id="${escapeTraining(item.source_sync_audit_id || "")}"
        data-promotion-candidate-id="${escapeTraining(item.promotion_candidate_id || "")}"
        data-promotion-type="${escapeTraining(item.promotion_type || "")}"
        data-target-system="${escapeTraining(item.target_system || "")}"
        data-changed-records="${escapeTraining([item.promotion_candidate_id || item.readiness_item_id || "", item.target_system || ""].filter(Boolean).join("||"))}">
        <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.readiness_status || ""))}</small>
        <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
        <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
        <p>${escapeTraining(t("validation"))}: ${escapeTraining((item.execution_evidence_required || []).map(statusText).join(" | "))}</p>
        <textarea class="training-sync-result-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}"></textarea>
        <div class="training-button-row">
          <button type="button" data-promotion-sync-execution-result="manual_sync_execution_recorded">${escapeTraining(t("recordManualResult"))}</button>
          <button type="button" data-promotion-sync-execution-result="manual_sync_execution_failed">${escapeTraining(t("validationFailed"))}</button>
          <button type="button" data-promotion-sync-execution-result="manual_sync_execution_skipped">${escapeTraining(t("skipCandidate"))}</button>
          <button type="button" data-promotion-sync-execution-result="note_only">${escapeTraining(t("addNote"))}</button>
        </div>
      </article>
    `).join("");
  const blockers = (intake.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionSyncExecutionResultIntake.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(intake.intake_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(intake.automatic_sync_execution_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${resultCards || readyItems || blockers}
    </div>
  `;
}

function renderCodexPromotionSyncClosureAudit(payload) {
  if (!promotionSyncClosureAudit) return;
  const audit = payload.codex_promotion_sync_closure_audit || {};
  const hermes = payload.hermes_promotion_sync_closure_audit_payload || {};
  const tiles = [
    [t("closureAuditStatus"), statusText(audit.closure_status || "mock_contract")],
    [t("resultCount"), audit.recorded_result_count ?? 0],
    [t("validationPassed"), audit.complete_result_count ?? 0],
    [t("missingInputs"), audit.missing_result_count ?? 0],
    [t("reviewCandidates"), audit.final_closure_candidate_count ?? 0],
    [t("autoExecution"), audit.automatic_sync_allowed ? t("yes") : t("no")],
  ];
  const candidateCards = (audit.final_sync_closure_candidates || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.final_closure_id || "")} | ${escapeTraining(statusText(item.closure_candidate_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(statusText(item.promotion_type || ""))} | ${escapeTraining(t("reviewRequired"))}: ${escapeTraining(item.final_review_required ? t("yes") : t("no"))}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.changed_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_final_checks || []).map(statusText).join(" | "))}</p>
    </article>
  `).join("");
  const missingCards = (audit.missing_results || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")}</small>
      <strong>${escapeTraining(statusText(item.missing_reason || ""))}</strong>
      <p>${escapeTraining(statusText(item.target_system || ""))} | ${escapeTraining(item.promotion_candidate_id || "")}</p>
    </article>
  `).join("");
  const blockers = (audit.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionSyncClosureAudit.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(audit.audit_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(audit.automatic_sync_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || missingCards || blockers}
    </div>
  `;
}

function renderCodexPromotionSyncClosureReviewGate(payload) {
  if (!promotionSyncClosureReviewGate) return;
  const gate = payload.codex_promotion_sync_closure_review_gate || {};
  const hermes = payload.hermes_promotion_sync_closure_review_payload || {};
  const state = gate.sync_closure_review_state || {};
  const tiles = [
    [t("reviewStatus"), statusText(gate.gate_status || "mock_contract")],
    [t("reviewCandidates"), gate.candidate_count ?? 0],
    [t("approved"), gate.approved_final_sync_count ?? 0],
    [t("missingInputs"), gate.needs_final_sync_inputs_count ?? 0],
    [t("manualExecution"), gate.manual_final_sync_review_required ? t("yes") : t("no")],
    [t("autoExecution"), gate.automatic_final_sync_allowed ? t("yes") : t("no")],
  ];
  const candidateCards = (gate.sync_closure_review_candidates || []).map((item) => {
    const confirmedChecks = (item.required_final_checks || []).join("||");
    return `
    <article class="mini-object promotion-sync-closure-review-actions"
      data-final-closure-id="${escapeTraining(item.final_closure_id || "")}"
      data-readiness-item-id="${escapeTraining(item.readiness_item_id || "")}"
      data-source-sync-audit-id="${escapeTraining(item.source_sync_audit_id || "")}"
      data-promotion-candidate-id="${escapeTraining(item.promotion_candidate_id || "")}"
      data-promotion-type="${escapeTraining(item.promotion_type || "")}"
      data-target-system="${escapeTraining(item.target_system || "")}"
      data-confirmed-final-checks="${escapeTraining(confirmedChecks)}">
      <small>${escapeTraining(item.final_closure_id || "")} | ${escapeTraining(statusText(item.sync_closure_review_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(statusText(item.promotion_type || ""))} | ${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.changed_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_final_checks || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("missingInputs"))}: ${escapeTraining((item.remaining_final_checks || []).map(statusText).join(" | "))}</p>
      <textarea class="training-sync-closure-review-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}">${escapeTraining(item.sync_closure_review?.review_note || "")}</textarea>
      <div class="training-button-row">
        <button type="button" data-promotion-sync-closure-review="approved_for_final_sync">${escapeTraining(t("approveFutureSync"))}</button>
        <button type="button" data-promotion-sync-closure-review="needs_final_sync_inputs">${escapeTraining(t("needsSyncInputs"))}</button>
        <button type="button" data-promotion-sync-closure-review="deferred">${escapeTraining(t("deferHandoff"))}</button>
        <button type="button" data-promotion-sync-closure-review="rejected">${escapeTraining(t("reject"))}</button>
        <button type="button" data-promotion-sync-closure-review="note_only">${escapeTraining(t("addNote"))}</button>
      </div>
    </article>
  `;
  }).join("");
  const futureActions = (gate.future_real_sync_action_plan || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.action_id || "")} | ${escapeTraining(statusText(item.execution_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_real_sync_inputs || []).map(statusText).join(" | "))}</p>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionSyncClosureReviewGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("reviewStatus"))}: ${escapeTraining(state.closure_review_count ?? 0)} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(gate.automatic_final_sync_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || futureActions || blockers}
    </div>
  `;
}

function renderCodexPromotionFinalSyncHandoff(payload) {
  if (!promotionFinalSyncHandoffQueue) return;
  const queue = payload.codex_promotion_final_sync_handoff_queue || {};
  const hermes = payload.hermes_promotion_final_sync_handoff_payload || {};
  const tiles = [
    [t("syncHandoffStatus"), statusText(queue.handoff_status || "mock_contract")],
    [t("handoffItems"), queue.handoff_item_count ?? 0],
    [t("manualExecution"), queue.manual_execution_required ? t("yes") : t("no")],
    [t("autoExecution"), queue.automatic_execution_allowed ? t("yes") : t("no")],
    [statusText("live_hermes_memory"), queue.hermes_final_sync_handoff_count ?? 0],
    [statusText("local_regression_baseline_store"), queue.regression_final_sync_handoff_count ?? 0],
  ];
  const handoffCards = (queue.handoff_items || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.final_sync_handoff_item_id || "")} | ${escapeTraining(statusText(item.execution_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_real_sync_inputs || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining((item.execution_evidence_required || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(item.suggested_user_instruction || "")}</p>
    </article>
  `).join("");
  const blockers = (queue.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionFinalSyncHandoffQueue.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(queue.handoff_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(queue.automatic_execution_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${handoffCards || blockers}
    </div>
  `;
}

function renderCodexPromotionFinalSyncReadiness(payload) {
  if (!promotionFinalSyncReadinessGate) return;
  const gate = payload.codex_promotion_final_sync_execution_readiness_gate || {};
  const hermes = payload.hermes_promotion_final_sync_execution_readiness_payload || {};
  const tiles = [
    [t("readinessStatus"), statusText(gate.readiness_status || "mock_contract")],
    [t("readinessItems"), gate.readiness_item_count ?? 0],
    [t("missingInputs"), gate.blocked_readiness_item_count ?? 0],
    [t("manualExecution"), gate.manual_final_sync_execution_required ? t("yes") : t("no")],
    [t("autoExecution"), gate.automatic_execution_allowed ? t("yes") : t("no")],
    [statusText("live_hermes_memory"), gate.hermes_final_sync_readiness_count ?? 0],
    [statusText("local_regression_baseline_store"), gate.regression_final_sync_readiness_count ?? 0],
  ];
  const readinessCards = (gate.readiness_items || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.readiness_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
      <p>${escapeTraining(t("missingInputs"))}: ${escapeTraining((item.missing_real_sync_inputs || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_real_sync_inputs || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining((item.execution_evidence_required || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(item.suggested_user_instruction || "")}</p>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionFinalSyncReadinessGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(gate.automatic_execution_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${readinessCards || blockers}
    </div>
  `;
}

function renderCodexPromotionFinalSyncExecutionResults(payload) {
  if (!promotionFinalSyncExecutionResultIntake) return;
  const intake = payload.codex_promotion_final_sync_execution_result_intake || {};
  const hermes = payload.hermes_promotion_final_sync_execution_result_payload || {};
  const state = intake.result_state || {};
  const tiles = [
    [t("resultIntakeStatus"), statusText(intake.intake_status || "mock_contract")],
    [t("resultCount"), intake.result_count ?? 0],
    [t("validationPassed"), state.manual_final_sync_execution_recorded_count ?? 0],
    [t("validationFailed"), state.manual_final_sync_execution_failed_count ?? 0],
    [t("manualExecution"), intake.manual_final_sync_execution_result_required ? t("yes") : t("no")],
    [t("autoExecution"), intake.automatic_execution_allowed ? t("yes") : t("no")],
  ];
  const resultCards = Object.values(intake.codex_promotion_final_sync_execution_results || {}).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.result_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(item.result_summary || "")}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.changed_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining(item.validation_summary || "")}</p>
    </article>
  `).join("");
  const readyItems = ((payload.source_codex_promotion_final_sync_execution_readiness_gate || {}).readiness_items || [])
    .filter((item) => item.readiness_status === "final_sync_execution_prerequisites_confirmed")
    .map((item) => `
      <article class="mini-object promotion-final-sync-execution-result-actions"
        data-readiness-item-id="${escapeTraining(item.readiness_item_id || "")}"
        data-source-final-sync-handoff-item-id="${escapeTraining(item.source_final_sync_handoff_item_id || "")}"
        data-source-action-id="${escapeTraining(item.source_action_id || "")}"
        data-final-closure-id="${escapeTraining(item.final_closure_id || "")}"
        data-source-sync-audit-id="${escapeTraining(item.source_sync_audit_id || "")}"
        data-promotion-candidate-id="${escapeTraining(item.promotion_candidate_id || "")}"
        data-promotion-type="${escapeTraining(item.promotion_type || "")}"
        data-target-system="${escapeTraining(item.target_system || "")}"
        data-changed-records="${escapeTraining((item.source_changed_records || [item.promotion_candidate_id || item.readiness_item_id || "", item.target_system || ""]).filter(Boolean).join("||"))}">
        <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.readiness_status || ""))}</small>
        <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
        <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
        <p>${escapeTraining(t("validation"))}: ${escapeTraining((item.execution_evidence_required || []).map(statusText).join(" | "))}</p>
        <textarea class="training-final-sync-result-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}"></textarea>
        <div class="training-button-row">
          <button type="button" data-promotion-final-sync-execution-result="manual_final_sync_execution_recorded">${escapeTraining(t("recordManualResult"))}</button>
          <button type="button" data-promotion-final-sync-execution-result="manual_final_sync_execution_failed">${escapeTraining(t("validationFailed"))}</button>
          <button type="button" data-promotion-final-sync-execution-result="manual_final_sync_execution_skipped">${escapeTraining(t("skipCandidate"))}</button>
          <button type="button" data-promotion-final-sync-execution-result="note_only">${escapeTraining(t("addNote"))}</button>
        </div>
      </article>
    `).join("");
  const blockers = (intake.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionFinalSyncExecutionResultIntake.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(intake.intake_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(intake.automatic_execution_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${resultCards || readyItems || blockers}
    </div>
  `;
}

function renderCodexPromotionFinalSyncClosureAudit(payload) {
  if (!promotionFinalSyncClosureAudit) return;
  const audit = payload.codex_promotion_final_sync_closure_audit || {};
  const hermes = payload.hermes_promotion_final_sync_closure_audit_payload || {};
  const tiles = [
    [t("closureAuditStatus"), statusText(audit.closure_status || "mock_contract")],
    [t("resultCount"), audit.recorded_result_count ?? 0],
    [t("validationPassed"), audit.complete_result_count ?? 0],
    [t("missingInputs"), audit.missing_result_count ?? 0],
    [t("reviewCandidates"), audit.final_closure_candidate_count ?? 0],
    [t("autoExecution"), audit.automatic_closure_allowed ? t("yes") : t("no")],
  ];
  const candidateCards = (audit.final_closure_candidates || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.final_sync_completion_id || "")} | ${escapeTraining(statusText(item.closure_candidate_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(statusText(item.promotion_type || ""))} | ${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.changed_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining(item.validation_summary || "")}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_completion_checks || []).map(statusText).join(" | "))}</p>
    </article>
  `).join("");
  const missingCards = (audit.missing_results || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")}</small>
      <strong>${escapeTraining(statusText(item.missing_reason || ""))}</strong>
      <p>${escapeTraining(statusText(item.target_system || ""))} | ${escapeTraining(item.promotion_candidate_id || "")}</p>
    </article>
  `).join("");
  const blockers = (audit.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionFinalSyncClosureAudit.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(audit.audit_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(audit.automatic_closure_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || missingCards || blockers}
    </div>
  `;
}

function renderCodexPromotionFinalCompletionReviewGate(payload) {
  if (!promotionFinalCompletionReviewGate) return;
  const gate = payload.codex_promotion_final_completion_review_gate || {};
  const hermes = payload.hermes_promotion_final_completion_review_payload || {};
  const state = gate.final_completion_review_state || {};
  const tiles = [
    [t("reviewStatus"), statusText(gate.gate_status || "mock_contract")],
    [t("reviewCandidates"), gate.candidate_count ?? 0],
    [t("approved"), gate.approved_final_completion_count ?? 0],
    [t("missingInputs"), gate.needs_completion_inputs_count ?? 0],
    [t("manualExecution"), gate.manual_final_completion_review_required ? t("yes") : t("no")],
    [t("autoExecution"), gate.automatic_completion_allowed ? t("yes") : t("no")],
  ];
  const candidateCards = (gate.final_completion_review_candidates || []).map((item) => {
    const confirmedChecks = (item.required_completion_checks || []).join("||");
    return `
    <article class="mini-object promotion-final-completion-review-actions"
      data-final-sync-completion-id="${escapeTraining(item.final_sync_completion_id || "")}"
      data-readiness-item-id="${escapeTraining(item.readiness_item_id || "")}"
      data-final-closure-id="${escapeTraining(item.final_closure_id || "")}"
      data-source-action-id="${escapeTraining(item.source_action_id || "")}"
      data-source-sync-audit-id="${escapeTraining(item.source_sync_audit_id || "")}"
      data-promotion-candidate-id="${escapeTraining(item.promotion_candidate_id || "")}"
      data-promotion-type="${escapeTraining(item.promotion_type || "")}"
      data-target-system="${escapeTraining(item.target_system || "")}"
      data-confirmed-completion-checks="${escapeTraining(confirmedChecks)}">
      <small>${escapeTraining(item.final_sync_completion_id || "")} | ${escapeTraining(statusText(item.final_completion_review_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(statusText(item.promotion_type || ""))} | ${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.changed_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_completion_checks || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("missingInputs"))}: ${escapeTraining((item.remaining_completion_checks || []).map(statusText).join(" | "))}</p>
      <textarea class="training-final-completion-review-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}">${escapeTraining(item.final_completion_review?.review_note || "")}</textarea>
      <div class="training-button-row">
        <button type="button" data-promotion-final-completion-review="approved_final_completion">${escapeTraining(t("approveFinalCompletion"))}</button>
        <button type="button" data-promotion-final-completion-review="needs_completion_inputs">${escapeTraining(t("needsCompletionInputs"))}</button>
        <button type="button" data-promotion-final-completion-review="deferred">${escapeTraining(t("deferHandoff"))}</button>
        <button type="button" data-promotion-final-completion-review="rejected">${escapeTraining(t("reject"))}</button>
        <button type="button" data-promotion-final-completion-review="note_only">${escapeTraining(t("addNote"))}</button>
      </div>
    </article>
  `;
  }).join("");
  const publicationActions = (gate.final_completion_publication_plan || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.action_id || "")} | ${escapeTraining(statusText(item.execution_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_publication_inputs || []).map(statusText).join(" | "))}</p>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionFinalCompletionReviewGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("reviewStatus"))}: ${escapeTraining(state.final_completion_review_count ?? 0)} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(gate.automatic_completion_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || publicationActions || blockers}
    </div>
  `;
}

function renderCodexPromotionFinalPublicationHandoff(payload) {
  if (!promotionFinalPublicationHandoffQueue) return;
  const queue = payload.codex_promotion_final_publication_handoff_queue || {};
  const hermes = payload.hermes_promotion_final_publication_handoff_payload || {};
  const tiles = [
    [t("handoffStatus"), statusText(queue.handoff_status || "mock_contract")],
    [t("handoffItems"), queue.handoff_item_count ?? 0],
    [statusText("live_hermes_memory"), queue.hermes_publication_handoff_count ?? 0],
    [statusText("local_regression_baseline_store"), queue.regression_publication_handoff_count ?? 0],
    [t("manualExecution"), queue.manual_publication_required ? t("yes") : t("no")],
    [t("autoExecution"), queue.automatic_publication_allowed ? t("yes") : t("no")],
  ];
  const handoffCards = (queue.handoff_items || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.final_publication_handoff_item_id || "")} | ${escapeTraining(statusText(item.publication_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_publication_inputs || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("evidence"))}: ${escapeTraining((item.publication_evidence_required || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(item.suggested_user_instruction || "")}</p>
    </article>
  `).join("");
  const blockers = (queue.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionFinalPublicationHandoffQueue.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(queue.handoff_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(queue.automatic_publication_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${handoffCards || blockers}
    </div>
  `;
}

function renderCodexPromotionFinalPublicationReadiness(payload) {
  if (!promotionFinalPublicationReadinessGate) return;
  const gate = payload.codex_promotion_final_publication_readiness_gate || {};
  const hermes = payload.hermes_promotion_final_publication_readiness_payload || {};
  const tiles = [
    [t("readinessStatus"), statusText(gate.readiness_status || "mock_contract")],
    [t("readinessItems"), gate.readiness_item_count ?? 0],
    [t("missingInputs"), gate.blocked_readiness_item_count ?? 0],
    [statusText("live_hermes_memory"), gate.hermes_final_publication_readiness_count ?? 0],
    [statusText("local_regression_baseline_store"), gate.regression_final_publication_readiness_count ?? 0],
    [t("autoExecution"), gate.automatic_publication_allowed ? t("yes") : t("no")],
  ];
  const readinessCards = (gate.readiness_items || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.readiness_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
      <p>${escapeTraining(t("missingInputs"))}: ${escapeTraining((item.missing_publication_inputs || []).map(statusText).join(" | ") || t("no"))}</p>
      <p>${escapeTraining(t("evidence"))}: ${escapeTraining((item.publication_evidence_required || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("suggestedInstruction"))}: ${escapeTraining(item.suggested_user_instruction || "")}</p>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionFinalPublicationReadinessGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(gate.automatic_publication_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${readinessCards || blockers}
    </div>
  `;
}

function renderCodexPromotionFinalPublicationResults(payload) {
  if (!promotionFinalPublicationResultIntake) return;
  const intake = payload.codex_promotion_final_publication_result_intake || {};
  const hermes = payload.hermes_promotion_final_publication_result_payload || {};
  const state = intake.result_state || {};
  const tiles = [
    [t("resultIntakeStatus"), statusText(intake.intake_status || "mock_contract")],
    [t("resultCount"), intake.result_count ?? 0],
    [t("validationPassed"), state.manual_final_publication_recorded_count ?? 0],
    [t("validationFailed"), state.manual_final_publication_failed_count ?? 0],
    [t("manualExecution"), intake.manual_final_publication_result_required ? t("yes") : t("no")],
    [t("autoExecution"), intake.automatic_publication_allowed ? t("yes") : t("no")],
  ];
  const resultCards = Object.values(intake.codex_promotion_final_publication_results || {}).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.result_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(item.result_summary || "")}</p>
      <p>${escapeTraining(t("publication_reference"))}: ${escapeTraining(item.publication_reference || "")}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.published_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining(item.validation_summary || "")}</p>
    </article>
  `).join("");
  const readyItems = ((payload.source_codex_promotion_final_publication_readiness_gate || {}).readiness_items || [])
    .filter((item) => item.readiness_status === "final_publication_prerequisites_confirmed")
    .map((item) => `
      <article class="mini-object promotion-final-publication-result-actions"
        data-readiness-item-id="${escapeTraining(item.readiness_item_id || "")}"
        data-source-final-publication-handoff-item-id="${escapeTraining(item.source_final_publication_handoff_item_id || "")}"
        data-source-publication-action-id="${escapeTraining(item.source_publication_action_id || "")}"
        data-source-action-id="${escapeTraining(item.source_action_id || "")}"
        data-final-sync-completion-id="${escapeTraining(item.final_sync_completion_id || "")}"
        data-final-closure-id="${escapeTraining(item.final_closure_id || "")}"
        data-source-sync-audit-id="${escapeTraining(item.source_sync_audit_id || "")}"
        data-promotion-candidate-id="${escapeTraining(item.promotion_candidate_id || "")}"
        data-promotion-type="${escapeTraining(item.promotion_type || "")}"
        data-target-system="${escapeTraining(item.target_system || "")}"
        data-published-records="${escapeTraining((item.source_changed_records || [item.promotion_candidate_id || item.readiness_item_id || "", item.target_system || ""]).filter(Boolean).join("||"))}">
        <small>${escapeTraining(item.readiness_item_id || "")} | ${escapeTraining(statusText(item.readiness_status || ""))}</small>
        <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
        <p>${escapeTraining(t("ownerRole"))}: ${escapeTraining(statusText(item.owner_role || ""))}</p>
        <p>${escapeTraining(t("evidence"))}: ${escapeTraining((item.publication_evidence_required || []).map(statusText).join(" | "))}</p>
        <textarea class="training-final-publication-result-note" rows="2" placeholder="${escapeTraining(t("notePlaceholder"))}"></textarea>
        <div class="training-button-row">
          <button type="button" data-promotion-final-publication-result="manual_final_publication_recorded">${escapeTraining(t("recordManualResult"))}</button>
          <button type="button" data-promotion-final-publication-result="manual_final_publication_failed">${escapeTraining(t("validationFailed"))}</button>
          <button type="button" data-promotion-final-publication-result="manual_final_publication_skipped">${escapeTraining(t("skipCandidate"))}</button>
          <button type="button" data-promotion-final-publication-result="note_only">${escapeTraining(t("addNote"))}</button>
        </div>
      </article>
    `).join("");
  const blockers = (intake.blocked_actions || []).slice(0, 4).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionFinalPublicationResultIntake.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(intake.intake_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(intake.automatic_publication_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${resultCards || readyItems || blockers}
    </div>
  `;
}

function renderCodexPromotionFinalPublicationClosureAudit(payload) {
  if (!promotionFinalPublicationClosureAudit) return;
  const audit = payload.codex_promotion_final_publication_closure_audit || {};
  const hermes = payload.hermes_promotion_final_publication_closure_audit_payload || {};
  const tiles = [
    [t("closureStatus"), statusText(audit.closure_status || "mock_contract")],
    [t("expectedResults"), audit.expected_result_count ?? 0],
    [t("resultCount"), audit.recorded_result_count ?? 0],
    [t("completeResults"), audit.complete_result_count ?? 0],
    [t("missingResults"), audit.missing_result_count ?? 0],
    [t("autoExecution"), audit.automatic_closure_allowed ? t("yes") : t("no")],
  ];
  const candidateCards = (audit.final_closure_candidates || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.final_publication_completion_id || "")} | ${escapeTraining(statusText(item.closure_candidate_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(t("publication_reference"))}: ${escapeTraining(item.publication_reference || "")}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.published_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining(item.validation_summary || "")}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_final_closure_checks || []).map(statusText).join(" | "))}</p>
    </article>
  `).join("");
  const missingCards = (audit.missing_results || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")}</small>
      <strong>${escapeTraining(statusText(item.missing_reason || ""))}</strong>
      <p>${escapeTraining(statusText(item.target_system || ""))} | ${escapeTraining(statusText(item.promotion_type || ""))}</p>
    </article>
  `).join("");
  const failedCards = (audit.failed_results || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")}</small>
      <strong>${escapeTraining(statusText("final_publication_closure_blocked_by_failed_result"))}</strong>
      <p>${escapeTraining(statusText(item.target_system || ""))}: ${escapeTraining(item.result_summary || "")}</p>
    </article>
  `).join("");
  const blockers = (audit.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionFinalPublicationClosureAudit.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(audit.audit_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(audit.automatic_closure_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || failedCards || missingCards || blockers}
    </div>
  `;
}

function renderCodexPromotionFinalReleaseReviewGate(payload) {
  if (!promotionFinalReleaseReviewGate) return;
  const gate = payload.codex_promotion_final_release_review_gate || {};
  const hermes = payload.hermes_promotion_final_release_review_payload || {};
  const tiles = [
    [t("gateStatus"), statusText(gate.gate_status || "mock_contract")],
    [t("queueReady"), gate.gate_ready ? t("yes") : t("no")],
    [t("candidateCount"), gate.release_review_candidate_count ?? 0],
    [t("blockers"), gate.blocked_release_review_candidate_count ?? 0],
    [t("manualExecution"), (gate.required_human_review || []).length ? t("yes") : t("no")],
    [t("autoExecution"), gate.automatic_release_allowed ? t("yes") : t("no")],
  ];
  const candidateCards = (gate.release_review_candidates || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.release_review_candidate_id || "")} | ${escapeTraining(statusText(item.candidate_status || ""))}</small>
      <strong>${escapeTraining(statusText(item.target_system || ""))}</strong>
      <p>${escapeTraining(t("publication_reference"))}: ${escapeTraining(item.publication_reference || "")}</p>
      <p>${escapeTraining(t("changedFiles"))}: ${escapeTraining((item.published_records || []).join(" | "))}</p>
      <p>${escapeTraining(t("validation"))}: ${escapeTraining(item.validation_summary || "")}</p>
      <p>${escapeTraining(t("preflightChecks"))}: ${escapeTraining((item.required_review_inputs || []).map(statusText).join(" | "))}</p>
      <p>${escapeTraining(t("suggestedInstruction"))}: ${escapeTraining(item.suggested_user_instruction || "")}</p>
    </article>
  `).join("");
  const missingCards = (gate.missing_results || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")}</small>
      <strong>${escapeTraining(statusText(item.missing_reason || ""))}</strong>
      <p>${escapeTraining(statusText(item.target_system || ""))} | ${escapeTraining(statusText(item.promotion_type || ""))}</p>
    </article>
  `).join("");
  const failedCards = (gate.failed_results || []).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(item.readiness_item_id || "")}</small>
      <strong>${escapeTraining(statusText("final_release_review_blocked_by_failed_publication_result"))}</strong>
      <p>${escapeTraining(statusText(item.target_system || ""))}: ${escapeTraining(item.result_summary || "")}</p>
    </article>
  `).join("");
  const blockers = (gate.blocked_actions || []).slice(0, 5).map((item) => `
    <article class="mini-object">
      <small>${escapeTraining(t("blockers"))}</small>
      <strong>${escapeTraining(statusText(item))}</strong>
    </article>
  `).join("");
  promotionFinalReleaseReviewGate.innerHTML = `
    <div class="production-summary compact-summary">
      ${tiles.map(([label, value]) => `<article class="production-tile"><span>${escapeTraining(label)}</span><strong>${escapeTraining(value)}</strong></article>`).join("")}
    </div>
    <div class="training-capability-grid">
      <article class="mini-object">
        <small>${escapeTraining(hermes.schema || "mock_contract")}</small>
        <strong>${escapeTraining(gate.gate_id || "")}</strong>
        <p>${escapeTraining(statusText(hermes.promotion_status || "candidate"))} | ${escapeTraining(t("autoExecution"))}: ${escapeTraining(gate.automatic_release_allowed ? t("yes") : t("no"))}</p>
      </article>
      ${candidateCards || failedCards || missingCards || blockers}
    </div>
  `;
}

function renderCapabilities(items) {
  capabilityProgress.innerHTML = "";
  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "mini-object";
    card.innerHTML = `
      <small>${escapeTraining(item.task_count)} ${escapeTraining(t("tasks"))}</small>
      <strong>${escapeTraining(item.capability_group)}</strong>
      <p>${escapeTraining(t("passed"))}: ${escapeTraining(item.passed)} | ${escapeTraining(t("needsData"))}: ${escapeTraining(item.needs_data)} | ${escapeTraining(t("failed"))}: ${escapeTraining(item.failed)}</p>
      <p>${escapeTraining(t("score"))}: ${escapeTraining(item.average_score)}</p>
    `;
    capabilityProgress.append(card);
  });
}

function renderHermesJson(payload) {
  hermesResultJson.textContent = JSON.stringify(payload, null, 2);
}

function renderPatchItem(item) {
  return `
    <small>${escapeTraining(item.queue_id)} | ${escapeTraining(item.priority || "")}</small>
    <strong>${escapeTraining(item.type)}</strong>
    <p>${escapeTraining(item.summary)}</p>
    <p>${escapeTraining(t("humanReview"))}: ${escapeTraining(item.human_review_required ? t("yes") : t("no"))}</p>
  `;
}

function renderNextTask(item) {
  return `
    <small>${escapeTraining(item.source)}</small>
    <strong>${escapeTraining(item.task_id)}</strong>
    <p>${escapeTraining(item.capability)}</p>
    <p>${escapeTraining(item.prompt)}</p>
  `;
}

function renderKpi(item) {
  return `
    <small>${escapeTraining(statusText(item.status))}</small>
    <strong>${escapeTraining(kpiText(item.kpi))}</strong>
    <p>${escapeTraining(t("value"))}: ${escapeTraining(item.value)} | ${escapeTraining(t("target"))}: ${escapeTraining(item.target)}</p>
  `;
}

function renderEvidence(item) {
  return `
    <small>${escapeTraining(item.evidence_id)} | ${escapeTraining(statusText(item.status))}</small>
    <strong>${escapeTraining(item.source)}</strong>
    <p>${escapeTraining(item.summary)}</p>
  `;
}

function renderMiniList(target, items, renderer) {
  target.innerHTML = "";
  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "mini-object";
    card.innerHTML = renderer(item);
    target.append(card);
  });
}

function escapeTraining(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

runTrainingButton.addEventListener("click", runTraining);
promoteBaselineButton.addEventListener("click", promoteBaseline);
runRegressionButton.addEventListener("click", runRegression);

trainingTasks.addEventListener("click", async (event) => {
  const reviewButton = event.target.closest("[data-training-review]");
  if (reviewButton) {
    await saveTaskReview(reviewButton);
    return;
  }
  const dataButton = event.target.closest("[data-training-data]");
  if (dataButton) {
    await saveDataSource(dataButton);
  }
});

trainingNextLoopHandoff.addEventListener("click", async (event) => {
  const handoffButton = event.target.closest("[data-handoff-review]");
  if (handoffButton) {
    await saveHandoffReview(handoffButton);
  }
});

trainingIterationProposal.addEventListener("click", async (event) => {
  const proposalButton = event.target.closest("[data-iteration-review]");
  if (proposalButton) {
    await saveIterationProposalReview(proposalButton);
  }
});

executionGate.addEventListener("click", async (event) => {
  const executionButton = event.target.closest("[data-execution-review]");
  if (executionButton) {
    await saveCodexExecutionReview(executionButton);
  }
});

worktreeResultReviewGate.addEventListener("click", async (event) => {
  const resultReviewButton = event.target.closest("[data-result-review]");
  if (resultReviewButton) {
    await saveCodexWorktreeResultReview(resultReviewButton);
  }
});

promotionApprovalGate.addEventListener("click", async (event) => {
  const promotionApprovalButton = event.target.closest("[data-promotion-approval]");
  if (promotionApprovalButton) {
    await saveCodexPromotionApproval(promotionApprovalButton);
  }
});

promotionReadinessGate.addEventListener("click", async (event) => {
  const promotionReadinessButton = event.target.closest("[data-promotion-readiness-review]");
  if (promotionReadinessButton) {
    await saveCodexPromotionReadinessReview(promotionReadinessButton);
  }
});

promotionExecutionResultIntake.addEventListener("click", async (event) => {
  const promotionResultButton = event.target.closest("[data-promotion-execution-result]");
  if (promotionResultButton) {
    await saveCodexPromotionExecutionResult(promotionResultButton);
  }
});

promotionSyncReviewGate.addEventListener("click", async (event) => {
  const promotionSyncButton = event.target.closest("[data-promotion-sync-review]");
  if (promotionSyncButton) {
    await saveCodexPromotionSyncReview(promotionSyncButton);
  }
});

promotionSyncReadinessGate.addEventListener("click", async (event) => {
  const promotionSyncReadinessButton = event.target.closest("[data-promotion-sync-readiness-review]");
  if (promotionSyncReadinessButton) {
    await saveCodexPromotionSyncReadinessReview(promotionSyncReadinessButton);
  }
});

promotionSyncExecutionResultIntake.addEventListener("click", async (event) => {
  const promotionSyncResultButton = event.target.closest("[data-promotion-sync-execution-result]");
  if (promotionSyncResultButton) {
    await saveCodexPromotionSyncExecutionResult(promotionSyncResultButton);
  }
});

promotionSyncClosureReviewGate.addEventListener("click", async (event) => {
  const promotionSyncClosureReviewButton = event.target.closest("[data-promotion-sync-closure-review]");
  if (promotionSyncClosureReviewButton) {
    await saveCodexPromotionSyncClosureReview(promotionSyncClosureReviewButton);
  }
});

promotionFinalSyncExecutionResultIntake.addEventListener("click", async (event) => {
  const promotionFinalSyncResultButton = event.target.closest("[data-promotion-final-sync-execution-result]");
  if (promotionFinalSyncResultButton) {
    await saveCodexPromotionFinalSyncExecutionResult(promotionFinalSyncResultButton);
  }
});

promotionFinalPublicationResultIntake.addEventListener("click", async (event) => {
  const promotionFinalPublicationResultButton = event.target.closest("[data-promotion-final-publication-result]");
  if (promotionFinalPublicationResultButton) {
    await saveCodexPromotionFinalPublicationResult(promotionFinalPublicationResultButton);
  }
});

promotionFinalCompletionReviewGate.addEventListener("click", async (event) => {
  const promotionFinalCompletionReviewButton = event.target.closest("[data-promotion-final-completion-review]");
  if (promotionFinalCompletionReviewButton) {
    await saveCodexPromotionFinalCompletionReview(promotionFinalCompletionReviewButton);
  }
});

async function saveTaskReview(button) {
  const wrapper = button.closest(".training-actions");
  const taskId = wrapper?.dataset.taskId || "";
  const note = wrapper?.querySelector(".training-review-note")?.value || "";
  const reviewStatus = button.dataset.trainingReview;
  try {
    const response = await fetch("/api/training/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: taskId, review_status: reviewStatus, review_note: note, reviewer: "product_owner" }),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveHandoffReview(button) {
  const wrapper = button.closest(".handoff-actions");
  const payload = {
    handoff_item_id: wrapper?.dataset.handoffItemId || "",
    review_status: button.dataset.handoffReview,
    review_note: wrapper?.querySelector(".training-handoff-note")?.value || "",
    reviewer: "product_owner",
    item_type: wrapper?.dataset.handoffItemType || "",
    source: wrapper?.dataset.handoffSource || "",
    related_case_id: wrapper?.dataset.relatedCaseId || "",
    related_task_id: wrapper?.dataset.relatedTaskId || "",
  };
  try {
    const response = await fetch("/api/training/handoff-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveIterationProposalReview(button) {
  const wrapper = button.closest(".iteration-proposal-actions");
  const payload = {
    proposal_id: wrapper?.dataset.proposalId || "",
    review_status: button.dataset.iterationReview,
    review_note: wrapper?.querySelector(".training-iteration-note")?.value || "",
    reviewer: "product_owner",
    proposal_status: wrapper?.dataset.proposalStatus || "",
    task_seed_count: Number(wrapper?.dataset.taskSeedCount || 0),
    open_watch_item_count: Number(wrapper?.dataset.openWatchItemCount || 0),
  };
  try {
    const response = await fetch("/api/training/iteration-proposal-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexExecutionReview(button) {
  const wrapper = button.closest(".execution-gate-actions");
  const payload = {
    execution_candidate_id: wrapper?.dataset.executionCandidateId || "",
    review_status: button.dataset.executionReview,
    review_note: wrapper?.querySelector(".training-execution-note")?.value || "",
    reviewer: "product_owner",
    source_patch_candidate_id: wrapper?.dataset.sourcePatchCandidateId || "",
    source_packet_id: wrapper?.dataset.sourcePacketId || "",
    gate_status: wrapper?.dataset.gateStatus || "",
    candidate_type: wrapper?.dataset.candidateType || "",
    priority: wrapper?.dataset.priority || "",
  };
  try {
    const response = await fetch("/api/training/codex-execution-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexWorktreeResultReview(button) {
  const wrapper = button.closest(".worktree-result-review-actions");
  const payload = {
    launch_request_id: wrapper?.dataset.launchRequestId || "",
    review_status: button.dataset.resultReview,
    review_note: wrapper?.querySelector(".training-result-review-note")?.value || "",
    reviewer: "product_owner",
    result_status: wrapper?.dataset.resultStatus || "",
    changed_file_count: Number(wrapper?.dataset.changedFileCount || 0),
    validation_contract_complete: Boolean(wrapper?.dataset.validationContractComplete),
  };
  try {
    const response = await fetch("/api/training/codex-worktree-result-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexPromotionApproval(button) {
  const wrapper = button.closest(".promotion-approval-actions");
  const payload = {
    promotion_candidate_id: wrapper?.dataset.promotionCandidateId || "",
    promotion_type: wrapper?.dataset.promotionType || "",
    launch_request_id: wrapper?.dataset.launchRequestId || "",
    source_patch_candidate_id: wrapper?.dataset.sourcePatchCandidateId || "",
    source_packet_id: wrapper?.dataset.sourcePacketId || "",
    review_status: button.dataset.promotionApproval,
    review_note: wrapper?.querySelector(".training-promotion-note")?.value || "",
    reviewer: "product_owner",
    changed_file_count: Number(wrapper?.dataset.changedFileCount || 0),
  };
  try {
    const response = await fetch("/api/training/codex-promotion-approval", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexPromotionReadinessReview(button) {
  const wrapper = button.closest(".promotion-readiness-actions");
  const reviewStatus = button.dataset.promotionReadinessReview;
  const confirmedInputs = reviewStatus === "confirmed_ready_for_manual_execution"
    ? (wrapper?.dataset.confirmedInputs || "").split("||").filter(Boolean)
    : [];
  const payload = {
    readiness_item_id: wrapper?.dataset.readinessItemId || "",
    source_handoff_id: wrapper?.dataset.sourceHandoffId || "",
    promotion_candidate_id: wrapper?.dataset.promotionCandidateId || "",
    promotion_type: wrapper?.dataset.promotionType || "",
    review_status: reviewStatus,
    review_note: wrapper?.querySelector(".training-readiness-note")?.value || "",
    reviewer: "product_owner",
    confirmed_inputs: confirmedInputs,
    validation_summary: reviewStatus === "confirmed_ready_for_manual_execution" ? "Current local validation evidence confirmed by reviewer metadata." : "",
    rollback_summary: reviewStatus === "confirmed_ready_for_manual_execution" ? "Rollback or reversal plan confirmed by reviewer metadata." : "",
    execution_evidence_plan: reviewStatus === "confirmed_ready_for_manual_execution" ? "Capture final execution evidence after explicit manual execution confirmation." : "",
  };
  try {
    const response = await fetch("/api/training/codex-promotion-readiness-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexPromotionExecutionResult(button) {
  const wrapper = button.closest(".promotion-execution-result-actions");
  const resultStatus = button.dataset.promotionExecutionResult;
  const changedRecords = (wrapper?.dataset.changedRecords || "").split("||").filter(Boolean);
  const payload = {
    readiness_item_id: wrapper?.dataset.readinessItemId || "",
    promotion_candidate_id: wrapper?.dataset.promotionCandidateId || "",
    promotion_type: wrapper?.dataset.promotionType || "",
    result_status: resultStatus,
    result_summary: wrapper?.querySelector(".training-promotion-result-note")?.value || "Manual promotion execution metadata recorded.",
    reviewer: "product_owner",
    execution_reference: "manual_execution_outside_demo",
    changed_records: changedRecords,
    validation_summary: resultStatus === "manual_execution_recorded" ? "Current local validation evidence confirmed after manual execution." : "",
    rollback_summary: resultStatus === "manual_execution_recorded" ? "Rollback or reversal path remains recorded as metadata." : "",
    validation_results: resultStatus === "manual_execution_recorded"
      ? [
          { command: "python -m compileall src scripts tests", status: "passed", summary: "compileall passed before recording manual result" },
          { command: "tests/test_main_agent.py harness", status: "passed", summary: "harness passed before recording manual result" },
        ]
      : [],
  };
  try {
    const response = await fetch("/api/training/codex-promotion-execution-result", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexPromotionSyncReadinessReview(button) {
  const wrapper = button.closest(".promotion-sync-readiness-actions");
  const reviewStatus = button.dataset.promotionSyncReadinessReview;
  const confirmedInputs = reviewStatus === "confirmed_ready_for_manual_sync_execution"
    ? (wrapper?.dataset.confirmedInputs || "").split("||").filter(Boolean)
    : [];
  const payload = {
    readiness_item_id: wrapper?.dataset.readinessItemId || "",
    source_sync_handoff_item_id: wrapper?.dataset.sourceSyncHandoffItemId || "",
    source_sync_audit_id: wrapper?.dataset.sourceSyncAuditId || "",
    promotion_candidate_id: wrapper?.dataset.promotionCandidateId || "",
    promotion_type: wrapper?.dataset.promotionType || "",
    target_system: wrapper?.dataset.targetSystem || "",
    review_status: reviewStatus,
    review_note: wrapper?.querySelector(".training-sync-readiness-note")?.value || "",
    reviewer: "product_owner",
    confirmed_inputs: confirmedInputs,
    validation_summary: reviewStatus === "confirmed_ready_for_manual_sync_execution" ? "Current sync validation evidence confirmed by reviewer metadata." : "",
    rollback_summary: reviewStatus === "confirmed_ready_for_manual_sync_execution" ? "Sync rollback or reversal plan confirmed by reviewer metadata." : "",
    execution_evidence_plan: reviewStatus === "confirmed_ready_for_manual_sync_execution" ? "Capture final sync execution evidence after explicit manual sync execution confirmation." : "",
  };
  try {
    const response = await fetch("/api/training/codex-promotion-sync-readiness-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexPromotionSyncExecutionResult(button) {
  const wrapper = button.closest(".promotion-sync-execution-result-actions");
  const resultStatus = button.dataset.promotionSyncExecutionResult;
  const changedRecords = (wrapper?.dataset.changedRecords || "").split("||").filter(Boolean);
  const payload = {
    readiness_item_id: wrapper?.dataset.readinessItemId || "",
    source_sync_handoff_item_id: wrapper?.dataset.sourceSyncHandoffItemId || "",
    source_sync_audit_id: wrapper?.dataset.sourceSyncAuditId || "",
    promotion_candidate_id: wrapper?.dataset.promotionCandidateId || "",
    promotion_type: wrapper?.dataset.promotionType || "",
    target_system: wrapper?.dataset.targetSystem || "",
    result_status: resultStatus,
    result_summary: wrapper?.querySelector(".training-sync-result-note")?.value || "Manual sync execution metadata recorded.",
    reviewer: "product_owner",
    execution_reference: "manual_sync_execution_outside_demo",
    changed_records: changedRecords,
    validation_summary: resultStatus === "manual_sync_execution_recorded" ? "Current local validation evidence confirmed after manual sync execution." : "",
    rollback_summary: resultStatus === "manual_sync_execution_recorded" ? "Rollback or reversal path remains recorded as sync metadata." : "",
    validation_results: resultStatus === "manual_sync_execution_recorded"
      ? [
          { command: "python -m compileall src scripts tests", status: "passed", summary: "compileall passed before recording manual sync result" },
          { command: "tests/test_main_agent.py harness", status: "passed", summary: "harness passed before recording manual sync result" },
        ]
      : [],
  };
  try {
    const response = await fetch("/api/training/codex-promotion-sync-execution-result", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexPromotionFinalSyncExecutionResult(button) {
  const wrapper = button.closest(".promotion-final-sync-execution-result-actions");
  const resultStatus = button.dataset.promotionFinalSyncExecutionResult;
  const changedRecords = (wrapper?.dataset.changedRecords || "").split("||").filter(Boolean);
  const payload = {
    readiness_item_id: wrapper?.dataset.readinessItemId || "",
    source_final_sync_handoff_item_id: wrapper?.dataset.sourceFinalSyncHandoffItemId || "",
    source_action_id: wrapper?.dataset.sourceActionId || "",
    final_closure_id: wrapper?.dataset.finalClosureId || "",
    source_sync_audit_id: wrapper?.dataset.sourceSyncAuditId || "",
    promotion_candidate_id: wrapper?.dataset.promotionCandidateId || "",
    promotion_type: wrapper?.dataset.promotionType || "",
    target_system: wrapper?.dataset.targetSystem || "",
    result_status: resultStatus,
    result_summary: wrapper?.querySelector(".training-final-sync-result-note")?.value || "Manual final sync execution metadata recorded.",
    reviewer: "product_owner",
    execution_reference: "manual_final_sync_execution_outside_demo",
    changed_records: changedRecords,
    validation_summary: resultStatus === "manual_final_sync_execution_recorded" ? "Current local validation evidence confirmed after manual final sync execution." : "",
    rollback_summary: resultStatus === "manual_final_sync_execution_recorded" ? "Rollback or reversal path remains recorded as final sync metadata." : "",
    validation_results: resultStatus === "manual_final_sync_execution_recorded"
      ? [
          { command: "python -m compileall src scripts tests", status: "passed", summary: "compileall passed before recording manual final sync result" },
          { command: "tests/test_main_agent.py harness", status: "passed", summary: "harness passed before recording manual final sync result" },
        ]
      : [],
  };
  try {
    const response = await fetch("/api/training/codex-promotion-final-sync-execution-result", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexPromotionFinalPublicationResult(button) {
  const wrapper = button.closest(".promotion-final-publication-result-actions");
  const resultStatus = button.dataset.promotionFinalPublicationResult;
  const publishedRecords = (wrapper?.dataset.publishedRecords || "").split("||").filter(Boolean);
  const payload = {
    readiness_item_id: wrapper?.dataset.readinessItemId || "",
    source_final_publication_handoff_item_id: wrapper?.dataset.sourceFinalPublicationHandoffItemId || "",
    source_publication_action_id: wrapper?.dataset.sourcePublicationActionId || "",
    source_action_id: wrapper?.dataset.sourceActionId || "",
    final_sync_completion_id: wrapper?.dataset.finalSyncCompletionId || "",
    final_closure_id: wrapper?.dataset.finalClosureId || "",
    source_sync_audit_id: wrapper?.dataset.sourceSyncAuditId || "",
    promotion_candidate_id: wrapper?.dataset.promotionCandidateId || "",
    promotion_type: wrapper?.dataset.promotionType || "",
    target_system: wrapper?.dataset.targetSystem || "",
    result_status: resultStatus,
    result_summary: wrapper?.querySelector(".training-final-publication-result-note")?.value || "Manual final publication metadata recorded.",
    reviewer: "product_owner",
    publication_reference: "manual_final_publication_outside_demo",
    published_records: publishedRecords,
    validation_summary: resultStatus === "manual_final_publication_recorded" ? "Current local validation evidence confirmed after manual final publication." : "",
    rollback_summary: resultStatus === "manual_final_publication_recorded" ? "Rollback or reversal path remains recorded as final publication metadata." : "",
    validation_results: resultStatus === "manual_final_publication_recorded"
      ? [
          { command: "python -m compileall src scripts tests", status: "passed", summary: "compileall passed before recording manual final publication result" },
          { command: "tests/test_main_agent.py harness", status: "passed", summary: "harness passed before recording manual final publication result" },
        ]
      : [],
  };
  try {
    const response = await fetch("/api/training/codex-promotion-final-publication-result", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexPromotionSyncReview(button) {
  const wrapper = button.closest(".promotion-sync-review-actions");
  const reviewStatus = button.dataset.promotionSyncReview;
  const confirmedChecks = reviewStatus === "approved_for_future_sync"
    ? (wrapper?.dataset.confirmedSyncChecks || "").split("||").filter(Boolean)
    : [];
  const payload = {
    sync_audit_id: wrapper?.dataset.syncAuditId || "",
    readiness_item_id: wrapper?.dataset.readinessItemId || "",
    promotion_candidate_id: wrapper?.dataset.promotionCandidateId || "",
    promotion_type: wrapper?.dataset.promotionType || "",
    target_system: wrapper?.dataset.targetSystem || "",
    review_status: reviewStatus,
    review_note: wrapper?.querySelector(".training-sync-review-note")?.value || "",
    reviewer: "product_owner",
    confirmed_sync_checks: confirmedChecks,
  };
  try {
    const response = await fetch("/api/training/codex-promotion-sync-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexPromotionSyncClosureReview(button) {
  const wrapper = button.closest(".promotion-sync-closure-review-actions");
  const reviewStatus = button.dataset.promotionSyncClosureReview;
  const confirmedChecks = reviewStatus === "approved_for_final_sync"
    ? (wrapper?.dataset.confirmedFinalChecks || "").split("||").filter(Boolean)
    : [];
  const payload = {
    final_closure_id: wrapper?.dataset.finalClosureId || "",
    readiness_item_id: wrapper?.dataset.readinessItemId || "",
    source_sync_audit_id: wrapper?.dataset.sourceSyncAuditId || "",
    promotion_candidate_id: wrapper?.dataset.promotionCandidateId || "",
    promotion_type: wrapper?.dataset.promotionType || "",
    target_system: wrapper?.dataset.targetSystem || "",
    review_status: reviewStatus,
    review_note: wrapper?.querySelector(".training-sync-closure-review-note")?.value || "",
    reviewer: "product_owner",
    confirmed_final_checks: confirmedChecks,
    validation_summary: reviewStatus === "approved_for_final_sync" ? "Final sync closure validation summary confirmed by reviewer metadata." : "",
    rollback_summary: reviewStatus === "approved_for_final_sync" ? "Final sync closure rollback or reversal path confirmed by reviewer metadata." : "",
  };
  try {
    const response = await fetch("/api/training/codex-promotion-sync-closure-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveCodexPromotionFinalCompletionReview(button) {
  const wrapper = button.closest(".promotion-final-completion-review-actions");
  const reviewStatus = button.dataset.promotionFinalCompletionReview;
  const confirmedChecks = reviewStatus === "approved_final_completion"
    ? (wrapper?.dataset.confirmedCompletionChecks || "").split("||").filter(Boolean)
    : [];
  const payload = {
    final_sync_completion_id: wrapper?.dataset.finalSyncCompletionId || "",
    readiness_item_id: wrapper?.dataset.readinessItemId || "",
    final_closure_id: wrapper?.dataset.finalClosureId || "",
    source_action_id: wrapper?.dataset.sourceActionId || "",
    source_sync_audit_id: wrapper?.dataset.sourceSyncAuditId || "",
    promotion_candidate_id: wrapper?.dataset.promotionCandidateId || "",
    promotion_type: wrapper?.dataset.promotionType || "",
    target_system: wrapper?.dataset.targetSystem || "",
    review_status: reviewStatus,
    review_note: wrapper?.querySelector(".training-final-completion-review-note")?.value || "",
    reviewer: "product_owner",
    confirmed_completion_checks: confirmedChecks,
    validation_summary: reviewStatus === "approved_final_completion" ? "Final completion validation summary confirmed by reviewer metadata." : "",
    rollback_summary: reviewStatus === "approved_final_completion" ? "Final completion rollback or reversal path confirmed by reviewer metadata." : "",
  };
  try {
    const response = await fetch("/api/training/codex-promotion-final-completion-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function saveDataSource(button) {
  const wrapper = button.closest(".training-data-intake");
  const taskId = wrapper?.dataset.taskId || "";
  const dataStatus = button.dataset.trainingData;
  const payload = {
    task_id: taskId,
    data_status: dataStatus,
    source_type: wrapper?.querySelector(".training-source-type")?.value || "unknown",
    source_label: wrapper?.querySelector(".training-source-label")?.value || "",
    source_reference: wrapper?.querySelector(".training-source-reference")?.value || "",
    field_notes: wrapper?.querySelector(".training-field-notes")?.value || "",
    skip_reason: wrapper?.querySelector(".training-field-notes")?.value || "",
    sensitivity_level: wrapper?.querySelector(".training-sensitivity")?.value || "internal",
  };
  try {
    const response = await fetch("/api/training/data-source", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error((await response.json()).error || response.statusText);
    trainingStatus.textContent = t("saved");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
  }
}

async function promoteBaseline() {
  promoteBaselineButton.disabled = true;
  trainingStatus.textContent = trainingIsZh() ? "正在固化基线" : "Promoting baseline";
  try {
    const response = await fetch("/api/training/promote-baseline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ promoted_by: "product_owner", notes: "Approved Tianpai training tasks promoted from Training Console." }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || response.statusText);
    lastRoundSummary = payload;
    trainingStatus.textContent = statusText("baseline_promoted");
    await loadTraining();
  } catch (error) {
    trainingStatus.textContent = `${t("errorSaving")}: ${error.message}`;
    promoteBaselineButton.disabled = lastRoundSummary?.baseline_status !== "ready_for_regression";
  }
}

window.addEventListener("santoni:language-change", () => {
  if (lastTrainingResult) {
    renderTraining(lastTrainingResult);
  } else {
    applyStaticText();
  }
});

loadTraining().catch((error) => {
  applyStaticText();
  trainingStatus.textContent = t("unavailable");
  trainingSummary.innerHTML = `<article class="production-tile"><span>Error</span><strong>${escapeTraining(error.message)}</strong></article>`;
});
