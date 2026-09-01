---
render_macros: true
---

# SRFI Support

Kaappi supports {{ srfi_count }} SRFIs (Scheme Requests for Implementation).
Of these, {{ srfi_builtin }} are built into the runtime as native Zig code and
{{ srfi_portable }} are portable R7RS libraries loaded on demand from `.sld` files. Three more
ship as [sub-libraries only](#sub-library-only), and SRFI 261 is a
[naming convention](#srfi-261) honored by the import resolver with no
library file at all.

Most SRFIs are imported with `(import (srfi N))`:

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
| 192 | Port positioning (`port-position`, `set-port-position!`, and the two capability predicates) | [Ports and I/O](../procedures/ports-and-io.md) |
| 254 | Ephemerons and guardians (GC-integrated weak references and finalization) | [Reference](../procedures/srfi-254.md) |
| 258 | Uninterned symbols (`string->uninterned-symbol`, `symbol-interned?`, `generate-uninterned-symbol`) | |
| 260 | Generated symbols (`generate-symbol` — fresh, readable, unique symbols) | |

## Portable SRFIs

These are loaded from `.sld` files when first imported. Sorted by SRFI number.

| SRFI | Title |
|------|-------|
| 0 | Feature-based conditional expansion (`cond-expand`) |
| 2 | `and-let*` — short-circuit `let` with guards |
| 4 | Homogeneous numeric vector datatypes (a thin re-export over `(srfi 160 <tag>)`) |
| 5 | A compatible `let` with signatures and rest arguments |
| 6 | Basic string ports |
| 7 | Feature-based program configuration language |
| 8 | `receive` — binding to formals from `values` |
| 11 | `let-values` and `let*-values` |
| 14 | Character sets |
| 16 | `case-lambda` — procedures with variable arity |
| 17 | Generalized `set!` |
| 19 | Time data types and procedures |
| 23 | `error` reporting |
| 25 | Multi-dimensional array primitives |
| 26 | `cut` and `cute` — partial application notation |
| 27 | Sources of random bits |
| 28 | Basic format strings |
| 29 | Localization |
| 30 | Nested multi-line comments (`#| ... |#`) |
| 31 | `rec` — recursive evaluation |
| 34 | Exception handling for programs |
| 35 | Conditions |
| 36 | I/O conditions |
| 37 | `args-fold` — program argument processor |
| 38 | External representation for data with shared structure |
| 41 | Streams (lazy lists) |
| 42 | Eager comprehensions |
| 43 | Vector library (R7RS-compatible) |
| 44 | Collections — generic operations over sequences and dictionaries |
| 45 | Primitives for expressing iterative lazy algorithms |
| 46 | Basic `syntax-rules` extensions (custom ellipsis identifier, tail patterns) |
| 48 | Intermediate format strings |
| 51 | Handling rest lists |
| 54 | Formatting |
| 57 | Records with inheritance via "schemes" |
| 59 | Vicinity — directory-relative filename conventions |
| 60 | Integers as bits |
| 61 | A more general `cond` clause |
| 62 | S-expression comments (`#;`) |
| 63 | Homogeneous and heterogeneous arrays (incompatible with SRFI 25/164 by design) |
| 64 | A Scheme API for test suites |
| 66 | Octet vectors |
| 67 | Compare procedures |
| 70 | Numbers |
| 71 | Extended `let` for multiple values |
| 74 | Octet-addressed binary blocks |
| 78 | Lightweight testing |
| 86 | `mu` and `nu` simulating `values` and `call-with-values` |
| 87 | `=>` in `case` clauses |
| 90 | Extensible hash table constructor |
| 94 | Type-restricted numerical functions |
| 95 | Sorting and merging |
| 98 | Interface to access environment variables |
| 101 | Purely functional random-access pairs and lists |
| 111 | Boxes |
| 112 | Environment inquiry |
| 113 | Sets and bags |
| 115 | Scheme regular expressions |
| 116 | Immutable list library |
| 117 | Queues based on lists |
| 118 | Simple adjustable-size strings |
| 120 | Timer APIs (each timer is owned by one thread — see the note below) |
| 123 | Generic accessor and modifier operators |
| 125 | Intermediate hash tables |
| 126 | R6RS-based hashtables |
| 127 | Lazy sequences |
| 128 | Comparators |
| 129 | Titlecase procedures |
| 130 | Cursor-based string library |
| 131 | ERR5RS record syntax (reduced) |
| 132 | Sort libraries |
| 134 | Immutable deques |
| 135 | Immutable texts |
| 136 | Extensible record types |
| 137 | Minimal unique types |
| 139 | Syntax parameters |
| 140 | Immutable strings |
| 141 | Integer division |
| 143 | Fixnums |
| 144 | Flonums |
| 145 | `assume` — assumptions |
| 146 | Mappings (also `(srfi 146 hash)`) |
| 147 | Custom macro transformers |
| 148 | Eager `syntax-rules` — `em-syntax-rules` and ~110 `em-` combinators |
| 149 | Basic `syntax-rules` template extensions |
| 150 | Hygienic ERR5RS record syntax |
| 151 | Bitwise operations |
| 152 | String library (reduced) |
| 153 | Ordered sets |
| 156 | Syntactic combiners for binary predicates |
| 158 | Generators and accumulators |
| 161 | Unifiable boxes |
| 162 | Comparators sub-library |
| 164 | Enhanced multi-dimensional arrays (a compatible extension of SRFI 25) |
| 165 | The environment monad |
| 166 | Formatting (also `base`, `pretty`, `columnar`, `unicode`, `color` sub-libraries) |
| 167 | Ordered key-value store |
| 168 | Generic tuple store database |
| 169 | Underscores in numbers |
| 171 | Transducers (also `(srfi 171 meta)`) |
| 173 | Hooks |
| 174 | POSIX timespecs |
| 175 | ASCII character library |
| 178 | Bitvector library |
| 180 | JSON |
| 181 | Custom ports, including transcoded ports (UTF-8 codec only) |
| 185 | Linear adjustable-length strings |
| 188 | Splicing binding constructs for syntactic keywords |
| 189 | `maybe` and `either` — optional values |
| 190 | Coroutine generators |
| 193 | Command line |
| 194 | Random data generators |
| 195 | Multiple-value boxes |
| 196 | Range objects |
| 197 | Pipeline operator |
| 201 | Syntactic extensions to the core bindings (also `(srfi 201 core)`) |
| 202 | Pattern-matching variant of `and-let*` |
| 203 | A simple picture language in the style of SICP |
| 207 | String-notated bytevectors |
| 209 | Enums and enum sets |
| 210 | Procedures and syntax for multiple values |
| 213 | Identifier properties (reachable only from a procedural transformer) |
| 214 | Flexvectors |
| 215 | Central log exchange |
| 216 | SICP prerequisites |
| 217 | Integer sets |
| 219 | Define higher-order lambda |
| 221 | Generator/accumulator sub-library |
| 222 | Compound objects |
| 223 | Bisecting search |
| 224 | Integer mappings (fxmappings) |
| 225 | Dictionaries |
| 227 | Optional arguments |
| 228 | Composing comparators |
| 229 | Tagged procedures |
| 231 | Intervals and generalized arrays (also seven phase sub-libraries, e.g. `(srfi 231 intervals)`) |
| 232 | Flexible curried procedures |
| 233 | `INI` file parser |
| 234 | Topological sorting |
| 235 | Combinators |
| 236 | Evaluating expressions in an unspecified order |
| 237 | R6RS records, refined for R7RS |
| 238 | Codesets |
| 239 | Destructuring lists |
| 240 | Reconciled records |
| 241 | R6RS-style `match` with catamorphisms |
| 242 | The CFG language |
| 244 | Multiple-value definitions |
| 247 | Syntactic monads |
| 248 | Minimal delimited continuations (`with-unwind-handler`, extended `guard`) |
| 250 | Insertion-ordered hash tables |
| 251 | Mixing groups of definitions with expressions within bodies |
| 252 | Property testing |
| 253 | Data type-checking |
| 255 | Restarting conditions |
| 257 | Pattern matcher with backtracking (also `(srfi 257 misc)`, `(srfi 257 box)`, `(srfi 257 rx)`) |
| 259 | Tagged procedures with type safety (`define-procedure-tag`) |
| 263 | Prototype object system (also `(srfi 263 syntax)`) |
| 264 | String syntax for Scheme regular expressions (SSRE ↔ SRE translation) |
| 267 | Raw strings — the `#"X"..."X"` literal syntax is built into the reader; the library adds port procedures |
| 270 | Hexadecimal floating-point constants |
| 271 | Random ports from OS entropy (also deterministic `(srfi 271 determinized)`) |

### Seven that collide with `(scheme base)`

R7RS 5.2 makes it an error to import one identifier from two libraries with
different bindings, and Kaappi enforces that at the `import`. Seven portable
SRFIs redefine a name `(scheme base)` already exports, so importing both
plainly is rejected:

| SRFI | Colliding name reported first |
|------|-------------------------------|
| 36 | `read-error?` |
| 43 | `vector-for-each` |
| 63 | `equal?` |
| 70 | `expt` |
| 101 | `pair?` |
| 140 | `list->string` |
| 141 | `truncate/` |

Each imports cleanly on its own. Alongside `(scheme base)`, reach for
`prefix` — which sidesteps the question entirely — or `except` the names you
do not need from that SRFI:

```scheme
(import (scheme base) (prefix (srfi 43) v43:))
(v43:vector-fold (lambda (i acc x) (+ acc x)) 0 #(1 2 3))
;=> 6
```

`only` does not help when the name you want *is* the colliding one.

!!! note "SRFI 120 timers belong to one thread"

    Each `make-timer` owns its task list in a dedicated thread. Driving one
    timer's procedures from more than one thread is a requirement violation,
    not a style preference — schedule and cancel a timer's tasks from the
    thread that created it.

## Sub-library-only SRFIs { #sub-library-only }

These three have no bare `(srfi N)` to import — only their sub-libraries.

| SRFI | Title | Import as |
|------|-------|-----------|
| 160 | Homogeneous numeric vector libraries | `(srfi 160 base)`, plus one per element type: `(srfi 160 u8)`, `s8`, `u16`, `s16`, `u32`, `s32`, `u64`, `s64`, `f32`, `f64`, `c64`, `c128` |
| 211 | Scheme macro libraries — the procedural macro transformers ([guide](er-macros.md)) | `(srfi 211 explicit-renaming)`, `(srfi 211 define-macro)`, `(srfi 211 syntax-parameter)` |
| 226 | Control features — a reduced, escape-only continuation-prompt subset | `(srfi 226 control prompts)`, `(srfi 226 control continuations)`, `(srfi 226 control times)` |

SRFI 211's other eight sub-libraries need syntax objects or output-provenance
tracking that a symbol-based expander cannot honestly provide, and are not
exported. SRFI 226 has no default library in its own spec, so the absence of a
bare `(srfi 226)` is per the SRFI rather than a Kaappi limitation.

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
