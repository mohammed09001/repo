# REPAIR EXECUTION REPO 03 — EXECUTION 01 — REAL FEDERATED DISCOVERY + INCREMENTAL KNOWLEDGE BUILD GRAPH

## Execution Identity
- Type: repair + architecture hardening
- Primary target: close discovery wiring, incremental refresh, stale invalidation, unnecessary repeated work
- Canonical scopes: `src/curiosity/application.py`, `src/curiosity/sources/`, `src/curiosity/ingest/`, `src/curiosity/store/`, discovery/refresh CLI, related tests
- Must not create a crawler or cloud service

# PARENT GOAL

Turn Curiosity's source/refresh path into a real user-facing **federated discovery and incremental knowledge build system**.

The key design move is to treat the pipeline like an incremental compiler/build system:

`Source Discovery → SourceRecord → Document → Chunk → Candidate → Verification → Pulse`

Each derived stage must have enough identity/version information to answer:

> Did an upstream truth or stage contract actually change?

If the answer is no, downstream expensive work must be skipped.

If the answer is yes, only the affected downstream branch is invalidated/rebuilt.

This Execution must make `curiosity discover` real, reduce repeated network/parser/model work, and create precise stale-lineage invalidation without adding GraphRAG or a graph database.

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

# CHILD LOOP — 01A — Build the real user-facing discovery control plane

## Child Goal

Make GitHub, Semantic Scholar, URL/feed, and permitted YouTube metadata reachable through one canonical application/CLI discovery flow with explicit source/provider selection and bounded budgets.

## Current Baseline Hypothesis

`CuriosityApplication.discover(adapter, query)` exists and adapters exist, but CLI `discover` currently prints an informational placeholder instead of invoking them.

Re-verify before editing.

## Required Outcomes

- Design one canonical discovery command surface. Prefer explicit modes such as `curiosity discover github <query>`, `curiosity discover papers <query>`, `curiosity discover feed <url>`, with stable help and non-zero failures.
- Wire GitHub and Semantic Scholar adapters to application use cases using config-owned credentials, never ad-hoc environment reads inside domain modules.
- Support source preview vs source registration deliberately: discovery results must not automatically become trusted knowledge.
- Add a bounded selection/register path so the user can turn selected results into registered sources without Python imports.
- Keep YouTube metadata-only policy truthful; no caption bypass.
- Re-evaluate adding Crossref only as a resilient DOI/metadata fallback. Admit it only if a fixture benchmark shows meaningful coverage/resilience and acceptable complexity.
- Persist discovery cursor/cache/rate state only where it prevents duplicate work; do not create a second general cache.
- Return concise discovery counters: provider, requests, results, deduped, registered, rate-limited/failed.
- Required CLI tests must exercise the application boundary rather than instantiate adapters directly.

## Deep Questions

1. What exact user action turns a search result into a fetchable source?
2. How will GitHub repository metadata become educational source content without executing repository code?
3. Should paper discovery store DOI/S2 identity separately from a landing-page URL?
4. How are duplicate discoveries from S2/Crossref/URL canonicalized before ingestion?
5. What should happen when a provider has no key or hits 429?
6. Can discovery remain useful with zero paid API keys?

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

- CLI fixture proves `discover github` calls GitHub adapter and can register a selected result.
- CLI fixture proves `discover papers` calls Semantic Scholar and preserves missing abstract honestly.
- 429/Retry-After fixture exits boundedly and records retry state without spin.
- Unknown provider and absent-key paths fail with truthful actionable messages.
- Normal playback tests remain completely independent of discovery adapters.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 01B — Introduce content-addressed incremental stage keys

## Child Goal

Make every expensive stage reusable when its semantic inputs are unchanged and invalidated when those inputs materially change.

## Current Baseline Hypothesis

Current ingestion has URL cache/ETag and content hashes, but downstream extraction/verification/pulse identity is not a complete stage-versioned incremental build graph.

Re-verify before editing.

## Required Outcomes

- Define a minimal `StageKey`/build-fingerprint contract using hashes of immutable semantic inputs, stage contract version, parser/extractor version, relevant config, and provider/model identity where applicable.
- Do not build a generic DAG framework. Persist only the lineage/fingerprint data required for Curiosity stages.
- On unchanged 304 + unchanged parser contract, reuse document/chunks and skip extraction downstream.
- On same raw bytes but changed parser version, intentionally re-parse.
- On changed document content, invalidate only downstream candidates/evidence/verifications/pulses/session items tied to the superseded document branch.
- Never invalidate unrelated source branches.
- Preserve historical source/document records when useful for inspect/audit while ensuring superseded pulses are no longer eligible.
- Make rebuild idempotent after interruption.
- Expose work counters showing skipped vs rebuilt stages.

## Deep Questions

