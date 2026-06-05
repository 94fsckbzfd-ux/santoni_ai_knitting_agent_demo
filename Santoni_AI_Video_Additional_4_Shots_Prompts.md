# Santoni AI Knitting Agent - Additional 4 Shots Prompts

目标：补齐老板 Word 分镜里现在版本还弱的四个点：

1. Circular vs Flat Knitting Decision
2. Digital Asset Protection + Collaboration
3. Manufacturing Agent + APS Factory Selection
4. Agent-driven Organization

Seedance / 即梦没有单独 Negative Prompt 时，把每条 prompt 末尾的 `Do not show...` 也放进主 prompt。

## 0. 现有素材选择

### A. SWS / 软件界面截图

优先使用这些，能看到 garment / pattern / machine-ready file：

- `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\SWS Demo Video Keyframes\SWS_060s_04_create_machine_ready_file.jpg`
- `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\SWS Demo Video Keyframes\SWS_435s_24_flat_pattern_export_view.jpg`
- `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\SWS Demo Video Keyframes\SWS_480s_26_pattern_layout_and_avatar_preview.jpg`

备选：

- `SWS_045s_03_3d_result_knit_structure.jpg`
- `SWS_285s_17_update_stitch_simulation.jpg`
- `SWS_525s_28_3d_stitch_simulation_closeup.jpg`

### B. 成衣 / 3D Garment 图

优先使用：

- `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\finished seamless sports garment.png`
- `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\SWS Demo Video Keyframes\SWS_090s_06_avatar_front_fit_preview.jpg`
- `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\SWS Demo Video Keyframes\SWS_210s_13_engineered_jacquard_garment_front.jpg`

### C. 供应商 / 设计师 / 工程师协作办公场景

现有可用：

- `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\textile design desk.jpg`
- `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\Santoni offline showing room.jpg`

如果你能补素材，最值得补一张：多人会议桌，包含电脑屏幕、面料样本、纱线、工程图纸，人物最好像 supplier / designer / engineer 在一起讨论。

### D. 已生成的图形素材

我已生成并保存到素材文件夹：

- `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\Santoni_AI_Agent_Architecture_Diagram.png`
- `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\Santoni_Agent_KPI_Responsibility_Workflow.png`

## Shot A - Circular vs Flat Knitting Decision

插入位置：放在 `Shot02-Production-aware AI Interface` 之后，`Machine Feasibility` 之前。它负责把“AI 生成方案”转成“选择正确工艺路线”。

上传素材：

- @Image1：`SWS_060s_04_create_machine_ready_file.jpg`
- @Image2：`SWS_480s_26_pattern_layout_and_avatar_preview.jpg` 或 `SWS_045s_03_3d_result_knit_structure.jpg`
- @Image3：`finished seamless sports garment.png` 或 `SWS_090s_06_avatar_front_fit_preview.jpg`
- @Image4：你准备的 flat knitting machine 照片或视频，若没有就先不传
- @Video1：`Seamless production video.mp4`，作为 Santoni circular seamless machine 参考

Prompt:

```text
Use @Image1 and @Image2 as the real SWS software reference, @Image3 as the garment reference, @Image4 as the flat knitting machine reference if available, and @Video1 as the Santoni seamless circular knitting machine reference. Create a 6-second 16:9 realistic B2B textile technology shot. On a professional SWS-style workstation, a seamless sportswear design is evaluated against two manufacturing paths: circular seamless knitting and flat knitting. The interface should show two clean abstract option panels without readable text. The circular seamless knitting option becomes selected, and the garment subtly adapts to the machine capability: seamless tube construction, feeder constraints, gauge, stitch length, and yarn tension. Transition visually from the software decision to the real Santoni circular knitting machine in the background. Style: credible enterprise textile CAD and real industrial workflow, not sci-fi. Do not show readable UI text, fake holograms, sewing machines, woven looms, wrong machine output, distorted hands, or a garment growing from the machine exterior.
```

旁边文字：

```text
The Agent chooses the right knitting path for production.
```

## Shot B - Digital Asset Protection + Collaboration

插入位置：放在 `Shot05-Digital Asset To Manufacturing` 之前或之后都可以。若想更接近老板原稿，建议放在 `Shot05` 之前：先保护并分享数字资产，再进入制造计划。

上传素材：

- @Image1：`SWS_465s_25_sws_brand_and_cylo_integration.jpg`
- @Image2：`SWS_555s_30_share_with_qr_code.jpg`
- @Image3：`textile design desk.jpg` 或你准备的多人协作办公照片
- @Image4：`SWS_480s_26_pattern_layout_and_avatar_preview.jpg`
- @Image5：Santoni / SWS / CYLO 官方 logo，建议仅作参考，最终文字和 logo 后期添加

Prompt:

