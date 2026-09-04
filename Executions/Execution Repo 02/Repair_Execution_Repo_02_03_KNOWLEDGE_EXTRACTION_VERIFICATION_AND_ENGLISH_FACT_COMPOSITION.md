# REPAIR EXECUTION REPO 02 — EXECUTION 03 — KNOWLEDGE EXTRACTION, VERIFICATION, AND ENGLISH FACT COMPOSITION

## Execution Identity

- Repository: `mohammed09001/repo`
- Target branch: current active branch; do not assume `main` without checking.
- Execution date baseline: 3 September 2026
- Execution type: repair + completion of an existing implementation.
- Agent-neutral: Claude Code, Codex, OpenCode, Anti-Gravity, Gemini CLI, or another capable coding agent may execute it.
- Completion standard: actual repository evidence, not historical reports.

# PARENT EXECUTION GOAL

Complete the knowledge-quality half of the product. Keep the deterministic offline path, integrate at least one real configurable structured-model path without coupling core domains to one vendor, strengthen verification, and produce the exact user-visible unit: one concise English educational fact with all source/topic/evidence metadata hidden during normal playback.

# VERIFIED REPOSITORY STATE FROM THE REVIEW

The review found deterministic `extract_no_llm`, a `StructuredProvider` protocol, `extract_structured`, deterministic evidence verification with an optional verifier, and composition. Tests used fake providers. No real production provider was connected. Current `compose_card()` created a hook like `Why does this matter: {claim}?` plus the claim, which conflicts with the latest minimal fact-only UX.

Re-verify these facts before implementation because the repository may have changed after this prompt was authored.

# CANONICAL SCOPE

`src/curiosity/knowledge/`, `verify/`, `compose/`, provider adapter boundary, pulse persistence/application build use case, relevant tests.

# NON-GOALS

- Do not turn the product into a chat assistant.
- Do not require an LLM for startup or playback of prebuilt/offline content.
- Do not let model output bypass evidence verification.
- Do not show source/topic in normal playback.
- Do not add fine-tuning or a trained recommender.



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

# CHILD LOOP — 03A — Integrate a real provider-neutral quality path

## Child Goal

Provide a real configurable structured-model capability while preserving offline deterministic operation and provider-neutral domain contracts.

## Known Repository Baseline

The reviewed code had StructuredProvider/FakeProvider abstractions but no actual production adapter wired to configuration/application use cases.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Keep provider-specific clients outside core knowledge/verify/compose contracts.
- Implement at least one real configurable provider adapter using a current official API or a clearly documented OpenAI-compatible structured-output boundary selected at execution time.
- Represent provider capability explicitly: disabled/offline/available/degraded.
- Validate structured responses against a strict schema before any canonical persistence.
- Capture model ID, prompt/contract version, usage metadata when available, latency, and bounded cost/request accounting.
- Cache model results by normalized input hash + contract version + model identity where semantically safe.
- Use bounded chunks/evidence rather than whole documents when possible.
- Missing credentials must degrade safely to offline mode, not break `doctor`, local store, or playback of existing pulses.

## Deep Questions

1. Which current official structured-output mechanism is stable enough today?
2. How is provider identity included in derived provenance and cache invalidation?
3. What is the fallback if structured output is malformed twice?
4. How do we avoid vendor SDK types leaking into core models?
5. What is the maximum context sent per extraction/verification/composition call?

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

- Provider contract tests use fake adapters and remain vendor-neutral.
- Recorded/sanitized fixture maps one real provider response into validated structured output.
- Malformed JSON/schema output never creates a playable pulse.
- Same input/model/contract hits cache and does not call provider twice.
- Offline mode still completes a fixture build.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 03B — Strengthen atomic knowledge selection

## Child Goal

Select one useful, self-contained, evidence-grounded idea suitable for a 10-second educational pulse.

## Known Repository Baseline

The deterministic extractor currently selects the first bounded declarative sentence from useful chunks and filters basic boilerplate.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Preserve deterministic extraction as a fallback but improve candidate quality using bounded heuristics.
- In quality mode, ask the structured provider to identify atomic claims, not summaries or multi-paragraph lessons.
- Store topic classification internally for ranking but keep it out of normal presentation.
- Represent uncertainty instead of forcing weak candidates.
- Deduplicate exact/near-identical candidates before expensive verification/composition using deterministic normalization and optional similarity only if already available.
- Reject marketing/navigation/low-information text.
- Keep one idea per candidate whenever possible.

