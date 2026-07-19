# Math & Statistics

`(kaappi math)` — scalar helpers, vector operations, and statistics.
Written in Zig and compiled to a shared library; also the reference
example of the [Zig extension](../guide/zig-extensions.md) pattern.

```bash
thottam install kaappi-math
```

Building requires a [Zig](https://ziglang.org/download/) toolchain on
your `PATH` (the install step runs `zig build-lib`). There are no other
system dependencies — the library links nothing beyond libc.

## Quick start

```scheme
(import (kaappi math))

(lerp 0 100 0.5)          ;=> 50.0
(vec-magnitude '(3 4))    ;=> 5.0
(mean '(1 2 3 4 5))       ;=> 3.0
```

## Scalar operations

All scalar procedures accept exact or inexact numbers and return
inexact results:

```scheme
(lerp 0 100 0.25)   ;=> 25.0 — linear interpolation a + (b - a) * t
(clamp 15 0 10)     ;=> 10.0 — clamp into [lo, hi]
(deg->rad 180)      ;=> 3.141592653589793
(rad->deg 3.141592653589793)  ;=> 180.0
```

## Vector operations

Vectors are plain lists of numbers — any dimension works, and both
vectors in a two-argument operation must have the same length:

```scheme
(vec-dot '(1 2 3) '(4 5 6))   ;=> 32.0
(vec-magnitude '(3 4))        ;=> 5.0 — L2 norm
(vec-distance '(0 0) '(3 4))  ;=> 5.0 — Euclidean distance
(vec-normalize '(3 4))        ;=> (0.6 0.8) — unit vector
```

`vec-normalize` returns a zero vector unchanged rather than dividing by
zero.

## Statistics

Statistics are population (not sample) measures:

```scheme
(mean '(1 2 3 4 5))            ;=> 3.0
(std-dev '(2 4 4 4 5 5 7 9))   ;=> 2.0
(variance '(2 4 4 4 5 5 7 9))  ;=> 4.0
```

`statistics` computes the full summary in one pass and returns it as an
association list:

```scheme
(statistics '(1 2 3 4 5))
;=> ((count . 5) (mean . 3.0) (std-dev . 1.4142135623730951)
;    (variance . 2.0) (min . 1.0) (max . 5.0) (sum . 15.0))
```

## How it works

The repo doubles as a working template for shipping native code as a
Kaappi package:

- `src/math.zig` — the implementation, exported with the C ABI
- `lib/kaappi/math/ffi.sld` — low-level FFI bindings
- `lib/kaappi/math.sld` — the public Scheme API

Statistics use an accumulator on the Zig side (values are pushed one at
a time), which keeps the numerical work native while staying within the
FFI's argument limits. See the
[Zig extensions guide](../guide/zig-extensions.md) for how to build your
own.

!!! note "Running from a source checkout"
    `thottam install` places the compiled library in `~/.kaappi/lib/`,
    where `ffi-open` finds it automatically. If you instead clone the
    repo and run `make` yourself, copy the resulting
    `libkaappi_math.dylib` / `.so` into `~/.kaappi/lib/` — relying on
    `DYLD_LIBRARY_PATH` does not work with the notarized macOS release
    binary.

## API reference

### Scalar

| Procedure | Description |
|-----------|-------------|
| `(lerp a b t)` | Linear interpolation: `a + (b - a) * t` |
| `(clamp x lo hi)` | Clamp *x* into `[lo, hi]` |
| `(deg->rad d)` | Degrees to radians |
| `(rad->deg r)` | Radians to degrees |

### Vectors

| Procedure | Description |
|-----------|-------------|
| `(vec-dot a b)` | Dot product |
| `(vec-magnitude v)` | Length (L2 norm) |
| `(vec-distance a b)` | Euclidean distance |
| `(vec-normalize v)` | Unit vector (zero vector returned unchanged) |

### Statistics

| Procedure | Description |
|-----------|-------------|
| `(mean lst)` | Arithmetic mean |
| `(std-dev lst)` | Population standard deviation |
| `(variance lst)` | Population variance |
| `(statistics lst)` | One-pass summary: count, mean, std-dev, variance, min, max, sum |
