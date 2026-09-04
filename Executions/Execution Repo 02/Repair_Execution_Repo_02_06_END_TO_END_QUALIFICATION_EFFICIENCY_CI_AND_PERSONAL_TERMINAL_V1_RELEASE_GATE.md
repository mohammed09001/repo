# REPAIR EXECUTION REPO 02 — EXECUTION 06 — END-TO-END QUALIFICATION, EFFICIENCY, CI, AND PERSONAL TERMINAL V1 RELEASE GATE

## Execution Identity

- Repository: `mohammed09001/repo`
- Target branch: current active branch; do not assume `main` without checking.
- Execution date baseline: 3 September 2026
- Execution type: repair + completion of an existing implementation.
- Agent-neutral: Claude Code, Codex, OpenCode, Anti-Gravity, Gemini CLI, or another capable coding agent may execute it.
- Completion standard: actual repository evidence, not historical reports.

# PARENT EXECUTION GOAL

Qualify the repaired repository as one daily-usable Personal Terminal Edition. Build a clean-install E2E path from source discovery through timed playback, integrate reliability/cost diagnostics, add independent CI, remove stale incomplete paths/docs, and refuse release if any critical capability still requires manual Python wiring or violates the minimal 10-second English-fact experience.

# VERIFIED REPOSITORY STATE FROM THE REVIEW

The review found many unit tests but no complete E2E proving `source → ingest → knowledge → verify → compose → rank → queue → play`. No visible GitHub status checks were present on the reviewed commit. README described the foundation and had malformed trailing null/encoding content. Reliability utilities were small primitives rather than an integrated qualification/cost layer.

Re-verify these facts before implementation because the repository may have changed after this prompt was authored.

# CANONICAL SCOPE

Whole repository, but changes outside integration/reliability/CI/docs must be narrowly justified by failures discovered during qualification.

# NON-GOALS

- Do not add commercial features.
- Do not add cloud multi-tenancy.
- Do not relax verification to make E2E pass.
- Do not skip heavy parser/source qualifications by mocking the whole application boundary.
- Do not declare V1 if normal play is not daily-usable.



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

# CHILD LOOP — 06A — Build the authoritative clean-install E2E test

## Child Goal

Prove the actual product path end-to-end using real internal engines and controlled external fixtures.

## Known Repository Baseline

The reviewed tests covered modules independently but did not prove the full product path.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Create an authoritative offline E2E starting from a fresh temp data/config directory.
- Run init.
- Configure a weighted profile.
- Register/discover at least one web source fixture.
- Process at least one paper/PDF fixture through the real parser boundary qualified by Execution 02.
- Run extraction, verification, pulse composition, ranking, queue preparation, and playback.
- Use fake clock so 10-second cadence is proven without real waiting.
- Use real SQLite persistence and close/reopen at least once.
- Assert normal playback output is one English fact and contains no Topic/Source/title/metadata.
- Assert explicit inspect can still reveal lineage.
- Do not bypass stages by directly inserting final pulses except for narrowly isolated tests separate from this E2E.

## Deep Questions

1. Which external boundaries should be fixture transport vs real local parser?
2. How do we prove Trafilatura/Docling are actually exercised?
3. What restart point provides the strongest persistence evidence?
4. How do we prove normal output did not accidentally inherit inspect metadata?
5. How is the test deterministic across OS?

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

- One documented command runs the complete E2E.
- Network is blocked/unused in authoritative E2E.
- Test fails if a pipeline stage is removed/bypassed.
- DB reopen is part of the path.
- Fake clock records 10-second cadence.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 06B — Integrate refresh budgets, diagnostics, and recovery

## Child Goal

Make expensive refresh work bounded, observable, recoverable, and demonstrably decoupled from playback.

## Known Repository Baseline

The reviewed reliability module had a small request/byte Budget and retry_delay helper; store had durable jobs/cache primitives.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Create one per-refresh run budget/ledger summarizing API requests, fetched bytes, cache hits, documents parsed, provider calls/input/output usage/cost when available, failures/retries, and elapsed stage timings.
- Reuse existing job/cache persistence rather than introducing a separate scheduler.
- Add deep doctor diagnostics for DB integrity, schema version, pending/abandoned jobs, parser/provider capabilities, queue readiness, and local storage paths.
- Add failure injection for 429/timeout/malformed JSON/noisy HTML/malformed PDF/provider schema failure/database busy/process interruption.
- Prove abandoned/interrupted jobs recover idempotently.
- Prove unchanged second refresh materially reduces external/parser/provider work.

