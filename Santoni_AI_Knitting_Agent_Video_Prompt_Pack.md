# Santoni AI Knitting Agent 宣传视频 Prompt Pack

## 1. 对现有脚本和 demo 的判断

现有 CEO 脚本的方向是对的：从 prompt 到设计、材料、生产、质量和组织级 agent。但现在的文字和 demo 画面更像通用 AI 平台宣传片，缺少 Santoni 在针织行业里的真实 know-how。

现有 demo 里最弱的几个点：

- 画面主体是白色 T 恤、全息 UI、泛工业机器人，Santoni 的 machine、needle bed、feeders、yarn path、seamless circular knitting 特征不明显。
- AI 生成结果看起来像 fashion image generation，而不是可生产的 knitwear engineering workflow。
- “Every option already tested”等表达过于绝对，商业上容易显得虚；建议改成“feasibility checked / production-aware / guided by machine constraints”。
- 没有把客户价值讲清楚：减少无效打样、把设计和机台能力提前对齐、缩短从创意到报价到排产的周期、保护数据并协同供应链。
- 缺少 Santoni 的行业语言：gauge、feeders、yarn tension、stitch length、terry zones、mesh zones、plating、jacquard、shrinkage、BOM、machine recipe、APS、quality feedback loop。

新的主张建议定为：

> Santoni AI Knitting Agent is not just generating images. It turns a design prompt into a manufacturable knitting decision, guided by Santoni machine know-how, material intelligence, and production reality.

中文表达：

> 它不是让 AI 随机画衣服，而是把 Santoni 的针织工程经验放进每一次设计、材料和生产决策里。

## 2. 统一生成规则

### 推荐片长

建议先做 90 到 120 秒商业版。CEO 原脚本可以保留为 3 到 4 分钟长版，但第一条 commercialization 视频应更快进入 Santoni 的真实价值。

### 画面风格

使用真实工业商业片质感，不要纯科幻：

- realistic premium industrial documentary
- real Santoni seamless circular knitting machines
- close-up macro shots of needles, yarn feeders, yarn cones, fabric structures
- clean enterprise software UI, not hologram fantasy
- calm confidence, high precision, European industrial innovation
- lighting: bright factory daylight, clean lab, real textile design studio
- color: Santoni red accents, neutral white/grey industrial base, black technical UI accents

### 给 AI 视频软件的通用设置

建议每个镜头单独生成 5 到 8 秒，再剪辑，不要一次生成整条片。

- Aspect ratio: 16:9
- Style: realistic commercial film, premium industrial documentary
- Camera: macro lens, slow dolly, clean handheld, shallow depth of field only for close-ups
- Text: avoid generating readable text inside the video; add captions and UI labels in editing
- Use references: real Santoni machine photos, yarn/fabric macro photos, product UI mockups, Santoni logo file

### 全片通用 negative prompt

Use this negative prompt for every generation:

> generic sci-fi holograms, fantasy machines, fake robots everywhere, random glowing UI, unreadable text, misspelled brand names, distorted hands, distorted faces, unrealistic fabric physics, woven loom instead of circular knitting machine, sewing machine instead of knitting machine, generic white t-shirt only, empty futuristic lab, cartoon look, plastic garment, overdramatic blue neon, stock footage look, impossible factory layout, wrong logo, extra limbs, shaky camera, blurry product, low-resolution UI text

### 无缝机台输出准确性

所有涉及 Santoni seamless circular knitting machine 的镜头，都要加这条约束。否则 AI 很容易错误地把成衣画成从机器外壳直接长出来：

> Machine accuracy: on a Santoni seamless circular knitting machine, the garment is not visible outside during knitting. During operation, show yarn cones, feeders, needles, control panel, side suction pipe, external collection basket, and machine motion, but no finished garment growing or emerging from the machine exterior. After one garment is completed, a pneumatic vacuum suction system pulls the finished knitted tube or garment through the side suction pipe next to the machine and ejects it into the external collection basket. If the finished result must be shown, show this post-completion vacuum tube transfer into the basket, or show the sample already placed on a quality inspection table.

如果使用真实参考视频：

> Use the real production reference video exactly for machine geometry: blue-and-white Santoni seamless circular knitting machine, front control panel and emergency button, transparent safety guard, overhead yarn cones and yarn guides, green external collection basket on the left, clear curved pneumatic suction pipe beside the machine. The green object is a collection basket, not fabric. Do not invent a conveyor belt or show a garment growing from the machine exterior.

