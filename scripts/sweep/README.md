# Docs sample sweep

Executes every code sample on the site against the installed `kaappi`
binary and asserts the documented results. This is how the whole site was
verified on 2026-07-26 (~2,200 checks), and the
[docs-samples workflow](../../.github/workflows/docs-samples.yml) keeps it
that way weekly.

```bash
scripts/sweep/run.sh                 # everything
scripts/sweep/run.sh guide procs     # selected sections
```

Sections → runners:

| Section | Runner | Covers |
|---------|--------|--------|
| `migrating` | `sweep_migrating.py` | guide/migrating.md, block by block |
| `cookbook` | `sweep_cookbook.py` + `sweep_cookbook2.py` | all cookbook pages: cumulative claim runs, live HTTP probes of the template servers, CLI transcript replay, `kaappi check` for network/pg/redis code |
| `guide` | `sweep_guide.py` | tutorial/REPL transcripts (pty-driven, answers linenoise cursor queries), diagnostics triggers vs the KP registry, error-message tables, sandbox matrix, a full cc build of the C-extensions walkthrough |
| `procs` | `sweep_procs.py` | all 21 procedures pages: each page replayed as one piped REPL session with block sentinels; every `;=>` claim asserted in order |
| `eco` | `sweep_eco.py` | ecosystem pages, service-backed: live redis + PostgreSQL, a local SMTP sink (`smtp_sink.py`) for email.md's send-email sample, workspace dylibs, per-block connection/schema preludes |
| `playground` | `sweep_playground.py` | the tour lessons and playground examples (extracted via node), plus a WASM-capability lint |

How claims are checked: kaappi's file/REPL modes write-echo every
non-unspecified top-level value, so `;=>` claims match program output
directly. Machine- or time-dependent outputs (pids, uids, timestamps,
listings, random values, tty state, temp names) are executed but not
value-asserted; prose-description claims in API signature blocks are
recognized and skipped.

Environment (see `_common.py`):

- `KAAPPI_WS` — multi-repo workspace root; supplies uninstalled
  pure-Scheme ecosystem libraries, workspace-built C-extension dylibs,
  and the core repo's `lib/` tree for `(kaappi parallel)` (missing from
  release tarballs up to v0.21.0). Anything unavailable is skipped with a
  notice, never failed.
- `SWEEP_PG_USE_EXISTING=1` — use an existing scratch `myapp` database
  (CI service container). Without it the sweep only ever touches a
  database it creates itself and drops afterwards, and refuses to run the
  pg section when a `myapp` database already exists.
- `SWEEP_WORK` — scratch directory (default: under the system tempdir).

The redis section reuses a server already listening on 6379 (CI service)
or starts and stops a private one. The email live check starts its own
SMTP sink on 1025 and leaves the port alone when something (a real
mailcatcher) is already listening there.
