# Curiosity Engine — Personal Terminal Edition

Curiosity Engine is local-first software for building a small, verified queue of
facts from sources you explicitly add. Normal playback is deliberately quiet:
one concise English fact every 10 seconds, with no topic, source, score, or
other metadata. Use `inspect` when you want provenance.

## Install and first use

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```powershell
git clone https://github.com/mohammed09001/repo.git
cd repo
uv sync --locked
uv run curiosity init
uv run curiosity profile set --interest general=3
uv run curiosity source add https://example.com/an-article
uv run curiosity refresh
uv run curiosity play
```

`play` displays the already-built local queue. It does not download, parse,
rank, or call a provider while its 10-second clock is running. Press Ctrl-C to
stop; the next invocation resumes from coherent local session state. Use
`--once` for a single fact. In an interactive terminal `play` replaces one
single region in place so normally only the current fact is visible; when
output is redirected it falls back to clean newline records with no terminal
control sequences.

```powershell
uv run curiosity inspect pulse_xxxxxxxxxxxxxxxxxxxxxxxx
uv run curiosity stats
uv run curiosity doctor --deep
```

`inspect` is the explicit provenance path: it includes source URL, evidence,
verification reasons, topics, and generation metadata. `stats` reports facts
and topics explored rather than screen-time streaks.

## Discovery and registration

Discovery providers are optional and never auto-register trusted sources.
Results land as untracked candidates that you turn into sources deliberately:

```powershell
uv run curiosity discover github <query> --limit 5
uv run curiosity discover papers <query> --limit 5
uv run curiosity discover feed <url>
uv run curiosity discover youtube <query> --limit 5
uv run curiosity discover list
uv run curiosity discover register --all
uv run curiosity refresh
```

`discover` prints per-provider counters (requests, results, deduped,
candidates, registered, rate-limited, failed). Rate limits are honored via
Retry-After, stored locally, and never retried in a busy loop. Discovery
credentials are read from your config file or environment variables and are
never printed: `CURIOSITY_GITHUB_TOKEN`, `CURIOSITY_SEMANTIC_SCHOLAR_API_KEY`
(alias `CURIOSITY_S2_API_KEY`), and `CURIOSITY_YOUTUBE_API_KEY`. An optional
model key `CURIOSITY_PROVIDER_API_KEY` enables structured extraction during
`refresh`. YouTube discovery is authorized metadata only; it never downloads
captions.

## Two-speed knowledge factory

`refresh` is a two-speed build: a deterministic fast lane proves direct,
concise, supported English claims with zero model calls, and a bounded quality
lane escalates only candidates the fast lane cannot prove (non-English
evidence, multi-claim sentences, verbose rewrites, or weak direct support).
Model work is value-of-information driven, never queue-driven:

```powershell
# config.toml (secrets stay in env/secret storage; never in the database)
provider_api_key = "..."
provider_model = "gpt-4o-mini"        # cheap tier
provider_strong_model = "gpt-4o"      # optional stronger tier
provider_base_url = "https://api.openai.com/v1"
provider_max_calls = 20               # hard per-refresh budget
provider_prices = { input = 0.15, output = 0.60 }  # per million tokens, explicit only
uv run curiosity refresh              # prints per-task token/cost model usage
uv run curiosity refresh --dry-run    # local-state work estimate, no network
```

Model results are cached locally by task+evidence+model+contract, so unchanged
quality builds make zero provider calls. Cost is reported only when you
explicitly configure prices; otherwise it is `unknown`, never zero. `doctor`
reports whether provider mode is truly constructible (`configured`) or offline,
and never claims a capability that cannot be built. The provider adapters
remain custom (OpenAI-compatible over HTTPX); LiteLLM and Instructor were
measured and rejected under the dependency gate (LiteLLM: 22s import + ~148 MB;
Instructor: requires a provider SDK and adds no validation we lack).

## Local data and recovery

The default configuration and data directories use the platform-standard
`curiosity-engine` locations reported by `curiosity doctor`. Supply
`--data-path <directory>` on any command for an isolated store. Back up that
directory, especially `curiosity.db`; it holds the SQLite database and durable
queue. To reset an isolated installation, close Curiosity and remove only that
explicit data directory.

No account, network credential, coding agent, or model provider is required for
the CLI itself. Sources do require network access during `refresh`; playback is
fully local afterward. The offline deterministic extractor is the default.

## Personal feed intelligence

Ranking and playback use real stored state, never fabricated scores:

- **Near-Duplicate Firewall.** Before a fact becomes a new pulse it is checked
  against the local fact index: exact normalized fingerprint, then an FTS5
  shortlist, then cheap RapidFuzz lexical similarity. A fact that re-states an
  existing idea (`same wording`/`same claim`) is suppressed; contradictory
  number/negation/direction anchors are never merged. No embeddings or vector
  store are used.
- **Exposure-aware cooldown.** What you have actually seen drives the feed. A
  fact (or a paraphrase of it) shown within the last few hours is excluded; it
  recovers after a deterministic wall-clock and exposure-distance cooldown.
  Verified quality class, source trust, and recency replace constant 1.0
  ranking signals, and every queue choice carries an internal reason code.
- **Continuous refill.** `curiosity play` keeps a durable local reservoir above
  a low watermark, refilling with locally ranked batches (no network/parse/model
  in the tick). Queued items invalidated by a removed or rebuilt source are
  skipped. When the local corpus is genuinely exhausted, playback finishes
  instead of tight-looping.
