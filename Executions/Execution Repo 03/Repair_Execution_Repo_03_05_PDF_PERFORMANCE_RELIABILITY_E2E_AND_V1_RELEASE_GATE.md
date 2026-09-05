# REPAIR EXECUTION REPO 03 — EXECUTION 05 — PDF QUALIFICATION + PERFORMANCE/COST LEDGER + FAILURE RECOVERY + AUTHORITATIVE V1 RELEASE GATE

## Execution Identity
- Type: final hardening / release qualification
- Primary target: real Docling success path, adaptive parser performance, run ledger, recovery, CI, final clean-install proof
- Canonical scopes: ingest/reliability/store/doctor/CI/tests/docs/repository hygiene
- This is the blocking Repo 03 release gate

# PARENT GOAL

Prove Personal Terminal Edition V1 as a daily-usable local product under realistic failures and cost constraints.

This Execution must not add broad new product scope.

It must close the remaining qualification holes:
- real PDF success rather than only failure;
- adaptive parser performance;
- refresh run/work ledger;
- interruption recovery;
- SQLite maintenance where justified;
- CI coverage of optional heavy paths;
- clean-install CLI E2E;
- final truthfulness of README/release state.

If a critical gate is not proven, final answer is `PARTIALLY` or `NO`.

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

# CHILD LOOP — 05A — Qualify Docling PDF success with hard resource bounds

## Child Goal

Turn PDF from an optional code path into a real tested supported capability on at least one qualified Personal Edition platform.

## Current Baseline Hypothesis

Docling is optional and `parse_pdf` exists, but current test expects the Docling-unavailable/failure path and required CI does not install the PDF extra.

Re-verify before editing.

## Required Outcomes

- Use current Docling `DocumentConverter` with engine-bounded local bytes/DocumentStream, never uncontrolled remote fetch.
- Use Docling's own `max_num_pages`, `max_file_size`, `page_range`, and `document_timeout` where available instead of only pre-counting PDF tokens.
- Default OCR/table/image-heavy work off unless document needs it or a specific mode enables it.
- Set bounded CPU thread behavior; GPU/MPS/CUDA acceleration remains optional and must never be required.
- Pre-download model artifacts only if needed for repeatable offline/CI behavior and license/size are acceptable; otherwise document first-use requirements truthfully.
- Preserve parser version and conversion status/timings.
- Malformed/oversize/timeout/partial-success behavior must not persist a canonical successful document unless policy explicitly qualifies partial content.
- Add at least one small real PDF fixture that succeeds end-to-end.

## Deep Questions

1. What minimal PDF fixture proves Docling is actually invoked?
2. Can CI install Docling reliably without downloading huge runtime assets?
3. Which pipeline options avoid unnecessary OCR?
4. How should PARTIAL_SUCCESS be treated?
5. What page/file/time bounds fit Personal Edition?

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

- `uv sync --locked --extra pdf` succeeds on the qualified environment.
- Real local PDF fixture becomes normalized text/chunks/pulse.
- Oversized/page-limit fixture is rejected before expensive conversion where possible.
- Timeout/malformed fixture leaves no eligible partial pulse.
- Second unchanged PDF refresh performs no reconversion.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 05B — Build adaptive HTML/PDF parser performance policy

## Child Goal

Use the cheapest parser mode that meets quality, with measurable fallback rather than always paying maximum extraction cost.

## Current Baseline Hypothesis

Current Trafilatura path favors precision and Docling uses default conversion settings.

Re-verify before editing.

## Required Outcomes

- Benchmark Trafilatura current precision path against `fast=True` on a small golden corpus of clean/noisy pages.
- Adopt a fast-first strategy only if quality gates reliably detect insufficient extraction; otherwise keep precision mode.
- Define extraction quality heuristics based on main-text length, boilerplate ratio, sentence density, and known fixture expectations—not model scoring.
- Only escalate from fast HTML extraction to precision/fallback when quality threshold fails.
- For PDF, disable OCR/table structure by default for born-digital text PDFs when current Docling supports this without quality loss; escalate selectively.
- Record parser mode and elapsed time in run ledger.
- Parser contract/version includes mode so cache invalidation is correct.

## Deep Questions

