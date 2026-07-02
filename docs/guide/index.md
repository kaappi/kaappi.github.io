# User Guide

Kaappi is a Scheme you can install in one command and start using immediately.
It implements the full R7RS-small standard with 72 SRFIs, C FFI, and a
package manager — everything you need to write real programs.

## Getting started

1. [Installation](installation.md) — one-line install or build from source
2. [Your First Program](first-program.md) — run a file, explore the REPL
3. [Scheme Tutorial](tutorial.md) — learn Scheme from scratch with runnable examples

Prefer the browser? Try the [interactive tour](../tour.md) or the
[playground](../playground.md) — no install needed.

## Language

- [Language Reference](language.md) — syntax lookup for every form and feature
- [Libraries](libraries.md) — importing libraries and what's available
- [Library Authoring](library-authoring.md) — creating your own libraries with `define-library`
- [SRFI Support](srfi-support.md) — all 72 supported SRFIs at a glance
- [Concurrency](concurrency.md) — green threads (fibers) and OS threads (SRFI-18)

## Tooling

- [REPL Guide](repl.md) — commands, history, tab completion, reverse search
- [CLI Reference](cli.md) — command-line flags and standalone binaries
- [Debugging](debugging.md) — stepping debugger, profiling, disassembly, performance tips
- [Editor Support](editors.md) — VS Code, Neovim, Emacs, Helix setup

## Extending

- [C Extensions](c-extensions.md) — calling C via FFI and packaging C extension libraries
- [Zig Extensions](zig-extensions.md) — writing extensions in Zig with memory safety and cross-compilation

## In production

- [Security](security.md) — SQL injection, XSS prevention, safe FFI, sandbox mode
- [Deployment](deployment.md) — standalone binaries, WebAssembly, Docker, systemd, reverse proxy
- [Migrating from Other Schemes](migrating.md) — differences from Racket, Guile, Chicken, and Common Lisp
- [Troubleshooting](troubleshooting.md) — common errors, pitfalls, and how to fix them
