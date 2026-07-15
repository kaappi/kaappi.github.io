# Standards Conformance

Kaappi's core language is a complete implementation of R7RS-small. On top of
that, a small set of runtime subsystems — fibers, an I/O reactor, cross-thread
channels — deliberately extend beyond what R7RS-small specifies, since the
standard has no concurrency model at all. This page states both plainly:
where the core language has known gaps against the spec, and where Kaappi
goes beyond the spec's scope on purpose.

Other Schemes document this distinction the same way — Guile's
["R7RS Incompatibilities"](https://www.gnu.org/software/guile/manual/html_node/R7RS-Incompatibilities.html),
Gauche's ["Standard conformance"](https://practical-scheme.net/gauche/man/gauche-refe/Standard-conformance.html)
chapter, CHICKEN's
["Deviations from the standard"](https://wiki.call-cc.org/man/5/Deviations%20from%20the%20standard) —
and this page follows the same shape.

## Core language

Every identifier in [R7RS Appendix A](https://small.r7rs.org/) is
implemented: 601 built-in procedures, 32 syntax forms, and all 14 standard
libraries. The R7RS conformance test suite passes in full. See
[CONFORMANCE.md](https://github.com/kaappi/kaappi/blob/main/CONFORMANCE.md)
in the core repo for exact counts and per-SRFI coverage detail — this page
doesn't restate numbers that live there, so it can't drift out of sync with
them.

## Known gaps against R7RS-small

| Gap | Detail |
|---|---|
| `syntax-case` | Not implemented — R7RS-small itself deliberately standardizes only `syntax-rules`; `syntax-case` is R6RS/implementation-specific territory (Chez, Racket), not a Kaappi omission against the spec it targets. |
| `call/cc` across REPL top-level forms | A continuation captured in one top-level REPL expression can't re-enter a *later* one. Shared behavior with Guile, Chibi, Chicken, Chez, and Racket — not a Kaappi-specific limitation. |
| Fiber parking inside native higher-order procedures | Callbacks driven by `map`, `for-each`, `vector-map`, `dynamic-wind`, and `force` can park a fiber (e.g. on an empty channel) and resume later. Other higher-order procedures — SRFI-1's `fold`/`filter`/`find`, `sort`, `hash-table-walk`, `eval`, and others — are native drivers whose call state can't be suspended; a fiber that blocks inside one of those needs restructuring into a plain Scheme loop. See [Concurrency](guide/concurrency.md#green-threads-fibers). |
| SRFI coverage | 72 SRFIs supported; a handful of optional or non-mutating-only procedures aren't implemented (linear-update list variants, `string-xcopy!`, and similar). See [SRFI Support](guide/srfi-support.md) and CONFORMANCE.md for the exact list. |

## Extensions beyond R7RS-small's scope

R7RS-small has no concurrency model — no threads, no I/O multiplexing, no
shared memory. Everything below is deliberate, documented extension into
that unspecified territory, tracked as [Kaappi Enhancement Proposals
(KEPs)](https://github.com/kaappi/keps).

| Subsystem | KEP | Status | Detect from code |
|---|---|---|---|
| Fibers + I/O reactor | [KEP-0001](https://github.com/kaappi/keps/blob/main/keps/0001-event-loop-reactor.md) | **Final** — shipped | `(cond-expand (kaappi-fibers ...))`, `(cond-expand (kaappi-reactor ...))` |
| SRFI-18 OS threads | — (R7RS-small doesn't cover threads; SRFI-18 predates this project) | Shipped | `(cond-expand (kaappi-threads ...))`, or `(cond-expand ((library (srfi 18)) ...))` |
| Cross-thread channels | [KEP-0002](https://github.com/kaappi/keps/blob/main/keps/0002-cross-thread-channels.md) | **Accepted** — core mechanism shipped; two known correctness issues open in the cross-thread wakeup path ([#1487](https://github.com/kaappi/kaappi/issues/1487), [#1489](https://github.com/kaappi/kaappi/issues/1489)) before this is recommended for production concurrent workloads | Not yet exposed via `cond-expand` — deliberately: see [KEP-0004](https://github.com/kaappi/keps/blob/main/keps/0004-discoverable-deviations.md), which withholds a `kaappi-shared-channels` identifier until the open issues above are resolved, the same way it withheld one earlier for an unmerged wakeup path that could crash the process |
| Shared flat numeric buffers | [KEP-0003](https://github.com/kaappi/keps/blob/main/keps/0003-shared-flat-numeric-data.md) | **Draft** — unimplemented, gated behind KEP-0002 usage data | None — doesn't exist yet |

See [Concurrency](guide/concurrency.md) for how to use fibers, the reactor,
and threads today.

## Detecting subsystems from code

`cond-expand` ([SRFI 0](https://srfi.schemers.org/srfi-0/srfi-0.html)) is the
portable way to branch on what a given Kaappi build actually has, rather than
probing behavior at runtime:

```scheme
(import (scheme base) (kaappi fibers))

(cond-expand
  (kaappi-reactor
    ;; a multiplexed async I/O reactor is compiled in (true on every
    ;; target today, including wasm32-wasi)
    (define (serve conn) (spawn (lambda () (handle conn)))))
  (else
    ;; fall back to a single-connection blocking loop
    (define (serve conn) (handle conn))))
```

A library that wants to degrade gracefully on a build where a subsystem is
absent can check for the library itself instead of (or in addition to) the
bare feature identifier:

```scheme
(cond-expand
  ((library (kaappi fibers)) (import (kaappi fibers)))
  (else (define (spawn thunk) (thunk))))  ; synchronous fallback
```

| Identifier | True when |
|---|---|
| `kaappi-fibers` | `(kaappi fibers)` is compiled in — every target, including wasm32-wasi |
| `kaappi-reactor` | An OS-level I/O multiplexing reactor (kqueue/epoll/`poll_oneoff`) is compiled in |
| `kaappi-threads` | SRFI-18 OS threads are compiled in — every target except wasm32-wasi |

`--sandbox` mode and a WASI host's actual (as opposed to compiled-in) I/O
capability are runtime facts that `cond-expand` — an expand-time construct —
cannot express; see [KEP-0004](https://github.com/kaappi/keps/blob/main/keps/0004-discoverable-deviations.md#unresolved-questions)
for the open question on whether a companion runtime predicate is worth
adding.

## Discovering capabilities from the command line

`cond-expand` answers these questions *inside* a program. `kaappi features`
answers them at the command line — for a person, or an agent, sizing up a build
before running anything:

```console
$ kaappi features --json
{"version":"0.14.1", … ,"features":["r7rs","kaappi", … ,"kaappi-threads"],
 "srfis":{"builtin":[1,9,13, … ],"portable":[0,2,4, … ]},
 "limits":{"initial_frame_capacity":480, … }}
```

It reports the version and git build id, target triple, build mode, the same
compiled-in subsystem identifiers as the table above (whether `--sandbox` is
available among them), and the built-in vs portable SRFIs — all derived from the
one table that drives `cond-expand`, so the CLI and the language can never
disagree about what a build has. Run `kaappi features` with no `--json` for a
human-readable table. See the
[`kaappi features` reference](https://github.com/kaappi/kaappi/blob/main/docs/dev/features.md)
for the full JSON shape.

## Further reading

- [CONFORMANCE.md](https://github.com/kaappi/kaappi/blob/main/CONFORMANCE.md) — exact R7RS and per-SRFI coverage
- [README "Known limitations"](https://github.com/kaappi/kaappi/blob/main/README.md#known-limitations) — the source this page's gaps table summarizes
- [Kaappi Enhancement Proposals](https://github.com/kaappi/keps) — design rationale for everything in the Extensions table above
- [Stability](stability.md) — what's guaranteed not to break, independent of spec conformance
