# Gemini / Veo 输入清单：Santoni AI Knitting Agent 宣传视频

## 0. 推荐工作方式

Gemini / Veo 更适合每次生成一个 8 秒左右的镜头，再后期剪辑。先不要让它一次生成完整 2 分钟视频。

建议第一版做 8 个镜头：

1. Prompt enters a real textile workflow
2. Trend becomes textile engineering
3. Santoni machine know-how
4. Production-aware design variations
5. Material intelligence
6. Cost, lead time, feasibility
7. Digital asset and manufacturing agent
8. Smart factory and feedback loop

每个镜头都用 16:9。字幕、logo、产品名建议后期加，不建议让 Gemini 直接生成可读文字或 logo。

## 1. Gemini 里先输入的全局风格说明

如果 Gemini 允许先对话再生成，先发这一段，让它理解项目风格。不要点生成视频，只是让它帮你进入上下文。

```text
I am creating a premium B2B commercial video for Santoni AI Knitting Agent.

The video must feel realistic, industrial, and credible for textile and knitting professionals. It should not look like a generic sci-fi AI demo.

Core message:
Santoni AI Knitting Agent is not just generating fashion images. It turns a product idea into production-ready knitwear decisions, combining generative AI with Santoni's knitting machine know-how, material intelligence, and manufacturing reality.

Visual style:
realistic premium industrial documentary, clean textile design studio, real seamless circular knitting machines, yarn cones, fabric swatches, macro shots of needles and yarn feeders, professional enterprise software UI, calm confidence, European industrial innovation, neutral white and grey industrial environment with small Santoni red accents.

Machine accuracy:
On a Santoni seamless circular knitting machine, the garment is not visible outside during knitting. During operation, show yarn cones, feeders, needles, control panel, side suction pipe, external collection basket, and machine motion, but no finished garment growing or emerging from the machine exterior. After one garment is completed, a pneumatic vacuum suction system pulls the finished knitted tube or garment through the side suction pipe next to the machine and ejects it into the external collection basket. If the finished result must be shown, show this post-completion vacuum tube transfer into the basket, or show the sample already placed on a quality inspection table.

Avoid:
generic sci-fi holograms, random glowing UI, fake futuristic robots everywhere, fantasy machines, sewing machines, woven looms, generic white t-shirts only, unreadable text, misspelled logos, distorted hands, distorted faces, plastic-looking fabric, overdramatic blue neon, empty futuristic lab, cartoon look, finished garment growing out of the machine exterior during knitting, shirt magically emerging from the machine side, conveyor belt output from the knitting machine exterior.

For every video prompt I give you, create one cinematic 8-second 16:9 shot with realistic motion and professional camera language. Do not add readable on-screen text; captions will be added later in editing.
```

## 2. 必备参考图片

最推荐上传真实图片。第一版没有真实图时，可以先用本地现有图做 placeholder，但后面一定要换真实 Santoni 资料。

### A. 必须准备的真实图片

1. Santoni logo  
   本地已有：`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\src\web_app\santoni-logo.png`

2. Santoni seamless circular knitting machine 正面或 45 度角照片  
   需要真实照片。现在本地没有找到足够好的真实机台图。临时 placeholder：  
   `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\ai_video_docx_media\image3.png`

2b. 真实无缝机生产参考视频，优先用于所有机台镜头：  
   `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\Seamless production video.mp4`  
   这个视频明确了真实结构：蓝白色无缝圆机、前方控制屏和急停按钮、透明防护罩、上方纱筒和导纱系统、左侧绿色收集篮、机旁透明弯管/负压管。绿色物体是收集篮，不是正在编织的布料。

3. Machine detail macro: needles, feeders, yarn path, take-down, control panel  
   需要真实照片。这个最能解决 CEO 说的“不够真实”。

3b. Machine side suction pipe and external collection basket  
   如果能拍到，这张非常重要。它可以纠正 AI 把成衣从机器外壳直接“长出来”的错误理解。真实逻辑是：成衣完成后由负压抽到机旁管道，再排到外部收集篮。

4. Yarn and fabric references: yarn cones, mesh knit, terry knit, rib knit, jacquard/structure swatches  
   需要真实照片，最好有手触摸面料或桌面样布。

5. AI platform UI / product mockup  
   临时可用：  
   `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\ai_video_docx_media\image2.png`  
   `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\gemini_reference_frames\draft_short\draft_short_032s.jpg`

6. Finished seamless garment or sports top reference  
   临时可用：  
   `C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\文档\New project\gemini_reference_frames\draft_short\draft_short_024s.jpg`

### B. 不建议作为主要参考的图片

