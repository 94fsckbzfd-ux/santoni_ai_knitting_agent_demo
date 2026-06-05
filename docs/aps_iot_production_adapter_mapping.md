# APS / IOT Production Adapter Mapping

Version: `v0.24.1`

Date: 2026-06-05

This note records the read-only APS and Santoni IOT page research behind the Production Operations Console. It is an adapter contract reference only. It does not contain APS/IOT usernames, passwords, API keys, customer-sensitive data, or write-action instructions.

## Scope

The Production Operations Console maps real production-system concepts into normalized local objects for demo and future read-only adapters:

- `production_order`
- `yarn_material_forecast`
- `aps_schedule_capacity`
- `iot_machine_execution`
- `iot_program_evidence`
- `garment_quality_output`

The demo remains mock-backed. Future integrations should replace mock snapshots with formal read-only API responses behind the same normalized objects.

## APS Sources

APS is the planned source for the order and scheduling side of the console.

- `织造监控`: 订单号, 交期, 逾期天数, 款式数, 剩余数量, 订单总数, 进行中, 即将到期, 已逾期.
- `机器排产`: 机器视角, 订单视角, 机台号, 开始日期, 结束日期, 订单号, 款式号, 筒径, 针距, 机器排程时间轴.
- `机台汇总`: 机器规格数, 总机台数, 开机数, 开机率, 订单总量, 订单完成数, 订单剩余数, 单机生产天数.
- `自动排产`: 订单状态, 交期, 款式数, 总数量, 排产数量, 机器范围, 排程设置, 计算模式.
- `纱线预估`: SKU, 部位, 机器尺寸, 预测产量, 纱线代码, 批次, 供应商, 颜色, 需求量(KG), 库存量(KG), 在途量(KG).
- `机台计划单`: 机台号, 生产订单号, 款式号, 尺码, 部位, 计划生产件数, 已生产件数, 计划时间, 状态.
- `生产单`: 订单编号, 客户, 需求款式, 交付期限, 状态, 分配工厂.
- `款式管理`: 款式编号, 生产单号, 名称, 描述.
- `机器资料`: 机台号, 机器编号, 筒径, 针距, 针数, 型号, 状态.

## IOT Sources

Santoni IOT is the planned source for the execution, machine, program-evidence, and output side of the console.

- `实时监控`: 全部/运行/空转/停止/离线机器数, 班次实际产量, 班次理论产量, 时间开动率, 性能开动率, 当前状态, 当前告警.
- `仪表盘`: 运行, 空转, 停止, 离线, 班次生产件数, 时间开动率, 性能开动率, 成品率, 班次OEE, 停机时长统计.
- `数据分析`: 机台号, 序列号, 机器型号, 订单号, 款式号, 班次, 理论生产周期, 实际产量, 理论产量, 性能开动率, 实际生产时间, 实际停机时间, 时间开动率, 废弃数量, 成品率.
- `单机详情`: 订单号, 款式号, 订单目标件数, 订单完成件数, 订单废品件数, `.co` 文件, `.cx` 文件, 最近实际周期, 理论生产周期, 班次废弃件数, 班次不良品件数, 班次OEE, 协议版本, 最后一条数据更新时间, 最近故障事件.
- `程序接口`: future formal API documentation and interface request entry; prefer this route over browser scraping.
- `工厂资源`: 工厂, 车间, 分组, 机器类型, 机器型号, 筒径, 针距, 针数, 序列号, 协议版本, IP.

## Console Mapping

- `订单`: APS `织造监控`, `生产单`, `款式管理`, and `纱线预估`.
- `排单`: APS `机器排产`, `自动排产`, `机台汇总`, and `机台计划单`.
- `机器`: IOT `实时监控`, `仪表盘`, `单机详情`, plus APS `机器资料` for machine master data.
- `成衣`: IOT `数据分析` and `单机详情`, with future Smartex or quality-system fields reserved.

## Read-Only Boundary

The Production MVP must not:

- start APS auto-scheduling,
- confirm or modify schedules,
- upload `.co`, `.cx`, or related program files,
- release orders to machines,
- control machines,
- save IOT settings,
- create real service tickets,
- store APS/IOT credentials or tokens in project files.

The console may create local analysis objects, evidence logs, KPI logs, and service request candidates for human review.