1. Can fast mode save enough time to justify fallback complexity?
2. What cheap heuristic detects fast-mode failure?
3. How do we detect scanned PDF versus born-digital PDF safely?
4. Should OCR escalation be automatic or explicit?

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

- Before/after corpus benchmark reports latency and extraction-quality assertions.
- Clean page uses cheapest qualified mode.
- Noisy page escalates only when needed.
- Parser-version/mode change invalidates cached parse intentionally.
- No model is used to decide parser mode.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 05C — Implement authoritative refresh run ledger and recovery

## Child Goal

Make expensive work bounded, auditable, restartable, and easy to diagnose.

## Current Baseline Hypothesis

Current reliability module is small; jobs/caches exist but application refresh does not expose a complete run ledger/recovery path.

Re-verify before editing.

## Required Outcomes

- Create one run summary owner using existing store/job primitives rather than a parallel observability framework.
- Record discovery requests, fetch requests, bytes, 304/cache hits, documents parsed/reused, parser timings, candidates before/after dedupe, verification counts, provider calls/tokens/cache/cost metadata, retries/failures, elapsed stage timings.
- Persist only bounded summaries; do not log source bodies/prompts/secrets.
- Give refresh/build a durable run ID.
- Use existing durable jobs or minimally extend them so interruption can resume idempotently at stage boundaries.
- Detect abandoned leases/process interruption and recover safely.
- Add per-stage retry classification with capped attempts.
- `doctor --deep` reports schema/integrity/recoverable jobs/last-run summary/queue readiness/parser/provider capabilities without secrets.
- Budget exhaustion is an explicit terminal run state, not an unhandled exception.

## Deep Questions

1. What stage boundaries are worth persisting?
2. How much metrics history should a personal app retain?
3. What job state is sufficient for safe resume?
4. How do we prove retry does not duplicate pulses?
5. Which failures are permanent versus transient?

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

- Kill/interruption fixture after document parse resumes without duplicate parse/pulse.
- 429/timeout fixture schedules bounded retry and no spin.
- Malformed provider/parser fixture records permanent failure accurately.
- Second unchanged refresh shows materially lower work counts.
- Doctor output includes useful summary and no secret/token values.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 05D — Tune SQLite only with evidence

## Child Goal

Keep the local database fast as history grows without premature database replacement.

## Current Baseline Hypothesis

SQLite/FTS5/WAL are already appropriate for Personal Edition; broad database replacement is not justified.

Re-verify before editing.

## Required Outcomes

- Build a synthetic corpus/exposure/run-history benchmark large enough to reveal query/index problems.
- Run `EXPLAIN QUERY PLAN` on hot queries: eligible pulses, exposure history, session queue, FTS shortlist, last run/jobs.
- Add indexes only when query plans/benchmarks justify them.
- Use current SQLite-recommended `PRAGMA optimize` at safe lifecycle points if supported by runtime SQLite.
- Evaluate FTS5 prefix/trigram only for actual query behavior; do not bloat index preemptively.
- Bound history-retention queries and add pruning only for non-authoritative ephemeral metrics if needed.
- Do not add Postgres/DuckDB/vector DB for Personal V1.

## Deep Questions

1. Which query becomes slow first as exposure history grows?
2. Does `PRAGMA optimize` fit short-lived connection lifecycle?
3. Would trigram FTS improve dedupe shortlist enough to justify index size?
4. Which records are authoritative and must never be pruned?

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

- Hot-query benchmark before/after reports p50/p95 or equivalent deterministic timing/work plan.
- Query plans use intended indexes.
- `PRAGMA optimize` path is capability-safe.
- Large synthetic DB still prepares/refills queue within target budget.
- No authoritative lineage is pruned.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 05E — Build the authoritative clean-install CLI E2E matrix

## Child Goal

Prove the product through the exact commands a new user runs, not only direct Python application calls.

## Current Baseline Hypothesis

Current E2E proves the application web path, SQLite restart, and terminal playback, but it does not cover real CLI orchestration or PDF success.

Re-verify before editing.

## Required Outcomes

