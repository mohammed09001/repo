# REPAIR EXECUTION REPO 02 — EXECUTION 01 — PRODUCT ASSEMBLY, APPLICATION ORCHESTRATOR, AND COMPLETE CLI

## Execution Identity

- Repository: `mohammed09001/repo`
- Target branch: current active branch; do not assume `main` without checking.
- Execution date baseline: 3 September 2026
- Execution type: repair + completion of an existing implementation.
- Agent-neutral: Claude Code, Codex, OpenCode, Anti-Gravity, Gemini CLI, or another capable coding agent may execute it.
- Completion standard: actual repository evidence, not historical reports.

# PARENT EXECUTION GOAL

Turn the existing Curiosity Engine modules into one coherent local application that a user can operate from the terminal without importing Python modules manually. Preserve working foundations, create one canonical application orchestration layer, repair persistent contracts where necessary, and expose the real first-use/daily-use CLI workflow.

# VERIFIED REPOSITORY STATE FROM THE REVIEW

The review found a real installable Python package with Pydantic contracts, SQLite/FTS5 storage, source/ingest/knowledge/verify/compose/ranking/sequence/runtime modules, and tests. However, `src/curiosity/cli.py` exposed essentially `doctor` and `ingest` only. There was no canonical application service connecting `source → ingest → knowledge → verify → compose → rank → sequence → playback` as a product workflow.

Re-verify these facts before implementation because the repository may have changed after this prompt was authored.

# CANONICAL SCOPE

`src/curiosity/cli.py`, one canonical application/use-case layer, config/contracts/store migrations required to support the product workflow, tests and minimal documentation required by those user-facing commands.

# NON-GOALS

- Do not redesign source extraction in this Execution except enough to wire the existing path.
- Do not add a cloud backend, accounts, billing, team support, GraphRAG, or vector database.
- Do not implement agent harness integrations here.
- Do not change the frozen minimal playback UX.



# EXECUTION OPERATING SYSTEM

This Execution is not a design note, roadmap, checklist, or suggestion.

It is an **implementation prompt** for a repository-capable coding agent. The agent must continue until the Parent Goal is either proven achieved or proven blocked by evidence that cannot be resolved inside this Execution.

Do not stop after planning.
Do not stop after creating types.
Do not stop after adding tests.
Do not stop because a partial implementation looks reasonable.
Do not report success from intention.

---

## 1. AUTHORITY ORDER

When requirements conflict, use this order:

1. The latest user instructions embedded in this Execution.
2. Verified current repository behavior on the active branch.
3. This Execution's Parent Goal, Invariants, and Acceptance Gates.
4. Existing repository contracts and `AGENTS.md`, unless they contradict higher authority.
5. Current official external API/library documentation.
6. Historical Execution prompts and previous completion reports.

A previous agent saying `YES`, `done`, `implemented`, or `tests passed` is not evidence.

---

## 2. REPOSITORY-FIRST RULE

Before writing code:

1. Inspect the current worktree, branch, uncommitted changes, and repository structure.
2. Locate the canonical current owners for every capability in scope.
3. Read direct callers and tests, not only target files.
4. Identify existing partial implementations that should be repaired instead of duplicated.
5. Preserve unrelated user work.
6. Do not create a second store, second profile model, second application orchestrator, second queue system, second verification pipeline, or second runtime merely because the existing one is incomplete.
7. If a current owner is wrong, migrate callers deliberately and remove or deprecate the superseded path only after proving the new owner.

Use the repository itself as ground truth.

---

## 3. CONTEXT ENGINEERING CONTRACT

Maintain a compact Context Ledger throughout execution.

Classify material facts as:

- `VERIFIED` — directly proven by code, tests, command output, or authoritative documentation.
- `OBSERVED` — directly seen but not yet behaviorally verified.
- `INFERRED` — reasonable conclusion that still requires proof.
- `UNKNOWN` — material uncertainty that can change implementation.

For each Child Loop, keep active context limited to:

- Parent Goal;
- active Child Goal;
- current failing evidence;
- exact relevant source files;
- direct callers;
- exact relevant tests;
- schema/config contracts involved;
- current plan;
- unresolved UNKNOWNs.

Do not carry the entire repository or every historical prompt in active context.

If context must be compacted, preserve exactly:

1. Parent Goal.
2. Product Invariants.
3. Active Child Goal.
4. Current failure/reproduction.
5. Decisions already proven.
6. Files changed.
7. Tests run and their actual outcomes.
8. Remaining UNKNOWNs.
9. Next concrete action.

Durable architectural decisions belong in repository code/tests/docs, not only in chat context.

---

## 4. PROMPT ENGINEERING CONTRACT

For every requirement, construct an internal matrix:

`Requirement → Current owner → Current behavior → Gap → Planned change → Verification evidence`