- `curiosity stats` reports learning coverage, including `semantic_facts_shown`
  and `semantic_repetitions` (distinct ideas vs total shown), never screen-time.

## Optional capabilities

Web HTML extraction uses Trafilatura in its precision mode: a cheap
sentence-density quality gate decides between the precision path and the
conservative HTML fallback. Trafilatura's `fast` mode was benchmarked against a
golden corpus of clean and noisy pages and rejected — it leaks navigation
boilerplate and can return empty text on clean small pages, and those failures
are not reliably detectable by cheap heuristics.

PDF parsing needs the optional `pdf` extra and a platform where Docling is
supported:

```powershell
uv sync --locked --extra pdf
```

PDF conversion is bounded and local: Docling converts engine-fetched bytes
through an in-memory document stream with its own `max_num_pages` and
`max_file_size` bounds, a `document_timeout`, and a single CPU thread. OCR and
table-structure are disabled by default for born-digital text PDFs. Only a full
`SUCCESS` conversion is qualified — malformed, oversize, timeout, and
partial-success PDFs never become canonical successful documents. A real PDF
fixture succeeds end-to-end in a dedicated CI job. The first PDF conversion on
a machine downloads Docling's local layout models (~300 MB) once into the
Hugging Face cache; after that, conversion is offline and cached by content.
PDF is not required for the normal web source workflow. YouTube integration
only obtains authorized metadata; it does not download captions or bypass
permissions. Provider keys are optional and never printed by `doctor`.

## Reliability and cost behavior

Every `refresh`/build run is durable and auditable through one bounded
`run_summaries` ledger row: fetch counts, 304 cache hits, bytes, parser mode and
timings, candidates, verification, model calls/tokens/cache/cost metadata,
retries/failures, and elapsed stage timings. Source bodies, prompts, and
secrets are never stored in the ledger.

```powershell
uv run curiosity refresh   # prints the run ledger counters
uv run curiosity doctor --deep   # schema/integrity/recoverable jobs/last-run/parser/provider
```

- **Display cost is decoupled from model/network cost.** `refresh` is the only
  expensive phase; `play` reads a precomputed local queue and performs zero
  network/model/parser/ranking work on its 10-second tick. No recurring cost is
  added to produce screen activity.
- **Interruptions recover safely.** A killed refresh leaves a leased `jobs` row
  that the next run detects and resets; every stage is idempotent (conditional
  GET + `ON CONFLICT`), so resuming never duplicates documents or pulses.
  Transient network/HTTP failures retry with capped exponential backoff;
  permanent failures are recorded accurately and never spin.
- **Budget exhaustion is an explicit terminal run state**, not an exception:
  `run_status budget_exhausted` is reported and the run still lands in the
  ledger.
- SQLite is tuned with evidence: the hot session-queue query uses a dedicated
  index, and `PRAGMA optimize` runs at safe close lifecycle points. No
  authoritative exposure/pulse lineage is ever pruned.

Coding-agent integrations are optional and separate from core playback. Claude
can install a minimized Stop hook; OpenCode can install a project plugin; Codex
is completion-notification-only. Supply an explicit path so no existing agent
configuration is overwritten:

```powershell
uv run curiosity harness install claude --path .claude/settings.local.json
uv run curiosity harness status claude --path .claude/settings.local.json
uv run curiosity harness uninstall claude --path .claude/settings.local.json
```

Lifecycle events feed a small local **ambient runtime controller**: raw adapter
events are translated into a provider-neutral state (`unknown`, `active_work`,
`waiting_or_idle`, `turn_complete`, `quiet`) that only influences whether an
ambient playback loop is active or quiet and whether the local queue may
refill. It never touches source truth, verification, knowledge content, or
ranking, and it performs no network/model/parse work implicitly. `play --ambient`
plays only while an adapter reports active work and stops at the next fact
boundary when the controller quiets (the current fact always finishes its
dwell). Manual `play` always bypasses the controller:

```powershell
uv run curiosity harness --data-path <dir> emit opencode working   # active
uv run curiosity play --ambient
uv run curiosity harness --data-path <dir> state                   # derived state
```

Adapter capabilities stay truthful to current documentation: OpenCode maps its
documented `session.status` busy/idle, `session.idle`, `session.created`, and
`session.error` events (with a per-kind debounce); Claude maps only the
documented `Stop` hook to completion and never claims busy/idle; Codex maps
only the `notify` completion payload. Prompt, code, transcript, and token/cost
content are never persisted.

## Development qualification

```powershell
uv sync --locked
uv run ruff check .
uv run pytest
uv run pytest tests/test_e2e.py -q
uv run pytest tests/test_cli_e2e.py -q   # clean-install CLI matrix
uv sync --locked --extra pdf
uv run pytest tests/test_pdf_qualify.py tests/test_cli_e2e.py -q   # PDF path
```

The web E2E uses a fixture transport, real SQLite, Trafilatura, extraction,
verification, composition, ranking, queue persistence, restart, and fake-clock
playback. The CLI E2E runs the real command handlers against local mock HTTP
servers (HTML article, RSS feed, PDF, and an OpenAI-compatible provider) — the
exact commands a new user runs — with no external network or credentials. The
PDF qualification converts a real PDF fixture through bounded Docling. GitHub
Actions runs the locked core qualification on every push and pull request and a
separate PDF job installs the `pdf` extra and runs the real PDF fixture. A
repository-hygiene test fails if a local runtime database or secret artifact is
ever committed.
