# REPAIR EXECUTION REPO 03 — EXECUTION 04 — AMBIENT HARNESS ORCHESTRATION + ONE-FACT TERMINAL RUNTIME

## Execution Identity
- Type: ambient UX / harness integration repair
- Primary target: make lifecycle events useful without coupling Curiosity to one coding agent
- Canonical scopes: harness/application/runtime/CLI/config/store/tests
- Standalone mode remains mandatory and universal

# PARENT GOAL

Turn the current harness layer from `events are recorded` into a small **Ambient Runtime Controller**.

The controller may influence:
- whether ambient playback is active/quiet;
- whether a local queue should be prepared/refilled;
- when an agent-completion transition should stop/quiet playback.

It must never influence source truth, verification outcome, knowledge content, or ranking rules beyond explicit user/runtime state.

The adapter capability matrix must remain conservative:
- OpenCode can expose richer lifecycle states when current docs support them.
- Codex completion notification must not be misrepresented as busy/idle.
- Claude behavior must use only current documented hooks/status-line signals and must not infer unsupported lifecycle states.

No screen scraping.

# VERIFIED CURRENT REPOSITORY BASELINE — RE-VERIFY BEFORE EDITING

The latest repository state reviewed for this Execution was:

- Repository: `mohammed09001/repo`
- Branch: `main`
- Reviewed commit: `68be399a5edcf4ec48f73a41cdea6f50884549ad`
- Review date: 4 September 2026

The current repository is no longer only a foundation. It has a working product core:
- `CuriosityApplication` coordinates source registration, ingestion, extraction, verification, pulse creation, ranking, durable sessions, playback, inspect, stats, and harness-event persistence.
- `CuriosityPulse.display_fact` is the canonical normal-playback projection.
- Normal playback is one English fact, default 10-second dwell, with no Topic/Source/title/score metadata.
- SQLite migrations, FTS5, caches, jobs, sessions, exposures, pulses, and CI exist.
- GitHub Actions currently runs locked `uv` sync, Ruff, pytest, and the current web E2E successfully.
- Trafilatura is a real dependency.
- Docling exists as an optional PDF dependency and code path, but the current authoritative tests prove only the failure/unavailable boundary, not a real successful PDF qualification.
- `GitHubAdapter`, `SemanticScholarAdapter`, `WebAdapter`, `YouTubeAdapter`, and a shared discovery HTTP client exist.
- `SemanticScholarAdapter.batch_metadata()` now uses one POST batch request.
- A provider-compatible structured model adapter exists, but the CLI creates `CuriosityApplication(store)` without wiring a configured production provider into normal refresh/build.
- `curiosity discover` is still effectively a placeholder user flow rather than real GitHub/paper discovery.
- Ranking receives constant quality/novelty/curiosity/freshness values in the current application path and does not feed persisted exposure history into ranking.
- A durable session queue exists, but normal `play` consumes a bounded queue and does not provide a continuous low/high-watermark refill policy.
- Harness adapters normalize/persist events, but events do not yet drive an ambient runtime controller.
- Reliability/accounting is much thinner than the Repair Repo 02 requirements.
- `.cli-verification/curiosity.db` is currently committed and `.gitignore` does not exclude `.cli-verification/`.

Historical reports, prior agents saying `YES`, and old Execution completion narratives are not evidence. Re-read current code/tests and re-run commands before accepting any baseline statement above.

# CURRENT EXTERNAL RESEARCH BASIS — RE-VERIFY AT EXECUTION TIME

Treat these as high-value starting points, not frozen truth. APIs, pricing, capabilities, and library behavior change.

## Discovery and HTTP efficiency
- GitHub REST rate limits / secondary limits:
  https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
- GitHub REST best practices:
  https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api
- Semantic Scholar API tutorial: batch/bulk endpoints, reduced fields, API-key behavior:
  https://www.semanticscholar.org/product/api/tutorial
- Crossref REST access and authentication / polite pool:
  https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/
- Crossref REST tips: caching, bounded pagination, cursor guidance:
  https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/
- HTTPX client pooling and resource limits:
  https://www.python-httpx.org/advanced/clients/
  https://www.python-httpx.org/advanced/resource-limits/
  https://www.python-httpx.org/advanced/timeouts/