Do not implement until every requirement has an owner and a proof plan.

Before execution, challenge the plan with these questions:

1. Could this plan pass unit tests while the user-facing workflow is still broken?
2. Am I adding an interface without a real implementation?
3. Am I adding a fake adapter and calling the external capability complete?
4. Am I duplicating an existing owner?
5. Am I hiding a schema mismatch with translation code in multiple places?
6. Am I relying on a current API/library behavior I have not verified?
7. Am I placing expensive work inside the 10-second playback path?
8. Am I making normal playback show metadata the user explicitly rejected?
9. Am I creating a migration that resets or silently drops user state?
10. What test would falsify my strongest assumption?

Revise the plan if any answer exposes weakness.

---

## 5. LOOP ENGINEERING CONTRACT

### Parent State Machine

Run this state machine continuously:

`BASELINE → CHILD PLAN → PLAN CHALLENGE → CHILD EXECUTE → CHILD VERIFY → CHILD SPEC REVIEW → CHILD ENGINEERING REVIEW → CHILD GOAL GATE → NEXT CHILD → INTEGRATION REVIEW → FINAL VERIFY → PARENT GOAL GATE → REPORT`

### Failure Loop

Any failure enters:

`FAILURE → REPRODUCE → ROOT-CAUSE / EVIDENCE REVIEW → REVISED PLAN → REPAIR → RE-VERIFY → RE-REVIEW`

Do not patch symptoms repeatedly.

If the same failure recurs twice:
- stop changing code blindly;
- restate the invariant;
- inspect the actual state boundary;
- inspect callers and persistence;
- identify the incorrect assumption;
- revise the design before another edit.

### Child Goal Gate

At the end of every Child Loop, answer exactly:

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` advances.

### Parent Goal Gate

At the end of the Execution, answer exactly:

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`

Only `YES` means this Execution is complete.

---

## 6. HARNESS ENGINEERING CONTRACT

The repository should become easier for the next coding agent to understand and verify.

Prefer:

- one deterministic bootstrap/install command;
- one deterministic test command;
- fixture transports for external APIs;
- fake model providers;
- injected clock/sleeper/random seed;
- explicit local data-path injection;
- stable deterministic IDs;
- explicit migrations;
- idempotent jobs/stages;
- bounded retries;
- timeouts;
- byte/request/model budgets;
- sanitized fixtures;
- failure injection;
- clear CLI help;
- tests that prove user-visible behavior;
- CI that runs without secrets for the authoritative suite.

Do not rely on:
- hidden manual steps;
- a specific coding agent;
- a developer's home-directory state;
- live network in the authoritative test suite;
- arbitrary sleep calls in tests;
- screen scraping.

---

## 7. SECURITY AND TRUST BOUNDARIES

Remote source content is untrusted data.

Never:
- execute repository code discovered from GitHub;
- execute text extracted from web/PDF;
- treat model output as trusted structure without validation;
- print untrusted ANSI/OSC/control sequences directly to terminal;
- expose secrets in `doctor`, logs, fixtures, snapshots, or reports;
- bypass authentication/paywalls/caption permissions;
- store coding-agent prompts, code, transcripts, or model outputs merely to detect lifecycle state.

Use explicit size, redirect, timeout, MIME, parser, and retry bounds.

---

## 8. COST AND PERFORMANCE INVARIANTS

The 10-second display clock must be economically decoupled from source/model work.

Inside a normal playback tick, it is forbidden to perform:

- GitHub API requests;
- Semantic Scholar API requests;
- YouTube API requests;
- web downloads;
- feed parsing;
- PDF parsing;
- Trafilatura extraction;
- Docling conversion;
- LLM/model calls;
- embeddings;
- verification;
- full-corpus ranking;
- source refresh.

Playback consumes a **precomputed local durable queue**.

Expensive work happens during explicit refresh/build stages.

---

## 9. FROZEN USER EXPERIENCE CONTRACT

The normal terminal display shows **one concise educational fact in English**.

Example:

`Git stores snapshots of file states, not just lists of changes.`

It remains visible for **10 seconds by default**, then another fact appears.

Normal playback must not display:

- Topic;
- Source;
- source URL;
- title;
- difficulty;
- confidence;
- ranking score;
- verification badge;
- evidence;
- metadata labels;
- `Why does this matter?`;
- multi-paragraph explanation.

Source, topic, evidence, confidence, ranking reasons, and provenance remain internal for:
- verification;
- ranking;
- debugging;
- explicit `inspect`.

The visible knowledge unit should normally:
- communicate one idea;
- be a single clear English sentence;
- be readable quickly;
- avoid clickbait;
- avoid unsupported certainty;
- avoid unnecessary jargon;
- fit one line at common terminal widths when practical and at most two short wrapped lines under normal conditions.