## Deep Questions

1. What metrics are diagnostic vs unnecessary complexity?
2. Where is the canonical run ledger persisted?
3. How are provider cost values represented when a provider doesn't return price?
4. What failure should retry vs fail permanently?
5. How does doctor avoid leaking secrets?

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

- Repeated unchanged refresh fixture shows cache-hit increase and reduced external/parser/provider calls.
- Budget exhaustion stops safely and can resume.
- `doctor --deep` finds seeded abandoned/invalid states.
- Failure injections do not duplicate canonical content.
- Playback instrumentation still reports zero external/heavy calls.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 06C — Add independent CI and clean-install qualification

## Child Goal

Make repository health independently verifiable on every relevant push/PR without secrets.

## Known Repository Baseline

The reviewed tree had no visible CI workflow/status gate.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Add GitHub Actions or equivalent repository-native CI.
- Use Python 3.12+ as supported by project metadata; choose a minimal truthful OS matrix based on dependencies actually qualified.
- Run locked dependency install.
- Run Ruff.
- Run full pytest.
- Run authoritative offline E2E.
- Cache dependencies only if it does not hide lockfile errors.
- Do not require API keys in required CI.
- Optional credentialed smoke tests must be separate/non-blocking or manually triggered.
- Fail CI on stale formatting/lint/test/E2E.

## Deep Questions

1. Can Docling install reliably on every matrix OS selected?
2. Should heavy parser qualification run on one OS while core runs broader?
3. How is uv installed/version-pinned?
4. How do we ensure CI uses the lockfile rather than resolving silently?

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

- CI YAML is syntactically valid.
- Local equivalent command sequence passes.
- Required jobs contain no secret dependency.
- Authoritative E2E is part of required CI.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 06D — Final product audit, cleanup, README, and V1 freeze

## Child Goal

Make the repository tell the truth about what is complete and freeze Personal Terminal Edition V1 only if daily use is actually possible.

## Known Repository Baseline

README previously described a local-first foundation, documented only doctor/ingest, and contained malformed trailing null/encoding text.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Fix README encoding/null artifacts.
- Document exact install path from clean machine assumptions: clone/install, `uv sync --locked`, init, profile, source/refresh, play, inspect, stats, doctor.
- Document local data/config locations, backup/reset, optional provider, optional harness adapters, YouTube limitations, PDF dependency/platform limitations if any.
- Document the frozen playback UX: English fact only, 10 seconds, no Topic/Source in normal view.
- Search repository for `TODO`, `NotImplemented`, deliberate failure strings, fake production adapters, stale old `Why does this matter`, and old normal `Source:` renderer paths.
- Remove/supersede stale critical paths after proving callers migrated.
- Perform privacy/secrets review.
- Perform manual terminal smoke in the current development environment.
- Set/freeze V1 version/release notes only if every critical gate is YES.

## Deep Questions

1. Can a new user follow README without knowing internal architecture?
2. Is any command documented but not implemented?
3. Does any critical source/parser/provider path still deliberately fail?
4. Can normal play accidentally show Source/Topic?
5. Is any optional capability being advertised as guaranteed?
6. What is the strongest remaining reason not to call this V1?

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

- Every README command is executed against a clean temp environment where possible.
- Repository search finds no critical stale deliberate-failure path.
- Manual `curiosity play` smoke demonstrates fact-only output.
- Final fresh full suite runs after the last documentation/code edit.

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

- Clean install/locked sync succeeds.
- CLI first-use path is complete.
- Web/GitHub/paper/PDF sources can reach verified pulses through qualified paths.
- Trafilatura and Docling are real successful integrations.
- Offline mode works; optional quality-provider mode has a real adapter.
- Weighted profile affects ranking.
- Durable queue/session survives restart.
- `curiosity play` displays only concise English facts and advances every 10 seconds by default.
- No Topic or Source appears during normal play.
- No heavy/external work occurs on playback ticks.
- Inspect preserves evidence/source traceability.
- CI independently runs lint/tests/E2E without secrets.
- README matches reality.
- Final gate explicitly states whether the repository is ready for daily personal use; if any critical item fails, answer NO or PARTIALLY and do not freeze V1.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`

Only `YES` completes Execution 06.

# FINAL REPORT

Use the exact Final Report Format from the Execution Operating System.