## Extraction and PDF performance
- Trafilatura Python usage and `fast=True` tradeoff:
  https://trafilatura.readthedocs.io/en/latest/usage-python.html
- Docling converter and hard bounds:
  https://docling-project.github.io/docling/reference/document_converter/
- Docling pipeline options / document timeout / accelerator:
  https://docling-project.github.io/docling/reference/pipeline_options/
- Docling advanced options / binary stream / page and file limits:
  https://docling-project.github.io/docling/usage/advanced_options/
- Docling accelerator example:
  https://docling-project.github.io/docling/_generated/examples/run_with_accelerator/

## Provider and model-economy techniques
- OpenAI Batch API:
  https://platform.openai.com/docs/api-reference/batch
- OpenAI prompt caching:
  https://openai.com/index/api-prompt-caching/
- Anthropic pricing, prompt caching, and batch processing:
  https://docs.anthropic.com/en/docs/about-claude/pricing
- Gemini API pricing, Batch, and context caching:
  https://ai.google.dev/gemini-api/docs/pricing
- LiteLLM provider abstraction / routing / cost tracking candidate:
  https://docs.litellm.ai/
- Instructor structured output / provider integrations candidate:
  https://python.useinstructor.com/

## Local search and deduplication
- SQLite FTS5:
  https://www.sqlite.org/fts5.html
- SQLite `PRAGMA optimize`:
  https://www.sqlite.org/pragma.html
- RapidFuzz:
  https://rapidfuzz.github.io/RapidFuzz/

## Harness surfaces
- Claude Code hooks/status line; re-verify current official docs at execution time:
  https://code.claude.com/docs/en/hooks
  https://code.claude.com/docs/en/statusline
- OpenCode plugin lifecycle events:
  https://opencode.ai/docs/plugins/
- Current Codex notify source/config reference:
  https://github.com/openai/codex/blob/main/codex-rs/core/src/config/mod.rs

Do not add any library above merely because it exists. Every new dependency needs a measurable repository-specific benefit and a rollback path.

# EXECUTION OPERATING SYSTEM — APPLIES TO THE ENTIRE FILE

This file is an implementation prompt, not a roadmap, design essay, suggestion list, or completion report.

The executing coding agent must continue until the Parent Goal is either:
1. proven achieved by current repository evidence; or
2. proven blocked by a concrete external constraint that cannot reasonably be repaired inside this Execution.

Never lower an acceptance gate merely to report success.

---

## 1. AUTHORITY ORDER

When requirements conflict, use this order:

1. Latest user requirements embedded in this Execution.
2. Verified current repository behavior on the active branch.
3. Parent Goal, frozen product invariants, and acceptance gates in this file.
4. Existing repository contracts / `AGENTS.md`, unless superseded above.
5. Current official external API/library documentation.
6. Historical Execution prompts and historical completion reports.

A prior `done`, `YES`, `passed`, or `implemented` statement has zero authority without fresh evidence.

---

## 2. REPOSITORY-FIRST RULE

Before writing code:

- inspect current branch, worktree, uncommitted changes, latest commit, repository tree, package metadata, lockfile, migrations, CI, and tests;
- find the canonical owner of every behavior in scope;
- read direct callers and direct tests, not only the target file;
- search for partial implementations before creating a new abstraction;
- preserve unrelated user work;
- avoid a second store, second profile model, second pulse model, second queue system, second provider registry, second runtime, or second application facade;
- if an existing owner is wrong, migrate callers deliberately and retire the superseded owner only after proof;
- identify schema/upgrade consequences before changing persisted data.

Do not design from memory when the repository can answer.

---

## 3. CONTEXT ENGINEERING CONTRACT

Maintain a bounded Context Ledger throughout execution.

Classify material facts:

- `VERIFIED`: directly proven by code, test, command output, database inspection, current official documentation, or current remote response fixture.
- `OBSERVED`: directly seen but not yet behaviorally tested.
- `INFERRED`: likely conclusion that still needs proof.
- `UNKNOWN`: uncertainty that can change the implementation.
- `REJECTED_ASSUMPTION`: a previously plausible assumption disproven by evidence.

For each Child Loop keep active context limited to:

- Parent Goal;
- current Child Goal;
- exact current failure/gap;
- canonical owner(s);
- direct callers;
- direct tests;
- schema/config contracts involved;
- relevant external API facts;
- current plan;
- unresolved UNKNOWNs;
- files modified;
- tests actually run.

Do not carry all 19 historical Execution prompts in working context.

If context must be compacted, preserve exactly:

1. Parent Goal.
2. Frozen product invariants.
3. Active Child Goal.
4. Current failing evidence/reproduction.
5. Decisions already proven.
6. Files changed.
7. Tests/benchmarks run and exact outcomes.
8. Remaining UNKNOWNs.
9. Next concrete action.
10. Any migration or rollback constraint.

Durable decisions must end in code/tests/short repository documentation, not only agent memory.

### Context Retrieval Discipline
- Search before opening large files.
- Open only sections needed for the current question.
- Prefer call graph + failing test + owner file over repository-wide reading.
- Re-read changed contracts before final integration review.
- Use fresh-context review for final spec review when the harness supports it.

---

## 4. PROMPT ENGINEERING CONTRACT

Create and maintain this internal matrix:

`Requirement → Current owner → Current behavior → Gap → Planned change → Failure risk → Verification evidence`

No material requirement may remain ownerless.

Before implementation, challenge the plan:

1. Could unit tests pass while the real CLI path stays broken?
2. Am I creating an interface without a production path?
3. Am I `supporting` a source/provider only in fixtures?
4. Am I adding a dependency when an existing primitive is enough?
5. Does the change reduce actual network/model/parse work or only rearrange code?
6. Can stale knowledge survive because downstream identity ignores an upstream version?
7. Could queue exhaustion cause synchronous network/model work in playback?
8. Could normal playback leak Topic/Source/title/score again?
9. Could a provider configuration claim `configured` while never being used?
10. Could an optional adapter silently become a core dependency?
11. Could a migration make old local state unreadable?
12. Could a benchmark be biased by tiny fixtures or warm caches?
13. Is the strongest assumption covered by a falsifying test?

Revise the plan if any answer exposes weakness.

---

## 5. LOOP ENGINEERING CONTRACT

Run continuously:

`BASELINE → REQUIREMENT MAP → CHILD PLAN → PLAN CHALLENGE → CHILD EXECUTE → CHILD VERIFY → FAILURE INJECTION → CHILD SPEC REVIEW → CHILD ENGINEERING REVIEW → CHILD GOAL GATE → NEXT CHILD → INTEGRATION REVIEW → FINAL VERIFY → PARENT GOAL GATE → REPORT`

Any failure enters:

`FAILURE → REPRODUCE → MINIMIZE → ROOT CAUSE → EVIDENCE REVIEW → REVISED PLAN → REPAIR → FOCUSED RE-VERIFY → REGRESSION VERIFY → RE-REVIEW`

Rules:
- never patch the same symptom repeatedly without root-cause review;
- after two recurrences of the same class, stop incremental patching and reassess ownership/invariant;
- a flaky test is a failure, not a pass;
- a test skipped because the required capability is absent does not prove that capability;
- if a Child Gate is PARTIALLY/NO, continue its repair loop before advancing unless an external hard blocker is documented.

---

## 6. HARNESS ENGINEERING CONTRACT

The repository/harness must make correctness easy to observe.

Prefer:
- deterministic IDs and seeds;
- dependency injection;
- fixture transports at external boundaries;
- real internal engines in integration/E2E tests;
- explicit timeouts and budgets;
- one-command focused tests;
- negative/adversarial fixtures;
- restart/close/reopen tests for persistence;
- capability matrices for optional integrations;
- structured diagnostics over log prose;
- fresh CI after the final code edit.

Do not:
- mock away the stage under test;
- add uncontrolled subagent fan-out;
- let one implementing agent self-certify based only on its own summary;
- accept `manual inspection` when a deterministic test can prove the invariant.

---

## 7. PERFORMANCE AND COST CONTRACT

Optimization means less total work, not merely faster syntax.

Every expensive stage must have measurable counters where relevant:

- discovery API requests;
- fetch requests;
- bytes downloaded;
- 200 vs 304/cache reuse;
- documents parsed;
- parser elapsed time;
- candidate count before/after dedupe;
- verification calls;
- provider calls;
- provider input/output/cached tokens when available;
- provider cost when safely derivable;
- queue refill latency;
- playback tick local read/write latency;
- retries/failures.

