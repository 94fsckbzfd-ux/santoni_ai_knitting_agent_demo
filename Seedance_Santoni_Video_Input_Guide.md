# Seedance 输入清单：Santoni AI Knitting Agent 宣传视频

## 0. 为什么 Seedance 版本要改 prompt

Seedance 比 Gemini 更适合用“参考素材驱动”：

- 用真实机台/面料/工厂图锁定 realism。
- 用 UI mockup 锁定软件界面方向。
- 用真实生产视频锁定 machine geometry 和 machine motion。
- 用真实生产视频抽出的关键帧补充锁定 needle area、side suction pipe 和 green collection basket。
- prompt 要更短、更像导演指令，不要写太多抽象商业文案。

建议工作方式：

1. 每条生成 6 到 10 秒。
2. 每条只讲一个动作，不要一个 prompt 里塞完整故事。
3. 每条都上传 2 到 5 个 reference assets。
4. 文字、logo、字幕后期加，不让 Seedance 直接生成可读文字。
5. 官网可上传视频时，优先上传真实生产视频作为 `@Video1`；同时上传关键帧作为 `@Image1`、`@Image2`、`@Image3`。如果某个入口不能传视频，再退回 image-only 版本。

## 1. 参考素材准备

### 现有可用素材

Santoni logo:

`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\src\web_app\santoni-logo.png`

现有 AI UI 概念图：

`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\ai_video_docx_media\image2.png`

现有机台概念图，临时用，不建议最终版依赖：

`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\ai_video_docx_media\image3.png`

现有 demo 中可临时当作 UI/构图参考的帧：

`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\gemini_reference_frames\draft_short\draft_short_024s.jpg`

`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\gemini_reference_frames\draft_short\draft_short_032s.jpg`

`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\gemini_reference_frames\draft_short\draft_short_072s.jpg`

SWS 真实软件演示关键帧，优先替换上面这些临时 UI / demo 帧：

素材文件夹：
`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\AI Video materials\SWS Demo Video Keyframes`

最适合用于新视频生成的 SWS 关键帧：

- `SWS_015s_01_new_project_from_template.jpg`：项目创建 / product brief 入口
- `SWS_030s_02_pattern_gallery_selection.jpg`：Pattern Gallery / 版型选择
- `SWS_045s_03_3d_result_knit_structure.jpg`：3D result / 针织结构结果
- `SWS_060s_04_create_machine_ready_file.jpg`：create machine-ready file / 机器文件输出
- `SWS_090s_06_avatar_front_fit_preview.jpg`：avatar 正面试穿预览
- `SWS_120s_08_physical_simulation_front_avatar.jpg`：物理仿真 + avatar
- `SWS_150s_10_surface_tension_heatmap.jpg`：surface tension / fit heatmap
- `SWS_165s_11_3d_measuring_santoni_texture.jpg`：3D measuring + Santoni 针织纹理
- `SWS_210s_13_engineered_jacquard_garment_front.jpg`：工程化 jacquard 成衣预览
- `SWS_270s_16_color_palette_material_selection.jpg`：颜色 / 材料选择
- `SWS_285s_17_update_stitch_simulation.jpg`：stitch simulation 更新
- `SWS_375s_21_write_text_prompt_ai_panel.jpg`：AI text prompt 面板
- `SWS_390s_22_ai_draping_result_frog_pattern.jpg`：AI draping result
- `SWS_405s_23_stitch_simulation_result_frog_pattern.jpg`：stitch simulation result
- `SWS_435s_24_flat_pattern_export_view.jpg`：flat pattern / export view
- `SWS_465s_25_sws_brand_and_cylo_integration.jpg`：SWS + CYLO 集成画面
- `SWS_480s_26_pattern_layout_and_avatar_preview.jpg`：pattern layout + avatar preview
- `SWS_525s_28_3d_stitch_simulation_closeup.jpg`：3D stitch simulation close-up
- `SWS_555s_30_share_with_qr_code.jpg`：QR code / 协作分享

替换原则：

- 所有软件界面、3D 仿真、数字资产、pattern / stitch / avatar 相关镜头，优先用 SWS 关键帧替换 `image2.png` 和 `draft_short_*.jpg`。
- 机台生产、针区运动、负压管出料、绿色收集篮相关镜头，继续以 `Seamless production video.mp4` 和 `seq_0080.jpg` / `seq_0120.jpg` / `seq_0180.jpg` 为主参考。
- SWS 帧里有文字和 logo，生成时只用它锁定真实软件质感和界面构图；prompt 里仍然要求 `no readable text`，最终字幕和品牌字建议后期加。

