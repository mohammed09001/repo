# REPAIR EXECUTION REPO 02 — EXECUTION 02 — REAL SOURCE DISCOVERY, CONDITIONAL REFRESH, TRAFILATURA, AND DOCLING

## Execution Identity

- Repository: `mohammed09001/repo`
- Target branch: current active branch; do not assume `main` without checking.
- Execution date baseline: 3 September 2026
- Execution type: repair + completion of an existing implementation.
- Agent-neutral: Claude Code, Codex, OpenCode, Anti-Gravity, Gemini CLI, or another capable coding agent may execute it.
- Completion standard: actual repository evidence, not historical reports.

# PARENT EXECUTION GOAL

Complete the source-to-chunk half of the product. Make GitHub, Semantic Scholar, URL/feed, and permitted YouTube metadata usable through the application; make repeated refresh efficient; replace the current HTML shortcut with a qualified Trafilatura path; and implement a real bounded Docling PDF success path.

# VERIFIED REPOSITORY STATE FROM THE REVIEW

The review found `GitHubAdapter`, `SemanticScholarAdapter`, `WebAdapter`, `YouTubeAdapter`, a bounded HttpClient, and an ingestion pipeline. GitHub metadata already captures rate/ETag headers, and explicit ingestion stores ETag/Last-Modified. However, source discovery was not wired to a real user flow. Semantic Scholar `batch_metadata()` looped over single calls. HTML used a small custom HTMLParser. PDF handling imported Docling if available and then deliberately raised `Docling integration is not enabled`. `pyproject.toml` did not include Trafilatura/Docling as qualified runtime dependencies.

Re-verify these facts before implementation because the repository may have changed after this prompt was authored.

# CANONICAL SCOPE

`src/curiosity/sources/`, `src/curiosity/ingest/`, application source/refresh use cases, relevant dependency declarations/lockfile, source/parser tests.

# NON-GOALS

- Do not build a crawler.
- Do not execute GitHub repository code.
- Do not scrape YouTube transcripts without an authorized/user-supplied path.
- Do not put source fetching in playback.
- Do not replace SQLite.


# CURRENT EXTERNAL GROUND TRUTH TO RE-VERIFY

- GitHub official REST best practices currently recommend authenticated conditional requests, ETag/If-None-Match, respecting Retry-After/x-ratelimit-reset, cacheable requests, and avoiding unnecessary concurrency: https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api
- Semantic Scholar's current tutorial explicitly recommends batch/bulk endpoints and API keys for efficiency; Recommendations API provides seed-based recommendations: https://www.semanticscholar.org/product/api/tutorial and https://api.semanticscholar.org/api-docs/recommendations
- Trafilatura 2.2 current Python docs expose `extract()` as main extraction with quality fallbacks: https://trafilatura.readthedocs.io/en/latest/usage-python.html
- Docling current quickstart exposes `DocumentConverter().convert(...)` and Markdown export: https://docling-project.github.io/docling/getting_started/quickstart/


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

# CHILD LOOP — 02A — Wire GitHub and web/feed discovery with conditional refresh

## Child Goal

Make source discovery and refresh usable, bounded, and cache-aware so unchanged sources do not repeatedly consume expensive work.

## Known Repository Baseline

GitHub adapter exists and captures ETag/rate headers. HttpClient has request budgets/retries. Ingestion has conditional headers for explicit source content, but no complete application-level repeated discovery/refresh lifecycle was proven.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Expose GitHub repository discovery through the canonical application source workflow.
- Support optional authenticated GitHub requests through secret-safe configuration.
- Persist source adapter cache state required for stable conditional GET refresh.
- Use ETag/If-None-Match and Last-Modified/If-Modified-Since where the endpoint supports them.
- Honor Retry-After and x-ratelimit-reset; do not aggressively retry 403/429.
- Keep request parameters stable and request only needed fields/results.
- Wire explicit URL and RSS/Atom discovery through the same canonical source registration path.
- Record concise refresh counts: discovered, fetched, unchanged/reused, parsed, failed.

## Deep Questions

1. Which GitHub endpoints are actually refreshed vs only searched?
2. Where should ETag live so it is bound to an exact stable request representation?
3. What happens if the token is added/removed between refreshes?
4. Can 304 correctly prevent downstream parsing/build?
5. How are secondary rate-limit errors distinguished from permanent 403?

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

- Fixture first GitHub metadata call returns 200+ETag; second sends If-None-Match and handles 304.
- 429/Retry-After fixture schedules/stops safely without busy-loop.
- Repeated unchanged refresh performs no duplicate downstream parse.
- URL/feed discovery produces canonical SourceRecords through the application path.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 02B — Repair Semantic Scholar efficiency and discovery semantics