Performance rules:
- no network, parser, model, embedding, discovery, or full-corpus ranking inside the display tick;
- dedupe before provider work;
- verify deterministically before model escalation;
- use content/version keys to skip unchanged downstream work;
- bound concurrency per remote provider;
- prefer batch/bulk APIs when they reduce request count and remain compatible with freshness needs;
- never increase recurring cost merely to produce more screen activity;
- optional high-cost quality modes must be explicit and budgeted.

Any claimed optimization must have a before/after benchmark or work-count comparison.

---

## 8. DEPENDENCY ADMISSION GATE

A new dependency is allowed only if all are true:

1. It solves a measured current problem.
2. Existing standard-library/current dependencies are materially worse.
3. It has a clear canonical owner.
4. Lockfile/install impact is measured.
5. Import/startup overhead is acceptable.
6. It works on supported Personal Edition platforms, or is explicitly optional.
7. Tests can run without external credentials where required.
8. A rollback path exists.
9. It does not create a server/cloud requirement.
10. It reduces complexity, cost, latency, or correctness risk enough to justify itself.

For candidates such as HTTPX, RapidFuzz, Instructor, or LiteLLM: benchmark and decide. Do not pre-decide adoption.

---

## 9. FROZEN PRODUCT INVARIANTS

Preserve throughout Repo 03:

- Personal, local-first, single-user edition.
- Standalone terminal is the guaranteed universal mode.
- Coding-agent integrations are optional adapters.
- Provider-neutral model boundary.
- Offline deterministic mode remains usable.
- Normal playback displays one concise English educational fact.
- Default dwell is 10 seconds.
- Normal playback shows no Topic, Source, URL, title, score, confidence, difficulty, or evidence.
- Explicit `inspect` may show provenance/evidence/topic.
- Playback tick performs zero network/model/parser/discovery/full-corpus work.
- No ads.
- No account/billing/cloud multi-tenancy.
- No GraphRAG or mandatory graph database.
- No dedicated vector database requirement.
- No mandatory embeddings.
- No opaque neural recommender.
- No addictive streak/time-on-screen optimization.
- Frozen source-click/browser-freeze/resume behavior remains out of scope.
- Do not execute remote source code.
- Do not scrape restricted YouTube transcripts.
- Do not turn remote content into trusted instructions.

---

## 10. SECURITY / PRIVACY CONTRACT

- Secrets stay in environment/secret storage and never enter logs, diagnostics, database payloads, test snapshots, or Git history.
- Remote HTML/PDF/repository text is untrusted data.
- Keep redirect, MIME, response-size, document-size, page, timeout, and decompression bounds.
- Sanitize terminal control characters and escape sequences.
- Harness adapters persist only minimum lifecycle state; never prompt/code/transcript by default.
- No provider request body containing user secrets may be logged.
- New telemetry is local by default.

---

## 11. TWO-PASS REVIEW

Every Child and the integrated Parent receives two reviews.

### Pass A — Goal / Spec
- Did behavior satisfy every written required outcome?
- Is the user-facing path actually reachable?
- Is anything test-only, placeholder, dead, or silently disabled?
- Were frozen UX and cost invariants preserved?
- Did we accidentally weaken a requirement?

### Pass B — Engineering
Inspect:
- ownership;
- call graph;
- persistence;
- migration;
- idempotency;
- stale invalidation;
- concurrency;
- restart recovery;
- budgets;
- timeouts;
- rate-limit behavior;
- privacy;
- security;
- terminal safety;
- dependency cost;
- dead code;
- CI;
- test strength;
- cross-platform impact.

A final `YES` requires both passes.

---

## 12. ANTI-ACCUMULATION RULE

Before final gate search for:
- TODO / FIXME / NotImplemented in repaired scope;
- placeholder CLI commands;
- fake production adapters;
- obsolete card renderers;
- duplicate provider abstractions;
- old Source/Topic normal renderer paths;
- stale queue planners;
- duplicate cache layers;
- unused migrations/tables;
- committed runtime verification databases;
- stale README claims;
- dead feature flags.

Migrate callers before deletion and verify after deletion.

---

## 13. COMPLETION EVIDENCE

After the final relevant edit run, at minimum:

