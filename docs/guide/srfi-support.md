# SRFI Support

Kaappi supports 72 SRFIs (Scheme Requests for Implementation). Eight are
built into the runtime as native Zig code. The remaining 64 are portable
R7RS libraries loaded on demand from `.sld` files.

All SRFIs are imported with `(import (srfi N))`:

```scheme
(import (srfi 1))   ; list library
(import (srfi 69))  ; hash tables
```

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
| 232 | Flexible curried procedures |
| 233 | `INI` file parser |
| 235 | Combinators |

---

Next: [Concurrency](concurrency.md)