真实无缝机生产视频，优先作为 Seedance 的 `@Video1` 上传：

`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\Seamless production video.mp4`

这个视频应该作为所有机台生产镜头的主参考，用来锁定真实机台结构和运动。它明确了真实画面：蓝白色无缝圆机、前方控制屏和急停按钮、透明防护罩、上方纱筒和导纱系统、左侧绿色收集篮、机旁透明弯管/负压管。绿色物体是收集篮，不是正在编织的布料。

从真实视频抽出的可用辅助参考帧：

`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\seamless_production_reference\sequential\seq_0080.jpg`

`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\seamless_production_reference\sequential\seq_0120.jpg`

`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\seamless_production_reference\sequential\seq_0180.jpg`

### 强烈建议补拍/补找的真实素材

这些素材比 prompt 更重要，会直接决定“真实感”：

1. Santoni seamless circular knitting machine 正面/45 度角照片。
2. 机台细节：needle、feeder、yarn path、take-down、control panel。
3. 真实运行中的机台短视频，或从视频抽出的关键帧。
4. Yarn cones 和 fabric swatches：mesh、terry、rib、jacquard、plating。
5. 工程师/操作员检查样衣、调机、看控制屏的照片。
6. 工厂环境：纱架、机台排布、质检台、样衣桌。
7. 如果能拍到，补一张“机旁负压出料管 / 外部收集篮”的照片或短视频。这一点很关键：无缝机器完成成衣后，会由负压抽到机旁管道，再排到外面的篮子里，而不是在编织过程中从机器外壳直接长出来。

如果只能先用现有素材，也可以生成测试版，但真实机台素材一补上，质量会明显上一个台阶。

## 2. 无缝机台输出规则

这一段可以直接加在所有涉及机台生产和出料的 prompt 后面。它用于纠正 AI 对机器输出方式的误解：

```text
Important machine accuracy: on a Santoni seamless circular knitting machine, the garment is not visible outside during knitting. During operation, the exterior view should show yarn cones, yarn feeders, needles, control panel, and machine motion, but no finished garment growing or emerging from the machine exterior. After one garment is completed, a pneumatic vacuum suction system pulls the finished knitted tube or garment through a side suction pipe next to the machine and ejects it into an external collection basket. If the finished result must be shown, show this post-completion vacuum tube transfer into the basket, or show the sample already placed on a quality inspection table.
```

更短版，额度紧张时用：

```text
Machine accuracy: during knitting, no garment is visible outside. After completion, the finished knitted item is pulled by pneumatic vacuum through a side suction pipe next to the machine and ejected into an external collection basket.
```

基于真实视频和抽帧的更强约束：

```text
Use the real production reference video and images exactly for machine geometry and motion: blue-and-white Santoni seamless circular knitting machine, front control panel and emergency button, transparent safety guard, overhead yarn cones and yarn guides, green external collection basket on the left, clear curved pneumatic suction pipe beside the machine. The green object is a collection basket, not fabric. Do not invent a conveyor belt or show a garment growing from the machine exterior.
```

## 3. Seedance 主 Prompt 末尾约束

Seedance 没有独立 Negative Prompt 输入框，所以不要单独写 negative prompt。把下面这段作为正向禁止句，直接放在每条主 prompt 的最后：

```text
Do not show sci-fi holograms, fantasy machines, sewing machines, woven looms, robots, conveyor belt output, unreadable text, distorted hands, plastic-looking fabric, or a shirt growing from the machine exterior. Do not turn the green collection basket into fabric. Keep the machine geometry consistent with the reference images.
```

机台镜头额外加这一句：

```text
During knitting, no finished garment is visible outside. Only after completion, the finished knitted item is pulled by pneumatic vacuum through the clear side suction pipe and ejected into the green external collection basket.
```

## 4. 第一轮建议先生成 6 条

先不要做 16 条。用 6 条建立质感，再扩展。

生成顺序建议：

1. Santoni machine know-how
2. Production-aware AI interface
3. Material intelligence
4. Machine feasibility
5. Digital asset to manufacturing
6. Quality feedback loop

