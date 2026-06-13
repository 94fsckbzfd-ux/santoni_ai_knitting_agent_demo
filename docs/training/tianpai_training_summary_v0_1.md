# Tianpai Athena Training Summary v0.1

Created: 2026-06-08

This document summarizes fragmented Tianpai VOC screenshots and Melos-provided IOT exports into a first Athena/Hermes training baseline.

## Source Files

- `Agnes VOC Tianpai 1.png`
- `Agnes VOC Tianpai 2.png`
- `Agnes VOC Tianpai 3.png`
- `产量统计.xlsx`
- `废品统计.xlsx`
- `故障分析.xlsx`
- Conversation fragment: current APS-side Tianpai workflow / scheduling-data note
- Conversation fragment: confirmed Tianpai actual onsite workflow

Raw files are stored under:

```text
C:/Users/rem_i/OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd/文档/Product/AI Knitting Agent/Athena Training
```

## Tianpai Actual Onsite Workflow

The latest workflow note refines the earlier APS-side fragment and should be treated as the current confirmed Tianpai onsite workflow logic.

After order intake, Tianpai enters the order into ERP. ERP tracks total order quantity and split deliveries, then divides work such as weaving and sewing. APS only handles scheduling for Tianpai's weaving portion. IOT currently does not participate in the actual production workflow.

Athena should learn the production flow as:

```text
order intake
-> ERP order entry / total quantity / split deliveries / work split
-> APS weaving scheduling
-> yarn picking
-> weaving greige
-> pre-treatment, such as spreading/stretching and stepping/pressing greige
-> storage before dyeing
-> dyeing scheduling and dyeing
-> inspection, with replenishment order if failed
-> cutting
-> sewing
-> packing
-> needle inspection and metal detection
-> packing
-> finished goods storage
-> container loading
```

This matters because Athena must not use the generic demo assumption that APS flows into IOT execution for Tianpai. Current IOT exports can still train machine-data analysis, scrap ranking, downtime review, and fault ranking, but they are not evidence of IOT participating in Tianpai's live production process.

This workflow note is now complemented by a metadata-only APS Planned Task delivery-time attachment with 127 rows. The attachment includes `produce_order_code`, machine, style, quantity, plan/actual/estimate timing, status, and `delivery_time`, so it can support APS schedule and delivery-time field coverage review. It still cannot prove APS-to-IOT order execution root cause until the `produce_order_code` / `order_id` join rule is confirmed, and downstream bottlenecks still need stage-level records for each physical production step.

## Material Inventory Summary

The Tianpai yarn inventory export is now registered as metadata-only material evidence. Raw Excel rows are not stored in the repository; Athena uses an aggregate snapshot in `src/mock_data/production_operations.mock.json`.

- Rows: 8,146
- Production task orders: 1,134
- Yarn codes: 128
- Batches: 392
- Suppliers: 67
- Unit: kg
- Zero balance rows: 968
- Negative balance rows: 4,055

This can train material structure, batch/supplier/color/twist distribution, balance-exception review, and data-readiness behavior. It cannot yet prove order-level yarn shortage or delivery impact because ERP/APS `produce_order_code` mapping and BOM yarn demand are not confirmed. Negative balance must be treated as a warehouse/ERP interpretation question, not automatically as a shortage.

## Business VOC

Agnes's Tianpai VOC gives a clear management priority:

1. **Delivery / 交期 is P0.**
   The Tianpai general manager mainly cares about delivery date. Many other concerns exist, but they ultimately connect back to delivery.

2. **Quality is P1.**
   Quality matters, but Agnes believes many quality issues come from sewing and dyeing. Basic knitting quality is already handled in normal workflow.

3. **Cost is useful but not currently supported by IOT alone.**
   Real-time average material and labor cost per garment would be valuable, but current purchasing/labor cost reports are likely post-order and difficult to produce.

4. **Late delivery has logistics-cost consequences.**
   If sea shipment becomes risky, Tianpai may switch to air shipment. Agnes mentioned sea shipment to the US may take about 45 days, air shipment about 7 days, and a US east-coast container may be around USD 8,000 while air freight may become much more expensive.

5. **Digital adoption must be practical.**
   Tianpai may not have enough development, maintenance, or system-adoption capacity to put everything online immediately. Athena should not require full digitalization before creating value.

## IOT Data Summary

### Production Output

- Rows: 2,118
- Machines: 123
- Styles: 224
- Model: TOP2S only in this export
- Record time range: 2026-05-12 05:35:35 to 2026-06-24 10:38:21
- Actual output: 69,492 pieces
- Theoretical output: 131,196 pieces
- Scrap quantity: 10,599
- Downtime: 30,960,473 seconds
- Order ID missing rate: 100%
- Serial missing rate: 100%

### Scrap Statistics

- Rows: 5,217
- Machines: 79
- Styles: 172
- Record time range: 2026-06-01 00:00:39 to 2026-06-05 17:31:24
- Converted scrap total: 3,355.19 pieces

Top converted-scrap machines:

- `7C-V04`: 103.08
- `7C-R03`: 90.97
- `7C-F05`: 87.79
- `7C-B05`: 84.26
- `7C-G03`: 77.58

Top converted-scrap styles:

- `2UH3572-01`: 179.32
- `RM3061A-01`: 162.79
- `9322L-01`: 136.52
- `RA3061A-01`: 106.87
- `SB25011-01`: 99.05

### Fault Analysis

- Rows: 11,389
- Machines: 119
- Styles: 199
- Fault codes: 229
- Fault duration total: 2,793,663 seconds

