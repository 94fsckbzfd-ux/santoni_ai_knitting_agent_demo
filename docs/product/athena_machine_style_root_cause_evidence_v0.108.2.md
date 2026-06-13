# Santoni Athena Machine Style Root Cause Evidence v0.108.2

Date: 2026-06-12

## Summary

Athena v0.108.2 improves machine/style mismatch evidence. A mismatch is no longer explained only as "cylinder_diameter mismatch" or "needle_spacing mismatch". Athena now includes the required style parameter, the actual machine parameter, and the table fields that produced the comparison.

## Judgment Rule

Athena compares:

- `Style_Component.cylinder_diameter` against `T_Machine_Info.f_cylinder_diameter`.
- `Style_Component.needle_spacing` against `T_Machine_Info.f_needle_spacing`.

The comparison is only made when both sides are available after no-header CSV parsing by the `表字段` DDL order and deleted-row filtering.

## Evidence Example

For task `238`:

- Planned task: `Planned_Task.id=238`.
- Machine: `C7-U12`.
- Required cylinder diameter: `18` from `Style_Component.cylinder_diameter`.
- Actual machine cylinder diameter: `17寸` from `T_Machine_Info.f_cylinder_diameter`.
- Root-cause statement: task `238` has a machine/style spec mismatch because the style requires cylinder diameter `18`, but machine `C7-U12` has cylinder diameter `17寸`.

For task `272`:

- Planned task: `Planned_Task.id=272`.
- Machine: `D7-N26`.
- Required cylinder diameter: `14` from `Style_Component.cylinder_diameter`.
- Actual machine cylinder diameter: `11寸` from `T_Machine_Info.f_cylinder_diameter`.

## Data Gap Example

Task `239` is active, but Athena does not currently mark it as a mismatch after the v0.108.1 deleted-row and active evidence guard because the active `Style_Component` lookup for `produce_order_code + sku_code + part` does not return a comparable component row. Athena should not claim a mismatch unless it has both required and actual values.

## Still Read-Only

Athena does not write APS, ERP, IOT, or Hermes. It does not change schedules, upload `.co` / `.cx`, dispatch Service, control machines, or correct customer data.

## Next Validation

Ask APS / engineering owners to confirm:

- Whether `Style_Component.cylinder_diameter` and `T_Machine_Info.f_cylinder_diameter` use the same unit and value convention.
- Whether `Style_Component.needle_spacing` and `T_Machine_Info.f_needle_spacing` use the same gauge convention.
- Whether allowed substitutions exist, such as using a nearby cylinder size under engineering approval.
