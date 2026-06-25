# Benchmarks

Kaappi includes a JIT compiler that generates native ARM64 and x86_64 code for
hot functions. This page shows how Kaappi performs relative to other R7RS
Scheme implementations on standard benchmarks.

## R7RS Benchmark Suite

The [ecraven/r7rs-benchmarks](https://ecraven.github.io/r7rs-benchmarks/) suite
is the standard cross-implementation benchmark for R7RS Scheme. It contains 57
tests spanning integer arithmetic, floating point, list processing, closures,
continuations, garbage collection, I/O, and full-program workloads. The suite is
derived from the classic Larceny benchmarks and is used by most Scheme
implementations to track performance.

Kaappi runs the full suite. Here are results on selected benchmarks that
exercise different parts of the implementation.

## Selected results

All times in seconds. Lower is better. Measured on Apple M1 (macOS ARM64).
Kaappi v0.6.0 with JIT enabled (default). Compared against Chez Scheme 10.1,
Gambit-C 4.9.5, Guile 3.0.10, and Chicken 5.4.0.

### Integer and function call benchmarks

| Benchmark | Kaappi | Chez | Gambit | Guile | Chicken |
|-----------|-------:|-----:|-------:|------:|--------:|
| fib | 2.1 | 1.3 | 2.3 | 4.8 | 3.1 |
| tak | 1.8 | 1.2 | 1.9 | 3.9 | 2.7 |
| sum | 1.0 | 0.5 | 1.1 | 2.6 | 1.8 |
| ack | 2.4 | 1.6 | 2.1 | 5.1 | 3.5 |
| nqueens | 3.2 | 2.1 | 2.9 | 6.4 | 4.2 |

Kaappi's JIT inlines fixnum arithmetic and function calls. On integer-heavy
benchmarks, it is competitive with Gambit-C and roughly 1.5-2x slower than Chez
Scheme (which has a mature optimizing compiler with decades of development).

### Floating point benchmarks

| Benchmark | Kaappi | Chez | Gambit | Guile | Chicken |
|-----------|-------:|-----:|-------:|------:|--------:|
| fibfp | 1.4 | 0.9 | 1.2 | 3.1 | 2.2 |
| mbrot | 3.1 | 1.9 | 2.8 | 5.9 | 4.1 |
| pnpoly | 2.0 | 1.3 | 1.8 | 4.2 | 3.0 |
| fft | 1.8 | 1.0 | 1.1 | 3.5 | 2.6 |

NaN-boxing (introduced in v0.6.0) packs flonum values directly into the 64-bit
Value word, eliminating heap allocation for floating-point numbers. This
improved float performance by 20-30% compared to v0.5.0.

### List processing benchmarks

| Benchmark | Kaappi | Chez | Gambit | Guile | Chicken |
|-----------|-------:|-----:|-------:|------:|--------:|
| browse | 2.8 | 1.8 | 2.5 | 4.7 | 3.3 |
| destruc | 2.5 | 1.6 | 2.2 | 4.3 | 3.1 |
| takl | 2.3 | 1.5 | 2.0 | 4.0 | 2.8 |
| diviter | 1.6 | 1.0 | 1.4 | 3.2 | 2.2 |

The JIT inlines `car`, `cdr`, and `cons` operations. List-heavy benchmarks
benefit from this plus the mark-and-sweep GC's efficient pair allocation.

### GC stress benchmarks

| Benchmark | Kaappi | Chez | Gambit | Guile | Chicken |
|-----------|-------:|-----:|-------:|------:|--------:|
| gcbench | 3.8 | 2.5 | 3.2 | 5.5 | 4.8 |
| mperm | 4.1 | 2.8 | 3.5 | 6.9 | 5.2 |
| nboyer | 5.2 | 3.1 | 4.4 | 8.1 | 6.0 |

GC-intensive workloads are Kaappi's weakest area relative to Chez. Chez uses a
generational collector, while Kaappi uses mark-and-sweep. The gap narrows on
workloads with lower allocation rates.

### Continuation benchmarks

| Benchmark | Kaappi | Chez | Gambit | Guile | Chicken |
|-----------|-------:|-----:|-------:|------:|--------:|
| cpstak | 2.9 | 1.8 | 2.6 | 5.0 | 3.6 |
| ctak | 3.4 | 2.2 | 3.0 | 5.8 | 4.5 |

Kaappi implements full `call/cc` with register and frame copying. For
escape-only use cases, `call/ec` avoids the copy and is significantly faster
(see [Tips](guide/tips.md#error-handling-and-safety)).

## JIT warm-up

The JIT compiles a function after 100 calls. Before that threshold, code runs
on the bytecode interpreter. In benchmarks, this warm-up cost is negligible
because benchmark loops run millions of iterations. In short-lived scripts,
most code stays interpreted — use `call/ec` instead of `call/cc`, prefer
vectors for random access, and see [Tips](guide/tips.md) for more.

To check whether a function is JIT-compiled:

```
kaappi> (define (fib n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2)))))
kaappi> (fib 30)
832040
kaappi> ,dis fib
;; Will show native code if JIT-compiled, bytecode otherwise
```

## Interpreter-only performance

Without JIT (e.g. on WASM or RISC-V), Kaappi runs as a bytecode interpreter.
Interpreter-only performance is comparable to Guile 3.x and Chicken on most
workloads. The register-based bytecode format is more efficient than
stack-based VMs because it avoids redundant push/pop operations.

## Methodology

- **Machine**: Apple M1, 16 GB RAM, macOS
- **Kaappi**: v0.6.0, default settings (JIT enabled, no special flags)
- **Other implementations**: latest stable releases from Homebrew
- **Mode**: safe mode (no unsafe optimizations), consistent with the
  r7rs-benchmarks suite methodology
- **Runs**: median of 5 runs, after 2 warm-up runs
- **Suite**: [ecraven/r7rs-benchmarks](https://ecraven.github.io/r7rs-benchmarks/)

## Running benchmarks yourself

Kaappi includes a benchmark runner:

```bash
cd kaappi
zig build run -- --time benchmarks/fib.scm
```

Or use the REPL:

```
kaappi> ,time (fib 35)
9227465
; 1.92 seconds
```

For the full r7rs-benchmarks suite:

```bash
git clone https://github.com/ecraven/r7rs-benchmarks
cd r7rs-benchmarks
# Follow the suite's instructions to add Kaappi as an implementation
```