可放入 negative prompt 的补充：

> finished garment growing out of the machine exterior during knitting, shirt magically emerging from the machine side, conveyor belt output from the knitting machine exterior, finished garment visible outside during knitting

## 3. 加强后的叙事结构

全片逻辑从“AI 会生成东西”改为“Santoni 让 AI 知道什么能被真实生产”：

1. 客户需求进入系统
2. AI 读取市场趋势，但不止于趋势
3. Santoni know-how layer 把设计转成针织结构
4. 系统检查 yarn、gauge、feeders、structure 和 machine feasibility
5. 设计、成本、交期和质量风险同时可见
6. 数字资产在品牌、供应商、工厂间安全协作
7. Manufacturing Agent 找到合适产能并排产
8. Smart Factory 生产、检测、反馈
9. 下一次设计从真实数据开始

## 4. Shot-by-shot AI Video Prompts

以下 prompt 用英文写，方便直接放入 AI 视频生成工具。旁白和字幕建议后期单独添加，避免 AI 生成错误文字。

### Scene 1 - Opening: From Prompt To Production Reality

目的：一开始就避免“普通 AI 设计工具”的感觉，把 prompt 和真实材料、机器联系起来。

旁白 CN：

> 一条产品需求，通常会经过设计、材料、打样、报价和排产。Santoni AI Knitting Agent 把这些判断提前放进同一个流程。

Screen text:

> From prompt to producible knitwear

Prompt EN:

> Realistic premium industrial commercial film. Close-up of a sportswear product manager typing a product brief on a laptop in a textile design studio. Around the desk are real yarn cones, knitted fabric swatches, measurement tools, and printed machine diagrams. Soft morning light, Santoni red accent on a small notebook or UI element. The screen is intentionally out of focus with clean abstract interface blocks, no readable text. Slow dolly-in from hands to fabric swatches, then a subtle reflection of a circular knitting machine on the glass wall. Cinematic, precise, credible, not sci-fi.

### Scene 2 - Market Trend Meets Textile Engineering

旁白 CN：

> AI 可以读取趋势，但真正的价值不是生成一张图。价值在于把趋势转成结构、材料和可生产的针织方案。

Screen text:

> Trend insight + knitting engineering

Prompt EN:

> A realistic enterprise AI interface in a design studio, showing moodboard-like sportswear trends transforming into structured textile engineering data. Visual elements include breathable zones, moisture management zones, terry texture close-ups, mesh knit macro textures, and a 3D seamless sports top silhouette. Keep the interface elegant and realistic, like professional CAD and PLM software, not a glowing hologram. Camera slowly pans across fabric macro samples and the 3D garment model. Use neutral industrial colors with small Santoni red accents.

### Scene 3 - Santoni Know-how Layer

旁白 CN：

> 这里加入的是 Santoni 的行业 know-how：机台能力、纱线路径、针织结构、张力窗口和生产经验。

Screen text:

> Santoni know-how layer

Prompt EN:

> Macro cinematic shot focused on the true working area of a real Santoni seamless circular knitting machine, using the real production reference video for machine geometry and motion: blue-and-white machine body, front control panel and emergency button, transparent safety guard, overhead yarn cones and yarn guides, green external collection basket on the left, clear curved pneumatic suction pipe beside the machine. Needles move with precision, yarn feeders guide multiple yarns, fine threads run under controlled tension, metallic components clean and realistic. Knitted fabric forms inside the machine body and is hidden from the exterior view during knitting. Overlay a subtle transparent engineering layer showing abstract structure mapping, feeder paths, stitch density zones, and quality checkpoints. The overlay should be minimal and professional, with no readable text. Machine accuracy: during knitting, no finished garment is visible outside. If output is shown at the end of the shot, show the completed knitted item being pulled by pneumatic vacuum through the side suction pipe and ejected into the green external collection basket. The green object is a collection basket, not fabric. The shot should feel like real machine knowledge becoming digital intelligence.

### Scene 4 - Design Variations, But Production-aware

旁白 CN：

> 每个设计变化，不只是外观变化。系统同步检查结构、纱线、机台和生产可行性。

Screen text:

> Every variation is production-aware

Prompt EN:

> Realistic UI scene on a large professional monitor. Multiple seamless sports top variations appear side by side, but each variation is connected to manufacturing indicators: yarn type, knit structure, machine compatibility, cost range, and lead time as clean visual badges. The garments look like engineered knitwear, not generic cotton T-shirts. Include visible zones for mesh ventilation, terry absorption, rib support, and seamless body construction. Camera moves slowly over the monitor while a designer compares options with a textile engineer.

### Scene 5 - Structure Mapping

旁白 CN：

> 透气、吸湿、支撑、弹性和手感，都来自具体的针织结构，而不是一句形容词。

Screen text:

> Performance becomes structure

Prompt EN:

> High-end technical visualization of a seamless sports garment transitioning into a knit structure map. Show macro fabric textures mapped onto body zones: mesh ventilation under arms and back, terry absorption at sweat zones, rib support at hem and cuffs, elastic zones around movement areas. Use realistic fabric detail and restrained UI overlays. Camera starts on the whole garment, then pushes into microscopic knitted loops and yarn texture, then returns to the 3D garment.

### Scene 6 - Machine Feasibility

旁白 CN：

> 设计会自动贴近真实机台能力：gauge、feeders、needle selection、stitch length、yarn tension 和可生产尺寸。

Screen text:

> Checked against machine reality

Prompt EN:

> A clean factory engineering room with a Santoni seamless circular knitting machine in the background and a technician reviewing a digital twin of the machine on a workstation. Use the real production reference video for the machine layout: blue-and-white body, transparent safety guard, front control panel, overhead yarn cones, clear curved side suction pipe, green external collection basket. The UI shows abstract machine feasibility checks through icons and colored status indicators, no readable text. Cut between the 3D garment, feeder positions, needle movement, and a real machine starting a sample run. During the sample run, show yarn cones, feeders, needle area, side suction pipe, external collection basket, and control panel from the outside, but no finished garment visible outside the machine. After completion, if showing the sample result, show pneumatic vacuum pulling the knitted item through the side suction pipe and ejecting it into the green external basket, or show it already on the inspection table. Realistic lighting, no fantasy holograms, believable industrial workflow.

### Scene 7 - Material Intelligence

旁白 CN：

> 纱线选择不再只是经验判断。每一种纤维、支数、库存和供应周期，都会影响性能、成本和交期。

Screen text:

> Yarn, cost, performance, lead time

Prompt EN:

> Cinematic close-up of yarn cones in a clean textile lab: recycled nylon, cotton blend, technical polyester, elastane-covered yarn, each represented by realistic color-coded swatches and knitted samples. A designer places a yarn cone on a smart scale or scanning station, and the software updates a professional material dashboard with abstract charts. Show hands, real yarn fibers, fabric touch, and a calm engineering atmosphere. Avoid sci-fi lighting.

### Scene 8 - Digital Fitting And Validation

旁白 CN：

> 在打样之前，产品已经可以被试穿、拉伸、调整和验证。不是替代工程师，而是让工程判断更早发生。

Screen text:

> Fit before sampling

Prompt EN:

> Realistic digital twin fitting scene on a workstation. A 3D athletic avatar moves naturally while wearing a seamless knitted sports top. Subtle heatmaps show stretch, pressure, ventilation, and moisture zones. Beside the screen, a real physical fabric swatch and measuring tape connect digital validation to textile reality. The camera alternates between the UI and the engineer's hand adjusting a garment parameter on a control surface. Professional and believable.

### Scene 9 - Cost And Optimization

旁白 CN：

> 设计、成本和交期不再分开。减少颜色、替换库存纱线、调整结构，每一次选择的影响都能被看见。

Screen text:

> Design decisions with business consequences

Prompt EN:

> A realistic executive product development dashboard on a large monitor, showing a seamless garment, yarn usage, machine time, sample iterations, cost range, and delivery scenarios as clean abstract graphics. A product manager and factory planner discuss options beside the screen. The background includes real fabric samples and machine planning documents. No exaggerated holograms. Camera moves from the garment design to the cost and lead-time dashboard.

### Scene 10 - Protected Digital Asset

旁白 CN：

> 当产品成为数字资产，真正重要的不只是分享，而是有选择地分享。

Screen text:

> Share what matters. Protect what matters.

Prompt EN:

> Premium enterprise software scene. A digital knitwear asset is packaged into protected layers: design intent, structure map, material data, machine recipe, costing, and production permissions. Show a clean visual metaphor of layered translucent documents and fabric samples, with security permissions represented by subtle lock icons and access rings. In the background, a brand team, yarn supplier, and factory engineer collaborate through a professional platform. Realistic office and textile lab environment.

