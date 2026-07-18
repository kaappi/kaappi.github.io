# FAQ

## General

### What is Kaappi?

Kaappi is a Scheme implementation that follows the R7RS-small standard. It is
written in Zig and includes a register-based bytecode VM, LLVM native compiler,
garbage collector, C FFI, package manager, and a growing ecosystem of libraries
for web development, databases, and data processing.

### Why another Scheme?

Most Scheme implementations focus on either standards conformance or
performance. Kaappi aims for both — full R7RS-small with 72 SRFIs, plus native
compilation via LLVM. It also ships as a single binary with no runtime
dependencies, which makes deployment straightforward.

### What does the name mean?

The name comes from South Indian languages such as Malayalam and Tamil, where
*kaappi* means "coffee" — a nod to the warm, everyday ritual of brewing
something energizing from simple ingredients.

### What license is Kaappi under?

MIT. All ecosystem libraries are also MIT licensed.

## Standards and Compatibility

### How complete is the R7RS-small implementation?

Kaappi implements the full R7RS-small standard — all required libraries, syntax
forms, and procedures. It passes the R7RS test suite.

### Which SRFIs are supported?

72 SRFIs total: 8 built-in (compiled into the interpreter) and 64 portable
(pure Scheme, installed via the install script). See
[SRFI Support](guide/srfi-support.md) for the complete list.

### Can I run code written for other Schemes?

R7RS-small code should work without changes. Code using implementation-specific
extensions from Racket, Guile, or Chicken will need modification. Key
differences:

- **Module system**: Kaappi uses R7RS `define-library` (not Racket's `#lang` or
  Guile's `define-module`)
- **FFI**: Kaappi has its own FFI syntax (not Chicken's `foreign-lambda` or
  Guile's dynamic FFI)
- **Continuations**: Full `call/cc` is supported, but Kaappi also provides
  `call/ec` for efficient escape-only continuations

## Performance

### How fast is Kaappi?

The bytecode interpreter is competitive with Guile and Chicken on most
workloads. For CPU-bound programs, `kaappi compile` produces native binaries
via the LLVM backend that are competitive with Chez Scheme, Gambit, and
Larceny on numeric and list-processing benchmarks.

### How does native compilation work?

`kaappi compile program.scm -o program` compiles a Scheme source file to a
native executable via LLVM IR. The compiler handles closures, tail calls,
continuations, and the full R7RS feature set. Operations not yet covered by
the native backend fall back to the bytecode interpreter automatically.

### Does native compilation work on all platforms?

Native compilation via `kaappi compile` is available on macOS ARM64, Linux
x86_64/ARM64, FreeBSD, OpenBSD, NetBSD, and Windows. On Windows x86_64 the
stock Zig toolchain serves as the C compiler; on Windows ARM64 the stock
Zig 0.16.0 toolchain has an upstream code-generation bug, so the link step
needs a Zig development build until 0.17 ships. Linux RISC-V and WebAssembly
run interpreter-only.

## Ecosystem

### How do I install libraries?

Use `thottam`, the built-in package manager:

```bash
thottam install kaappi-web
```

It handles dependencies, native builds, and library discovery automatically.
See [thottam](ecosystem/thottam.md) for details.

### Can I use third-party libraries?

Yes. `thottam` can install from any Git URL:

```bash
thottam install my-lib::https://github.com/someone/my-lib
```

The library needs a `kaappi.pkg` manifest and `.sld` files following the R7RS
`define-library` convention.

### Is Kaappi ready for production use?

Kaappi is pre-1.0 software. The core language is stable and well-tested (the
R7RS suite, 28 robustness tests, 31 sandbox escape tests, and fuzz targets all
pass in CI). The ecosystem libraries are functional and tested nightly.

That said, the API may still change between minor versions. If you use Kaappi in
production, pin your `thottam` dependencies and test upgrades before deploying.

## Development

### How do I report a bug?

Open an issue at [github.com/kaappi/kaappi/issues](https://github.com/kaappi/kaappi/issues).
Include the Kaappi version (`kaappi --version`), your OS, and a minimal
reproducing example.

### How do I contribute?

Fork the repo, make your changes, and open a pull request. The project uses
`zig fmt` for code style (checked in CI). See the
[contributing guide](https://github.com/kaappi/kaappi/blob/main/CONTRIBUTING.md)
for details.

### Where is the community?

[GitHub Discussions](https://github.com/orgs/kaappi/discussions) is the primary
community channel for questions, ideas, and show-and-tell.

### How do I build from source?

```bash
git clone https://github.com/kaappi/kaappi
cd kaappi
zig build
```

Requires Zig 0.16. The build produces `zig-out/bin/kaappi` and
`zig-out/bin/thottam`.

### Is there a code formatter?

Yes, built in: `kaappi fmt` applies canonical 2-space R7RS indentation
with 80-column reflow, preserves comments, and is guarded by a reader
round-trip check so it can never change a program's meaning. `kaappi
fmt --check` verifies formatting in CI, and with no files it works as a
stdin filter for editors. See
[Editor Support](guide/editors.md#formatting).

### Can I check a program without running it?

`kaappi check program.scm` reads, expands, and compiles without
executing, reporting read/compile errors plus lint findings for calls
that are guaranteed to fail at run time (wrong arity or wrong-type
literal on a built-in). It never rejects a program R7RS permits. See
[Debugging](guide/debugging.md#catching-errors-before-running).

## Deployment

### Can I compile to a standalone binary?

Yes. Kaappi can bundle a Scheme program into a single executable:

```bash
zig build -Dbundle-src=app.scm
```

The binary includes the full runtime — no Kaappi installation needed on the
target machine. Cross-compile to Linux x86_64/ARM64/RISC-V, Windows (ARM64
and x86_64), FreeBSD, OpenBSD, or NetBSD from any platform. See
[Standalone Binaries](guide/deployment.md#standalone-binaries).

### Does Kaappi run in the browser?

Yes, via WebAssembly. `zig build wasm` produces a WASM binary that runs in
browsers and WASI runtimes. The [playground](playground.md) and
[interactive tour](tour.md) use this. The WASM build does not include native
compilation, FFI, file I/O, or OS threads.

### What platforms are supported?

| Platform | Native compile | Prebuilt binary |
|----------|:--------------:|:---------------:|
| macOS ARM64 (Apple Silicon) | yes | yes |
| Linux x86_64 | yes | yes |
| Linux ARM64 | yes | yes |
| Linux RISC-V 64 | no | yes |
| Windows ARM64 | yes | yes |
| Windows x86_64 | yes | from the next release |
| FreeBSD x86_64 / ARM64 | yes | yes |
| OpenBSD x86_64 / ARM64 | yes | yes |
| NetBSD x86_64 / ARM64 | yes | yes |
| WebAssembly (wasm32-wasi) | no | yes |
