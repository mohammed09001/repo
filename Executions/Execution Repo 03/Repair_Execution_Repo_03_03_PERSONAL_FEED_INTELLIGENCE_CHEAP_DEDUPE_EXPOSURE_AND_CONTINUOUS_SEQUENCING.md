# REPAIR EXECUTION REPO 03 — EXECUTION 03 — PERSONAL FEED INTELLIGENCE + CHEAP DEDUPE + EXPOSURE-AWARE CONTINUOUS SEQUENCING

## Execution Identity
- Type: personalization/sequence repair
- Primary target: replace constant-score ranking, use real exposure state, suppress near-duplicates cheaply, maintain continuous local feed
- Canonical scopes: profile/ranking/sequence/store/application/runtime tests
- No opaque recommender, no mandatory embeddings

# PARENT GOAL

Make the feed feel intelligently personal without becoming an opaque social-media recommender.

The feed should answer four questions locally:
1. Is this fact relevant enough to this user?
2. Is it high enough quality to deserve attention?
3. Has the user effectively seen the same idea recently?
4. What is the best next fact to preserve variety and learning continuity?

Use explainable signals and cheap local algorithms first.

The key technique is a **Near-Duplicate Firewall**:

`exact normalized hash → FTS5/local candidate shortlist → cheap lexical similarity → optional embedding only if explicitly enabled and proven necessary`

Do not pay embedding/model cost for every pair.

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

# CHILD LOOP — 03A — Replace synthetic constant scores with stored real signals

## Child Goal

Build ranking candidates from actual pulse/source/verification/exposure state rather than hard-coded 1.0 quality/novelty/curiosity/freshness values.

## Current Baseline Hypothesis

Current application supplies constant quality, novelty, curiosity, and freshness to ranking.

Re-verify before editing.

## Required Outcomes

- Define explicit bounded signal owners: interest match, verification confidence class, source-quality class if objectively known, educational usefulness, freshness, novelty/repetition, source diversity.
- Do not manufacture a numeric signal when the repository has no evidence; use neutral/default with a reason code.
- Persist or derive only signals that are actually consumed.
- Ranking reasons must remain inspectable internally.
- Use current clock injection for freshness tests.
- Normalize user weights deterministically and preserve custom topics.
- Exclusions are absolute for normal playback.
- Unexpected discovery cannot bypass verification/exclusions.

## Deep Questions

1. What real data exists today for quality?
2. Should source quality be categorical rather than false precision?
3. How does an unseen custom topic get scored?
4. How does freshness differ between evergreen technical facts and news?
5. Which signals should remain neutral until better evidence exists?

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

- Fixture corpus with different topics/verification/source classes produces explainable distinct scores.
- Changing profile weights changes order.
- Excluded topic never appears.
- Same state/clock/seed gives deterministic order.
- Rank reasons correspond to actual stored inputs.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 03B — Build the Near-Duplicate Firewall before ranking/refill

## Child Goal

Prevent repeated/paraphrased facts from occupying attention or model budget using cheap local stages.

## Current Baseline Hypothesis

Current pipeline deduplicates exact normalized candidates within a build but lacks robust cross-source/cross-session near-duplicate suppression.

Re-verify before editing.

## Required Outcomes

- Stage 1: exact normalized content hash for zero-cost duplicates.
- Stage 2: use SQLite/FTS5 to shortlist plausible similar facts rather than compare entire corpus pairwise.
- Stage 3: benchmark RapidFuzz against a small internal similarity implementation on the real short-fact corpus. Admit RapidFuzz only if it materially improves throughput/quality.
- Optionally test compact SimHash only if FTS5+lexical matching is inadequate; no stale/unmaintained dependency may enter without platform qualification.
- Store only minimal similarity fingerprints/index data required.
- Do not merge facts with explicit numeric/entity/negation disagreements.
- Separate `same wording`, `same claim`, and `related concept` so sequencing can keep useful related ideas while blocking repetition.
- Run dedupe before any optional embedding/model stage.
- Do not require vector DB.

## Deep Questions

1. What similarity threshold preserves distinct but related facts?
2. How do we prevent `X increases Y` from merging with `X decreases Y`?
3. How large can the local corpus become before FTS shortlist needs indexing changes?
4. Does RapidFuzz justify a dependency for one-sentence facts?
5. Should dedupe happen at candidate, pulse, or both?

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

- Exact duplicate from two sources is suppressed without provider call.
- Near-paraphrase fixture is suppressed at chosen threshold.
- Contradictory number/negation fixture is not merged.
- Benchmark reports candidate comparisons reduced versus naive all-pairs.
- Full tests pass with dependency both present/absent if made optional.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 03C — Make persisted exposure history drive novelty and cooldown

## Child Goal

Use what the user has actually seen to reduce repetition without optimizing for addictive engagement.

## Current Baseline Hypothesis

`rank()` accepts recent IDs/topics, but application currently does not pass real persisted exposure history.

Re-verify before editing.

## Required Outcomes

