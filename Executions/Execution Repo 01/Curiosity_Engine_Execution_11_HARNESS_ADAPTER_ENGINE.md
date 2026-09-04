# CURIOSITY ENGINE HARNESS ADAPTER ENGINE EXECUTION 11 — ADD OPTIONAL CLAUDE CODE + OPENCODE + CODEX LIFECYCLE ADAPTERS WITHOUT COUPLING THE PRODUCT TO THEM

## Execution Identity

- **Execution:** Curiosity Engine Harness Adapter Engine Execution 11
- **Edition:** Personal Terminal Edition V1
- **Wave:** Wave 2 — Parallel
- **Dependencies:** Execution 10 = YES
- **May run in parallel with:** Execution 04 and Execution 08
- **Canonical write scope:** `src/curiosity/harness/`, adapter installer/config docs/tests
- **Prompt version:** Personal Terminal Edition V1 / Execution Pack O1
- **Created:** 3 September 2026
- **Purpose:** Provide thin optional local lifecycle integrations so Curiosity can respond to supported coding-agent activity while preserving standalone behavior and minimizing captured data.
- **Self-contained:** Yes. Read the shared files when present, but this Execution embeds the operating discipline needed to run independently.
- **Target coding harness:** Claude Code CLI, Codex CLI, OpenCode CLI, Anti-Gravity, or another repository-capable coding agent.

# PARENT LOOP — EXECUTION GOAL

## Main Goal

Deliver the **Harness Adapter Engine** as one coherent, repository-native capability for the Personal Terminal Edition. Every Child Loop must reach `YES`, the integrated engine must preserve shared contracts and local-first/provider-neutral invariants, and fresh final-state verification must support the complete Goal.

This is not a design-only task. The result must be usable code, tests, configuration, migration/state behavior where applicable, and concise operator documentation.

## Parent Loop State Machine

`BASELINE → CHILD PLAN → CHILD EXECUTE → CHILD VERIFY → CHILD REVIEW → CHILD GOAL GATE → NEXT CHILD → INTEGRATION REVIEW → FINAL VERIFY → PARENT GOAL GATE → REPORT`

On material failure:

`FAILURE → REPRODUCE → ROOT-CAUSE / EVIDENCE REVIEW → REVISED PLAN → REPAIR → RE-VERIFY → RE-REVIEW`

Do not skip forward to manufacture a positive completion narrative.

# EXECUTION CONTRACT — APPLIES TO THIS FILE

Read and apply, when present:
1. `Product Definition.md`
2. `Shared Architecture Contract.md`
3. `Execution Contract.md`
4. `Parallel Execution Protocol.md`
5. `Research Basis.md`
6. repository `AGENTS.md` and scoped instructions.

### Repository-first
Inspect the real repository, worktree, existing owners, tests, dependencies, and prior implementation before adding code.

### Context engineering
Build a bounded context ledger: `VERIFIED / OBSERVED / INFERRED / UNKNOWN`. Retrieve targeted context; do not fill the context window with irrelevant repository text. Preserve durable decisions in code/contracts/tests.

### Prompt discipline
Treat requirements as testable contracts. Explicitly map requirement → owner → implementation → evidence. Do not silently weaken a requirement because implementation is inconvenient.

### Harness engineering
Prefer deterministic commands, fixtures, fake adapters, stable IDs, idempotent operations, timeouts, budgets, structured diagnostics, and one-command verification. Maintain provider-neutral behavior.

### Parallel safety
Respect this Execution's canonical write scope. If a shared contract must change, serialize that change and update contract tests; do not create a local shadow contract.

### Anti-hallucination / no-sycophancy
Never invent current API behavior, test results, files, schemas, or completion. Agreement is not evidence.

### Efficiency
No AI inference or remote fetch may be placed in the 10-second display tick. Deduplicate/cache before expensive work.

### Verification
No success claim is valid without fresh verification after the final relevant edit.

## Engine Invariants

- Local-first single-user release.
- No commercial/account/billing/cloud multi-tenant infrastructure.
- No GraphRAG or dedicated graph database.
- No mandatory external vector database.
- Provider-specific code remains behind adapters.
- Raw source/evidence truth is not mutated by derived knowledge or presentation layers.
- Remote text is untrusted and must not execute.
- The frozen browser/source-click pause/resume feature remains out of scope.

