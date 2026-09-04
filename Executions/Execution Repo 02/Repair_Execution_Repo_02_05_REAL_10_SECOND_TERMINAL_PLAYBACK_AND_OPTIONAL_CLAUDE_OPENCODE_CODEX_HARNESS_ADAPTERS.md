# REPAIR EXECUTION REPO 02 — EXECUTION 05 — REAL 10-SECOND TERMINAL PLAYBACK AND OPTIONAL CLAUDE / OPENCODE / CODEX HARNESS ADAPTERS

## Execution Identity

- Repository: `mohammed09001/repo`
- Target branch: current active branch; do not assume `main` without checking.
- Execution date baseline: 3 September 2026
- Execution type: repair + completion of an existing implementation.
- Agent-neutral: Claude Code, Codex, OpenCode, Anti-Gravity, Gemini CLI, or another capable coding agent may execute it.
- Completion standard: actual repository evidence, not historical reports.

# PARENT EXECUTION GOAL

Deliver the actual ambient terminal product. `curiosity play` must render only one concise English fact, wait 10 seconds by default, render the next precomputed fact, record durable exposure/session progress safely, and remain fully usable without any coding-agent integration. Then add thin reversible native lifecycle adapters for supported agents without collecting prompts/code/transcripts.

# VERIFIED REPOSITORY STATE FROM THE REVIEW

The review found `runtime.py` with safe_text(), Playback.next/pause/resume/stop, and render() that printed hook/body plus `Source:`. The runtime test used one in-memory card and no real timed loop. `harness.py` normalized a few events and exposed a small capability map but did not install Claude/OpenCode adapters. Standalone playback was not a complete product.

Re-verify these facts before implementation because the repository may have changed after this prompt was authored.

# CANONICAL SCOPE

`src/curiosity/runtime*`, play/inspect/stats CLI/application wiring, harness adapter implementation/configuration, runtime/harness tests.

# NON-GOALS

- Do not redesign knowledge extraction.
- Do not require Claude Code/OpenCode/Codex for standalone use.
- Do not capture coding-agent prompts, code, transcripts, model responses, or tool payload contents.
- Do not use screen scraping.
- Do not add browser UI.
- Do not show Source or Topic in normal playback.


# CURRENT EXTERNAL GROUND TRUTH TO RE-VERIFY

- Claude Code current status-line docs say the local command receives JSON on stdin and can refresh on an interval; hooks/statusline are local shell-executed integrations: https://code.claude.com/docs/en/statusline
- Claude Code configuration/debug docs document hook registration and `disableAllHooks`: https://code.claude.com/docs/en/debug-your-config
- OpenCode current plugin docs list `session.idle`, `session.status`, `session.created`, and other lifecycle events: https://opencode.ai/docs/plugins/
- Codex lifecycle capability must be re-verified from current official OpenAI/Codex documentation during execution; never infer a busy/idle stream from a completion-only notify feature.


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

# CHILD LOOP — 05A — Implement the real timed playback loop

## Child Goal

Make `curiosity play` a complete local runtime over a persisted precomputed queue.

## Known Repository Baseline

The reviewed Playback primitive advanced in-memory tuples but did not sleep/rotate as a real product and render() included Source.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Consume the persisted queue prepared by the application/sequence layer.
- Render exactly one English fact in normal mode.
- Default dwell is exactly 10 seconds.
- Inject clock/sleeper/event source so tests do not wait 10 real seconds.
- Record exposure and advance durable queue/session state with a clearly defined crash-consistency order.
- Support Ctrl-C clean shutdown.
- Support pause/resume/stop controls where technically appropriate without adding a complex TUI.
- Handle empty/exhausted queue gracefully and tell the user to refresh only outside the tick.
- Sanitize ANSI/OSC/C0/C1 terminal control sequences from displayed fact text.
- Do not clear unrelated terminal history unless explicitly required by the chosen minimal renderer.

## Deep Questions

1. What exact sequence is render → persist exposure → advance position, and what crash duplicate behavior is acceptable?
2. Should the runtime replace the same terminal line or print each fact as a new line?
3. What is the simplest behavior that does not become a TUI?
4. How is 10 seconds tested with fake time?
5. What happens if stdout is redirected/non-interactive?

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

