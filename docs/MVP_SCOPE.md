# MVP Scope

## Product Definition

AI Knitting Agent is a unified natural language interface for Santoni digitalization services.

The MVP should prove that one Main Agent can route different user intents into specialized sub-agents and produce business-grade results with mocked data.

## Primary Users

### Designer

Likely user: Decathlon brand designer.

Goal: convert a natural language product idea into a knitting design and sampling proposal.

Core flow:

```text
Designer brief
  -> Main Agent
  -> Translation Agent
  -> Digital Twin Agent
  -> Design proposal + simulated SWS output
```

Expected output:

- Image understanding result when a reference image is uploaded
- Product interpretation
- Yarn recommendation
- Knit structure recommendation
- Santoni machine recommendation
- Simulated SWS parameter package
- 3D preview description or placeholder
- Cost estimate
- Sampling lead time
- Yield estimate
- Risks and next actions

### Customer Equipment Engineer

Likely user: equipment engineer at a customer factory.

Goal: report installation or maintenance needs, receive safe online assistance first, and confirm ticket creation/dispatch when onsite support is needed.

Core flow:

```text
Customer issue
  -> Main Agent
  -> Service Dispatch Agent
  -> Ticket creation
  -> Engineer assignment
  -> Customer ETA + dispatch summary
```

Expected output:

- Image understanding result when an alarm, component, or defect image is uploaded
- Issue classification
- Missing information checklist
- Priority
- Created ticket ID
- Assigned Santoni service engineer
- Recommended spare parts
- ETA
- Dispatch rationale
- Current ticket status

## Out of Scope for Phase 1

- Real SWS API integration
- Real APS integration
- Real DPP integration
- Real service ticket system integration
- Real device telemetry
- Autonomous machine control
- Full predictive maintenance model
- Persistent long-term memory
- Real image recognition in phase 1

## Phase 1 Data Policy

All data is mocked, including:

- Customer profiles
- Machine profiles
- Designer briefs
- Process rules
- Factory capacity
- Service engineers
- Spare parts inventory
- Ticket state
- Image understanding results