Additional invariants:
- Adapters capture lifecycle state only; no prompt/output/code surveillance in this release.
- Native integration is preferred over screen scraping.

# PARENT LOOP — BASELINE GATE

Before Child Loop 1:

- inspect `git status`, branch/worktree state, root instructions, package configuration, migrations, tests, and existing architecture;
- verify that declared dependency Executions are actually present in repository reality; do not trust a report alone;
- locate canonical owners relevant to ``src/curiosity/harness/`, adapter installer/config docs/tests`;
- identify pre-existing failures that could contaminate verification;
- inspect external API/library docs only when current behavior materially affects this execution;
- record any shared-contract conflict before implementation.

### Parent Baseline Questions

- What proves the dependency baseline?
- Which module currently owns this engine's responsibility?
- Which public/domain contracts must remain stable?
- Which unrelated user changes must be preserved?
- What is the highest-risk false assumption?
- What would make it dishonest or unsafe to continue?

Do not ask the user for facts the repository or authoritative documentation can answer.

---

# CHILD LOOP — TASK 1: Freeze Harness Event Contract and Standalone Fallback

## Task Source Requirement

Harness integrations enrich ambient behavior; they are not required for knowledge, ranking, sequencing, or playback.

Required outcomes:

- Implement HarnessEvent adapter protocol with minimal lifecycle states such as working/idle/turn_complete/session_start/session_end when available.
- Normalize timestamps/adapter identity and minimize payload; never require prompts, tool outputs, or source code.
- Unknown/unsupported events degrade safely.
- Standalone `curiosity play` remains the guaranteed fallback.
- Adapter failure must not corrupt core DB or stop unrelated ingestion.

## Objective

Implement **Freeze Harness Event Contract and Standalone Fallback** as a coherent capability integrated with canonical owners. Preserve the functional intent above while adapting details to verified repository architecture.

## Final Goal for This Child Loop

An independent reviewer can inspect the final repository and fresh evidence and conclude that **Freeze Harness Event Contract and Standalone Fallback** works end-to-end, handles the stated failure boundaries, preserves shared architecture contracts, and leaves no unjustified duplicate ownership or placeholder-only implementation.

## Phase A — Ground Truth / Context

Before coding:
- inspect current implementation, callers, tests, configuration, persistence, migrations, and external boundaries relevant to this Task;
- verify predecessors and current API/library behavior when version-sensitive;
- identify canonical owners and consumers;
- classify material findings `VERIFIED / OBSERVED / INFERRED / HYPOTHESIZED / UNKNOWN`;
- establish the smallest context set needed for a defensible plan;
- identify pre-existing failures;
- search for existing code before adding dependencies or abstractions.

Do not edit implementation code until enough evidence exists for a defensible plan.

## Phase B — Deep Questions That Must Be Answered

1. What is VERIFIED from the repository now, what is only required by this Execution, what is INFERRED, and what remains UNKNOWN?
2. Who currently owns this responsibility, and is there an existing partial/duplicate/legacy implementation to reuse, repair, migrate, or remove?
3. Which assumption would most damage correctness if false, and what evidence can falsify it before implementation?
4. What could look complete while still passing only narrow happy-path tests?
5. Which identity, persistence, concurrency, privacy, trust, compatibility, or recovery boundary can this change accidentally violate?
6. What final-state evidence is required to prove the Goal without trusting the implementing agent's narrative?
7. Can any model call, network call, new dependency, abstraction, or persistent state be removed while preserving the Goal?
8. What happens when the external dependency is slow, malformed, unavailable, rate-limited, or returns partial data?
9. What must be idempotent so rerunning after interruption does not duplicate work or cost?
10. Which data is authoritative, which is derived, and where could the implementation accidentally collapse that distinction?
11. What is the smallest end-to-end implementation that is actually usable instead of a disconnected framework or set of types?
12. Which negative/adversarial case is most likely to falsify the claim that this Child is complete?

## Phase C — Plan Mode

