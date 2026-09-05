# REPAIR EXECUTION REPO 03 — EXECUTION 02 — PROVIDER ECONOMY + VERIFIED ENGLISH FACT + MODEL COST CONTROL

## Execution Identity
- Type: repair + quality/cost architecture
- Primary target: wire real provider mode, reduce LLM calls, enforce fidelity, translate safely, cache and account for model work
- Canonical scopes: provider/config/application/knowledge/verify/compose/store/CLI/tests
- Must preserve full offline deterministic operation

# PARENT GOAL

Create a **two-speed Knowledge Factory**:

1. `FAST LANE` — deterministic extraction + deterministic verification + deterministic fact composition whenever evidence is strong enough.
2. `QUALITY LANE` — provider-assisted extraction/translation/verification/rewrite only when the expected quality gain justifies cost.

The engine must never use `one model for everything`.

Instead it should perform **value-of-information escalation**:

`cheap deterministic checks → cheap capable model if needed → stronger model only on unresolved ambiguity`

Every model call must be necessary, bounded, attributable, cacheable where semantically safe, provider-neutral, and impossible inside normal playback ticks.

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

# CHILD LOOP — 02A — Wire a real provider registry into config, application, and CLI

## Child Goal

Make configured provider mode actually usable by `refresh/build` while preserving provider-neutral core contracts and safe offline fallback.

## Current Baseline Hypothesis

`OpenAICompatibleStructuredProvider` and provider API-key config exist, but the normal CLI constructs `CuriosityApplication(store)` without a production provider.

Re-verify before editing.

## Required Outcomes

- Define one minimal provider registry/factory outside core domain logic.
- Support at least the existing OpenAI-compatible adapter as a real CLI/application path.
- Add provider/model/base-url configuration without storing secrets in DB.
- Capability reporting must distinguish `offline`, `configured`, `reachable/degraded` when safely testable.
- Missing credentials must automatically preserve deterministic offline operation.
- Do not let `doctor` claim model generation is configured if no usable provider/model configuration can actually be constructed.
- Evaluate Instructor and LiteLLM under the Dependency Admission Gate. Do not add both. Prefer the smallest option that materially improves provider portability/structured validation/cost accounting.
- If retaining custom adapters is simpler, make that an explicit evidence-backed decision.
- Provider-specific SDK/types must not leak into KnowledgeCandidate/Verification/Pulse contracts.

## Deep Questions

1. What is the smallest provider abstraction that supports OpenAI-compatible, Anthropic, and Gemini without a framework tax?
2. Do we need a generic router library now, or only a stable internal protocol?
3. How is model identity represented for cache invalidation?
4. What exactly constitutes provider readiness?
5. How does CLI select provider/model without complicating normal use?

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

- Fixture config creates a real production provider object through the same path CLI uses.
- Offline mode still builds and plays a fixture with no keys.
- Malformed/missing provider config degrades safely.
- Provider-specific object never appears in persisted canonical domain payloads.
- Doctor capability output matches actual constructible behavior.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 02B — Implement value-of-information escalation and model cascade

## Child Goal

Spend model tokens only on candidates that cannot meet product quality/fidelity requirements deterministically.

## Current Baseline Hypothesis

Current `refresh_build()` chooses structured extraction whenever a provider exists, otherwise NoLLM, effectively making provider availability a global switch rather than a per-candidate quality decision.

Re-verify before editing.

## Required Outcomes

- Create explicit escalation reasons such as non-English evidence, ambiguous claim boundaries, multi-claim sentence, weak direct support, fidelity rewrite requirement, or policy-sensitive ambiguity.
- Run deterministic extraction/dedupe/verification first.
- Do not call a model for direct, concise, supported English claims that already meet display grammar.
- Allow a cheap model tier for atomic extraction/translation/rewrite and a stronger tier only after a first result remains uncertain or fails fidelity.
- Never upgrade uncertain evidence merely to fill queue inventory.
- Bound calls per document/source/refresh.
- Record escalation reason and outcome in local diagnostics, not normal playback.
- Use a deterministic fallback/reject policy when all model tiers fail.

## Deep Questions

1. Which exact cases truly benefit from model work?
2. How do we estimate expected quality gain without an ML recommender?
3. What is the maximum number of calls a single source can trigger?
4. What failure should fall back versus reject?
5. Could a cheap model rewrite a true claim into an unsupported causal claim?

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

- Golden corpus proves obvious direct English facts require zero provider calls.
- Non-English or ambiguous fixture triggers only the expected bounded escalation.
- Repeated failed model output cannot create a pulse.
- Provider call count is asserted per fixture.
- Changing queue size alone never triggers more model work.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 02C — Add semantic-safe provider cache, prompt-cache friendliness, and optional batch capability

## Child Goal

Reduce repeated token spend by reusing semantically identical model work and exposing provider-specific economy features behind capabilities.

## Current Baseline Hypothesis

No canonical model-result cache or provider capability matrix currently proves repeated quality builds avoid duplicate calls.

Re-verify before editing.

## Required Outcomes