## Child Goal

Use current Semantic Scholar APIs correctly and efficiently for paper search/details/recommendations.

## Known Repository Baseline

The reviewed adapter had keyword search and a `batch_metadata()` function that simply invoked metadata repeatedly rather than using a true batch endpoint.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Re-verify current Semantic Scholar Academic Graph paper bulk/batch endpoints and Recommendations API before coding.
- Implement a true paper batch details request for multiple IDs where the current API supports it.
- Use bulk search where appropriate for broad keyword discovery rather than unnecessarily expensive per-paper flows.
- Keep Recommendations API as an explicit seed-based recommendation mode; do not silently substitute it for keyword search.
- Support optional API key and truthful unauthenticated capability state.
- Request only fields the engine actually consumes.
- Normalize all returned papers into canonical SourceRecords without inventing abstract/full-text availability.
- Enforce request budgets/rate behavior.

## Deep Questions

1. What exact distinction should exist between keyword search, bulk search, batch details, and recommendations?
2. Which endpoints are POST vs GET today?
3. How will tests prove N paper IDs do not cause N HTTP calls?
4. What happens when an ID is missing in a batch response?
5. How is API-key absence surfaced?

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

- Multiple IDs use a single batch transport call in a fixture.
- Recommendation fixture uses positive/negative seed body only when explicitly requested.
- Missing abstract is represented as missing, never synthesized.
- Rate/budget failure is bounded and resumable.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 02C — Make Trafilatura the real primary web extractor

## Child Goal

Use Trafilatura for high-quality main-content extraction from already-bounded fetched HTML while retaining only a clearly scoped safe fallback.

## Known Repository Baseline

The reviewed ingestion pipeline used a small local HTMLParser that removed script/style/nav/header/footer but did not use Trafilatura.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Add a compatible Trafilatura dependency and lock it.
- Create one canonical HTML extraction adapter around Trafilatura `extract()` or current equivalent.
- Feed already-fetched bounded HTML bytes/string into extraction; do not let Trafilatura introduce an uncontrolled second network path.
- Extract main content with comments/boilerplate disabled as appropriate.
- Version the parser behavior so cache invalidation is deterministic after extractor upgrades/config changes.
- Retain the old simple parser only as a named fallback if justified; never silently treat fallback quality as primary.
- Reject empty/near-empty extraction rather than persisting junk.

## Deep Questions

1. What exact output format best preserves enough structure for deterministic chunking?
2. What parser-version inputs must be included in cache identity?
3. When should fallback run?
4. How can extraction quality be tested without brittle full-page exact strings?

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

- Noisy fixture page keeps main article text and drops navigation/script/footer.
- Test proves primary Trafilatura path was actually invoked.
- Empty/malformed page follows explicit error/fallback policy.
- Parser-version change causes intentional reprocessing rather than stale reuse.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 02D — Implement real bounded Docling PDF extraction

## Child Goal

Turn the current deliberate PDF failure into a real successful document conversion path without unbounded work.

## Known Repository Baseline

The reviewed code detected `application/pdf`, imported Docling if installed, then always raised an IngestError saying Docling integration is not enabled.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Add/qualify Docling dependency or a clearly documented optional extra that Personal V1 actually tests.
- Create one Docling parser adapter using current `DocumentConverter` behavior.
- Pass a bounded local file or in-memory stream produced by the engine fetch policy; do not let Docling bypass the engine's remote-fetch controls.
- Export normalized Markdown/text from the converted document.
- Preserve useful page/section provenance if available without overcomplicating the canonical model.
- Enforce file-size/page/time/resource bounds.
- Keep OCR/VLM/expensive pipelines opt-in unless required by a fixture.
- Parser failure must not leave a partial canonical document.

## Deep Questions

1. What is the safest boundary between engine downloader and DocumentConverter?
2. How will page limits be enforced before/while conversion?
3. How is parser provenance represented?
4. What happens when Docling is unavailable on a supported installation?
5. Which minimal PDF fixture proves real success?

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

- A small real PDF fixture successfully becomes normalized document/chunks.
- Oversized/page-limit fixture fails safely.
- Malformed PDF leaves no partial canonical document.
- Repeated unchanged PDF is reused and not reconverted.

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

- GitHub discovery/refresh is exposed and conditional/cache-aware.
- Semantic Scholar batch behavior is real rather than a loop.
- Trafilatura is the qualified primary HTML extractor.
- Docling has a proven PDF success path.
- Repeated unchanged refresh demonstrably avoids unnecessary fetch/parse work.
- All authoritative tests remain offline/fixture-backed.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`

Only `YES` completes Execution 02.

# FINAL REPORT

Use the exact Final Report Format from the Execution Operating System.