Create an evidence-based plan before editing.

The plan must:
- map every material requirement to files/owners and expected evidence;
- identify what is reused, extended, replaced, or removed;
- identify data/provenance/idempotency/failure/compatibility invariants;
- define tests before implementation;
- include migration/restart/recovery behavior when state changes;
- include budget/timeouts for remote/model work;
- remain the smallest coherent plan.

### Plan Challenge

Attempt to falsify the plan:
- Does it depend on an unverified API or library behavior?
- Does it create a second source of truth?
- Does it place expensive work on an interactive path?
- Does it omit partial failure/restart/idempotency?
- Does it make an optional provider mandatory?
- Does it create a framework without a complete user-visible path?
- Would a simpler extension of a canonical owner achieve the Goal?

Revise the plan if challenged successfully.

## Phase D — Execute

Implement the plan.

- Deliver working behavior, not TODOs or disconnected types.
- Keep authoritative source/evidence separate from derived/presentation data.
- Validate all external/provider payloads.
- Apply bounded concurrency, timeouts, retry policies, and budgets.
- Keep changes within the canonical scope except strictly necessary contract/integration changes.
- If a predecessor is incomplete, repair only the minimum safe prerequisite or expose the blocker truthfully.
- Do not add speculative extensibility whose first consumer does not exist.

## Phase E — Verification

Fresh final-state evidence must include:

- Fake adapter events normalize correctly.
- Payload minimization test rejects/strips prompt/code fields if an adapter accidentally supplies them.
- Unknown adapter/event does not crash runtime.
- Core playback test passes with all harness adapters disabled.

Also:
- run lint/format/type/static checks configured for the repository;
- run focused unit and integration tests;
- run at least one negative/adversarial case;
- rerun the strongest relevant checks after the last code edit;
- inspect actual outputs when claims concern provenance, ordering, persistence, deduplication, budgets, or terminal behavior.

For each material claim, state what the evidence proves and what it does not prove.

## Phase F — Review

### Goal/Spec Review
Compare the final diff and evidence clause-by-clause against this Task requirement. Search for omitted clauses, silently weakened behavior, accidental ownership shifts, and unsupported completion claims.

### Engineering Review
Inspect callers, data transitions, error handling, concurrency, resource limits, security/privacy, performance, compatibility, tests, dead code, duplicate ownership, and migration/restart behavior.

Prefer a fresh-context reviewer/subagent when supported, with bounded scope and no authority to mutate unrelated modules.

## Phase G — Repair Loop

If verification/review fails:
1. do not advance;
2. reproduce;
3. determine verified root cause or preserve uncertainty;
4. revise the same Task plan;
5. apply the smallest responsible repair;
6. re-run verification and both reviews;
7. repeat until `YES` or a genuine external blocker remains.

Do not stack speculative patches.

## Phase H — Child Final Goal Gate

**HAVE WE ACHIEVED THE FINAL GOAL FOR TASK 1? — YES / PARTIALLY / NO**

Advance only on `YES`.


---

# CHILD LOOP — TASK 2: Implement Claude Code and OpenCode Native Adapters

## Task Source Requirement

Claude Code provides local status-line/hooks; OpenCode plugins expose session.status/session.idle and other events. Use documented native surfaces rather than screen scraping.

Required outcomes:

- Claude adapter installer must be explicit and reversible; preserve existing user statusline/hooks configuration instead of overwriting blindly.
- Claude integration may query local Curiosity state from a fast command/cache; keep status-line execution fast and never trigger source/model work.
- OpenCode plugin subscribes only to required lifecycle events and sends minimized local HarnessEvents.
- Both adapters are optional feature modules.
- Document exactly what each adapter can/cannot detect.

## Objective

Implement **Implement Claude Code and OpenCode Native Adapters** as a coherent capability integrated with canonical owners. Preserve the functional intent above while adapting details to verified repository architecture.

## Final Goal for This Child Loop

An independent reviewer can inspect the final repository and fresh evidence and conclude that **Implement Claude Code and OpenCode Native Adapters** works end-to-end, handles the stated failure boundaries, preserves shared architecture contracts, and leaves no unjustified duplicate ownership or placeholder-only implementation.