如果这 6 条质感对了，再补 opening、customer loop、organization agent。

## 5. Seedance Prompt 模板

如果你的 Seedance 界面支持引用名，比如 `@Video1`、`@Image1`、`@Image2`，就用这个格式。如果界面不是这个写法，把 `@Video1` 理解成“上传的真实生产参考视频”，把 `@Image1` 理解成“第一张上传图”即可。

通用结构：

```text
Use @Video1 as the motion and machine geometry reference when available. Use @Image1 as the visual reference for [subject]. Use @Image2 as the reference for [environment/style]. Create a [duration]-second 16:9 realistic B2B industrial commercial shot. [Subject action]. Camera: [movement]. Lighting: [lighting]. Style: realistic premium textile industry documentary, no readable text. End with direct constraints: Do not show [wrong elements].
```

## 6. Shot-by-shot 输入

### Shot 00 - Opening: Product Brief Enters The Agent

用途：作为整片开场。现在的 Shot 01 直接进入机器，技术可信度很强，但缺少客户需求入口。这个镜头用来说明“一切从产品需求开始”。

上传素材：

- @Image1：`SWS_375s_21_write_text_prompt_ai_panel.jpg` 或 `SWS_015s_01_new_project_from_template.jpg`，真实 SWS prompt / project entry 软件界面
- @Image2：yarn cones / fabric swatches / design desk
- @Image3：`SWS_030s_02_pattern_gallery_selection.jpg` 或 Santoni logo，可选

Prompt:

```text
Use @Image1 as the real SWS software interface reference, @Image2 as the textile design desk reference, and @Image3 as the pattern gallery or subtle brand identity reference if available. Create a 6-second 16:9 realistic B2B commercial opening shot. A sportswear product manager or designer types a new product brief into a professional AI platform on a laptop or large monitor. On the desk are real yarn cones, knitted fabric swatches, measurement tools, and machine engineering notes. The camera slowly moves from the tactile yarn and fabric samples to the SWS-style software interface. The screen should follow the reference layout and professional CAD/PLM feeling, but show clean abstract UI blocks, not readable text. The tone is calm, precise, premium, and industrially credible. Do not show sci-fi holograms, fantasy UI, unreadable fake text, distorted hands, or plastic-looking fabric.
```

后期字幕：

```text
It starts with a product idea.
```

### Shot 01 - Santoni Machine Know-how

用途：先解决“不够真实”。这是整条片最重要的镜头。

上传素材：

- @Video1：`Seamless production video.mp4`，真实机台运动和结构主参考
- @Image1：`seq_0080.jpg`，整机正面 + 绿色收集篮
- @Image2：`seq_0120.jpg`，针区/内部工作区域
- @Image3：`seq_0180.jpg`，透明弯管/负压出料管 + 绿色收集篮
- @Image4：`seq_0000.jpg` 或 `seq_0040.jpg`，上方纱筒 + 导纱系统，可选
- 临时替代：`image3.png`

Prompt:

```text
Use @Video1 as the primary reference for machine motion and real geometry. Use @Image1 for the full machine layout, @Image2 for the needle working area, @Image3 for the side suction pipe and green collection basket, and @Image4 for overhead yarn cones if available. Create an 8-second 16:9 realistic industrial commercial shot of the same type of Santoni seamless circular knitting machine. Preserve the real geometry from the reference video and images: blue-and-white machine body, front control panel and emergency button, transparent safety guard, overhead yarn cones and yarn guides, green external collection basket on the left, clear curved pneumatic suction pipe beside the machine. Start with a macro view of needles and yarn movement, then slowly pull back to the real machine front. During knitting, no finished garment is visible outside. If output is shown at the end, show the completed knitted item being pulled by pneumatic vacuum through the side suction pipe and ejected into the green external collection basket. The green object is a collection basket, not fabric. Real metal, real yarn, real factory lighting. Do not show sci-fi holograms, fantasy machines, sewing machines, woven looms, robots, conveyor belt output, unreadable text, distorted hands, plastic-looking fabric, or a shirt growing from the machine exterior. Do not turn the green collection basket into fabric. Keep the machine geometry consistent with the reference video and images.
```

后期字幕：

```text
Santoni know-how becomes digital intelligence
```

### Shot 02 - Production-aware AI Interface

用途：把“AI 生成图片”改成“AI 生成可生产决策”。