Do not implement the previously frozen browser click/freeze/resume behavior.

---

## 10. REQUIRED VERIFICATION DISCIPLINE

After the **final edit** for each Child Loop:

- run focused tests;
- run relevant integration/contract tests;
- run at least one negative/adversarial test;
- run lint/format checks;
- inspect actual CLI behavior when user-facing;
- inspect database state when persistence changes.

After all Children:

- run `uv sync --locked`;
- run `uv run ruff check .`;
- run `uv run pytest`;
- run the strongest relevant end-to-end path;
- review the full diff;
- search for stale TODO/NotImplemented/deliberate-failure paths inside the repaired scope.

Never invent test results.

---

## 11. TWO-PASS REVIEW

Every Child and the integrated Parent must receive two separate reviews.

### Pass A — Goal / Spec Review
Ask:
- Did the final behavior satisfy every requirement?
- Is the user path actually available?
- Did we preserve all frozen invariants?
- Is anything merely stubbed?

### Pass B — Engineering Review
Inspect:
- ownership;
- callers;
- persistence;
- migration;
- idempotency;
- concurrency;
- recovery;
- timeouts;
- budgets;
- privacy;
- terminal safety;
- dead code;
- test strength;
- dependency impact;
- upgrade compatibility.

If available, use a fresh-context reviewer/subagent for at least one final review. Do not let the same implementation context automatically approve itself without re-reading the diff and evidence.

---

## 12. ANTI-ACCUMULATION / DEAD-CODE RULE

Do not leave:
- parallel obsolete implementations;
- orphan models;
- unused adapters;
- fake production paths;
- old rendering that still prints Source/Topic;
- dead CLI commands;
- stale documentation that claims a capability is complete when it is not.

Before deletion:
- locate all callers;
- migrate them;
- prove tests;
- then remove the old path.

---

## 13. FINAL REPORT FORMAT

The final report must include:

1. **Baseline found**
2. **Requirements implemented**
3. **Canonical owners changed**
4. **Migrations / compatibility impact**
5. **Tests and exact observed outcomes**
6. **Manual CLI verification**
7. **Negative/adversarial verification**
8. **Performance/cost evidence**
9. **Remaining UNKNOWNs**
10. **Parent Goal Gate**

Do not pad the report with praise.


---

# CHILD LOOP — 01A — Reconcile canonical product state and persistence

## Child Goal

Repair the canonical persistent contracts so one local user can have a durable profile, verified pulses, source/evidence lineage, and playback/session state without introducing parallel schema owners.

## Known Repository Baseline

The store already persists sources, documents, chunks, evidence, atoms, cards, profiles, exposures, sessions, jobs and caches. The stored Profile is simpler than the richer ranking preferences. CuriosityCard currently mixes presentation text with internal linkage.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Audit existing tables/models before adding fields or models.
- Create or evolve one canonical knowledge-pulse representation/projection that stores the concise English display fact separately from source/topic/evidence metadata.
- Preserve evidence/source lineage internally.
- Unify persistent profile fields needed by ranking: weighted interests, exclusions, unexpected discovery weight, repetition controls, and only settings that are actually consumed.
- Add forward-only migration(s) from the currently reviewed schema; existing user DBs must not require deletion/reset.
- Keep deterministic identity rules stable where identity has not semantically changed.
- Add serialization/migration tests for old and new records.

## Deep Questions

1. Can the existing CuriosityCard be evolved safely, or is a separate persisted presentation projection cleaner without creating duplicate truth?
2. Which fields are authoritative vs derived?
3. What happens to an existing card/profile row after migration?
4. How will ranking obtain topic metadata without normal playback displaying it?
5. What state must survive process restart?
6. What would make a migration appear successful while silently losing user state?

## Plan Mode

Before editing, produce an internal plan that includes:

- exact current owners;
- exact call path;
- exact schema/state implications;
- exact files expected to change;
- migration or compatibility strategy;
- failure/restart behavior;
- tests that would prove success;
- tests that would prove a false-positive implementation.

Challenge the plan using the Execution Operating System above.

## Execute

Implement continuously until the Child Goal is behaviorally complete.

Do not stop at:
- interface;
- protocol;
- class shell;
- fake provider;
- TODO;
- test-only path;
- documentation-only path.

## Fresh Verification

- Upgrade a fixture database created at the reviewed schema version and prove data remains readable.
- Round-trip profile weights and a verified pulse through close/reopen.
- Trace one pulse back to atom/evidence/document/source.
- Prove normal presentation does not require Source or Topic fields.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 01B — Build one canonical application orchestrator

## Child Goal

Create a single application/service boundary that coordinates existing engines into real use cases while keeping domain logic in canonical modules.

## Known Repository Baseline