## Phase A — Ground Truth / Context

Before coding:
- inspect current implementation, callers, tests, configuration, persistence, migrations, and external boundaries relevant to this Task;
- verify predecessors and current API/library behavior when version-sensitive;
- identify canonical owners and consumers;
- classify material findings `VERIFIED / OBSERVED / INFERRED / HYPOTHESIZED / UNKNOWN`;
- establish the smallest context set needed for a defensible plan;
- identify pre-existing failures;
- search for existing code before adding dependencies or abstractions.

Do not edit implementation code until enough evidence exists for a defensible plan.

## Phase B — Deep Questions That Must Be Answered

1. What is VERIFIED from the repository now, what is only required by this Execution, what is INFERRED, and what remains UNKNOWN?
2. Who currently owns this responsibility, and is there an existing partial/duplicate/legacy implementation to reuse, repair, migrate, or remove?
3. Which assumption would most damage correctness if false, and what evidence can falsify it before implementation?
4. What could look complete while still passing only narrow happy-path tests?
5. Which identity, persistence, concurrency, privacy, trust, compatibility, or recovery boundary can this change accidentally violate?
6. What final-state evidence is required to prove the Goal without trusting the implementing agent's narrative?
7. Can any model call, network call, new dependency, abstraction, or persistent state be removed while preserving the Goal?
8. What happens when the external dependency is slow, malformed, unavailable, rate-limited, or returns partial data?
9. What must be idempotent so rerunning after interruption does not duplicate work or cost?
10. Which data is authoritative, which is derived, and where could the implementation accidentally collapse that distinction?
11. What is the smallest end-to-end implementation that is actually usable instead of a disconnected framework or set of types?
12. Which negative/adversarial case is most likely to falsify the claim that this Child is complete?

## Phase C — Plan Mode

Create an evidence-based plan before editing.

The plan must:
- map every material requirement to files/owners and expected evidence;
- identify what is reused, extended, replaced, or removed;
- identify data/provenance/idempotency/failure/compatibility invariants;
- define tests before implementation;
- include migration/restart/recovery behavior when state changes;
- include budget/timeouts for remote/model work;
- remain the smallest coherent plan.

### Plan Challenge

Attempt to falsify the plan:
- Does it depend on an unverified API or library behavior?
- Does it create a second source of truth?
- Does it place expensive work on an interactive path?
- Does it omit partial failure/restart/idempotency?
- Does it make an optional provider mandatory?
- Does it create a framework without a complete user-visible path?
- Would a simpler extension of a canonical owner achieve the Goal?

Revise the plan if challenged successfully.

## Phase D — Execute

Implement the plan.

- Deliver working behavior, not TODOs or disconnected types.
- Keep authoritative source/evidence separate from derived/presentation data.
- Validate all external/provider payloads.
- Apply bounded concurrency, timeouts, retry policies, and budgets.
- Keep changes within the canonical scope except strictly necessary contract/integration changes.
- If a predecessor is incomplete, repair only the minimum safe prerequisite or expose the blocker truthfully.
- Do not add speculative extensibility whose first consumer does not exist.

## Phase E — Verification

Fresh final-state evidence must include:

- Claude generated config/script fixture merges or refuses safely when conflicting existing config exists.
- Statusline query benchmark stays within a strict local latency target chosen during plan.
- OpenCode event fixtures map session.status/idle correctly.
- Uninstall/disable restores non-integrated behavior without deleting user content.

Also:
- run lint/format/type/static checks configured for the repository;
- run focused unit and integration tests;
- run at least one negative/adversarial case;
- rerun the strongest relevant checks after the last code edit;
- inspect actual outputs when claims concern provenance, ordering, persistence, deduplication, budgets, or terminal behavior.

For each material claim, state what the evidence proves and what it does not prove.

## Phase F — Review

### Goal/Spec Review
Compare the final diff and evidence clause-by-clause against this Task requirement. Search for omitted clauses, silently weakened behavior, accidental ownership shifts, and unsupported completion claims.

### Engineering Review
Inspect callers, data transitions, error handling, concurrency, resource limits, security/privacy, performance, compatibility, tests, dead code, duplicate ownership, and migration/restart behavior.