上传素材：

- @Image1：`SWS_045s_03_3d_result_knit_structure.jpg`，真实 SWS 3D / knit structure 软件界面
- @Image2：`SWS_090s_06_avatar_front_fit_preview.jpg` 或 `SWS_120s_08_physical_simulation_front_avatar.jpg`，avatar fit preview
- @Image3：`SWS_150s_10_surface_tension_heatmap.jpg` 或 `SWS_525s_28_3d_stitch_simulation_closeup.jpg`，surface tension / stitch simulation
- @Image4：`SWS_210s_13_engineered_jacquard_garment_front.jpg`，工程化成衣预览，可选

Prompt:

```text
Use @Image1 as the real SWS 3D knit structure software reference, @Image2 as the avatar fit preview reference, @Image3 as the simulation or stitch structure reference, and @Image4 as the engineered garment reference if available. Create an 8-second 16:9 realistic B2B software commercial shot. On a professional workstation monitor, multiple seamless sports top variations appear side by side inside an SWS-style CAD/PLM interface. Each variation is connected to clean abstract manufacturing indicators: yarn, knit structure, machine compatibility, cost range, and lead time. A designer adjusts one parameter and the garment updates smoothly, showing mesh ventilation zones, terry absorption zones, rib support zones, surface tension, and seamless construction. The UI should feel like professional textile engineering software, not hologram fantasy. No readable text. Do not show sci-fi holograms, random glowing UI, distorted hands, unreadable text, or plastic-looking fabric.
```

后期字幕：

```text
Every variation is checked against production reality
```

### Shot 03 - Material Intelligence

用途：体现 Santoni 不只是软件，而是理解材料和结构。

上传素材：

- @Image1：真实 yarn cones
- @Image2：mesh / terry / rib swatches
- @Image3：材料实验室或设计桌
- @Image4：`SWS_270s_16_color_palette_material_selection.jpg`，颜色 / 材料选择软件参考，可选
- @Image5：`SWS_525s_28_3d_stitch_simulation_closeup.jpg`，stitch simulation close-up，可选

Prompt:

```text
Use @Image1 as the yarn reference, @Image2 as the fabric structure reference, @Image3 as the environment reference, and @Image4 or @Image5 as the SWS-style material and stitch simulation software reference if uploaded. Create an 8-second 16:9 realistic textile lab commercial shot. A textile expert picks up a yarn cone and compares it with mesh, terry, and rib knit samples on a clean worktable. The camera moves from macro yarn fibers to a hand touching knitted fabric, then to a professional material dashboard in the background with abstract charts for performance, cost, availability, and lead time. Make the fabric tactile and physically real, while the background software feels like real textile CAD/simulation instead of generic dashboards. Neutral industrial lighting with small Santoni red accents. No readable text. Do not show fake neon lab visuals, plastic-looking fabric, generic fashion moodboards, or distorted hands.
```

后期字幕：

```text
Yarn choices shape performance, cost, and speed
```

### Shot 04 - Machine Feasibility

用途：把 gauge、feeders、stitch length、tension 这些工程判断放进去。

上传素材：

- @Image1：真实 Santoni machine
- @Image2：control panel / machine screen / operator
- @Image3：`SWS_060s_04_create_machine_ready_file.jpg` 或 `SWS_285s_17_update_stitch_simulation.jpg`，machine-ready file / stitch simulation 软件参考
- @Video1：`Seamless production video.mp4`，真实机台运动和布局参考
- @Image4：`seq_0080.jpg`，真实机台布局参考，可选
- @Image5：`seq_0180.jpg`，负压管和绿色收集篮参考，可选

Prompt:

```text
Use @Video1 as the primary reference for real machine motion and layout. Use @Image1 as the machine reference, @Image2 as the operator and control panel reference, @Image3 as the real SWS machine-ready file or stitch simulation software reference, @Image4 as the full machine layout reference, and @Image5 as the side suction pipe reference if available. Create an 8-second 16:9 realistic industrial workflow shot. A Santoni engineer reviews a digital twin of a seamless sports top on a workstation beside a real seamless circular knitting machine. The SWS-style system checks gauge, feeders, stitch length, yarn tension, and size feasibility using clean abstract status indicators. The engineer confirms the settings, and the machine begins a short sample run. Camera cuts from the digital garment to the front control panel, then to yarn feeding into the needle area. Preserve the real machine layout from the reference video and images: blue-and-white body, transparent guard, overhead yarn cones, green collection basket, clear curved side suction pipe. During knitting, no finished garment is visible outside. After completion, if the sample result is shown, pneumatic vacuum pulls the knitted item through the side suction pipe and ejects it into the green external basket, or the sample is already on the inspection table. No readable text, no fantasy UI. Do not show sci-fi holograms, wrong machine types, sewing machines, woven looms, robots, or a shirt growing from the machine side.
```