```text
Use @Image1 as the SWS and platform integration reference, @Image2 as the collaboration and sharing reference, @Image3 as the real textile office collaboration reference, and @Image4 as the pattern and avatar preview reference. Create a 7-second 16:9 realistic B2B software collaboration shot. A seamless knitwear product becomes a protected digital asset inside a professional SWS-style platform. The asset contains design intent, garment pattern, material choices, machine recipe, costing assumptions, and production permissions. A designer, supplier, and engineer collaborate around the same asset while ownership and access rights remain controlled. Show clean abstract permission layers, role-based sharing, and secure handoff, but no readable text. The atmosphere should feel premium, practical, and trustworthy, like real enterprise textile software. Do not show blockchain cliches, floating sci-fi holograms, fake readable text, misspelled logos, distorted hands, or generic startup dashboard visuals.
```

旁边文字：

```text
The product becomes shareable, but protected.
```

## Shot C - Manufacturing Agent + APS Factory Selection

插入位置：放在 `Business Value Shot` 后面、`Shot05-Digital Asset To Manufacturing` 前面，或直接替换部分 Business Value Shot。它负责补老板原稿里的 Manufacturing Agent、global machine network、APS。

上传素材：

- @Image1：`factory planning 1.jpg`，多台 Santoni 机器 / 产能环境
- @Image2：`factory planning 2.jpg`，纱线和机台细节
- @Image3：`Santoni_Agent_KPI_Responsibility_Workflow.png`
- @Image4：`SWS_060s_04_create_machine_ready_file.jpg` 或 `SWS_480s_26_pattern_layout_and_avatar_preview.jpg`
- @Image5：你准备的真实 APS / 排产系统截图，若没有可不传

Prompt:

```text
Use @Image1 and @Image2 as the real Santoni factory and capacity reference, @Image3 as the agent workflow reference, @Image4 as the SWS digital asset reference, and @Image5 as the APS scheduling reference if available. Create a 7-second 16:9 realistic B2B manufacturing intelligence shot. A Manufacturing Agent receives a production-ready knitwear asset and compares multiple factory and machine options using a clean APS-style planning interface. The visual should suggest cost, lead time, capacity, machine availability, yarn readiness, and delivery scenarios through abstract blocks and timeline bars without readable text. Transition from software planning to a real Santoni machine room with multiple seamless circular knitting machines and yarn feeders. The feeling is practical industrial planning, not fantasy automation. Do not show unreadable fake text, sci-fi holograms, robots taking over the factory, impossible machine layouts, wrong textile machines, or conveyor-belt garment output.
```

旁边文字：

```text
The Manufacturing Agent matches design with cost, capacity, and delivery.
```

## Shot D - Agent-driven Organization

插入位置：放在 `Quality Feedback Loop` 后面、`Customer Loop` 前面；如果视频太长，也可以放在 end card 前作为 4-5 秒的“ecosystem”过渡。

上传素材：

- @Image1：`Santoni_AI_Agent_Architecture_Diagram.png`
- @Image2：`Santoni_Agent_KPI_Responsibility_Workflow.png`
- @Image3：`textile design desk.jpg` 或真实团队办公照片
- @Image4：`SWS_555s_30_share_with_qr_code.jpg`，协作分享参考，可选

Prompt:

```text
Use @Image1 as the AI agent architecture reference, @Image2 as the KPI and responsibility workflow reference, @Image3 as the real work environment reference, and @Image4 as the collaboration platform reference if available. Create a 6-second 16:9 realistic B2B enterprise technology shot. A traditional organization chart transforms into a network of specialized AI agents: Designer Agent, Material Agent, Machine Agent, Manufacturing Agent, Quality Agent, Service Agent, Sales Agent, and Customer Loop Agent. Each agent is shown as a clean professional node connected to real workflow responsibilities and KPIs, while employees continue working in a textile office and factory environment. The visual should feel like a credible enterprise operating system, not a sci-fi command center. Use subtle motion graphics, restrained colors, and no readable small text. Do not show fantasy holograms, random glowing circles, fake charts, distorted faces, or misspelled words.
```

旁边文字：

```text
The organization becomes a network of specialized agents.
```

## Recommended Insert Order

如果只补这四个镜头，建议插入到 13 段剪辑里：

1. Problem Shot
2. Shot00 - Opening
3. Shot02 - Production-aware AI Interface
4. Shot A - Circular vs Flat Knitting Decision
5. Decision Moment Shot
6. Shot03 - Material Intelligence
7. Shot04 - Machine Feasibility
8. Shot01 - Santoni Machine Know-how
9. Shot07 / Business Value
10. Shot C - Manufacturing Agent + APS Factory Selection
11. Shot B - Digital Asset Protection + Collaboration
12. Shot05 - Digital Asset To Manufacturing
13. Shot06 - Quality Feedback Loop
14. Shot D - Agent-driven Organization
15. Shot08 - Customer Loop
16. Shot09 - End Card

如果要控制在 90 秒以内，优先补 Shot A、Shot C、Shot B；Shot D 可以缩短成 4 秒或放进 end card 前的过渡。