不要大量上传现有 demo 的黑底全息 UI 帧，否则 Gemini 会继续生成“泛未来科技感”。最多只把其中 1 张作为 UI 构图参考，且 prompt 里明确说 realistic enterprise UI, not hologram fantasy。

## 3. 每个镜头给 Gemini 的输入

下面每个镜头都单独生成一次。Gemini 里选择 Create video / Video，然后上传对应图片，再粘贴 prompt。

### Shot 01 - Opening: prompt enters real textile workflow

上传图片：

- Santoni logo
- 真实 fabric swatches / yarn cones 图片
- 真实 Santoni 机台照片，或临时用 `image3.png`

Prompt:

```text
Create one cinematic 8-second 16:9 video.

A realistic premium industrial documentary shot inside a textile design studio. A sportswear product manager types a product brief on a laptop. On the desk are real yarn cones, knitted fabric swatches, a measuring tape, and machine engineering sketches. In the background, through glass, there is a subtle view or reflection of a seamless circular knitting machine. The camera slowly dollies from the hands to the fabric swatches, then toward the laptop glow. Keep the screen out of focus with abstract UI blocks only, no readable text. Calm, credible, high-end B2B commercial style. Neutral white and grey tones with small Santoni red accents. Avoid sci-fi holograms and fantasy UI.

Audio: soft keyboard typing, quiet textile studio ambience, subtle modern industrial music.
```

剪辑字幕建议：

```text
From prompt to production-ready knitwear
```

### Shot 02 - Trend becomes textile engineering

上传图片：

- AI platform UI reference: `image2.png` 或 `draft_short_032s.jpg`
- finished garment reference: `draft_short_024s.jpg`
- fabric swatch / mesh / terry 真实图片

Prompt:

```text
Create one cinematic 8-second 16:9 video.

A realistic enterprise AI interface on a large professional monitor in a textile design studio. Market trend images and sportswear inspiration transform into textile engineering information: breathable mesh zones, terry moisture absorption zones, rib support zones, and a 3D seamless sports top silhouette. The UI should look like professional CAD and PLM software, not a glowing hologram. A designer and textile engineer compare the screen while real knitted fabric swatches sit beside the keyboard. Slow lateral camera pan across the monitor and fabric samples. No readable text, only clean abstract interface elements.

Audio: low studio ambience, soft UI interaction sounds, restrained modern music.
```

剪辑字幕建议：

```text
Trend insight becomes knitting engineering
```

### Shot 03 - Santoni machine know-how layer

上传图片：

- 真实 Santoni seamless circular knitting machine 图片，优先
- 真实 needle / feeder / yarn path 微距图片，优先
- 真实生产视频：`Seamless production video.mp4`
- 临时 placeholder: `image3.png`

Prompt:

```text
Create one cinematic 8-second 16:9 video.

Use the real production reference video for machine geometry and motion. Macro realistic shot focused on the true working area of a Santoni seamless circular knitting machine. Preserve the real layout: blue-and-white machine body, front control panel and emergency button, transparent safety guard, overhead yarn cones and yarn guides, green external collection basket on the left, clear curved pneumatic suction pipe beside the machine. Needles move with precision, yarn feeders guide multiple yarns, fine threads run under controlled tension, and knitted fabric forms inside the machine body, hidden from the exterior view during knitting. Add only a subtle transparent engineering overlay showing abstract feeder paths, stitch density zones, yarn tension windows, and quality checkpoints. Camera begins with an extreme close-up of needles and yarn, then pulls back slightly to reveal the full machine front. Machine accuracy: during knitting, no finished garment is visible outside. If output is shown at the end of the shot, show the completed knitted item being pulled by pneumatic vacuum through the side suction pipe next to the machine and ejected into the green external collection basket. The green object is a collection basket, not fabric. Real metal, real yarn, real textile machinery.

Audio: precise machine rhythm, soft yarn movement, clean industrial ambience.
```

剪辑字幕建议：

```text
Santoni know-how becomes digital intelligence
```

### Shot 04 - Production-aware design variations

上传图片：

- AI platform UI: `draft_short_032s.jpg` or `image2.png`
- garment reference: `draft_short_024s.jpg`
- fabric/structure swatches

Prompt:

```text
Create one cinematic 8-second 16:9 video.

On a large workstation monitor, multiple seamless sports top variations appear side by side. Each variation is connected to manufacturing-aware indicators represented by clean abstract badges: yarn type, knit structure, machine compatibility, cost range, and lead time. The garments should look like engineered seamless knitwear, not generic cotton T-shirts. Show visible mesh ventilation zones, terry absorption zones, rib support zones, and seamless body construction. A designer adjusts one parameter and the garment updates smoothly. Realistic enterprise software UI, no readable text, no hologram fantasy.

Audio: soft UI clicks, quiet office ambience, subtle confident music.
```

