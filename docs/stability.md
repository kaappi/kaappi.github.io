# Stability Policy

Kaappi follows [Semantic Versioning](https://semver.org/). This page
describes what is stable, what may change, and how upgrades are handled.

## Current status

Kaappi is pre-1.0. The language and CLI are stable, but the project has
not yet committed to the full backwards-compatibility guarantees that come
with a 1.0 release.

## What is stable

These interfaces will not break without a minor version bump (e.g., 0.5 to
0.6):

| Component | Guarantee |
|-----------|-----------|
| **R7RS procedures** | All 600+ built-in procedures retain their current behavior |
| **Library system** | `define-library`, `import`, `export` syntax and semantics |
| **SRFI support** | All 78 currently supported SRFIs remain available |
| **CLI interface** | `kaappi [flags] [file]` and the subcommands (`compile`, `check`, `explain`, `features`, `test`, `ast`/`expand`/`ir`, `doctor`, `fmt`, `cache`) — flags and subcommands may be added but not removed |
| **Diagnostic codes** | A `KP` code never changes meaning and is never reused; new codes may be added. See the [Diagnostic Reference](guide/diagnostics.md) |
| **thottam CLI** | `install`, `remove`, `list`, `update`, `verify` commands |
| **`kaappi.pkg` format** | Package manifest fields are additive-only |

## What may change

| Component | Status | Impact |
|-----------|--------|--------|
| **Bytecode format** (`.sbc`) | Unstable | Cache entries are keyed by compiler version and build id — a new binary never reads stale bytecode; sources are recompiled automatically |
| **Build options** (`-Dmax-frames`, etc.) | Unstable | May be added or adjusted |
| **Internal APIs** (embedding the VM) | Unstable | No stability promise for Zig-level API |
| **Error message text** | Unstable | Wording may improve — match the stable `KP` code instead ([`error-object-code`](procedures/extensions.md#error-object-code), `--diagnostics=json`) |
| **LLVM native backend** | Unstable | Compilation behavior and optimizations may change |
| **Performance** | Best effort | Performance may improve or regress between versions |

## Upgrade process

### Checking your version

```bash
kaappi --version
```

### Upgrading

```bash
curl -fsSL https://kaappi-lang.org/install.sh | bash
```

This installs the latest release of both `kaappi` and `thottam`.

### After upgrading

1. There is no cache to invalidate by hand — bytecode cache entries are
   keyed by the exact binary that wrote them, so the new version recompiles
   automatically. To reclaim the space held by the old entries:

   ```bash
   kaappi cache clear
   ```

2. Check the [GitHub releases](https://github.com/kaappi/kaappi/releases) for breaking changes.

3. Verify the installation, then run your test suite:

   ```bash
   kaappi doctor
   kaappi tests/test-all.scm    # or: kaappi test tests/  (SRFI-64 suites)
   ```

### Pinning ecosystem packages

Use `thottam`'s lockfile for reproducible builds:

```bash
thottam verify                  # check installed packages match lockfile
thottam --locked install ...    # refuse to install unlocked packages
```

See [thottam](ecosystem/thottam.md#lockfile-and-reproducible-installs) for
details.

## Deprecation process

When a feature is deprecated:

1. It continues to work for at least one minor version
2. Usage produces a warning message to stderr
3. The [release notes](https://github.com/kaappi/kaappi/releases) list it under a "Deprecated" heading
4. The documentation is updated to recommend the replacement

No feature has been deprecated yet.

## Criteria for 1.0

All of the following must be met before a 1.0 release:

- **Input robustness** — the reader, compiler, and bytecode loader handle
  all malformed input gracefully (no crashes on any input)
- **Concurrency safety** — OS threads either have a proven-safe GC or
  remain clearly documented as experimental
- **Security** — the sandbox boundary is proven, native-compiled code memory
  is W^X on all platforms, and the threat model is documented
- **CI** — formatting, multi-platform testing, and the conformance suite
  gate every PR
- **No known memory-safety issues** in the interpreter core

## Support policy

Only the latest release is supported. There are no long-term-support
branches. Security fixes are applied to `main` and included in the next
release.

## Reporting issues

- **Bugs**: [github.com/kaappi/kaappi/issues](https://github.com/kaappi/kaappi/issues)
- **Security**: [SECURITY.md](https://github.com/kaappi/kaappi/blob/main/SECURITY.md)
  (private advisory, not a public issue)
- **Questions**: [GitHub Discussions](https://github.com/orgs/kaappi/discussions)
