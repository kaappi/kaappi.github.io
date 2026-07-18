# Installation

For pre-built binaries, see the [Download](../download.md) page.

This page covers building from source.

### Prerequisites

- **Zig 0.16+** -- the sole build tool (no cmake, make, or cargo)
- **C toolchain** -- needed to compile the vendored linenoise library (line
  editing for the REPL). On macOS this comes with Xcode Command Line Tools; on
  Linux it comes with `gcc` or `clang`.

## Supported platforms

| OS | Architecture | Native compilation |
|----|-------------|-------------------|
| macOS | aarch64 (Apple Silicon) | LLVM backend |
| Linux | x86_64 | LLVM backend |
| Linux | aarch64 | LLVM backend |
| Linux | riscv64 | LLVM backend |
| Windows | aarch64 (ARM64), x86_64 | LLVM backend |
| FreeBSD | x86_64, aarch64 | LLVM backend (base `cc` suffices) |
| OpenBSD | x86_64, aarch64 | LLVM backend (base `cc` suffices) |
| NetBSD | x86_64, aarch64 | LLVM backend (needs `clang` from pkgsrc) |
| WebAssembly | wasm32-wasi | interpreter only |

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

## Windows

**On x86_64:** download Zig 0.16+ from
[ziglang.org/download](https://ziglang.org/download/) (the `x86_64-windows`
build), extract it, and add it to your `PATH`. Then from PowerShell:

```powershell
git clone https://github.com/kaappi/kaappi
cd kaappi
zig build
```

The executables are `zig-out\bin\kaappi.exe` and `zig-out\bin\thottam.exe`.

**On ARM64:** building natively does not work yet — the Zig 0.16.0
`aarch64-windows` toolchain itself crashes compiling any project (an upstream
code-generation bug, fixed in Zig's development builds; native builds unblock
when Zig 0.17 ships). Use the [prebuilt binaries](../download.md) instead, or
cross-compile from macOS or Linux:

```bash
zig build -Dtarget=aarch64-windows
```

If you need to build on the ARM64 machine itself, an `x86_64-windows` Zig
works under Windows 11's built-in x64 emulation: it produces x64 binaries,
which run on the same machine through that emulation layer.

## FreeBSD, OpenBSD, NetBSD

The [install script](../download.md) and the prebuilt release binaries work
from the base system alone. To build from source instead, install Zig 0.16+
from your ports/packages collection (or
[ziglang.org/download](https://ziglang.org/download/)), then:

```bash
git clone https://github.com/kaappi/kaappi
cd kaappi
zig build
```

The `kaappi compile` native backend links with the base system `cc` on
FreeBSD and OpenBSD. NetBSD's base `cc` is GCC, which cannot consume the
LLVM IR the backend emits — install clang first (`pkgin install clang`);
everything else (interpreter, REPL, thottam, FFI) needs only the base
system.

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

Then let Kaappi check its own installation — binary, library search
path, package manager, native backend, REPL, and FFI, with a suggested
fix for anything that fails:

```bash
kaappi doctor
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