- `uv sync --locked`
- relevant optional-extra sync where that capability is being qualified
- `uv run ruff check .`
- focused tests per Child
- full `uv run pytest`
- authoritative E2E(s)
- CLI smoke for user-visible behavior
- database close/reopen where state changed
- fresh CI or exact local equivalent
- repository diff review
- stale/dead path search

Never invent results.

---

## 14. FINAL REPORT FORMAT

Report only after final verification:

1. Baseline re-verified
2. Requirements implemented
3. Canonical owners changed
4. Dependencies admitted/rejected and why
5. Migrations / compatibility
6. Tests with exact outcomes
7. Manual CLI verification
8. Failure/adversarial verification
9. Performance before/after
10. Cost/work-count before/after
11. Remaining UNKNOWNs/blockers
12. Child Goal Gates
13. Parent Goal Gate: `YES / PARTIALLY / NO`

If any critical acceptance item is not proven, do not report `YES`.

---

# CHILD LOOP — 04A — Define one Ambient Runtime state machine

## Child Goal

Translate minimized HarnessEvents into a provider-neutral local runtime state without giving adapters ownership of playback internals.

## Current Baseline Hypothesis

Current application persists HarnessEvents and explicitly states adapters have no control over playback.

Re-verify before editing.

## Required Outcomes

- Create a small state machine such as `UNKNOWN / ACTIVE_WORK / WAITING_OR_IDLE / TURN_COMPLETE / QUIET` only where semantics are defensible.
- Separate raw adapter event from derived ambient runtime state.
- Persist only state required for restart/debounce.
- Unknown/unsupported events must not guess.
- Manual standalone mode must bypass/ignore ambient controller when user explicitly starts `curiosity play`.
- Define debounce/deduplication for repeated lifecycle events.
- Controller may request local queue refill but never remote refresh/model/parser work implicitly.
- Adapter failure cannot stop core CLI.

## Deep Questions

1. What does `idle` mean per adapter?
2. Should `turn_complete` stop playback immediately or after current dwell?
3. How is manual mode prioritized over ambient mode?
4. How are duplicate events within milliseconds handled?
5. What state survives restart?

## Plan Mode

Before editing, produce an internal plan containing:
- exact canonical owner(s);
- direct callers;
- persistence/schema impact;
- external capability assumptions requiring re-verification;
- files expected to change;
- dependency admission decision if relevant;
- migration/compatibility strategy;
- failure/restart semantics;
- cost/performance budget;
- focused tests;
- falsifying tests;
- rollback strategy.

Run the Plan Challenge from the Execution Operating System. Do not code until the plan can falsify its strongest assumption.

## Execute

Implement continuously until the Child Goal is behaviorally complete.

Do not stop at:
- interface/protocol only;
- class shell;
- TODO;
- fake adapter;
- test-only path;
- docs-only path;
- feature flag that is never consumed;
- counter that is never read;
- provider class that application/CLI never wires;
- migration with no upgrade test.

## Fresh Verification

- State transition table has deterministic tests.
- Unsupported Codex idle event is rejected.
- Duplicate event fixture is debounced/idempotent.
- Standalone play works with no harness tables/events.
- Controller never touches source/verification content.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 04B — Re-qualify and harden Claude Code adapter

## Child Goal

Use only current documented Claude surfaces, preserve settings, and expose no more capability than current Claude actually proves.

## Current Baseline Hypothesis

Current adapter installs a Stop hook and maps it to turn_complete; this is privacy-minimized but not a full busy/idle lifecycle.

Re-verify before editing.

## Required Outcomes

- Re-read current official Claude Code hooks and status-line docs at execution time.
- Keep Stop/turn-complete if still documented and semantically correct.
- Do not claim busy/idle unless a current documented signal reliably exposes it.
- Install/status/uninstall must preserve unrelated settings exactly.
- Handle `disableAllHooks` safely.
- Do not persist prompt, transcript path, code, tool payload, token/cost context.
- If status line is useful for ambient display integration, use it only if it does not create high-frequency process overhead or interfere with user status line; otherwise reject it explicitly.
- Add compatibility/version diagnostics without scraping Claude output.

## Deep Questions