### Scene 11 - Collaboration Network

旁白 CN：

> 品牌、设计师、材料供应商、工厂和工程师可以协同，但每一方只看到自己需要的数据。

Screen text:

> Collaboration without losing ownership

Prompt EN:

> Realistic split-location collaboration montage: a brand designer in a studio, a yarn supplier in a material lab, a Santoni engineer near a circular knitting machine, and a factory planner in a control room. Their screens show the same seamless garment asset with different permission views, represented by clean abstract UI panels. Smooth transitions connect the locations through fabric threads and data lines. Premium commercial style, grounded and human.

### Scene 12 - Manufacturing Agent

旁白 CN：

> 生产不是最后才考虑的问题。系统会根据机台能力、产能、质量记录、材料可用性和交期，推荐最合适的生产路径。

Screen text:

> The right machine, the right factory, the right plan

Prompt EN:

> A realistic manufacturing planning interface overlaid on a global but restrained network map, connected to real factory scenes. Show production options evaluated by machine compatibility, capacity, cost, quality history, and delivery time using clean visual cards. Avoid game-like graphics. Transition from the map into a real Santoni machine line preparing for production. Professional APS planning feeling, credible for an industrial audience.

### Scene 13 - Smart Factory Activation

旁白 CN：

> 订单进入工厂后，数字资产会变成生产配方：纱线、结构、机台参数、质检标准和排产节奏。

Screen text:

> Digital asset to production recipe

Prompt EN:

> Bright clean textile factory floor with real seamless circular knitting machines running, using the real production reference video for machine geometry and motion. Operators prepare yarn cones, scan a work order, load machine settings, and monitor the sample run. Show close-ups of yarn feeding, needles moving, and fabric forming inside the circular machine body, hidden from the exterior view during knitting. Preserve the real details: blue-and-white machine body, front control panel, transparent safety guard, overhead yarn cones, clear curved side suction pipe, green external collection basket. Do not show a finished garment visible outside during knitting. After completion, show pneumatic vacuum pulling the knitted tube or garment sample through the side suction pipe and ejecting it into the green external basket, then an operator checking it on a quality table. The green object is a collection basket, not fabric. Use realistic industrial lighting and documentary camera movement. Santoni red accent details where appropriate.

### Scene 14 - Quality Feedback Loop

旁白 CN：

> 质量不只是最后检查。张力波动、结构偏差和尺寸风险，会回到系统，成为下一次调整的依据。

Screen text:

> Quality becomes feedback

Prompt EN:

> Realistic quality control station in a textile factory. A seamless knitted garment sample has just been ejected by pneumatic vacuum through the side suction pipe into the external collection basket beside the machine, then placed on the inspection table. It is scanned by a vision system and measured by an operator. Subtle overlays highlight stitch consistency, size tolerance, tension variation, and fabric defects as abstract indicators. The machine receives a correction suggestion and the next sample improves. Keep it believable: real scanner, real operator, real knitted garment, minimal UI overlay. Do not show the garment growing from the exterior side of the knitting machine during production.

### Scene 15 - Agent-driven Organization

旁白 CN：

> 未来的工厂不是一个孤立系统，而是一组协同 agent：设计、材料、排产、质量、服务和客户反馈持续优化。

Screen text:

> A system of specialized agents

Prompt EN:

> Realistic Santoni-style industrial control room and office environment. Multiple professional dashboards represent specialized agents: Design Agent, Material Agent, Manufacturing Agent, Quality Agent, Service Agent, Customer Feedback Agent. The visuals should feel like enterprise operations software, not a sci-fi command center. Human experts remain present, reviewing decisions and approving actions. Camera slowly pulls back to show people, machines, and software connected.

### Scene 16 - Customer Loop And Closing

旁白 CN：

> 当产品到达用户，反馈会重新回到设计和生产。下一次开发，从真实数据开始。

Screen text:

> From real use back to better design

Prompt EN:

> Premium lifestyle-meets-industrial closing shot. An athlete wears a seamless knitted performance top during training, with realistic fabric stretch, ventilation zones, and comfortable fit. Cut back to the design platform where user feedback becomes a new product brief and updated knit structure. Final transition to a real Santoni machine running, then to the finished garment on a clean table with yarn cones and fabric swatches. Elegant, credible, optimistic, not futuristic fantasy.

## 5. 更适合商业片的英文旁白版本