后期字幕：

```text
Checked against real machine capability
```

### Shot 05 - Digital Asset To Manufacturing

用途：讲 protected digital asset + manufacturing agent。

上传素材：

- @Image1：`SWS_060s_04_create_machine_ready_file.jpg`，machine-ready file 软件参考
- @Image2：`SWS_435s_24_flat_pattern_export_view.jpg` 或 `SWS_480s_26_pattern_layout_and_avatar_preview.jpg`，flat pattern / pattern layout 软件参考
- @Video1：`Seamless production video.mp4`，真实机台运动和布局参考
- @Image3：`seq_0080.jpg` 或真实 factory / machine line
- @Image4：`seq_0180.jpg`，负压管和绿色收集篮参考，可选
- @Image5：Santoni logo，可选，建议后期添加而不是让 Seedance 生成

Prompt:

```text
Use @Image1 as the real SWS machine-ready file reference, @Image2 as the flat pattern or pattern layout reference, @Video1 as the machine motion and layout reference, @Image3 as the factory/machine reference, @Image4 as the suction pipe and basket reference if available, and @Image5 only as brand identity reference if uploaded. Create an 8-second 16:9 premium B2B commercial shot. A digital knitwear asset is packaged into protected layers: design intent, structure map, material data, machine recipe, costing, and production permissions, shown as clean abstract layers with no readable text. The asset connects to a manufacturing planning screen and then transitions into a real seamless machine preparing for production. Show yarn cones, front control panel, transparent safety guard, green external collection basket, clear side suction pipe, and operator checking parameters. Do not show garments directly growing out from the exterior side of the machine during knitting. If output is shown, use the realistic post-completion pneumatic suction pipe transfer into the green basket. The visual should feel secure, collaborative, and industrially credible. Do not show misspelled logos, fake holograms, fantasy factories, unreadable text, overdramatic neon, or fake conveyor output.
```

后期字幕：

```text
From digital asset to manufacturing plan
```

### Shot 06 - Quality Feedback Loop

用途：让价值闭环，而不是停在“生成视频好看”。

上传素材：

- @Video1：`Seamless production video.mp4`，真实机台运动和负压出料主参考
- @Image1：`seq_0180.jpg`，负压管 + 绿色收集篮
- @Image2：`seq_0080.jpg`，整机正面 + 收集篮
- @Image3：garment quality inspection / measurement
- @Image4：knitted garment sample

Prompt:

```text
Use @Video1 as the primary reference for real machine motion and pneumatic output behavior. Use @Image1 as the reference for the side suction pipe and green collection basket, @Image2 as the full machine layout reference, @Image3 as the quality inspection reference, and @Image4 as the garment reference. Create an 8-second 16:9 realistic textile factory commercial shot. A blue-and-white Santoni seamless circular knitting machine runs with yarn cones, feeders, needles, transparent safety guard, side suction pipe, green external collection basket, and front control panel visible. During knitting, no garment is visible outside. After one garment is completed, pneumatic vacuum pulls the knitted tube or garment sample through the clear curved side suction pipe next to the machine and ejects it into the green external collection basket. An operator takes the sample from the basket and places it on a quality control table. A scanner or measuring system evaluates stitch consistency, size tolerance, tension variation, and fabric defects with subtle abstract overlays. Documentary camera movement, real operators, real yarn, real knitted fabric, bright clean factory lighting. No readable text. Do not show robots, sci-fi command centers, wrong textile machinery, plastic-looking fabric, distorted hands, a finished shirt growing from the machine exterior, or conveyor belt output.
```

后期字幕：

```text
Quality data improves the next decision
```

### Shot 07 - Business Optimization: Cost, Lead Time, Capacity

用途：补齐商业价值。Shot 01-06 已经讲清楚技术和生产，但还需要让 CEO/客户看到为什么它能减少试错、缩短报价和排产周期。

