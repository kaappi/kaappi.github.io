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

## Verifying releases

Every GitHub release includes `SHA256SUMS` (checksums for all binaries) and
`SHA256SUMS.asc` (a detached GPG signature). The install script verifies
checksums automatically, but you can also verify manually:

### SHA256 checksums

```bash
cd ~/Downloads  # or wherever you downloaded the binary
curl -LO https://github.com/kaappi/kaappi/releases/latest/download/SHA256SUMS
sha256sum --check --ignore-missing SHA256SUMS
```

### GPG signature

The release checksums are signed with the maintainer's GPG key. The public key
is available at [keybase.io/baijum](https://keybase.io/baijum).

```bash
# Import the public key from Keybase
curl https://keybase.io/baijum/pgp_keys.asc | gpg --import

# Download the signature and verify
curl -LO https://github.com/kaappi/kaappi/releases/latest/download/SHA256SUMS.asc
gpg --verify SHA256SUMS.asc SHA256SUMS
```

A successful verification shows "Good signature from ..." in the output.

### macOS binaries

macOS binaries are additionally Developer ID signed and Apple notarized — no
Gatekeeper warnings when downloading from GitHub releases.

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

