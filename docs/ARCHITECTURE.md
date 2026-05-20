# Architecture

## High-Level Structure

```text
Web Entry / Feishu Entry
  -> Main Agent API
      -> Image Understanding Agent
      -> Designer Workflow
          -> Understanding Agent
          -> Translation Agent
          -> Digital Twin Agent
      -> Service Workflow
          -> Understanding Agent
          -> Service Dispatch Agent
              -> Ticket Creator
              -> Priority Scorer
              -> Engineer Matcher
              -> Parts Recommender
      -> Mock Data Layer
```

## Main Agent

The Main Agent is an orchestrator, not a domain calculator.

Responsibilities:

- Identify user role: Designer or Customer Equipment Engineer
- Identify intent: design request, sampling request, installation request, maintenance request, service status request
- Maintain short-term conversation state
- Route tasks to sub-agents
- Call Image Understanding Agent first when the user uploads images
- Ask clarification questions when required information is missing
- Merge sub-agent outputs into a clear user-facing response
- Format output for Web or Feishu

## Sub-Agents

### Image Understanding Agent

Shared image service used before workflow-specific agents.

Phase 1 behavior:

- Accepts image attachments from Web or Feishu
- Returns mocked image analysis
- Provides workflow hints and detected signals to downstream agents

Future behavior:

- Use GPT Vision or a dedicated computer vision model
- Extract garment/fabric references for Designer workflow
- Extract alarm screens, machine components, and defect signals for Service workflow

### Translation Agent

Converts a natural language design brief into structured knitting requirements.

The current workflow first uses Understanding Agent to extract a `DesignBrief` JSON object, then Translation Agent converts it into knitting recommendations.

Output examples:

- Product category
- Target user
- Style direction
- Functional requirements
- Yarn recommendation
- Knit structure
- Machine recommendation
- Constraints and open questions

### Digital Twin Agent

Simulates SWS 3D and production preview.

Output examples:

- Simulated SWS project ID
- Parameter package
- 3D preview description
- Cost estimate
- Sampling time
- Production time
- Yield estimate
- Risks

### Service Dispatch Agent

Creates and dispatches installation or maintenance tickets after intake, online assistance, and user confirmation when onsite support is needed.

The current workflow first uses Understanding Agent to extract a `ServiceIssue` JSON object, then Service Dispatch Agent converts it into ticket, priority, engineer, and parts recommendations.

### Understanding Agent

LLM-backed structured text parser.

Phase 1 behavior:

- Uses OpenAI Responses API with JSON Schema when `OPENAI_API_KEY` is available
- Falls back to local rule-based parsing when no API key is configured
- Extracts `DesignBrief` and `ServiceIssue`

This keeps the demo usable without network access while preserving the GPT integration point.

Output examples:

- Ticket ID
- Issue category
- Priority
- Assigned engineer
- Recommended spare parts
- ETA
- Dispatch rationale
- Status

## Entry Strategy

Web is the fastest demo and the low-friction customer trial entry.

Feishu is the advanced workflow entry for users with identity, memory, task tracking, and enterprise collaboration.

Both entries must call the same Agent Core.