上传素材：

- @Image1：`SWS_285s_17_update_stitch_simulation.jpg` 或 `SWS_270s_16_color_palette_material_selection.jpg`，真实 SWS 工程 / 材料决策界面
- @Image2：`SWS_210s_13_engineered_jacquard_garment_front.jpg` 或真实样衣
- @Image3：真实 fabric swatches / yarn cones
- @Image4：`SWS_480s_26_pattern_layout_and_avatar_preview.jpg` 或 factory planning / machine photo，可选

Prompt:

```text
Use @Image1 as the real SWS engineering or material decision interface reference, @Image2 as the engineered garment reference, @Image3 as the material reference, and @Image4 as the pattern layout or manufacturing reference if available. Create a 7-second 16:9 realistic B2B commercial shot. A product development dashboard shows a seamless knitted garment beside clean abstract business indicators for yarn usage, machine time, sample iterations, cost range, capacity, and delivery scenarios. A product manager and a factory planner compare two production options before sampling begins. The environment should feel like a professional textile planning office with real yarn and fabric samples on the desk. Use restrained SWS-style engineering UI graphics, no readable text. Do not show sci-fi holograms, fantasy dashboards, unreadable fake text, distorted hands, or plastic-looking garments.
```

后期字幕：

```text
See cost, timing, and production risk before sampling begins.
```

### Shot 08 - Customer Loop: From Use Back To Better Design

用途：作为结尾前的情绪镜头，把“生产完成”拉回客户价值和反馈闭环。没有这个镜头，整片会停在工厂端，商业片缺少最终体验。

上传素材：

- @Image1：finished seamless sports garment / athlete wearing garment
- @Image2：`SWS_555s_30_share_with_qr_code.jpg` 或 `SWS_480s_26_pattern_layout_and_avatar_preview.jpg`，协作分享 / feedback dashboard 软件参考
- @Image3：fabric detail / texture swatch
- @Image4：`SWS_405s_23_stitch_simulation_result_frog_pattern.jpg`，stitch simulation result，可选

Prompt:

```text
Use @Image1 as the finished garment and user reference, @Image2 as the real SWS collaboration or feedback platform reference, @Image3 as the textile texture reference, and @Image4 as the stitch simulation result reference if uploaded. Create a 7-second 16:9 premium commercial shot. An athlete or model wears a seamless knitted performance top during light movement in a clean studio or training environment. The garment shows realistic stretch, ventilation zones, and soft textile texture. Cut or transition visually to a professional SWS-style AI platform where user feedback becomes updated design and structure data. The mood should be refined, human, and credible, connecting real product use back to better design decisions. Do not show fashion runway fantasy, unrealistic fabric physics, plastic-looking garment, unreadable fake text, or exaggerated sci-fi overlays.
```

后期字幕：

```text
Real use becomes the next design decision.
```

### Shot 09 - Closing Brand End Card

用途：最后 3 到 5 秒收束品牌和一句话定位。这个镜头建议不要用 Seedance 生成，最好后期直接做静态或轻微动效，避免 logo 或文字变形。

素材：

- Santoni logo: `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\src\web_app\santoni-logo.png`
- 背景可以用 Shot 01 或 Shot 06 的一帧轻微虚化

后期画面建议：

```text
Santoni AI Knitting Agent
From prompt to production-ready knitwear.
```

如果必须用 Seedance 生成背景，不要让它生成文字，只生成干净背景：

```text
Create a 5-second 16:9 clean premium industrial closing background for a B2B textile technology commercial. Use a softly defocused real Santoni seamless knitting machine and yarn cones in the background, with calm white and grey factory lighting and subtle Santoni red accent. Leave clean empty space in the center for logo and tagline to be added later in editing. Do not generate any text, logo, or readable letters.
```

## 7. 如果你想做 60 秒版，剪辑顺序

推荐剪辑顺序：

