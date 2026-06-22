# Performance Benchmarks

Baseline measurements on Apple M-series (macOS, ReleaseSafe build).

## Benchmark Programs

### fib -- Naive Fibonacci

Pure recursion with fixnum arithmetic. Exercises function call overhead
and JIT compilation of hot paths.

```scheme
(define (fib n)
  (if (< n 2) n
      (+ (fib (- n 1)) (fib (- n 2)))))
```

### tak -- Takeuchi Function

Deep recursion with arithmetic and comparisons. A classic benchmark for
call overhead and argument passing.

```scheme
(define (tak x y z)
  (if (not (< y x))
      z
      (tak (tak (- x 1) y z)
           (tak (- y 1) z x)
           (tak (- z 1) x y))))
```

## Results

| Benchmark | Input | Result | Kaappi | Notes |
|-----------|-------|--------|--------|-------|
| **fib** | 35 | 9227465 | **~1.9s** | Pure recursion, fixnum arithmetic |
| **tak** | 33,22,11 | 12 | **~46s** | Deep recursion + arithmetic + comparisons |

Measured with `(current-jiffy)` / `(jiffies-per-second)`. Pre-built executable (`zig-out/bin/kaappi`), no compilation overhead.

### Micro-benchmarks

Informal measurements of individual operations (not from the benchmark
harness above):

| Operation | Input | Kaappi | Notes |
|-----------|-------|--------|-------|
| `hash-table-set!` | 10K entries | ~1ms | Open-addressing with linear probing |
| `hash-table-set!` | 50K entries | ~5ms | Linear scaling |
| `iota` | 100K elements | ~1.4ms | List allocation + GC |
| `fold +` | 100K elements | ~2.1ms | List traversal |

## Comparison Context

Approximate results from [ecraven/r7rs-benchmarks](https://ecraven.github.io/r7rs-benchmarks/)
for the same benchmark programs. These numbers are from different hardware
and implementation versions -- they show rough relative positioning, not
exact comparisons.

| Implementation | fib(35) | tak(33,22,11) | Type |
|---------------|---------|---------------|------|
| **Chez Scheme** | ~0.15s | ~1.2s | Native compiler |
| **Chicken** | ~0.5s | ~4s | AOT compiler (C backend) |
| **Gauche** | ~1.8s | ~15s | Bytecode interpreter |
| **Chibi** | ~3.5s | ~30s | Bytecode interpreter |
| **Kaappi** | ~1.9s | ~46s | Bytecode interpreter + JIT |

Kaappi is faster than Chibi for `fib` (1.9s vs 3.5s) and comparable on
`tak`. The JIT inlines fixnum arithmetic, comparisons, `car`/`cdr`, and
`cons` for hot functions.

## Optimizations Implemented

- **JIT compiler** (AArch64, x86_64): hot functions (100+ calls) compiled to native code; inline fixnum `+`/`-`/`*`/`<`/`>`/`<=`/`>=`/`=`, predicates (`zero?`, `null?`, `pair?`, `not`), `car`/`cdr`, `cons`. On riscv64, the interpreter handles all execution (no JIT backend yet).
- **NativeFn fast path**: `call_global` bypasses the full dispatch chain for native functions
- **Constant folding**: `(+ 1 2)` → `3` at compile time
- **Inline global cache**: `call_global` caches resolved function pointers with version invalidation
- **Open-addressing hash tables**: O(1) lookup/insert (was O(n) linear scan — 1000x speedup)
- **Self-tail-call optimization**: detected at compile time, reuses the current frame

## Running Benchmarks

```bash
kaappi benchmarks/tak_direct.scm   # run tak(33,22,11)
```

The `benchmarks/` directory contains additional benchmark scripts that
read parameters from stdin via the r7rs-benchmarks harness:

| Script | Input format | Example |
|--------|-------------|---------|
| `fib.scm` | `count input expected` | `1 35 9227465` |
| `tak.scm` | `count x y z expected` | `1 33 22 11 12` |
| `nqueens.scm` | `count n expected` | `1 10 724` |
| `primes.scm` | `count n expected` | `1 10000 1229` |

A separate call/cc micro-benchmark is also available:

```bash
zig build bench    # call/cc capture overhead benchmark
```

### GC Metrics

Use `--gc-stats` to see garbage collection statistics alongside benchmark
results (collections, live objects, heap size):

```bash
kaappi --gc-stats benchmarks/fib.scm
```

The benchmark runner also outputs JSON for programmatic analysis. Compare
two JSON snapshots with `benchmarks/compare-benchmarks.sh` to flag
regressions above a configurable threshold (default 10%):

```bash
benchmarks/compare-benchmarks.sh baseline.json current.json
```

The script exits non-zero on regression, making it suitable for CI gates.
Set `THRESHOLD` to adjust the sensitivity (e.g., `THRESHOLD=5`).

Use `--profile` to get per-function timing for any Scheme program:

```bash
kaappi --profile program.scm
```

---
