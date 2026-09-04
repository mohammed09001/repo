# REPAIR EXECUTION REPO 02 — EXECUTION 04 — PERSISTENT PERSONALIZATION, RANKING, EXPOSURE HISTORY, AND DURABLE SEQUENCING

## Execution Identity

- Repository: `mohammed09001/repo`
- Target branch: current active branch; do not assume `main` without checking.
- Execution date baseline: 3 September 2026
- Execution type: repair + completion of an existing implementation.
- Agent-neutral: Claude Code, Codex, OpenCode, Anti-Gravity, Gemini CLI, or another capable coding agent may execute it.
- Completion standard: actual repository evidence, not historical reports.

# PARENT EXECUTION GOAL

Finish the local feed intelligence. Make weighted interests and unexpected discovery persist, make ranking operate on real verified pulses plus exposure history, and make sequence queues durable across restart while remaining entirely local and precomputed before playback ticks.

# VERIFIED REPOSITORY STATE FROM THE REVIEW

The review found an in-memory `ProfilePreferences` with topic weights/exclusions/unexpected discovery and a simple `rank()` function, while the canonical stored Profile was simpler. `plan_queue()` returned an in-memory tuple with a topic-streak rule. Exposure/session tables existed, but there was no proven durable end-to-end feed queue/resume workflow.

Re-verify these facts before implementation because the repository may have changed after this prompt was authored.

# CANONICAL SCOPE

`src/curiosity/ranking/`, `sequence/`, profile/session/exposure persistence, application feed preparation, relevant store/migration tests.

# NON-GOALS

- Do not build a neural recommender.
- Do not optimize for screen time, clicks, or addiction.
- Do not introduce a graph database.
- Do not show ranking reasons/topic/source in normal playback.
- Do not perform full-corpus ranking every 10 seconds.



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

# CHILD LOOP — 04A — Unify and persist the actual user preference model

## Child Goal

Make one canonical persisted preference model drive ranking across restarts.

## Known Repository Baseline

The reviewed ranking preferences were richer than the stored Profile model.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Persist weighted topic interests.
- Persist explicit exclusions.
- Persist unexpected-discovery weight.
- Persist repetition/topic-streak controls actually used by ranking/sequence.
- Keep custom arbitrary topics supported.
- Normalize weights deterministically while preserving user intent.
- Provide migration/defaults for existing simpler profiles.
- Expose profile set/show/reset through the application/CLI owner from Execution 01.

## Deep Questions

1. Which fields belong in canonical Profile vs a separate preference record?
2. How are topic identifiers normalized without blocking user-defined topics?
3. What happens when all weights are zero?
4. How does exclusion interact with unexpected discovery?
5. What defaults preserve the original general-by-default philosophy?

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

- Profile weights survive DB reopen.
- Migration from old simple profile retains user interests.
- Custom topic changes ranking outcome.
- Excluded topic never enters eligible ranking.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 04B — Integrate bounded explainable ranking with real stored pulses

## Child Goal

Rank real verified pulses for one user using explicit explainable signals and persisted exposure history.

## Known Repository Baseline

The reviewed rank() summed interest, quality, novelty, curiosity, freshness, and repetition penalty on supplied in-memory candidates.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Reuse the explicit ranking philosophy rather than replacing it with opaque ML.
- Build bounded candidate retrieval from eligible verified pulses.
- Use user-interest match, quality, novelty, educational usefulness/curiosity, freshness, source diversity/quality where available, and repetition penalties.
- Read actual exposure history rather than caller-supplied fake recent IDs only.
- Keep ranking reasons internally inspectable for debugging.
- Reserve a configurable share for verified quality-gated unexpected discovery.
- Do not let unexpected discovery override exclusions or verification.
- Use injected clock/seed for deterministic tests.

## Deep Questions

1. Which score components are available from real stored state today?
2. What happens when a topic has no explicit weight?
3. How many candidates should be retrieved per refill?
4. How is source diversity represented without making source visible?
5. How do we avoid the same fact paraphrased from multiple sources repeating?

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

- Synthetic stored corpus statistically/structurally reflects a configured weighted profile.
- Recent exposure materially reduces/reorders repeat candidates.
- Unexpected discovery appears only at configured bounded share.
- Same seed/clock/state gives same ranking order.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 04C — Implement durable queue planning and restart continuity

## Child Goal

Precompute and persist a playback queue that survives process restart and can be refilled without remote/model work.

## Known Repository Baseline

The reviewed sequence planner returned an in-memory tuple and enforced only a simple topic streak.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Persist session queue items with order and current position.
- Persist sequence relationship/reason internally when useful.
- Prepare/refill queue outside display tick.
- Skip pulses that become invalidated after queue creation.
- Resume after process restart at the correct next pulse.
- Define corpus-exhaustion behavior explicitly: pause/reuse after a minimum cooldown/local refill; never tight-loop and never force synchronous network refresh from tick.
- Use exposure history during refill.
- Allow short coherent runs of related ideas without displaying topic labels.

## Deep Questions

1. Does existing `sessions` + `session_cards` suffice, or is a queue state migration needed?
2. When is an exposure recorded relative to advancing position?
3. How is crash-after-render-before-commit handled?
4. What invalidation check is cheap enough at playback time?
5. How is a tiny corpus handled without appearing broken?

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

- Build queue, close DB/process, reopen, resume at correct next item.
- Invalidate a queued pulse and prove it is skipped safely.
- Tiny corpus reaches documented exhaustion behavior without CPU spin.
- Spy confirms queue refill performs no remote/model/parser work when invoked from runtime.

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

- One persisted profile drives ranking after restart.
- Exposure history changes later feed order.
- Unexpected discovery is bounded, quality-gated, and cannot bypass exclusions.
- A durable queue exists and can resume/refill locally.
- No full-corpus/external work is required per 10-second tick.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`

Only `YES` completes Execution 04.

# FINAL REPORT

Use the exact Final Report Format from the Execution Operating System.