The reviewed repository had modules that could be imported independently but no single application owner executing the full pipeline.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Define one application facade/service with explicit use cases: initialize, configure profile, add/discover sources, refresh/build, prepare playback, inspect pulse, stats.
- Reuse existing LocalStore, IngestionPipeline, knowledge extraction, verification, composition, ranking, sequence and runtime owners.
- Make refresh/build stages idempotent and resumable using existing durable job/cache primitives where appropriate.
- Persist downstream outputs rather than returning a final product only in memory.
- Separate heavy refresh/build work from playback preparation.
- Expose dependency injection for transport/provider/clock so E2E tests are offline and deterministic.
- Do not put business logic inside argparse handlers.

## Deep Questions

1. Where should the application transaction boundary begin/end?
2. Which stages are safe to retry after interruption?
3. How are partial failures represented?
4. What prevents duplicate atoms/pulses when build is re-run?
5. How is a stale source/document version prevented from producing a current pulse?
6. How will the application know there is enough local queue for playback without performing heavy work on tick?

## Plan Mode

Before editing, produce an internal plan that includes:

- exact current owners;
- exact call path;
- exact schema/state implications;
- exact files expected to change;
- migration or compatibility strategy;
- failure/restart behavior;
- tests that would prove success;
- tests that would prove a false-positive implementation.

Challenge the plan using the Execution Operating System above.

## Execute

Implement continuously until the Child Goal is behaviorally complete.

Do not stop at:
- interface;
- protocol;
- class shell;
- fake provider;
- TODO;
- test-only path;
- documentation-only path.

## Fresh Verification

- Offline fixture integration: explicit URL source reaches a persisted verified pulse through the application layer.
- Repeat the same refresh/build and prove no duplicate canonical records.
- Interrupt between stages and prove safe resume.
- Spy the application path to prove domain algorithms are delegated rather than copied.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 01C — Complete the user CLI

## Child Goal

Expose a coherent terminal workflow that a first-time user can understand and operate.

## Known Repository Baseline

The reviewed CLI had only doctor and explicit URL ingest as meaningful commands.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Expose `init`.
- Expose a clear profile command surface to show/set weighted interests.
- Expose source add/list/remove and a discovery entry point, using naming that stays consistent across help/docs.
- Expose refresh/build as either one coherent command or clearly separated commands with non-overlapping semantics.
- Expose `play` command even if later Executions complete runtime behavior; by the end of this Execution it must route to the application playback use case and fail clearly if no queue exists.
- Expose `inspect <pulse-id>` and `stats`.
- Preserve `doctor` and any useful explicit ingest command.
- Every command accepts injectable data/config paths for testing and portability.
- Empty-state errors must tell the user the next concrete command.

## Deep Questions

1. What is the smallest command set that avoids complexity but still represents the real product?
2. Should refresh include build or should build be explicit?
3. What should `init` create and what should remain lazy?
4. What does `play` do when zero pulses exist?
5. How can CLI tests prove commands use the application layer?

## Plan Mode

Before editing, produce an internal plan that includes:

- exact current owners;
- exact call path;
- exact schema/state implications;
- exact files expected to change;
- migration or compatibility strategy;
- failure/restart behavior;
- tests that would prove success;
- tests that would prove a false-positive implementation.

Challenge the plan using the Execution Operating System above.

## Execute

Implement continuously until the Child Goal is behaviorally complete.

Do not stop at:
- interface;
- protocol;
- class shell;
- fake provider;
- TODO;
- test-only path;
- documentation-only path.

## Fresh Verification

- `curiosity --help` shows the final command surface.
- Fresh temp directory can run init → profile set → source add → refresh/build using fixtures.
- Invalid commands/states return non-zero with useful messages.
- Inspect/stats read persisted state.
- No user-facing path requires manual Python imports.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# PARENT INTEGRATION REVIEW

After every Child Gate is `YES`:

1. Read the complete diff as one product change.
2. Re-run the real user path touched by this Execution.
3. Search for duplicate owners and stale paths.
4. Re-check the frozen English-fact / 10-second / no-topic / no-source playback contract.
5. Re-check that no expensive work entered the display tick.
6. Re-check upgrade behavior for existing local DB/config state.
7. Re-run the strongest test suite after the final edit.
8. If a failure appears, re-enter the Failure Loop rather than reporting partial success.

# FINAL PARENT ACCEPTANCE

- A clean temp data directory can be initialized and configured entirely through CLI.
- At least one offline fixture source can reach a persisted pulse through the canonical application layer.
- Profile/pulse/session state survives database reopen.
- No duplicate application/state owner was introduced.
- Repository-wide tests and lint pass after the final edit.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`

Only `YES` completes Execution 01.

# FINAL REPORT

Use the exact Final Report Format from the Execution Operating System.