下面是可以替代原 CEO script 的英文旁白草案，语气更真实，也更突出 Santoni。

> It starts with a prompt.  
> But not every prompt becomes a product.  
>  
> In knitwear, every decision has consequences: yarn, structure, gauge, feeders, fit, cost, lead time, and machine reality.  
>  
> Santoni AI Knitting Agent brings those decisions into one intelligent workflow.  
>  
> It reads the market, but it also understands textile engineering.  
> It generates design directions, but checks them against what machines can truly produce.  
>  
> A breathable zone becomes a mesh structure.  
> A moisture requirement becomes terry placement.  
> A fit adjustment becomes a manufacturable knitting recipe.  
>  
> Designers explore faster.  
> Engineers validate earlier.  
> Brands see cost and timing before sampling begins.  
>  
> The product becomes a protected digital asset: shareable across teams, suppliers, and factories, without giving away what should remain private.  
>  
> Then the Manufacturing Agent connects the design to real capacity, real machines, real material availability, and real delivery windows.  
>  
> On the factory floor, production data and quality feedback return to the system, improving the next decision.  
>  
> This is not AI replacing expertise.  
> This is Santoni know-how becoming accessible, scalable, and connected.  
>  
> From prompt to producible knitwear.  
> From digital asset to smart manufacturing.  
> From customer feedback to the next generation of products.  
>  
> Santoni AI Knitting Agent.

## 6. 中文旁白草案

> 一切从一个 prompt 开始。  
> 但在针织行业里，不是每一个创意都能变成产品。  
>  
> 纱线、结构、gauge、feeders、版型、成本、交期和机台能力，每一个决定都会影响最终结果。  
>  
> Santoni AI Knitting Agent 把这些判断放进同一个智能流程。  
>  
> 它理解趋势，也理解针织工程。  
> 它生成设计方向，也会用真实机台能力检查可生产性。  
>  
> 一个透气需求，会变成具体的 mesh structure。  
> 一个吸湿需求，会变成 terry zone 的布局。  
> 一个版型调整，会变成可执行的 knitting recipe。  
>  
> 设计师更快探索。  
> 工程师更早验证。  
> 品牌在打样之前，就能看到成本、交期和生产风险。  
>  
> 产品成为受保护的数字资产，可以在品牌、供应商和工厂之间协同，同时保留各自的数据边界。  
>  
> Manufacturing Agent 会把设计连接到真实产能、真实机台、真实材料和真实交期。  
>  
> 在工厂端，生产和质量数据会回到系统，持续优化下一次决策。  
>  
> 这不是用 AI 替代经验。  
> 而是让 Santoni 的 know-how 可以被连接、放大和复用。  
>  
> 从 prompt 到可生产针织产品。  
> 从数字资产到智能制造。  
> 从用户反馈到下一代产品。  
>  
> Santoni AI Knitting Agent。

## 7. 关键画面补强清单

如果要让下一版 demo 更真实，建议至少补齐这些 reference assets，再喂给 AI 视频工具：

- 真实 Santoni 机台照片或短视频，尤其是 seamless circular knitting machine 的正面、侧面和工作特写。
- 真实生产参考视频：`C:\Users\rem_i\OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd\桌面\Seamless production video.mp4`。这条视频应作为所有机台生产镜头的主参考。
- 针、feeders、yarn path、fabric take-down、控制面板的 macro shots。
- 机旁负压出料管 / 外部收集篮 / 成衣由管道排入篮子的照片或短视频。这一点能避免 AI 错误生成“成衣从机器外壳直接长出来”。
- 真实 yarn cones、fabric swatches、mesh、terry、rib、jacquard 的微距照片。
- 真实工厂环境：不要空旷科幻工厂，要有机台、纱架、操作员、样衣检查台。
- Santoni AI Knitting Agent 的 UI mockup，哪怕是 Figma 静帧，也比让 AI 随机生成 UI 更可信。
- 品牌色和 logo 的标准文件，建议后期叠加，不建议让 AI 直接生成 logo。

## 8. 一句话商业定位

建议用于封面、结尾或对外介绍：

> Santoni AI Knitting Agent turns product ideas into production-ready knitwear decisions, combining generative AI with Santoni's textile engineering and machine intelligence.

中文：

> Santoni AI Knitting Agent 把产品创意转化为可生产的针织决策，把生成式 AI 与 Santoni 的针织工程和机台智能连接起来。