1. Which semantic inputs actually change a stage's meaning?
2. Which records are immutable history versus current eligibility projections?
3. How can stale pulses be excluded without destructive cascading deletes?
4. How will existing schema rows migrate forward safely?
5. What happens if a provider model changes but source/document does not?
6. Can a partial build restart without redoing already-proven stages?

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

- First refresh builds; second unchanged refresh demonstrates fewer fetch/parse/downstream operations.
- Changing only parser version re-runs parse/chunk stages but not discovery.
- Changing source content invalidates only that source's old eligible pulses.
- Close process after an intermediate durable stage, reopen, and resume without duplicate canonical rows.
- Inspect can still trace an old historical pulse while normal ranking excludes it.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 01C — Make HTTP transport efficient, bounded, and benchmark-driven

## Child Goal

Reduce connection/setup overhead and improve remote safety without adding async complexity that does not pay for itself.

## Current Baseline Hypothesis

Current discovery uses urllib transports with central retry/budget behavior. It is correct enough for fixtures but does not pool connections.

Re-verify before editing.

## Required Outcomes

- Benchmark current transport against a persistent pooled client candidate such as HTTPX on representative multi-request GitHub/S2 fixture/server workloads.
- Adopt HTTPX only if it materially improves latency/resource use or materially simplifies timeout/pooling policy; otherwise document rejection and retain current transport.
- If adopted, use one long-lived client per discovery/refresh run or provider group, with explicit connection limits and connect/read/write/pool timeouts.
- Do not instantiate an async client in a hot loop.
- Preserve fixture-injectable transport contracts.
- Honor GitHub Retry-After and x-ratelimit-reset behavior; do not aggressively retry 403/429.
- Keep per-provider concurrency below documented/observed safe bounds.
- Stream/bound response bodies where practical before allocating unbounded memory.
- Record requests, bytes, retries, cache results, elapsed time per provider.

## Deep Questions

1. Is connection pooling a measurable win at Personal Edition request volumes?
2. Would async add complexity without enough parallelism?
3. How does the transport keep testability equal or better?
4. How are redirect and decompression bounds enforced?
5. How do rate-limit headers influence durable retry timing?

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

- Before/after benchmark with at least repeated requests to same host.
- Pool/concurrency limits are unit-tested.
- Timeout categories are distinguishable.
- Rate-limit fixtures prove no busy-loop.
- Full offline tests remain network-free.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 01D — Repair source identity, discovery dedupe, and repository hygiene

## Child Goal

Prevent duplicate source branches and remove runtime artifacts from version control.

## Current Baseline Hypothesis

Source URLs are canonicalized, but cross-provider identity and committed `.cli-verification/curiosity.db` require cleanup.

Re-verify before editing.

## Required Outcomes

- Create conservative source identity rules: canonical URL first; DOI/paper/repository stable IDs when directly provided; never merge solely on similar titles.
- Deduplicate discovered candidates before fetch.
- Keep source aliases/identifiers only if required to preserve provenance.
- Remove `.cli-verification/curiosity.db` from tracked repository state if confirmed to be a runtime artifact.
- Add `.cli-verification/`, local DB/WAL/SHM artifacts, and other verified runtime scratch paths to `.gitignore` without masking legitimate fixtures.
- Add a repository test or hygiene check preventing accidental committed personal runtime DBs where practical.
- Do not delete intentional fixture databases without evidence.

## Deep Questions

1. What makes two paper results truly the same work?
2. Could DOI canonicalization accidentally collapse versions/preprints?
3. Which DB files are test fixtures versus personal verification output?
4. Should source aliases be persistent or recomputed?

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

- Git status/tree after cleanup contains no personal verification DB.
- Duplicate discovery fixtures from two providers produce one registration candidate only when stable identity proves equivalence.
- Different versions without shared stable identity remain separate.
- Full tests and migration upgrade tests pass.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

# PARENT INTEGRATION REVIEW

After all Child Gates are YES:
- trace two independent sources through discovery→registration→refresh;
- prove unchanged source performs minimal work;
- mutate only one source and prove branch-local invalidation;
- prove `curiosity discover` is no longer a placeholder;
- prove no network/parser/model work entered playback;
- verify no duplicate source/cache/build owner was introduced;
- inspect migrations and existing-profile compatibility;
- run full tests and CI-equivalent commands after final edit.

# FINAL PARENT ACCEPTANCE

- Real GitHub and paper discovery are reachable from CLI/application.
- Explicit URL/feed still work.
- Discovery is bounded, rate-aware, credential-safe, and provider-neutral.
- Incremental stage fingerprints skip unchanged downstream work.
- Stale pulses cannot remain eligible after material upstream change.
- Historical provenance remains inspectable where policy allows.
- Transport decision is benchmark-driven, not fashion-driven.
- Runtime verification DB artifacts are removed/ignored.
- Playback tick remains purely local.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`

Only `YES` completes Repo 03 Execution 01.