Prefer a fresh-context reviewer/subagent when supported, with bounded scope and no authority to mutate unrelated modules.

## Phase G — Repair Loop

If verification/review fails:
1. do not advance;
2. reproduce;
3. determine verified root cause or preserve uncertainty;
4. revise the same Task plan;
5. apply the smallest responsible repair;
6. re-run verification and both reviews;
7. repeat until `YES` or a genuine external blocker remains.

Do not stack speculative patches.

## Phase H — Child Final Goal Gate

**HAVE WE ACHIEVED THE FINAL GOAL FOR TASK 2? — YES / PARTIALLY / NO**

Advance only on `YES`.


---

# CHILD LOOP — TASK 3: Implement Codex/Generic Adapter Strategy Without False Capability Claims

## Task Source Requirement

Current Codex config exposes an external notify command after completed turns; this is not a complete busy/idle stream. Do not pretend it is. Generic/unsupported agents rely on standalone playback unless a reliable local signal is available.

Required outcomes:

- Implement Codex completion notifier adapter using documented `notify` configuration only if it can be installed safely and reversibly.
- Represent capability matrix per adapter: can detect start? busy? idle? complete?
- Do not add PTY wrapping/node-pty unless repository evidence and manual qualification prove it is required for the personal release.
- Provide generic manual/standalone mode for Anti-Gravity/future agents.
- Never screen-scrape arbitrary terminal output as a correctness dependency.

## Objective

Implement **Implement Codex/Generic Adapter Strategy Without False Capability Claims** as a coherent capability integrated with canonical owners. Preserve the functional intent above while adapting details to verified repository architecture.

## Final Goal for This Child Loop

An independent reviewer can inspect the final repository and fresh evidence and conclude that **Implement Codex/Generic Adapter Strategy Without False Capability Claims** works end-to-end, handles the stated failure boundaries, preserves shared architecture contracts, and leaves no unjustified duplicate ownership or placeholder-only implementation.

## Phase A — Ground Truth / Context

Before coding:
- inspect current implementation, callers, tests, configuration, persistence, migrations, and external boundaries relevant to this Task;
- verify predecessors and current API/library behavior when version-sensitive;
- identify canonical owners and consumers;
- classify material findings `VERIFIED / OBSERVED / INFERRED / HYPOTHESIZED / UNKNOWN`;
- establish the smallest context set needed for a defensible plan;
- identify pre-existing failures;
- search for existing code before adding dependencies or abstractions.

Do not edit implementation code until enough evidence exists for a defensible plan.

## Phase B — Deep Questions That Must Be Answered

1. What is VERIFIED from the repository now, what is only required by this Execution, what is INFERRED, and what remains UNKNOWN?
2. Who currently owns this responsibility, and is there an existing partial/duplicate/legacy implementation to reuse, repair, migrate, or remove?
3. Which assumption would most damage correctness if false, and what evidence can falsify it before implementation?
4. What could look complete while still passing only narrow happy-path tests?
5. Which identity, persistence, concurrency, privacy, trust, compatibility, or recovery boundary can this change accidentally violate?
6. What final-state evidence is required to prove the Goal without trusting the implementing agent's narrative?
7. Can any model call, network call, new dependency, abstraction, or persistent state be removed while preserving the Goal?
8. What happens when the external dependency is slow, malformed, unavailable, rate-limited, or returns partial data?
9. What must be idempotent so rerunning after interruption does not duplicate work or cost?
10. Which data is authoritative, which is derived, and where could the implementation accidentally collapse that distinction?
11. What is the smallest end-to-end implementation that is actually usable instead of a disconnected framework or set of types?
12. Which negative/adversarial case is most likely to falsify the claim that this Child is complete?

## Phase C — Plan Mode

Create an evidence-based plan before editing.

The plan must:
- map every material requirement to files/owners and expected evidence;
- identify what is reused, extended, replaced, or removed;
- identify data/provenance/idempotency/failure/compatibility invariants;
- define tests before implementation;
- include migration/restart/recovery behavior when state changes;
- include budget/timeouts for remote/model work;
- remain the smallest coherent plan.