- Create a clean temp environment/data path and exercise CLI command handlers/application path for init→profile→source/discovery→refresh→play→inspect→stats→doctor.
- Use fixture transports/no external secrets for required CI.
- Add one web HTML E2E and one PDF E2E on the qualified PDF job.
- Prove close/reopen/restart in the real path.
- Prove 10-second cadence with fake/injected sleeper rather than real waiting.
- Prove normal output is English fact only and metadata-free.
- Prove discover is real and not placeholder.
- Prove provider mode through recorded/sanitized fixture path; required CI must not need live API keys.
- Prove continuous refill beyond six items.
- Prove stale invalidation and near-duplicate suppression in integration.

## Deep Questions

1. How can CLI E2E remain fast and deterministic?
2. Which boundaries should be fixture transports versus real parser?
3. How do we prove no pipeline stage is bypassed?
4. What OS matrix is truthful for PDF?

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

- One documented command runs core clean-install E2E.
- Required core CI is fully offline/secretless.
- PDF job separately installs extra and runs real PDF fixture.
- Test fails if discovery command becomes placeholder.
- Test fails if Source/Topic appears in normal play.
- Test fails if network/model/parser is called during tick.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 05F — Final CI, repository cleanup, documentation truth, and V1 freeze

## Child Goal

Declare V1 only if every critical user flow and cost/performance invariant is independently proven.

## Current Baseline Hypothesis

CI currently passes core tests, but optional PDF and several Repo 03 gaps are not yet in required qualification.

Re-verify before editing.

## Required Outcomes

- Keep core CI: locked sync, Ruff, full pytest, authoritative core E2E.
- Add a separate PDF qualification job with `--extra pdf` on a platform proven stable.
- Pin/setup critical CI tooling versions enough for reproducibility without freezing insecure old versions.
- Add repository hygiene check for accidentally committed local DB/secrets/runtime artifacts.
- Execute every README command against clean/isolated state where feasible.
- Document exact default UX and command flow.
- Document provider modes, offline mode, discovery providers, PDF optional requirements, local data backup/reset, harness capability matrix.
- Document cost behavior: display cadence is decoupled from model/network cost; refresh is the expensive phase.
- Search and remove stale placeholder discovery text, dead renderers, obsolete Why-does-this-matter paths, duplicate adapters, stale V1 claims.
- Do not create a release/version tag if critical gates are not all YES.

## Deep Questions

1. Can a new user succeed without knowing architecture?
2. Is any documented capability still test-only?
3. Does any required CI job depend on a secret?
4. What is the strongest remaining reason not to call it V1?
5. Does repository state contain any personal data artifact?

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

- Fresh GitHub Actions run is green after final edit.
- README commands match implemented CLI.
- Repository secret/runtime-artifact scan is clean.
- Core and PDF E2Es are green on qualified jobs.
- Final review finds no critical placeholder paths.
- Final report explicitly states V1 ready YES/PARTIALLY/NO with evidence.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

# FINAL REPO 03 INTEGRATION AUDIT

Before declaring this Execution complete, re-run the full product path incorporating outputs of Repo 03 Executions 01–04:

`discover/register → incremental refresh → extract → dedupe → deterministic/model-escalated knowledge → verify → English fact → rank with profile+exposure → continuous local queue → ambient/manual playback → inspect/stats/doctor`

Then verify:
- a second unchanged refresh is dramatically cheaper in work count;
- a changed source invalidates only affected downstream work;
- a direct English fact needs no provider call;
- provider mode is real when enabled;
- near duplicates do not dominate feed;
- play continues beyond six items;
- agent adapters are optional;
- PDF succeeds on qualified path;
- no remote/model/parser work occurs in tick;
- clean install and CI prove the same architecture.

# FINAL PARENT ACCEPTANCE

- All Repo 03 critical gates are proven.
- Real discovery is usable.
- Incremental invalidation prevents repeated unnecessary work.
- Provider use is selective, cached, budgeted, and fidelity-safe.
- Ranking uses real stored signals/exposure history.
- Near-duplicate suppression is cheap and effective.
- Continuous local feed works.
- Ambient harness integration is useful but optional.
- One-fact terminal UX is clean.
- Real PDF path is qualified.
- Reliability/run ledger and restart recovery are proven.
- CI independently qualifies core and PDF paths.
- Repository contains no accidental personal runtime DB.
- README tells the truth.
- V1 is frozen only if every critical gate is YES.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL AND PERSONAL TERMINAL EDITION V1 RELEASE GATE? — YES / PARTIALLY / NO`

Only `YES` may declare V1 ready for daily personal use.
