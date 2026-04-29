# Commission the Multi-Agent System

> A practical guide to multi-agent workflows — from one overloaded technician to a fully coordinated commissioning crew.

**Live guide:** https://aleszcz.github.io/Multi-Agent-System/

---

## Benchmark Results

| Metric | Single Agent | Multi-Agent |
|--------|-------------|-------------|
| Avg. run time | 36.5 min | 5.2 min |
| Manual interventions | 12 | 2 |
| Success rate | 0% | 100% |
| Effective context | ~200K tokens | 25M+ tokens |

Results from a real benchmark: using Codex and the Figma MCP to copy a website into Figma. The single-agent workflow had a 100% failure rate. The multi-agent workflow succeeded on the first try.

---

## The Problem

Every developer building with AI agents eventually hits the same wall. It works fine for simple tasks — but the moment your project becomes even slightly complex, things fall apart.

The agent gets overwhelmed. Context bloats. Errors compound. Progress slows to a crawl.

The issue isn't the model. It's the architecture.

Trying to make a single AI agent handle everything is like sending one HVAC technician to commission an entire skyscraper alone — running load calculations, balancing air distribution, testing controls, verifying refrigerant charge, and signing off on safety interlocks all at once. It doesn't scale. It doesn't specialise. And it fails.

---

## Architecture

Multi-agent workflows fix the single-agent bottleneck at the architecture level.

```
Human
  └─▶ Orchestrator (Lead Commissioning Engineer)
        ├─▶ Subagent A — Air Balancing       [fresh context]
        ├─▶ Subagent B — Controls & BMS      [fresh context]
        ├─▶ Subagent C — Leak & Safety Tests [fresh context]
        └─▶ Subagent D — Sign-off Docs       [fresh context]
```

**Key principle:** The field technician doesn't get the full project history or the 15,000-line spec. They get the minimum viable context to commission one specific system on one specific floor.

### How it works

1. **Human** → talks exclusively to the orchestrator with the high-level goal
2. **Orchestrator** → breaks the goal into scoped, verifiable tickets; stripped of all tools except `delegate_task`
3. **Subagents** → each spawned with a fresh context window; execute independently with read/write/MCP access
4. **Subagents → Orchestrator** → return a summary of their work (never raw logs) back to the lead

This effectively extends the orchestrator's context window to as many subagents as it can spawn.

---

## 5 Patterns That Actually Work

### 01 — The Pre-Commissioning Survey
**Easiest · Start here**

Run many independent checks in parallel, then select the best results.

- Dispatch multiple subagents with the same brief
- Let them generate outputs in parallel
- Manually curate the best results; discard the rest
- Tasks must be fully independent — no shared files

*Example: dispatch 5 Codex Spark subagents to generate 10 UI variations each. Cherry-pick the best.*

---

### 02 — The Commissioning Swarm
**Parallel execution**

All trades on site simultaneously — each owns a separate zone.

- Multiple subagents run simultaneously on clearly partitioned scopes
- Deeply specific scope per subagent with verifiable acceptance criteria
- **No shared files.** If two subagents must edit the same file, use a different pattern

Good fits: building multiple independent app components, writing tests for different modules, porting pages between frameworks.

---

### 03 — Commissioning Phases
**Large projects**

Each phase signs off before the next one starts.

```
Phase 1 — Map systems, define acceptance criteria
Phase 2 — Multiple subagents work in parallel (functional testing)
Phase 3 — Cross-system checks, failure mode tests
Phase 4 — Handover & documentation, sign-off
```

Perfect for full app rebuilds or large refactors.

---

### 04 — The Test-and-Handoff Pipeline
**Long-horizon tasks**

Sequential work orders — state lives in files, not memory.

- Each subagent does one bounded job, validates it, then hands off to the next
- State lives in files and task queues — not in conversation history
- Do not drag unrelated prior context through a single giant thread

Best for: research pipelines, hardware bring-up, multi-step deployments.

---

### 05 — The Independent Witness
**Always. Layer on top of everything.**

Separate the installer from the inspector.

- The subagent that writes code is never the same one that verifies it
- One builder works; one or more verifiers run tests independently
- If a verifier flags an issue, the builder is respawned with the specific failure
- Nothing is accepted without a signed test result

---

## Builder vs. Verifier Loop

```
Install → Witness test → Fail? Respawn with defect list → Rectify & retest → ✓ Accepted
```

| Role | Responsibility |
|------|---------------|
| 🔨 Builder / Installer | Writes code, configures systems, generates outputs. Does not participate in verification. |
| 🔍 Commissioning Witness | Runs tests, checks outputs against acceptance criteria, records results. Does not touch the installation. |

This is the difference between "it runs" and "it actually works."

---

## Key Takeaways

- **Break problems into scoped, verifiable work orders.** Each subagent gets minimum viable context for one task.
- **Delegate precisely.** The orchestrator's only tool is `delegate_task`.
- **Accept nothing without evidence it works.** Every output needs a signed test result.
- **Always layer on Pattern 05.** The independent witness signs everything off.

> "You're not writing prompts anymore. You're managing a commissioning crew."

---

## Further Reading

- [Codex & Codex Spark best practices](https://www.cerebras.ai/blog/codex-spark-best-practices)
- [Factory.ai — Phased mission architecture](https://factory.ai/news/missions)
- [MoonshotAI — Kimi-K2.5 swarm training](https://huggingface.co/moonshotai/Kimi-K2.5)