1. Shot 00 - Opening：产品经理输入需求，桌上有 yarn 和 swatches。
2. Shot 02 - Production-aware AI Interface：AI 生成设计方案，但同步显示结构、机台、成本、交期。
3. Shot 03 - Material Intelligence：纱线和面料结构选择。
4. Shot 04 - Machine Feasibility：工程师检查 gauge、feeders、tension、stitch length。
5. Shot 01 - Santoni Machine Know-how：真实机台、needle、feeder、yarn path。
6. Shot 07 - Business Optimization：成本、交期和产能可见。
7. Shot 05 - Digital Asset To Manufacturing：数字资产进入制造计划。
8. Shot 06 - Quality Feedback Loop：生产、检测、反馈。
9. Shot 08 - Customer Loop：真实使用反馈回到下一次设计。
10. Shot 09 - Closing：Santoni AI Knitting Agent。

## 8. 60 秒中文旁白

```text
一切从一个产品需求开始。

但在针织行业里，不是每一个创意都能变成产品。

纱线、结构、gauge、feeders、版型、成本、交期和机台能力，每一个决定都会影响最终结果。

Santoni AI Knitting Agent 把这些判断放进同一个智能流程。

它理解趋势，也理解针织工程。

一个透气需求，会变成具体的 mesh structure。
一个吸湿需求，会变成 terry zone 的布局。
一个版型调整，会变成可执行的 knitting recipe。

设计师更快探索，工程师更早验证，品牌在打样之前就能看到成本、交期和生产风险。

产品成为受保护的数字资产，在品牌、供应商和工厂之间协同。

生产和质量数据回到系统，持续优化下一次决策。

这不是用 AI 替代经验。
而是让 Santoni 的 know-how 可以被连接、放大和复用。

Santoni AI Knitting Agent。
```

## 9. 60 秒英文旁白

```text
It starts with a product idea.

But in knitwear, not every idea can become a product.

Yarn, structure, gauge, feeders, fit, cost, lead time, and machine capability all shape the final result.

Santoni AI Knitting Agent brings these decisions into one intelligent workflow.

It understands trends, but it also understands textile engineering.

A breathability requirement becomes a mesh structure.
A moisture requirement becomes terry zone placement.
A fit adjustment becomes an executable knitting recipe.

Designers explore faster. Engineers validate earlier. Brands see cost, timing, and production risk before sampling begins.

The product becomes a protected digital asset, shared across brands, suppliers, and factories.

Production and quality data return to the system, improving the next decision.

This is not AI replacing expertise.
This is Santoni know-how becoming connected, scalable, and reusable.

Santoni AI Knitting Agent.
```

## 10. Seedance 调参建议

如果有模式选择：

- 优先用 Pro / Quality 生成关键镜头：Shot 01、Shot 04、Shot 06。
- Fast 只用于测试构图和动作。
- 如果入口支持上传视频参考，机台镜头优先上传 `Seamless production video.mp4` 作为 reference video。
- 同时上传 `seq_0080.jpg`、`seq_0120.jpg`、`seq_0180.jpg` 作为补充图片，防止模型改错机台结构。
- 如果某个入口不支持视频参考，再使用 image-only：`seq_0080.jpg` + `seq_0120.jpg` + `seq_0180.jpg`。
- 软件和数字流程镜头优先上传 SWS 关键帧，不再优先用 `image2.png` 或 `draft_short_*.jpg`。最重要的组合是：Shot 00 用 `SWS_375s` / `SWS_015s`，Shot 02 用 `SWS_045s` + `SWS_090s` + `SWS_150s`，Shot 04 / 05 用 `SWS_060s`，Shot 07 用 `SWS_285s` / `SWS_270s`，Shot 08 用 `SWS_555s`。
- 有 start/end frame 时，start 用真实机台或 UI，end 用稍微变化后的同一场景，不要跨场景太大。
- 如果生成画面太科幻，把 prompt 里的 `abstract overlay` 改成 `almost no overlay`。
- 如果生成机器不对，减少 UI 描述，增加 machine reference，并在 prompt 里写 `not a sewing machine, not a woven loom, not an embroidery machine`。
- 如果它又把成衣从机器外壳直接“长出来”，在 prompt 最前面加：`Critical machine accuracy: during knitting, no garment is visible outside. After completion, pneumatic vacuum pulls the finished knitted item through a side suction pipe next to the machine and ejects it into an external collection basket.`

## 11. 最小可行测试

如果今天只想快速验证，先生成这 3 条：

1. Shot 01 - Santoni Machine Know-how
2. Shot 02 - Production-aware AI Interface
3. Shot 06 - Quality Feedback Loop

这三条能判断 Seedance 是否能把“真实机台 + AI 平台 + 质量闭环”做出来。