## Deep Questions

1. What makes a claim useful enough to teach rather than merely true?
2. How can deterministic fallback avoid selecting headings/menu fragments?
3. Where should topic classification live?
4. What dedupe threshold avoids collapsing distinct facts?
5. How will source-language content become English without changing factual meaning?

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

- Golden corpus includes technical and non-technical sources.
- Boilerplate/vague/multi-claim fixtures are filtered or split.
- Duplicate inputs do not generate duplicate canonical candidates.
- Topic exists internally but is absent from presentation snapshots.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 03C — Harden evidence verification and stale-lineage behavior

## Child Goal

Ensure only supported, current, policy-safe claims can become playable facts.

## Known Repository Baseline

The reviewed verifier checks source/document/chunk lineage, numeric anchors, direct textual support, optional support verifier, and risk flags.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Persist candidate verification status and reason codes rather than treating verification as ephemeral.
- Run deterministic lineage/numeric/entity/support checks first.
- Use model-assisted verification only when configured and deterministic support is ambiguous.
- Never upgrade uncertain content merely because the queue is short.
- Bind verification to exact source/document/chunk versions.
- Invalidate/rebuild downstream pulse when its verified source/evidence version changes materially.
- Retain explicit rejected/uncertain records for audit only if useful; they must not enter normal playback.

## Deep Questions

1. Which evidence changes invalidate an old verification result?
2. How will model-assisted support judgment be bounded and cached?
3. Can a claim be direct-text supported but still unsafe or misleading?
4. What happens to already-queued pulses after invalidation?

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

- Change a number/entity in a claim and prove it becomes uncertain/rejected.
- Replace evidence document version and prove stale verification cannot remain playable.
- Risk-flagged high-stakes claim is excluded from normal playback.
- Rejected/uncertain candidate cannot be persisted as an eligible pulse.

Then perform both review passes and repair all failures.

## Child Goal Gate

`HAVE WE ACHIEVED THE FINAL GOAL FOR THIS CHILD? — YES / PARTIALLY / NO`

If `PARTIALLY` or `NO`, continue the repair loop.

---

# CHILD LOOP — 03D — Replace card grammar with one concise English educational fact

## Child Goal

Make the normal visible output exactly the simple fact-only experience the user requested.

## Known Repository Baseline

The reviewed composition created a `Why does this matter:` hook and renderer later printed a Source line. This must be superseded for normal playback.

Treat this baseline as a starting hypothesis. Re-verify it against the current branch before editing.

## Required Outcomes

- Create one canonical display fact string in English.
- Default composition should be declarative, not a question/title/body structure.
- Target one sentence and approximately 8–24 English words in ordinary cases; enforce a configurable hard character/wrap budget rather than blindly counting words.
- Do not include source, topic, URL, title, difficulty, confidence, score, evidence, or labels in the normal presentation object.
- Keep pulse ID and lineage internally so explicit inspect can reveal details.
- Quality-provider rewrite may simplify language but cannot introduce unsupported numbers/entities/causal claims.
- Implement a fidelity check comparing the final fact with verified atom/evidence.
- Keep a deterministic fallback fact path.
- Remove or isolate old `Why does this matter` behavior so it cannot leak into normal playback.

## Deep Questions

1. Should the canonical pulse store only fact text or also a presentation version?
2. How is English translation verified against non-English evidence?
3. What wrap budget should be tested at 80/100/120 columns?
4. What should happen when a true claim cannot be safely shortened?
5. How can tests catch accidental Source/Topic leakage?

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

- Golden snapshot normal output is one English fact only.
- Test explicitly fails if `Source:`, topic, title, score, or metadata appears.
- Long fact is simplified or rejected according to the explicit policy.
- Unsupported attractive rewrite is rejected by fidelity guard.
- Non-English source fixture produces verified English fact without adding content.

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

- A real ingested source can produce a persisted verified English fact.
- Only verified/policy-safe knowledge becomes eligible.
- Offline deterministic mode remains usable.
- At least one real configurable quality-provider path exists behind a provider-neutral boundary.
- The old question/source-rich normal card pattern can no longer leak into normal playback.

# FINAL PARENT GOAL GATE

`HAVE WE ACHIEVED THE PARENT EXECUTION GOAL? — YES / PARTIALLY / NO`

Only `YES` completes Execution 03.

# FINAL REPORT

Use the exact Final Report Format from the Execution Operating System.