1. Which Claude event is the strongest lifecycle signal today?
2. Does status-line invocation frequency make it a bad orchestration channel?
3. How do we avoid replacing a user's existing statusLine configuration?
4. What is the safe behavior when hooks are disabled?

## Plan Mode

Before editing, produce an internal plan containing:
- exact canonical owner(s);
- direct callers;
- persistence/schema impact;
- external capability assumptions requiring re-verification;
- files expected to change;
- dependency admission decision if relevant;
- migration/compatibility strategy;
- failure/restart semantics;
- cost/performance budget;
- focused tests;
- falsifying tests;
- rollback strategy.

Run the Plan Challenge from the Execution Operating System. Do not code until the plan can falsify its strongest assumption.

## Execute

Implement continuously until the Child Goal is behaviorally complete.

Do not stop at:
- interface/protocol only;
- class shell;
- TODO;
- fake adapter;
- test-only path;
- docs-only path;
- feature flag that is never consumed;
- counter that is never read;
- provider class that application/CLI never wires;
- migration with no upgrade test.

## Fresh Verification

- Install/uninstall round-trip preserves unrelated JSON.
- Private fields in fixture are discarded.
- Current documented Stop fixture maps correctly.
- Unsupported lifecycle claims fail capability tests.
- No Claude installation is required for standalone tests.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 04C — Upgrade OpenCode integration using native lifecycle events

## Child Goal

Use OpenCode's currently documented events to drive ambient state accurately without scraping terminal output.

## Current Baseline Hypothesis

Current OpenCode plugin listens to session.created, session.idle, session.status and emits minimized events.

Re-verify before editing.

## Required Outcomes

- Re-verify current OpenCode plugin event names and payloads.
- Map `session.status` busy/idle and `session.idle` conservatively.
- Handle session.error explicitly as a quiet/terminal state only if useful.
- Preserve project/global plugin strategy without overwriting unrelated plugin files.
- Make install/status/uninstall reversible and ownership-marked.
- If newer OpenCode client/server lifecycle APIs provide a cleaner local integration, evaluate them but do not introduce remote-server dependency.
- Debounce event storms.
- Keep only adapter identity, normalized event type, timestamp, and minimal state.

## Deep Questions

1. Which events fire redundantly?
2. Can a project plugin survive OpenCode upgrades safely?
3. Should session.created activate ambient mode before actual work begins?
4. How do errors affect display state?

## Plan Mode

Before editing, produce an internal plan containing:
- exact canonical owner(s);
- direct callers;
- persistence/schema impact;
- external capability assumptions requiring re-verification;
- files expected to change;
- dependency admission decision if relevant;
- migration/compatibility strategy;
- failure/restart semantics;
- cost/performance budget;
- focused tests;
- falsifying tests;
- rollback strategy.

Run the Plan Challenge from the Execution Operating System. Do not code until the plan can falsify its strongest assumption.

## Execute

Implement continuously until the Child Goal is behaviorally complete.

Do not stop at:
- interface/protocol only;
- class shell;
- TODO;
- fake adapter;
- test-only path;
- docs-only path;
- feature flag that is never consumed;
- counter that is never read;
- provider class that application/CLI never wires;
- migration with no upgrade test.

## Fresh Verification

- Current session.status busy→idle fixture produces expected controller states.
- Repeated idle events do not duplicate work.
- Install/uninstall preserves unrelated plugins/config.
- Privacy snapshot contains no message/tool content.
- OpenCode absence leaves core product unaffected.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 04D — Keep Codex capability truthful and completion-only unless current evidence improves

## Child Goal

Support only what current Codex actually guarantees.

## Current Baseline Hypothesis

Current Codex config source documents `notify` after completed turns; this does not prove busy/idle.

Re-verify before editing.

## Required Outcomes

- Re-verify current official Codex config/schema/source.
- Keep completion-only capability if that is still the only reliable external notifier.
- Provide a safe helper/config snippet or installer only if it can preserve existing config; otherwise keep explicit manual configuration.
- Never parse prompt/input fields from notifier payload for Curiosity.
- Map only event type/turn completion and minimal client identity if needed.
- Do not invent start/working/idle events.

## Deep Questions

1. Does current Codex expose any supported lifecycle beyond completion?
2. Can config installation be safely merged in TOML without clobbering?
3. What notifier payload fields should be ignored?

## Plan Mode

