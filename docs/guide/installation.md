# Installation

For pre-built binaries, see the [Download](../download.md) page.

This page covers building from source.

### Prerequisites

- **Zig 0.16+** -- the sole build tool (no cmake, make, or cargo)
- **C toolchain** -- needed to compile the vendored linenoise library (line
  editing for the REPL). On macOS this comes with Xcode Command Line Tools; on
  Linux it comes with `gcc` or `clang`.

## Supported platforms

| OS | Architecture | JIT |
|----|-------------|-----|
| macOS | aarch64 (Apple Silicon) | AArch64 native |
| Linux | x86_64 | x86_64 native |
| Linux | aarch64 | AArch64 native |
| Linux | riscv64 | No (interpreter only) |
| WebAssembly | wasm32-wasi | No (interpreter only) |

## macOS

```bash
brew install zig
git clone https://github.com/kaappi/kaappi
cd kaappi
zig build
```

## Linux

Download Zig 0.16+ from [ziglang.org/download](https://ziglang.org/download/),
extract it, and add it to your `PATH`. Then:

```bash
git clone https://github.com/kaappi/kaappi
cd kaappi
zig build
```

## Install

The executables are placed at `zig-out/bin/kaappi` and `zig-out/bin/thottam`.
Add them to your `PATH`:

```bash
cp zig-out/bin/kaappi zig-out/bin/thottam /usr/local/bin/
```

Verify:

```bash
echo '(+ 1 2)' | kaappi
# Output: 3
```

Run the test suite to confirm everything works:

```bash
zig build test
```

## Build modes

The default build uses **ReleaseSafe** (fast execution with bounds checking).
For maximum throughput use `-Doptimize=ReleaseFast`. The Debug mode is roughly
500x slower for allocation-heavy workloads -- only use it when debugging the
runtime itself:

```bash
zig build -Doptimize=Debug
```

---

Next: [Your First Program](first-program.md)