剪辑字幕建议：

```text
Every variation is checked against production reality
```

### Shot 05 - Material intelligence

上传图片：

- 真实 yarn cones 图片
- 真实 fabric swatches 图片
- 如有材料实验室或样品桌照片，也上传

Prompt:

```text
Create one cinematic 8-second 16:9 video.

A clean textile material lab with yarn cones, knitted swatches, and technical fabric samples on a worktable. A textile expert picks up a yarn cone and compares it with mesh, terry, and rib knit samples. A professional material dashboard updates in the background with abstract charts for performance, cost, availability, and lead time. The camera moves from the texture of the yarn fibers to the expert's hand touching the knitted fabric. Make the fabric tactile and realistic. Avoid fake neon lighting and generic lab visuals.

Audio: soft fabric handling, quiet lab ambience, restrained modern music.
```

剪辑字幕建议：

```text
Yarn choices shape performance, cost, and speed
```

### Shot 06 - Cost, lead time, feasibility

上传图片：

- AI platform UI mockup: `image2.png`
- real workstation / planning office reference if available
- fabric swatch or garment image

Prompt:

```text
Create one cinematic 8-second 16:9 video.

A realistic product development dashboard on a large monitor in a planning office. A seamless knitted garment is shown beside clean abstract business indicators for yarn usage, machine time, sample iterations, cost range, capacity, and delivery scenarios. A product manager and factory planner discuss the options beside the screen, with real fabric samples and production documents on the desk. The visual message is that design, cost, and delivery are evaluated together before sampling. Professional B2B commercial style, no readable text, no exaggerated holograms.

Audio: quiet office discussion murmur, soft UI notification, calm industrial music.
```

剪辑字幕建议：

```text
Design decisions with business consequences
```

### Shot 07 - Protected digital asset and manufacturing agent

上传图片：

- UI mockup: `image2.png`
- Santoni logo
- machine/factory reference, or `draft_short_072s.jpg` as temporary placeholder

Prompt:

```text
Create one cinematic 8-second 16:9 video.

A premium enterprise software scene showing a digital knitwear asset packaged into protected layers: design intent, structure map, material data, machine recipe, costing, and production permissions. The asset connects to a restrained manufacturing network: brand team, yarn supplier, Santoni engineer, and factory planner each see a different permission view. Keep all UI text abstract and unreadable. Use subtle lock icons, layered translucent panels, and real textile objects in the environment. The camera moves from the digital garment asset to a factory planning screen with real machine capacity represented by clean visual cards. Realistic, not sci-fi.

Audio: soft digital confirmation sounds, quiet collaboration ambience, confident music.
```

剪辑字幕建议：

```text
Share what matters. Protect what matters.
```

### Shot 08 - Smart factory and feedback loop

上传图片：

- 真实 Santoni factory / machine line photo, priority
- 真实生产视频：`Seamless production video.mp4`
- 真实 quality inspection / garment measurement photo if available
- temporary placeholder: `draft_short_072s.jpg`

Prompt:

```text
Create one cinematic 8-second 16:9 video.

A bright clean textile factory floor with seamless circular knitting machines running, using the real production reference video for machine layout and motion. Operators prepare yarn cones, scan a work order, and load machine settings. Preserve the real details: blue-and-white machine, transparent safety guard, front control panel, overhead yarn cones, clear curved side suction pipe, green external collection basket. During production, no finished garment is visible outside the machine. After one garment is completed, pneumatic vacuum pulls the knitted tube or garment sample through the clear curved side suction pipe next to the machine and ejects it into the green external collection basket. An operator takes the sample from the basket and places it on a quality control table. A scanner or measuring system evaluates stitch consistency, size tolerance, tension variation, and fabric defects with subtle abstract overlays. The green object is a collection basket, not fabric. Everything must feel physically real: real yarn, real machines, real operators, real knitted fabric. Documentary-style camera movement, premium industrial lighting.

Audio: rhythmic knitting machine sound, soft factory ambience, uplifting but restrained closing music.
```

剪辑字幕建议：

```text
Quality data improves the next decision
```

## 4. 后期旁白建议

先不要让 Gemini 直接生成英文旁白，因为它容易把口型、字幕和内容做乱。建议视频生成时只要 ambient audio，旁白后期加。

60 秒版中文旁白：

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

60 秒版英文旁白：

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

## 5. 生成顺序建议

先跑这 3 条，判断风格是否对：

1. Shot 03 - Santoni machine know-how layer
2. Shot 04 - Production-aware design variations
3. Shot 08 - Smart factory and feedback loop

如果这三条还是很“虚”，说明参考图片不够真实，需要先补真实机台、针路、纱线和工厂图，再继续生成其他镜头。
