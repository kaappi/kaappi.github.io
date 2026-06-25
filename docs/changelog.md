# Changelog

All notable changes to Kaappi are documented here. For the full technical
changelog, see [CHANGELOG.md on GitHub](https://github.com/kaappi/kaappi/blob/main/CHANGELOG.md).

## v0.6.0 — 2026-06-25

**REPL improvements and 72 SRFIs.**

- 5 new REPL commands: `,quit`, `,exit`, `,version`, `,load`, `,import`, `,dis`
- Grouped `,help` output with section headers
- Usage hints for bare comma commands (e.g. `,time` without arguments shows usage)
- `thottam` supports fetching packages from arbitrary Git URLs
- 21 new portable SRFIs (total: 72)
- Portable SRFI libraries bundled in releases and installed by the install script
- **NaN-boxing**: floating-point values are now packed directly into the Value
  word — no heap allocation, less GC pressure, faster float arithmetic
- Library import errors now report the actual missing dependency
- WASM build compatibility with NaN-boxing

**Upgrading from v0.5.0:** No breaking changes. Run `curl -fsSL https://kaappi-lang.org/install.sh | bash` to update.

## v0.5.0 — 2026-06-25

**Resource limits and sandbox hardening.**

- `--timeout` and `--max-memory` CLI flags for capping script execution
- REPL history moved to `~/.kaappi/history` with comma command tab completion
- Sandbox mode now blocks SRFI-18 OS threads
- Type error messages include expected-vs-actual context across all primitives
- Improved error messages for failed imports and arity mismatches

## v0.4.0 — 2026-06-24

**WebAssembly and code coverage.**

- WebAssembly (wasm32-wasi) build target: `zig build wasm`
- WASM binary included in release artifacts
- `--coverage` flag reports which exported library procedures a test exercises
- `--coverage-xml` flag writes Cobertura XML for CI integration
- GPG-signed SHA256SUMS in release artifacts
- JIT fixes: tail_call corruption, closure handling, STP writeback bug
- Thread deep copy hardened with proper error handling

## v0.3.0 — 2026-06-23

**Language Server Protocol and 72 SRFIs.**

- LSP server (`kaappi-lsp`) with diagnostics, completions, and hover
- Works with VS Code, Neovim, Emacs, and Helix
- REPL: Ctrl+R reverse history search, `,type`, `,describe`, `,apropos`, `_`
- 21 new SRFIs (total: 72)
- SRFI 19 expanded: timezone support, date parsing, format directives
- x86_64 JIT crash fix (byte order bug)

## v0.2.0 — 2026-06-23

**Package manager rewrite.**

- `thottam` rewritten from shell script to compiled Zig binary
- Ships alongside `kaappi` in release artifacts for all platforms
- macOS binaries are Developer ID signed and Apple notarized
- Dependency cycle detection

## v0.1.0 — 2026-06-23

**Initial release.** Complete R7RS-small implementation.

- 554 built-in procedures, 32 syntax forms, 14 standard libraries
- 51 SRFIs (8 built-in, 43 portable)
- Register-based bytecode VM with mark-and-sweep GC
- JIT compiler backends: AArch64 and x86_64
- C FFI with callbacks
- Green threads (fibers) with channels
- OS threads (SRFI-18) with per-thread heaps
- Profiler, stepping debugger, bytecode caching
- Standalone binary bundling with cross-compilation
- Sandbox mode with resource limits
- Release binaries for macOS ARM, Linux x86_64, Linux ARM, Linux RISC-V
