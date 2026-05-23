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

- @Image1：AI platform UI mockup，`image2.png` 或 `draft_short_032s.jpg`
- @Image2：finished seamless sports garment，`draft_short_024s.jpg`
- @Image3：真实 fabric swatches / mesh / terry / rib

Prompt:

```text
Use @Image1 as the UI style reference, @Image2 as the garment reference, and @Image3 as the textile structure reference. Create an 8-second 16:9 realistic B2B software commercial shot. On a professional workstation monitor, multiple seamless sports top variations appear side by side. Each variation is connected to clean abstract manufacturing indicators: yarn, knit structure, machine compatibility, cost range, and lead time. A designer adjusts one parameter and the garment updates smoothly, showing mesh ventilation zones, terry absorption zones, rib support zones, and seamless construction. The UI should feel like professional CAD and PLM software, not hologram fantasy. No readable text. Do not show sci-fi holograms, random glowing UI, distorted hands, unreadable text, or plastic-looking fabric.
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

Prompt:

```text
Use @Image1 as the yarn reference, @Image2 as the fabric structure reference, and @Image3 as the environment reference. Create an 8-second 16:9 realistic textile lab commercial shot. A textile expert picks up a yarn cone and compares it with mesh, terry, and rib knit samples on a clean worktable. The camera moves from macro yarn fibers to a hand touching knitted fabric, then to a professional material dashboard in the background with abstract charts for performance, cost, availability, and lead time. Make the fabric tactile and physically real. Neutral industrial lighting with small Santoni red accents. No readable text. Do not show fake neon lab visuals, plastic-looking fabric, generic fashion moodboards, or distorted hands.
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
- @Image3：3D garment or AI UI reference
- @Video1：`Seamless production video.mp4`，真实机台运动和布局参考
- @Image4：`seq_0080.jpg`，真实机台布局参考，可选
- @Image5：`seq_0180.jpg`，负压管和绿色收集篮参考，可选

Prompt:

```text
Use @Video1 as the primary reference for real machine motion and layout. Use @Image1 as the machine reference, @Image2 as the operator and control panel reference, @Image3 as the digital garment reference, @Image4 as the full machine layout reference, and @Image5 as the side suction pipe reference if available. Create an 8-second 16:9 realistic industrial workflow shot. A Santoni engineer reviews a digital twin of a seamless sports top on a workstation beside a real seamless circular knitting machine. The system checks gauge, feeders, stitch length, yarn tension, and size feasibility using clean abstract status indicators. The engineer confirms the settings, and the machine begins a short sample run. Camera cuts from the digital garment to the front control panel, then to yarn feeding into the needle area. Preserve the real machine layout from the reference video and images: blue-and-white body, transparent guard, overhead yarn cones, green collection basket, clear curved side suction pipe. During knitting, no finished garment is visible outside. After completion, if the sample result is shown, pneumatic vacuum pulls the knitted item through the side suction pipe and ejects it into the green external basket, or the sample is already on the inspection table. No readable text, no fantasy UI. Do not show sci-fi holograms, wrong machine types, sewing machines, woven looms, robots, or a shirt growing from the machine side.
```

后期字幕：

```text
Checked against real machine capability
```

### Shot 05 - Digital Asset To Manufacturing

用途：讲 protected digital asset + manufacturing agent。

上传素材：

- @Image1：AI UI mockup
- @Image2：Santoni logo
- @Video1：`Seamless production video.mp4`，真实机台运动和布局参考
- @Image3：`seq_0080.jpg` 或真实 factory / machine line
- @Image4：`seq_0180.jpg`，负压管和绿色收集篮参考，可选

Prompt:

```text
Use @Image1 as the enterprise software reference, @Image2 only as brand identity reference, @Video1 as the machine motion and layout reference, @Image3 as the factory/machine reference, and @Image4 as the suction pipe and basket reference if available. Create an 8-second 16:9 premium B2B commercial shot. A digital knitwear asset is packaged into protected layers: design intent, structure map, material data, machine recipe, costing, and production permissions, shown as clean abstract layers with no readable text. The asset connects to a manufacturing planning screen and then transitions into a real seamless machine preparing for production. Show yarn cones, front control panel, transparent safety guard, green external collection basket, clear side suction pipe, and operator checking parameters. Do not show garments directly growing out from the exterior side of the machine during knitting. If output is shown, use the realistic post-completion pneumatic suction pipe transfer into the green basket. The visual should feel secure, collaborative, and industrially credible. Do not show misspelled logos, fake holograms, fantasy factories, unreadable text, overdramatic neon, or fake conveyor output.
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

## 7. 如果你想做 60 秒版，剪辑顺序

推荐剪辑顺序：

1. Opening：产品经理输入需求，桌上有 yarn 和 swatches。
2. Production-aware AI interface：AI 生成设计方案，但同步显示结构、机台、成本、交期。
3. Santoni Machine Know-how：真实机台、needle、feeder、yarn path。
4. Material Intelligence：纱线和面料结构选择。
5. Machine Feasibility：工程师检查 gauge、feeders、tension、stitch length。
6. Digital Asset To Manufacturing：数字资产进入制造计划。
7. Quality Feedback Loop：生产、检测、反馈。
8. Closing：finished garment + Santoni AI Knitting Agent。

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
