# CURIOSITY ENGINE PERSONALIZATION & RANKING ENGINE EXECUTION 08 — BUILD GENERAL-BY-DEFAULT TOPIC MIXES + DIVERSITY + UNEXPECTED DISCOVERY + EXPLAINABLE LOCAL RANKING

## Execution Identity

- **Execution:** Curiosity Engine Personalization & Ranking Engine Execution 08
- **Edition:** Personal Terminal Edition V1
- **Wave:** Wave 2 — Parallel
- **Dependencies:** Execution 02 = YES
- **May run in parallel with:** Execution 04 and Execution 11
- **Canonical write scope:** `src/curiosity/ranking/`, profile commands/tests
- **Prompt version:** Personal Terminal Edition V1 / Execution Pack O1
- **Created:** 3 September 2026
- **Purpose:** Implement user-controlled specialization without an addictive opaque feed: topic weights, depth/style preferences, diversity, novelty, repetition penalties, and explainable ranking.
- **Self-contained:** Yes. Read the shared files when present, but this Execution embeds the operating discipline needed to run independently.
- **Target coding harness:** Claude Code CLI, Codex CLI, OpenCode CLI, Anti-Gravity, or another repository-capable coding agent.

# PARENT LOOP — EXECUTION GOAL

## Main Goal

Deliver the **Personalization & Ranking Engine** as one coherent, repository-native capability for the Personal Terminal Edition. Every Child Loop must reach `YES`, the integrated engine must preserve shared contracts and local-first/provider-neutral invariants, and fresh final-state verification must support the complete Goal.

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

# PARENT LOOP — BASELINE GATE

Before Child Loop 1:

- inspect `git status`, branch/worktree state, root instructions, package configuration, migrations, tests, and existing architecture;
- verify that declared dependency Executions are actually present in repository reality; do not trust a report alone;
- locate canonical owners relevant to ``src/curiosity/ranking/`, profile commands/tests`;
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

# CHILD LOOP — TASK 1: Implement Local Profile and Topic Mix

## Task Source Requirement

The product is general and customizable. A profile may blend many topics and reserve a controlled portion for unexpected discovery.

Required outcomes:

- Create default general profile with transparent topic mix.
- Support user-defined weighted topics and exclusions through CLI.
- Support depth and curiosity-style preferences without forcing one domain.
- Validate/normalize weights and preserve user intent when totals do not equal 100.
- Persist `unexpected_discovery_weight` with a safe default and allow zero.

## Objective

Implement **Implement Local Profile and Topic Mix** as a coherent capability integrated with canonical owners. Preserve the functional intent above while adapting details to verified repository architecture.

## Final Goal for This Child Loop

An independent reviewer can inspect the final repository and fresh evidence and conclude that **Implement Local Profile and Topic Mix** works end-to-end, handles the stated failure boundaries, preserves shared architecture contracts, and leaves no unjustified duplicate ownership or placeholder-only implementation.

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

- CLI can create/show/edit a mixed profile including a non-programming topic.
- Invalid/negative weights fail clearly.
- Profile persists across process restart.
- No account/cloud identity is introduced.

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

# CHILD LOOP — TASK 2: Implement Explainable Candidate Scoring

## Task Source Requirement

Personal release ranking should begin with an explicit scoring function, not a trained recommender. Ranking reasons must be inspectable and deterministic under a seed.

Required outcomes:

- Score bounded candidate sets using interest match, knowledge quality, novelty, curiosity quality, diversity pressure, freshness, source quality, and repetition penalties.
- Keep weights configurable and versioned.
- Return reason codes/score components with selection; do not hide logic in an LLM prompt.
- Never use raw time-on-screen as the optimization objective.
- Avoid full-corpus scoring on each 10-second tick; prefetch a candidate queue.

## Objective

Implement **Implement Explainable Candidate Scoring** as a coherent capability integrated with canonical owners. Preserve the functional intent above while adapting details to verified repository architecture.

## Final Goal for This Child Loop

An independent reviewer can inspect the final repository and fresh evidence and conclude that **Implement Explainable Candidate Scoring** works end-to-end, handles the stated failure boundaries, preserves shared architecture contracts, and leaves no unjustified duplicate ownership or placeholder-only implementation.

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

- Unit fixtures prove each major score component can affect ordering.
- Same seed/profile/corpus yields deterministic ranking.
- Reason codes explain why a card was selected.
- Performance test confirms bounded candidate ranking, not full-corpus model reranking.

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

# CHILD LOOP — TASK 3: Implement Diversity, Repetition, and Unexpected Discovery Policy

## Task Source Requirement

Personalization must not collapse into a filter bubble or repetitive feed.

Required outcomes:

- Enforce configurable maximum consecutive same-topic/source/sequence repetition.
- Track exposures and penalize recently shown cards/atoms/sources.
- Reserve unexpected-discovery slots from quality-qualified content outside dominant topic weights.
- Do not use random discovery to bypass verification/quality gates.
- Provide deterministic test mode with seeded RNG/clock.

## Objective

Implement **Implement Diversity, Repetition, and Unexpected Discovery Policy** as a coherent capability integrated with canonical owners. Preserve the functional intent above while adapting details to verified repository architecture.

## Final Goal for This Child Loop

An independent reviewer can inspect the final repository and fresh evidence and conclude that **Implement Diversity, Repetition, and Unexpected Discovery Policy** works end-to-end, handles the stated failure boundaries, preserves shared architecture contracts, and leaves no unjustified duplicate ownership or placeholder-only implementation.

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

- Synthetic corpus test shows dominant topic does not occupy every slot when unexpected discovery > 0.
- Recently exposed card is not immediately repeated unless corpus is exhausted and policy explicitly allows fallback.
- Diversity constraints never select rejected/unverified content.
- Seeded selection is reproducible.

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

- User can configure a topic mix and see it reflected in ranked fixture output.
- Selection exposes reason codes and preserves deterministic testability.
- Unexpected discovery is controlled, quality-gated, and configurable.

# PARENT GOAL GATE

Answer exactly:

**HAVE WE ACHIEVED THE PARENT EXECUTION GOAL FOR PERSONALIZATION & RANKING ENGINE? — YES / PARTIALLY / NO**

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
