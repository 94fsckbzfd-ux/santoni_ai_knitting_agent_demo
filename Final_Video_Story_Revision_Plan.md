# 202605251441 Final Cut 故事性增强建议

## 1. 当前版本的问题

当前视频画面真实感明显提升，尤其是无缝机、针区、负压出料管、收集篮和面料样布都比 demo 版可信。但故事性弱于之前 demo，主要不是素材问题，而是叙事连接问题。

核心问题：

- 开头直接进入“材料桌 + AI UI”，但没有建立客户痛点：为什么需要这个 Agent？
- 中段是功能并列展示：UI、材料、机台、面料、生产、质检都出现了，但缺少“一个产品需求如何一步步变成可生产方案”的因果关系。
- Santoni know-how 很真实，但出现方式偏“机器展示”，还没有被旁白明确绑定到客户价值。
- 商业价值出现不够明显：减少试错、提前验证、报价更快、排产更准、质量反馈闭环，这些需要更直接地说出来。
- 结尾有品牌画面，但缺少一句强收束，观众看完还不一定记住“这到底改变了什么”。

## 2. 不一定要重做全部，建议补 4 类镜头

### A. Problem Shot - 客户痛点

放在最前面，6 秒左右。

目的：先建立“传统流程慢、试错多、设计和生产脱节”。

Prompt:

```text
Create a 6-second 16:9 realistic B2B textile product development scene. A sportswear product manager and textile engineer review a product brief, fabric swatches, yarn cones, sample notes, and production planning documents on a desk. The mood is focused and slightly pressured, not dramatic. Show multiple sample versions and handwritten notes suggesting repeated sampling, cost uncertainty, and production feasibility questions. Professional textile studio, real materials, calm industrial lighting. Do not show sci-fi UI, fantasy visuals, unreadable fake text, distorted hands, or plastic-looking fabric.
```

字幕：

```text
In knitwear, every idea must survive material, machine, cost, and time.
```

### B. Decision Moment Shot - AI 不是生成图片，而是做生产决策

放在 UI 镜头之后、机台之前，5-6 秒。

目的：把 AI UI 和 Santoni machine know-how 连接起来。

Prompt:

```text
Create a 6-second 16:9 realistic B2B software-to-manufacturing transition shot. On a professional workstation, a seamless sportswear design is transformed into structured production data: yarn selection, knit structure map, gauge, feeders, stitch length, tension window, machine compatibility, cost range, and lead time shown as clean abstract UI cards. The screen then visually connects to a real Santoni seamless circular knitting machine in the background. The style is credible enterprise software, not sci-fi. No readable text. Do not show holograms, fantasy UI, wrong machines, sewing machines, woven looms, or distorted hands.
```

字幕：

```text
The Agent turns a design prompt into production-aware decisions.
```

### C. Business Value Shot - 成本/交期/产能

当前版本里有平台和生产，但“为什么有商业价值”还不够直接。建议补 6-7 秒。

Prompt:

```text
Create a 7-second 16:9 realistic textile planning office shot. A product manager and factory planner compare two production options on a professional dashboard. The dashboard shows a seamless garment beside abstract indicators for yarn usage, machine time, sample iterations, cost range, capacity, and delivery scenarios. Real yarn cones and fabric swatches are on the desk. The emotion is clarity and confidence: the team can see cost, timing, and risk before sampling. No readable text. Do not show sci-fi holograms, fake charts, distorted hands, or plastic-looking garments.
```

字幕：

```text
Cost, timing, and production risk become visible before sampling.
```

### D. Customer Loop Shot - 使用反馈回到下一次设计

放在质检之后、品牌结尾之前，6-7 秒。

目的：补完整闭环，从“工厂生产”回到“客户价值”。

Prompt:

```text
Create a 7-second 16:9 premium commercial shot. An athlete wears a seamless knitted performance top during light movement in a clean training studio. Show realistic fabric stretch, ventilation zones, and textile texture. Then transition visually to a professional AI platform where user feedback becomes updated design and knit structure data. The mood is human, refined, and credible. Do not show runway fashion fantasy, unrealistic fabric physics, unreadable fake text, plastic-looking garments, or exaggerated sci-fi overlays.
```

字幕：

```text
Real use becomes the next design decision.
```

## 3. 推荐重新剪辑结构

现在的视频可以保留大部分画面，但建议换成更强的因果顺序：

1. Problem Shot：传统针织开发很难，创意必须经过材料、机台、成本和交期。
2. 现有 0-4s：材料桌 + AI prompt，进入 Agent。
3. 现有 8-16s：AI 设计和结构区域。
4. Decision Moment Shot：AI 将设计转成 yarn、structure、gauge、feeders、machine compatibility。
5. 现有 18-22s：工程师 + 真实机台。
6. 现有 24-32s：纱线和面料结构。
7. Business Value Shot：成本、交期、产能和打样风险。
8. 现有 34-42s：机台真实运行。
9. 现有 44-50s：平板/数字资产/平台。
10. 现有 52-60s：工厂产线 + 负压管/收集篮。
11. 现有 62s：样衣质检。
12. Customer Loop Shot：用户使用反馈回到下一次设计。
13. 现有 64-68s 品牌结尾，但建议后期重做静态 end card。

## 4. 旁白建议：用旁白补故事，而不是靠画面自己解释

当前画面很多，但少了“所以怎样”的连接。建议用这一版 60 秒旁白：

```text
In knitwear, an idea is only the beginning.

Every product must pass through material, structure, machine capability, cost, and delivery time.

Santoni AI Knitting Agent brings these decisions into one intelligent workflow.

It reads the brief, explores design directions, and turns performance needs into real knit structures.

Breathability becomes mesh.
Moisture absorption becomes terry placement.
Fit becomes a manufacturable knitting recipe.

Then Santoni know-how checks the design against real machines: gauge, feeders, stitch length, yarn tension, and production feasibility.

Before sampling begins, teams can see cost, timing, capacity, and risk.

The design becomes a protected digital asset, ready for manufacturing.

On the factory floor, production and quality data return to the system.

And real use becomes the next design decision.

This is not AI replacing expertise.
This is Santoni know-how becoming connected, scalable, and reusable.

Santoni AI Knitting Agent.
```

## 5. 最小改动版本

如果不想重新生成太多，最少补这 3 个：

1. Problem Shot
2. Business Value Shot
3. Customer Loop Shot

然后把现有视频重排成：

```text
Problem -> existing 0-16s -> existing 18-32s -> Business Value -> existing 34-62s -> Customer Loop -> End Card
```

这会比单纯继续补机台镜头更有效，因为当前缺的不是技术真实感，而是故事弧线。