### Plan Challenge

Attempt to falsify the plan:
- Does it depend on an unverified API or library behavior?
- Does it create a second source of truth?
- Does it place expensive work on an interactive path?
- Does it omit partial failure/restart/idempotency?
- Does it make an optional provider mandatory?
- Does it create a framework without a complete user-visible path?
- Would a simpler extension of a canonical owner achieve the Goal?

Revise the plan if challenged successfully.

## Phase D — Execute

Implement the plan.

- Deliver working behavior, not TODOs or disconnected types.
- Keep authoritative source/evidence separate from derived/presentation data.
- Validate all external/provider payloads.
- Apply bounded concurrency, timeouts, retry policies, and budgets.
- Keep changes within the canonical scope except strictly necessary contract/integration changes.
- If a predecessor is incomplete, repair only the minimum safe prerequisite or expose the blocker truthfully.
- Do not add speculative extensibility whose first consumer does not exist.

## Phase E — Verification

Fresh final-state evidence must include:

- Codex notifier fixture accepts official JSON event shape and ignores unrelated events.
- Capability matrix truthfully marks unsupported lifecycle states.
- Generic agent scenario remains usable through standalone Curiosity runtime.
- No Node runtime/PTy dependency is introduced unless this execution documents and proves the necessity.

Also:
- run lint/format/type/static checks configured for the repository;
- run focused unit and integration tests;
- run at least one negative/adversarial case;
- rerun the strongest relevant checks after the last code edit;
- inspect actual outputs when claims concern provenance, ordering, persistence, deduplication, budgets, or terminal behavior.

For each material claim, state what the evidence proves and what it does not prove.

## Phase F — Review

### Goal/Spec Review
Compare the final diff and evidence clause-by-clause against this Task requirement. Search for omitted clauses, silently weakened behavior, accidental ownership shifts, and unsupported completion claims.

### Engineering Review
Inspect callers, data transitions, error handling, concurrency, resource limits, security/privacy, performance, compatibility, tests, dead code, duplicate ownership, and migration/restart behavior.

Prefer a fresh-context reviewer/subagent when supported, with bounded scope and no authority to mutate unrelated modules.

## Phase G — Repair Loop

If verification/review fails:
1. do not advance;
2. reproduce;
3. determine verified root cause or preserve uncertainty;
4. revise the same Task plan;
5. apply the smallest responsible repair;
6. re-run verification and both reviews;
7. repeat until `YES` or a genuine external blocker remains.

Do not stack speculative patches.

## Phase H — Child Final Goal Gate

**HAVE WE ACHIEVED THE FINAL GOAL FOR TASK 3? — YES / PARTIALLY / NO**

Advance only on `YES`.

---

# PARENT INTEGRATION REVIEW

After all Child Loops reach `YES`:

- inspect the full engine diff as one unit;
- verify dependency direction and contract compatibility;
- search duplicate owners and stale paths;
- inspect local-startup and restart behavior;
- inspect cost/latency/resource implications;
- confirm no commercial/frozen feature leaked into scope;
- confirm optional dependencies fail soft where required;
- run contract/regression tests for neighboring engines touched.

# FINAL VERIFY

Run the strongest repository-native final-state suite applicable to this engine, including a clean or representative integration path.

Additional engine acceptance requirements:

- Claude and OpenCode adapter paths are fixture-tested and reversible.
- Codex integration does not overclaim lifecycle visibility.
- Disabling every adapter leaves the complete core terminal product usable.

# PARENT GOAL GATE

Answer exactly:

**HAVE WE ACHIEVED THE PARENT EXECUTION GOAL FOR HARNESS ADAPTER ENGINE? — YES / PARTIALLY / NO**

Only `YES` unblocks dependent Executions.

# FINAL REPORT CONTRACT

Report:
1. baseline discovered;
2. implemented capability by Child;
3. files/modules changed;
4. contract/migration changes;
5. exact tests/commands run and observed result;
6. negative cases exercised;
7. efficiency/cost impact;
8. remaining risks/UNKNOWNs;
9. exact dependent Executions now unblocked.

Do not report planned work as completed work.