Top fault codes by duration:

- `11109001`: Fabric pipe monitoring, no fabric detected
- `11137018`: Path 2 needle break self-stop
- `11133027`: BTSR feeder stop
- `111713020`: 传感器 20 采样失败
- `11137019`: Path 6 needle break self-stop

Top machines by fault duration:

- `7C-K02`
- `7C-L06`
- `7C-Q03`
- `7C-L05`
- `7C-K06`

## Data Quality Limits

Athena must not overclaim from this dataset.

## Training Governance

Current training governance confirmed by user:

- First training persona: Tianpai general manager.
- Answer format: management summary + reason/evidence + recommended action.
- Recommendation scope: Athena may propose weaving-process recommendations for now. Recommendations outside weaving should be framed as data needs or items requiring confirmation. Future ERP-backed expansion requires human confirmation.
- KPI priority: delivery > quality > cost.
- KPI relationship: poor quality may reduce repeat orders; long delivery may trigger air freight or other cost increases, so both quality and delivery can affect cost.
- Data insufficiency: Athena is allowed and expected to say when data is insufficient, then name the missing data.
- Terminology format: use `standard_field_name (site_term)`, for example `pre_treatment (撑白坯 / 踩白坯)` and `needle_and_metal_detection (验针 / 金属检测)`.
- Automation boundary: small fixes can proceed automatically; large feature changes, new pages, real data integration, feature-version changes, and major-version changes require user confirmation.
- Acceptance standard: no fixed pass/fail standard yet. Standards will be discovered through repeated training tasks and evaluation JSON.

Current allowed training:

- Machine-level monitoring
- Style-level scrap ranking
- Shift/machine downtime analysis
- Fault-code ranking
- Order-mainline workflow understanding
- ERP / APS / IOT boundary understanding
- Physical process-stage mapping
- Material inventory structure and balance-readiness review
- Data-gap explanation
- General-manager VOC alignment

Blocked until more data:

- Full order-to-garment analysis by `order_id`
- Delivery-risk root cause by order
- Order-level material shortage claims without ERP/APS `produce_order_code` mapping and BOM yarn demand
- APS-to-IOT schedule execution comparison because IOT currently does not participate in Tianpai's production flow
- APS schedule variance root cause without detailed schedule rows
- Downstream bottleneck analysis after weaving without stage-level records
- Real-time per-garment cost calculation
- Material/labor root cause
- Full-factory KPI if not all machines are connected

## Recommended Training Tasks

1. **TPI-GM-DELIVERY-001**
   Ask Athena what Tianpai's general manager cares about most.
   Expected answer: delivery first, quality second, cost as future data-dependent capability.

2. **TPI-IOT-DATA-GAP-001**
   Ask Athena why current data cannot support full order-level root cause.
   Expected answer: IOT production output has no usable `order_id`.

3. **TPI-IOT-DOWNTIME-001**
   Ask Athena which machines have the highest downtime.
   Expected answer: rank machines by downtime and avoid claiming delivery impact without order linkage.

4. **TPI-IOT-SCRAP-001**
   Ask Athena which machines and styles have the highest converted scrap.
   Expected answer: rank machine and style data with evidence.

5. **TPI-IOT-FAULT-001**
   Ask Athena which fault types most affect the site.
   Expected answer: rank fault codes by duration, separate widespread issues from one-machine issues, and avoid claiming a confirmed root cause before accepted service evidence exists.

6. **TPI-GM-COST-001**
   Ask Athena whether it can calculate real-time per-garment cost now.
   Expected answer: no; purchasing, material, labor, and order data are required.

7. **TPI-APS-WORKFLOW-001**
   Ask Athena how to use the APS Planned Task delivery-time attachment when the APS-to-IOT join rule is not confirmed yet.
   Expected answer: map the workflow sequence, use the attachment for APS schedule/delivery-time field coverage, and avoid claiming full APS-to-IOT order root cause until `produce_order_code` mapping is confirmed.

8. **TPI-WORKFLOW-BOUNDARY-001**
   Ask Athena how ERP, APS, and IOT participate in Tianpai's production process.
   Expected answer: ERP records orders and work split; APS only schedules weaving; IOT currently does not participate in the live production workflow.

9. **TPI-PROCESS-STAGES-001**
   Ask Athena to list Tianpai's physical production stages from yarn picking to container loading.
   Expected answer: separate physical stages from IT systems, and ask for timestamp, quantity, WIP, hold, defect, and rework fields before root-cause analysis.

10. **TPI-MATERIAL-RISK-001**
    Ask Athena whether yarn inventory alone can identify which orders will be delayed by material shortage.
    Expected answer: it can describe material structure and balance review signals, but order-level shortage and delivery impact require ERP/APS mapping and BOM yarn demand.

11. **TPI-DATA-READINESS-001**
    Ask Athena which general-manager questions can be answered before ERP and direct general-manager VOC are available.
    Expected answer: classify questions as answerable, partial, or blocked; keep the question bank as hypothesis until reviewed; name the next data owner.

## Next Data Requests

To move from machine/style training to real Tianpai order-flow training, request:

- Detailed APS weaving schedule export for the same date window
- Tianpai onsite workflow document covering ERP order entry/work split, APS weaving scheduling, and every physical production stage
- Stage-level production records for each process step
- Machine master table
- Order-machine-style-shift join rule
- Quality inspection / garment output table
- Material and labor cost data if ROI/cost training is required
- General manager review questions and desired answer style

The structured JSON version is:

```text
docs/training/tianpai_training_pack_v0_1.json
```
