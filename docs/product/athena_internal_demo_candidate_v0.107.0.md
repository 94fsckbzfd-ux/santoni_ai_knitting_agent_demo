# Santoni Athena Internal Demo Candidate v0.107.0

Date: 2026-06-11

## Summary

Athena v0.107.0 is an internal demo candidate for the General Manager production decision workflow. It is not a live production deployment and should not be presented as real-time APS/IOT/ERP control.

The current demo can show how Athena helps a General Manager answer: "What should I watch first today?" It turns structured production evidence into top-priority risk cards, verification drilldowns, Service confirmation candidates, local follow-up items, and Hermes-style training/memory candidates.

## Demoable Now

- User page General Manager entry with today's top-three risk cards.
- Stable story shortcuts that send questions into the original chat stream.
- Production Console guided demo flow.
- Presenter mode with recommended narration and test questions.
- Evidence boundary layer separating `actual_export`, `mock_contract`, `hybrid`, and `data_gap`.
- GM question regression set for delivery, machine/style, Service, material, data gap, and today's priorities.
- Data Request Wizard for ERP, IOT, quality, labor, cost, and shipping fields.
- Service Risk Confirmation Flow that asks maintenance-confirmation questions without dispatching.
- Visible Athena Skill Process in manager language.
- Local Hermes training/memory candidates with review and promotion status.

## Actual APS/ERP Evidence

Current actual-export evidence can support internal demo stories around:

- Delivery and schedule risk from `Produce_Order`, `Weaving_Part_Order`, `Planned_Task`, and `Manual_Machine_Production`.
- Machine/style fit from `Style_Component` and `T_Machine_Info`.
- APS/ERP source-field visibility and evidence refs in risk cards and drilldowns.

This evidence is file-export based, not live database/API evidence.

## Mock Or Hybrid Parts

- IOT machine live status, alarm duration, and OEE are still mock or future adapter contract.
- Service risk and Service ticket impact are local candidates, not real service tickets.
- Quality, labor effective-hour history, shipment, freight, rework, purchasing, and per-garment cost are not complete.
- The service-impact story is hybrid: actual order/schedule context plus mock IOT/Service signal.

## Cannot Claim

- Athena does not write APS, ERP, IOT, or Hermes.
- Athena does not change schedules, release orders, upload `.co` / `.cx`, control machines, dispatch Service, or create real tickets.
- Athena does not prove final root cause without missing IOT, quality, labor, cost, and downstream workflow data.
- Athena does not replace General Manager or production-owner confirmation.

## Recommended Demo Path

1. Open `/` and choose `总经理`.
2. Show today's top-three priorities and Service/equipment risk.
3. Click a stable story shortcut or risk card to ask Athena for drilldown in the original chat stream.
4. Show the verification process: checked objects, finding, evidence level, cannot conclude, and suggested owner.
5. Generate a local follow-up candidate.
6. Open `/production.html` for presenter mode, evidence boundary, data requests, and Hermes candidates.

## Recommended Test Questions

- 今天先看哪三件事？
- 哪个订单最可能影响交付？证据是什么？
- 有没有机台和款式规格不匹配的风险？
- 这台机如果继续停机会影响哪个订单？
- 物料数据现在能支持什么判断？还缺什么？
- 目前哪些结论不能说死？

## Data Gaps

- Live IOT status, alarms, downtime, and order-to-machine joins.
- Quality defects and replenishment closure by order/stage.
- Labor effective hours and historical baseline.
- Cost, rework, freight, and purchasing records.
- Customer-validated General Manager VOC and acceptance thresholds.
- Formal APS/IOT API or database access policy.

## Next Real Data Needs

- ERP order, split-delivery, status, and customer/style fields.
- APS planned task and machine schedule data with stable order key.
- IOT machine running status, alarm code, downtime, and order linkage.
- Quality inspection and defect reason data by order/stage.
- Labor effective-hour history by shift/team/machine.
- Shipping/cost records only after sensitivity and access rules are approved.

## v1.0.0 Recommendation

Do not move to v1.0.0 yet. Athena is ready for internal demo candidate review, but v1.0.0 should wait until at least one real read-only integration path, customer-validated GM workflow, and a stable evidence/permission governance model are confirmed.
