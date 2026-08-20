# Design Decisions Log

## Date: 2026-08-06 to 2026-08-08
## Session: System Design (Architecture, Workflow, State, Data Model)

---

## Core Architecture Decisions

### Q: Why Celery + RabbitMQ instead of Temporal?
**A:** Temporal is a full durable-execution engine with its own programming model. Celery is a Python-native task queue that works with RabbitMQ. For a 24-hour portfolio project, Celery demonstrates the same core concepts (durable queues, acks, redelivery, retries) without introducing a new programming paradigm. The tradeoff: Celery requires MANUAL idempotency and state management, while Temporal provides them natively. That's actually the point — we want to demonstrate we understand these concepts by implementing them ourselves.

### Q: Why Postgres as source of truth instead of Redis?
**A:** Postgres is durable (data persists on disk, ACID transactions). Redis is in-memory (fast, but data can be lost). For workflow state, we need durability — if the worker crashes, the state must survive. Postgres also provides relational querying (find next task by task_order). Redis would be a cache, not a source of truth.

### Q: Why mock tools instead of real integrations (Splunk, Kubernetes, etc.)?
**A:** The project demonstrates durable workflow orchestration, not API integrations. Real integrations would consume the entire timeline on authentication, data parsing, and vendor docs. Mock tools return realistic structured data, and the tool interface is swappable — replacing mocks with real APIs requires zero changes to orchestration logic.

### Q: Why sequential task execution instead of parallel?
**A:** Parallel execution (steps 1-3 run simultaneously, then synthesize) would require a more complex recovery state machine — tracking "3 of 3 complete" vs "2 of 3" etc. Sequential execution keeps recovery simple: find the first non-SUCCEEDED step, run it. The performance difference is irrelevant for a demo. This is a deliberate tradeoff, documented for interview defense.

### Q: Why explicit task publishing (Option B) instead of Celery chains?
**A:** Celery chains rely on the framework to publish the next task after the current one returns. If the worker crashes between "task 1 returned" and "framework published task 2," the chain breaks silently. Explicit publishing (each task publishes the next before returning) makes the handoff part of the recoverable task logic. If the worker crashes before publishing, the task hasn't acked yet, so RabbitMQ redelivers and it publishes on retry.

### Q: Why idempotency via Postgres status check instead of unique constraints?
**A:** Each task starts by querying Postgres for its own status. If status is SUCCEEDED, it skips execution and publishes the next task. This handles both duplicate delivery (crash before ack) and re-execution (crash mid-task). The check is on status, not result existence — because a task might write result but crash before updating status to SUCCEEDED.

### Q: Why request_id instead of idempotency_key?
**A:** Both work. "idempotency_key" is industry standard but confusing next to "investigation_id." "request_id" makes it clear the CLIENT supplied this value to deduplicate requests. The API checks it before creating a new investigation.

### Q: Why task_order column in investigation_steps?
**A:** Enables recovery query: "find the next non-succeeded step" via ORDER BY task_order LIMIT 1. Without it, the code would need to hardcode the workflow sequence or match on step names (fragile). Adding a new step = inserting a new row with task_order=5, no code change.

### Q: Why polling instead of webhooks for result delivery?
**A:** Webhooks require the client to deploy an endpoint and handle retries. Polling (GET /investigations/{id}) is stateless from the server's perspective and matches the use case — an SRE triggering an investigation and checking back later. Real-time push is not a requirement for this tool.

---

## Key Design Patterns Identified

### At-least-once delivery with idempotent consumers
RabbitMQ delivers messages at-least-once (redelivery after crash). Consumers must be idempotent — checking Postgres before executing work. This is the pattern that prevents duplicate execution.

### Checkpoint-resume recovery
Workflow resumes from last persisted state, not from scratch. Each step writes to Postgres before publishing the next step. Crash mid-step = that step re-runs from its start; previous steps are not re-executed.

### State machine per step
Each step has explicit states: PENDING, RUNNING, RETRYING, SUCCEEDED, FAILED. Transitions are triggered by worker actions and crash-recovery events.

---

## Tradeoffs Explicitly Accepted

| Tradeoff | Why Accepted |
|----------|--------------|
| Manual idempotency (vs Temporal) | Demonstrates understanding of distributed systems concepts |
| Sequential over parallel | Simpler recovery, no performance requirement |
| Mock tools | Focus on orchestration, not integrations |
| Single LLM provider | Timeline constraint, interface left swappable |
| No Grafana dashboard | Metrics endpoint sufficient, existing resume evidence |

---

## What Would Change the Design

### When to use Temporal instead of Celery:
- If we needed automatic saga/compensation patterns
- If the workflow required dynamic branching/planning (AI decides next step)
- If we needed built-in retry with exponential backoff + circuit breakers
- If we had a team (not solo) and could invest in learning Temporal's programming model

### When to use Redis instead of Postgres:
- If we only needed caching/in-memory state
- If durability wasn't a requirement (rarely true for workflow state)
- If write throughput was the bottleneck (Redis is faster for simple operations)

### When to use parallel execution:
- If the investigation required time-sensitive responses (parallel tools = faster)
- If the recovery complexity was justified by performance needs
- In v2, steps 1-3 could run in parallel with a fan-in pattern