- Read bounded recent exposure history from SQLite for the active profile.
- Apply repeat cooldown by fact/claim fingerprint, not only card ID.
- Decay repetition penalties over time or exposure distance using an explicit deterministic rule.
- Use topic streak controls from Profile in both ranking and sequencing.
- Track saved/dismissed outcomes only if product already exposes those controls; do not invent engagement events.
- Do not track total-screen-time streaks.
- Stats should report useful learning coverage/repetition rather than time spent.
- Ensure history queries are indexed/bounded.

## Deep Questions

1. What is a reasonable personal cooldown unit: time, number of exposures, or both?
2. How is a changed/reverified fact treated after prior exposure?
3. How much history should be loaded per refill?
4. How do custom topic weights interact with cooldown?

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

- Recently shown fact is materially demoted/excluded.
- After configured cooldown it becomes eligible according to policy.
- Repeated semantic fingerprint from another source is also penalized.
- History query stays bounded on large synthetic exposure table.
- Stats repetition count reflects semantic policy when feasible.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 03D — Implement continuous low/high-watermark local queue refill

## Child Goal

Make `curiosity play` continue smoothly from a local reservoir without network/model/parser work and without always replaying the same first items.

## Current Baseline Hypothesis

Current bounded session typically ends after its prepared queue and later invocations may rerank the same corpus without exposure-aware refill.

Re-verify before editing.

## Required Outcomes

- Define queue low/high watermarks and a local-only refill operation.
- Refill may call ranking/dedupe/sequence using persisted local pulses only; it may not discover/fetch/parse/model.
- Runtime can request/trigger refill outside the actual render critical section, but the 10-second display operation must remain local and bounded.
- Persist queue generation, position, reasons, and eligibility snapshot needed for restart.
- Skip pulses invalidated after queue construction.
- On corpus exhaustion, choose a documented safe behavior: pause with actionable message, reuse only after cooldown, or finish; never tight-loop.
- Allow continuous sessions larger than six facts without precomputing the whole corpus.
- Preserve restart consistency with at-least-once display semantics.
- Do not silently call `refresh` when local reservoir is empty.

## Deep Questions

1. What is the smallest local refill that prevents visible stalls?
2. How do we avoid repeated reranking of the entire corpus?
3. What happens if queue item becomes stale between refill and display?
4. What does a tiny corpus do after all facts are seen?
5. How do we keep refill cost below the 10-second cadence budget?

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

- Synthetic corpus plays beyond the old six-item limit.
- Spy proves zero network/model/parser calls across every display/refill cycle.
- Invalidated queued pulse is skipped.
- Close/reopen resumes correct next item.
- Tiny corpus reaches documented exhaustion without CPU spin.
- Exposure history changes later refill ordering.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

---

# CHILD LOOP — 03E — Add explainable diversity/continuity policy without opaque ML

## Child Goal

Balance related mini-runs and surprising discovery using transparent bounded rules.

## Current Baseline Hypothesis

Current sequence planner is simple and does not fully exploit internal relationships or configured unexpected discovery share.

Re-verify before editing.

## Required Outcomes

- Use topic/source/claim-similarity information to choose between continuity and exploration.
- Implement an MMR-like or equivalent transparent diversity objective using locally available similarity—not a trained recommender.
- Reserve a configured unexpected-discovery share only from verified high-quality candidates.
- Cap consecutive same-topic facts.
- Allow short related runs such as concept→mechanism→contrast when relationships are explicitly known.
- Never expose relationship/topic labels in normal display.
- Every queue choice gets an internal reason code.
- Use deterministic seed where any tie-breaking randomness exists.

## Deep Questions

1. How much continuity is educational versus repetitive?
2. How can unexpected discovery avoid becoming random junk?
3. What similarity metric can power MMR cheaply?
4. How do we test ratio behavior without statistical flakiness?

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

- Configured topic mix is reflected structurally across a long synthetic queue.
- Unexpected discovery stays within configured tolerance and never bypasses exclusions.
- Same seed/state gives same queue.
- Related mini-run fixture is coherent but respects streak cap.
- Queue reason codes explain every selected item.

Then run both review passes. Any failure re-enters the Failure Loop.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

Only `YES` permits this Child to be considered complete.

# PARENT INTEGRATION REVIEW

Build a synthetic persisted corpus large enough to expose O(n²) mistakes and repetition problems.
Verify:
- real profile changes rank;
- exposure history changes later order;
- near duplicates are blocked before expensive work;
- continuous queue crosses multiple refill cycles;
- stale queued items are skipped;
- no external/heavy work happens in tick;
- no opaque recommender or mandatory embeddings were introduced.

# FINAL PARENT ACCEPTANCE

- Constant synthetic scoring is removed from the real application path.
- Real stored state drives explainable ranking.
- Cross-source near-duplicate repetition is strongly reduced using cheap local stages.
- Exposure history influences subsequent feed order.
- Continuous local refill works beyond the old bounded session.
- Unexpected discovery remains explicit, bounded, and quality-gated.
- Queue remains deterministic/testable and local.
- Normal display UX is unchanged.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`