- Fake-clock test observes exact 10-second default intervals.
- Golden normal output contains fact text only.
- Spy proves zero network/model/parser/verification calls during ticks.
- Ctrl-C/restart preserves a coherent next position.
- Malicious ANSI/OSC fixture cannot inject terminal controls.
- Empty queue exits or waits according to documented behavior without remote refresh.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 05B — Keep inspect/stats separate from normal playback

## Child Goal

Allow explicit evidence/source/topic inspection and useful learning history without polluting the ambient display.

## Known Repository Baseline

The product needs internal traceability even though source/topic are hidden normally.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- `inspect <pulse-id>` shows pulse text, source identity/URL where available, evidence excerpt, verification status/reasons, internal topic, provenance, and generation metadata.
- `stats` uses persisted exposure/session state to summarize knowledge shown/topics explored/repetition/coverage.
- Do not optimize stats around total screen time or addictive streaks.
- Use a distinct renderer/code path for inspect/stats so normal play cannot accidentally inherit metadata.

## Deep Questions

1. What stats are meaningful for learning without gamifying time-on-screen?
2. How is inspect behavior defined for a deleted/stale source?
3. What sensitive config/provider data must never appear?
4. How can snapshots ensure play and inspect renderers stay separated?

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

- Inspect one fixture pulse and trace it to source/evidence.
- Stats changes after recorded exposures.
- Play snapshot remains source/topic-free while inspect snapshot contains lineage.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 05C — Add Claude Code lifecycle adapter safely and reversibly

## Child Goal

Use current native Claude Code surfaces to optionally trigger/synchronize Curiosity without making Claude a dependency.

## Known Repository Baseline

The reviewed repository did not contain a complete Claude installer/adapter.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Re-verify current Claude Code hooks and status-line configuration before implementation.
- Prefer native documented hooks/status-line command execution; never scrape terminal output.
- Implement install/status/uninstall with preservation of pre-existing Claude settings.
- Use only minimized lifecycle/session-state fields needed to decide active/idle/complete behavior.
- Do not store prompt text, code, transcript, cost, context contents, or tool payloads unless a future product requirement explicitly changes this.
- On configuration conflict, fail safely rather than overwriting user settings.
- Adapter emits normalized local HarnessEvents into the Curiosity application boundary.

## Deep Questions

1. Which Claude event actually provides the state needed today?
2. Should statusline be used for display integration, lifecycle signal, or not at all?
3. How are existing statusLine/hooks merged safely?
4. What does uninstall remove vs preserve?
5. How is `disableAllHooks` handled?

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

- Fixture JSON from current documented Claude shape maps to minimized events.
- Install/uninstall round-trip preserves unrelated settings.
- Privacy test proves prompt/transcript fields are ignored/not persisted.
- Standalone play still works with Claude adapter absent.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 05D — Add OpenCode and conservative Codex adapters

## Child Goal

Support native available lifecycle signals without overstating capabilities.

## Known Repository Baseline

The reviewed harness capability map mentioned `codex_notify` but lacked complete adapters. OpenCode currently documents session.idle/session.status plugin events.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- OpenCode: implement a thin local plugin using documented session lifecycle events such as `session.idle` and `session.status`.
- Provide reversible project/global installation strategy and avoid editing unrelated plugin config.
- Codex: re-verify current official notification/lifecycle surface at execution time.
- Implement only states that current Codex actually exposes; if it exposes completed-turn notification only, represent completion only and leave busy/idle unsupported.
- Maintain an explicit capability matrix tested against adapters.
- Normalize all signals into minimal HarnessEvents.
- Do not make any harness adapter a dependency of core playback.

## Deep Questions

1. What are the exact current OpenCode event payloads?
2. Which fields are necessary vs private/noisy?
3. What does Codex actually guarantee today?
4. How should unsupported lifecycle states degrade?
5. How are adapter events debounced/deduplicated?

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

- OpenCode session.idle/status fixture produces correct minimized event.
- Codex fixture proves only documented capability is represented.
- Capability matrix rejects unsupported claims.
- All adapters disabled still pass full standalone runtime tests.

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

- `curiosity play` rotates one English fact every 10 seconds by default.
- Normal playback shows no Topic, Source, title, or metadata.
- Playback tick performs zero heavy/external work.
- Exposure/session progress survives restart.
- Claude/OpenCode/Codex integrations are optional, truthful, reversible, and privacy-minimized.
- Standalone terminal use remains the universal guaranteed mode.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`

Only `YES` completes Execution 05.

# FINAL REPORT

Use the exact Final Report Format from the Execution Operating System.