Before editing, produce an internal plan containing:
- exact canonical owner(s);
- direct callers;
- persistence/schema impact;
- external capability assumptions requiring re-verification;
- files expected to change;
- dependency admission decision if relevant;
- migration/compatibility strategy;
- failure/restart semantics;
- cost/performance budget;
- focused tests;
- falsifying tests;
- rollback strategy.

Run the Plan Challenge from the Execution Operating System. Do not code until the plan can falsify its strongest assumption.

## Execute

Implement continuously until the Child Goal is behaviorally complete.

Do not stop at:
- interface/protocol only;
- class shell;
- TODO;
- fake adapter;
- test-only path;
- docs-only path;
- feature flag that is never consumed;
- counter that is never read;
- provider class that application/CLI never wires;
- migration with no upgrade test.

## Fresh Verification

- Current completion fixture maps to turn_complete.
- Idle/busy claims remain false unless current evidence proves otherwise.
- Privacy test ignores prompt/message payloads.
- Config helper is reversible or intentionally not auto-installed.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 04E — Deliver the one-fact-at-a-time terminal experience

## Child Goal

Make the terminal visually behave like a calm ambient learning surface while preserving non-interactive safety.

## Current Baseline Hypothesis

Current runtime prints each fact as a new line; user requirement is one simple fact, and the product should avoid terminal clutter when interactive.

Re-verify before editing.

## Required Outcomes

- Keep fact-only rendering and 10-second default.
- In an interactive TTY, evaluate a minimal single-region replace/update strategy so normally only the current fact is visible.
- Do not build a complex full-screen TUI unless evidence proves necessary.
- On redirected/non-TTY stdout, fall back to newline records rather than ANSI cursor control.
- Sanitize C0/C1/ANSI/OSC sequences before rendering.
- Handle resize/wrap safely at common widths.
- Ctrl-C must leave terminal state clean and durable session coherent.
- If ambient controller reaches turn_complete/quiet, define whether current fact finishes its dwell or stops immediately; make policy explicit/tested.
- Do not clear unrelated terminal history.

## Deep Questions

1. Can one-line replacement work portably on Windows/macOS/Linux?
2. What happens when a fact wraps to two terminal lines?
3. How do we restore cursor/line state on Ctrl-C?
4. Should ambient mode and manual play use identical renderer?

## Plan Mode

Before editing, produce an internal plan containing:
- exact canonical owner(s);
- direct callers;
- persistence/schema impact;
- external capability assumptions requiring re-verification;
- files expected to change;
- dependency admission decision if relevant;
- migration/compatibility strategy;
- failure/restart semantics;
- cost/performance budget;
- focused tests;
- falsifying tests;
- rollback strategy.

Run the Plan Challenge from the Execution Operating System. Do not code until the plan can falsify its strongest assumption.

## Execute

Implement continuously until the Child Goal is behaviorally complete.

Do not stop at:
- interface/protocol only;
- class shell;
- TODO;
- fake adapter;
- test-only path;
- docs-only path;
- feature flag that is never consumed;
- counter that is never read;
- provider class that application/CLI never wires;
- migration with no upgrade test.

## Fresh Verification

- TTY fixture/simulation proves one current fact region without stale metadata.
- Non-TTY snapshot has clean newline facts and zero control sequences.
- Malicious OSC/ANSI input is neutralized.
- Ctrl-C leaves next durable position coherent.
- Source/Topic never appear in normal output.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

# PARENT INTEGRATION REVIEW

Exercise:
- standalone manual play with no adapter;
- OpenCode busy→idle/complete sequence;
- Claude completion-only sequence;
- Codex completion-only sequence;
- repeated/noisy/unknown events;
- TTY and non-TTY rendering;
- queue-low event with local-only refill.

Prove harness state never mutates knowledge truth and never triggers implicit remote refresh.

# FINAL PARENT ACCEPTANCE

- Harness events have a real, bounded ambient use.
- Adapter capabilities remain truthful and current.
- Standalone terminal remains universal.
- No prompt/code/transcript surveillance exists.
- Local queue can be prepared/refilled without external work.
- Interactive terminal normally shows one fact at a time without clutter.
- Non-TTY behavior remains safe.
- Ctrl-C/restart remains coherent.
- No agent is hard-coded as the product.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`
