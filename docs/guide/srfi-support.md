# SRFI Support

Kaappi supports 85 SRFIs (Scheme Requests for Implementation). Eleven are
built into the runtime as native Zig code, and 73 are portable R7RS
libraries loaded on demand from `.sld` files. SRFI 261 is a
[naming convention](#srfi-261) honored by the import resolver with no
library file at all.

All SRFIs are imported with `(import (srfi N))`:

```scheme
(import (srfi 1))   ; list library
(import (srfi 69))  ; hash tables
```

Portable code can detect whether a given SRFI is available before importing
it with `(cond-expand ((library (srfi N)) ...) (else ...))`, or with the
equivalent `srfi-<n>` feature identifier:

```scheme
(cond-expand
  (srfi-250 (import (srfi 250)))  ; insertion-ordered hash tables
  (else     (import (srfi 69))))  ; fall back to plain hash tables
```

Both spellings answer through the same check, so they always agree with
what `(import (srfi N))` would do — including under `--sandbox` and on
WASM builds. See [Standards Conformance](../conformance.md) for how this
compares to R7RS-small's own scope, and for the equivalent `cond-expand`
identifiers covering fibers, the reactor, and threads.

## Built-in SRFIs

These are implemented in Zig for performance and are always available.

| SRFI | Title | Docs |
|------|-------|------|
| 1 | List library (fold, filter, find, any, every, iota, ...) | [Reference](../procedures/srfi-1.md) |
| 9 | Defining record types | [Syntax forms](../procedures/syntax-forms.md) |
| 13 | String library (contains, split, join, trim, ...) | [Reference](../procedures/srfi-13.md) |
| 18 | Multithreading (threads, mutexes, condition variables) | [Reference](../procedures/threads.md) |
| 39 | Parameter objects | [Control flow](../procedures/control-flow.md) |
| 69 | Hash tables | [Reference](../procedures/hash-tables.md) |
| 133 | Vector library (vector-map, vector-fold, ...) | [Reference](../procedures/srfi-133.md) |
| 170 | POSIX API (file-info, directories, symlinks, env, ...) | [Reference](../procedures/srfi-170.md) |
| 254 | Ephemerons and guardians (GC-integrated weak references and finalization) | [Reference](../procedures/srfi-254.md) |
| 258 | Uninterned symbols (`string->uninterned-symbol`, `symbol-interned?`, `generate-uninterned-symbol`) | |
| 260 | Generated symbols (`generate-symbol` — fresh, readable, unique symbols) | |

## Portable SRFIs

These are loaded from `.sld` files when first imported. Sorted by SRFI number.

| SRFI | Title |
|------|-------|
| 0 | Feature-based conditional expansion (`cond-expand`) |
| 2 | `and-let*` — short-circuit `let` with guards |
| 4 | Homogeneous numeric vector datatypes |
| 6 | Basic string ports |
| 8 | `receive` — binding to formals from `values` |
| 11 | `let-values` and `let*-values` |
| 14 | Character sets |
| 16 | `case-lambda` — procedures with variable arity |
| 17 | Generalized `set!` |
| 19 | Time data types and procedures |
| 23 | `error` reporting |
| 26 | `cut` and `cute` — partial application notation |
| 27 | Sources of random bits |
| 28 | Basic format strings |
| 31 | `rec` — recursive evaluation |
| 34 | Exception handling for programs |
| 35 | Conditions |
| 36 | I/O conditions |
| 37 | `args-fold` — program argument processor |
| 38 | External representation for data with shared structure |
| 41 | Streams (lazy lists) |
| 42 | Eager comprehensions |
| 43 | Vector library (R7RS-compatible) |
| 45 | Primitives for expressing iterative lazy algorithms |
| 48 | Intermediate format strings |
| 60 | Integers as bits |
| 61 | A more general `cond` clause |
| 64 | A Scheme API for test suites |
| 78 | Lightweight testing |
| 87 | `=>` in `case` clauses |
| 98 | Interface to access environment variables |
| 111 | Boxes |
| 113 | Sets and bags |
| 115 | Scheme regular expressions |
| 116 | Immutable list library |
| 117 | Queues based on lists |
| 125 | Intermediate hash tables |
| 127 | Lazy sequences |
| 128 | Comparators |
| 130 | Cursor-based string library |
| 132 | Sort libraries |
| 134 | Immutable deques |
| 141 | Integer division |
| 143 | Fixnums |
| 144 | Flonums |
| 145 | `assume` — assumptions |
| 146 | Mappings (also `(srfi 146 hash)`) |
| 151 | Bitwise operations |
| 152 | String library (reduced) |
| 158 | Generators and accumulators |
| 166 | Formatting (also `pretty`, `columnar`, `unicode`, `color` sub-libraries) |
| 174 | POSIX timespecs |
| 175 | ASCII character library |
| 189 | `maybe` and `either` — optional values |
| 195 | Multiple-value boxes |
| 196 | Range objects |
| 197 | Pipeline operator |
| 210 | Procedures and syntax for multiple values |
| 219 | Define higher-order lambda |
| 222 | Compound objects |
| 227 | Optional arguments |
| 229 | Tagged procedures |
| 232 | Flexible curried procedures |
| 233 | `INI` file parser |
| 235 | Combinators |
| 248 | Minimal delimited continuations (`with-unwind-handler`, extended `guard`) |
| 250 | Insertion-ordered hash tables |
| 257 | Pattern matcher with backtracking (also `(srfi 257 misc)`, `(srfi 257 box)`, `(srfi 257 rx)`) |
| 259 | Tagged procedures with type safety (`define-procedure-tag`) |
| 263 | Prototype object system (also `(srfi 263 syntax)`) |
| 264 | String syntax for Scheme regular expressions (SSRE ↔ SRE translation) |
| 267 | Raw strings — the `#"X"..."X"` literal syntax is built into the reader; the library adds port procedures |
| 271 | Random ports from OS entropy (also deterministic `(srfi 271 determinized)`) |

## SRFI 261 — portable SRFI library references { #srfi-261 }

SRFI 261 is a naming convention, not a library file: `(srfi srfi-<n>)` and
`(srfi <mnemonic>-<n>)` resolve to `(srfi <n>)`.

```scheme
(import (srfi srfi-1))      ; same as (import (srfi 1))
(import (srfi lists-1))     ; mnemonic form
(import (srfi vectors-133)) ; same as (import (srfi 133))
```

The trailing number alone is authoritative, and a literal registry or file
name wins when one exists. There is no `(srfi 261)` file to import — the
convention is honored by the import resolver itself, and the `srfi-261`
feature identifier reports true.

---

Next: [Concurrency](concurrency.md)