- Define cache identity from normalized bounded input + task contract version + model/provider identity + relevant output schema version.
- Never reuse cache across changed evidence or changed verification/composition contract.
- Persist validated structured results, not raw secret-bearing request payloads.
- Expose capability flags such as `supports_structured`, `supports_prompt_cache`, `supports_batch`, `supports_usage_tokens`, `supports_cost_metadata`.
- Order static instructions/schema before variable evidence when a provider benefits from prefix prompt caching.
- Record provider-reported cached-token usage when available.
- Support batch only as an explicit non-interactive quality mode where semantics and latency allow; do not make 24h batch the normal refresh path.
- Provider Batch APIs are optional optimization surfaces, not product requirements.
- Use local cache first; provider prompt cache is a second-level optimization, never correctness storage.

## Deep Questions

1. Which inputs are safe to cache?
2. How do we invalidate a translation/rewrite after evidence changes?
3. Does batch make sense for one-user refresh volumes?
4. What capability metadata can be provider-neutral?
5. How do we avoid storing full prompts containing unnecessary source text?

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

- Same input/model/contract hits local cache and performs zero second provider call.
- Changed source evidence misses cache.
- Changed model or contract version misses cache.
- Cached-token metadata is recorded when present but absence does not fail.
- Batch-disabled provider follows synchronous bounded path.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 02D — Produce one verified English educational fact with fidelity/translation gates

## Child Goal

Guarantee that normal display text is concise English and cannot introduce unsupported meaning during simplification or translation.

## Current Baseline Hypothesis

Current composition mostly reuses candidate atom statement and enforces basic length/clickbait checks; there is no complete translation/fidelity layer.

Re-verify before editing.

## Required Outcomes

- Keep normal fact exactly one concise declarative English sentence.
- Target roughly 8–24 words for ordinary facts; use a hard character/wrap budget as the real UI constraint.
- Do not expose Topic/Source/title/score/etc. in normal presentation.
- For non-English evidence, create a translation step only when needed and bind the English fact back to original evidence.
- Implement deterministic anchor checks for numbers, dates, named entities, negation, comparison direction, and modality.
- Model-assisted fidelity judgment is allowed only after deterministic checks and must itself be bounded/cached.
- Reject attractive rewrites that add causal claims, certainty, superlatives, or entities not supported by evidence.
- Persist final fact contract/version so composition changes trigger intentional rebuild.
- Explicit inspect must show original evidence and final fact lineage.

## Deep Questions

1. What does fidelity mean for translation rather than paraphrase?
2. Which anchors can be checked deterministically?
3. What should happen if a correct fact cannot be shortened safely?
4. How do we avoid forcing English when source meaning cannot be confidently preserved?
5. How can tests detect subtle negation reversal?

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

- English fixture stays unchanged without model call.
- Non-English fixture produces a verified English fact tied to original evidence.
- Changed number/entity/negation rewrite is rejected.
- Long but true claim is safely shortened or excluded according to policy.
- Snapshot normal output contains only the fact.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 02E — Build model-work accounting and explicit budgets

## Child Goal

Make token/cost consumption observable and enforceable per refresh without turning the project into a billing platform.

## Current Baseline Hypothesis

Provider adapter can return token counts/latency, but current application does not own a full model-work ledger.

Re-verify before editing.

## Required Outcomes

- Persist/run-summary model usage: calls, input tokens, output tokens, cached tokens when provided, latency, task type, model ID, cache hit/miss, escalation tier.
- Represent cost only when pricing is explicitly configured/currently known; never invent provider prices.
- Allow hard budgets per refresh: max model calls, max input chars/tokens when known, max output tokens, optional max configured cost.
- Budget exhaustion stops quality escalation safely while preserving already-verified deterministic content.
- Expose `refresh --dry-run` or equivalent work estimate if it can be implemented truthfully from local state.
- Do not build subscriptions, invoices, or cloud billing.
- Add summary output that lets the user see why a refresh cost money.

## Deep Questions

1. How do we handle providers that do not return usage?
2. Should price tables live in code or user config?
3. What happens mid-document when budget is exhausted?
4. Can dry-run estimate safely without making provider calls?
5. How does batch/prompt caching appear in the ledger?

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

- Budget fixture stops before exceeding max calls.
- Usage persists across close/reopen when required for audit.
- Unknown price is reported as unknown, never zero-cost.
- Cache hit records zero provider call.
- Playback stats remain learning-oriented and do not become cost gamification.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

# PARENT INTEGRATION REVIEW

- Run one source that needs zero model calls and one source that requires quality escalation.
- Prove configured provider is actually used by CLI/application.
- Prove a repeated unchanged quality build hits local model cache.
- Prove provider failure cannot create an unverified playable pulse.
- Prove English translation/fidelity path preserves evidence anchors.
- Prove no model work happens during playback.
- Review dependency choice (custom vs Instructor vs LiteLLM) against measurable burden/benefit.

# FINAL PARENT ACCEPTANCE

- Real provider mode is wired, not merely present as a class.
- Offline mode remains first-class.
- Deterministic fast lane minimizes model calls.
- Quality lane is bounded and reason-driven.
- Model outputs are validated/cached/invalidation-safe.
- Prompt-cache/batch capabilities are opportunistic and provider-neutral.
- Final fact is concise English and fidelity-proven.
- Model usage/cost work is observable and budgeted.
- No model call exists in the 10-second tick.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`
