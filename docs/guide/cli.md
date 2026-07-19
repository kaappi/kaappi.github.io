# Command-Line Reference

```
kaappi [OPTIONS] [FILE] [SCRIPT-ARGS...]
kaappi compile FILE [-o OUTPUT]
kaappi check FILE
kaappi explain CODE
kaappi features [--json]
kaappi test [PATHS...]
kaappi ast|expand|ir FILE
kaappi doctor [--json]
kaappi fmt [--check] [FILES...]
kaappi cache status|clear
```

## Commands

| Command | Description |
|---------|-------------|
| `kaappi compile FILE` | Compile Scheme source to a native binary via LLVM. Use `-o` to set the output path. |
| `kaappi check FILE` | Compile-only static analysis: read, expand, and compile without executing, reporting read/compile errors plus `KP4xxx` lint findings (see the [Diagnostic Reference](diagnostics.md#static-analysis-kp4xxx)). Honors `--diagnostics=json`; `--deny-warnings` makes lint findings fail the exit code. |
| `kaappi explain CODE` | Print a diagnostic code's registry entry — meaning, a minimal triggering example, and the fix — e.g. `kaappi explain KP3001`. `--json` emits one machine-readable object; `--all` prints every registered code. |
| `kaappi features` | Report this build's capabilities: version and build id, target triple, build mode, compiled-in subsystems, built-in vs. portable SRFIs, and VM limits. `--json` for tooling. See [Standards Conformance](../conformance.md#discovering-capabilities-from-the-command-line). |
| `kaappi test [PATHS...]` | Run SRFI-64 test suites (files or directories), one subprocess per file, and print an aggregate summary with a reproducible seed. `--json`, `--seed N`, `--lib-path DIR`; `--changed` / `--list-affected [--since REV]` select only suites whose import closure actually changed. |
| `kaappi ast FILE` | Print the post-read datums — the program as the reader saw it, before macro expansion. |
| `kaappi expand FILE` | Print the program after full macro expansion. The output round-trips: it is valid source. |
| `kaappi ir FILE` | Print the compiler's IR tree after the optimization passes; `--no-opt` shows it before them. |
| `kaappi doctor` | Check the installation and environment — binary, library path, package manager, native backend, REPL, FFI — reporting PASS/WARN/FAIL per check with a fix for each failure. `--json` for tooling. |
| `kaappi fmt [FILES...]` | Format Scheme source in place: canonical 2-space R7RS indentation with 80-column reflow, preserving comments, guarded by a reader round-trip check so it can never change a program's meaning. `--check` lists files that need formatting and exits 1 without writing; with no files, formats stdin to stdout. |
| `kaappi cache status` | Show the bytecode cache location, entries, sizes, and staleness. |
| `kaappi cache clear` | Remove all bytecode cache entries. |

## Options

| Option | Description |
|--------|-------------|
| *(no arguments)* | Launch the REPL |
| `FILE` | Run a Scheme source file |
| `-h`, `--help` | Show usage and available flags |
| `--version` | Show version string |
| `--compile FILE` | Compile to bytecode (.sbc) without running |
| `-o FILE` | Output path for `--compile`, `--emit-llvm`, or `compile` |
| `--lib-path DIR` | Add a directory to the library search path (repeatable) |
| `--profile` | Profile execution (per-function timing, call counts, allocations) |
| `--sandbox` | Sandbox mode — blocks FFI, file I/O, `eval`, `load`, env access, threads |
| `--timeout MS` | Execution timeout in milliseconds |
| `--max-memory BYTES` | Maximum heap memory in bytes |
| `--emit-llvm` | Emit LLVM IR text (`.ll` file) for native compilation |
| `--profile-json FILE` | Write profiling data as JSON |
| `--timings[=FMT]` | Report per-stage pipeline wall time (read, expand, lower, optimize, emit, execute) and a cache HIT/MISS line on stderr; `FMT` is `text` (default) or `json` |
| `--diagnostics=FMT` | Diagnostic output format: `text` (default) or `json` — JSON Lines on stderr, shaped as LSP `Diagnostic` objects |
| `--deny-warnings` | With `kaappi check`: treat lint warnings as errors for the exit code |
| `--no-ir-opt` | Disable the IR optimization passes (skips the bytecode cache) |
| `--disassemble FILE` | Show compiled bytecode without running |
| `--gc-stats` | Print GC statistics on exit |
| `--coverage` | Report library procedure coverage |
| `--coverage-xml FILE` | Write Cobertura XML coverage report |
| `--completions SHELL` | Output shell completion script (`bash`, `zsh`, or `fish`) |

## Shell Completions

Enable tab completion for `kaappi` flags, subcommands, and `.scm` files:

```bash
# Bash — add to ~/.bashrc
eval "$(kaappi --completions bash)"

# Zsh — add to ~/.zshrc
eval "$(kaappi --completions zsh)"

# Fish — add to ~/.config/fish/config.fish
kaappi --completions fish | source
```

The `thottam` package manager also supports `--completions`:

```bash
eval "$(thottam --completions bash)"   # or zsh / fish
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `KAAPPI_HOME` | Override the default `~/.kaappi/` directory for libraries, packages, the bytecode cache, and REPL history. |
| `KAAPPI_LIB_DIR` | Directory containing `libkaappi_rt.a` for `kaappi compile`. Overrides the default search paths. |
| `NO_COLOR` | When set to a non-empty value, disables all REPL syntax highlighting and prompt colors. See [no-color.org](https://no-color.org/). |

## Build-Time Options

These are passed to `zig build` (not the `kaappi` CLI) and control
compile-time settings:

| Option | Default | Description |
|--------|---------|-------------|
| `-Dmax-frames=N` | 480 | Initial call frame capacity (grows to 32768) |
| `-Dmax-registers=N` | 2048 | Initial register count (grows to 65536) |
| `-Dgc-threshold=N` | 8192 | Initial GC object threshold |
| `-Doptimize=MODE` | ReleaseSafe | Optimization mode (Debug, ReleaseSafe, ReleaseFast) |
| `-Dnative-src=FILE` | — | Compile Scheme source to a native binary via LLVM IR |

```bash
# Build with larger initial frame capacity
zig build -Dmax-frames=1024

# Build with larger GC threshold for allocation-heavy programs
zig build -Dgc-threshold=32768

# Compile Scheme to native binary
zig build native -Dnative-src=program.scm
./zig-out/bin/program
```

## Standalone Binaries

Embed a Scheme program into a self-contained executable. This uses Zig's
build system (not the `kaappi` CLI) because the program is compiled into
the binary at build time:

```bash
zig build -Dbundle-src=program.scm    # compile + embed in one step
zig build -Dbundle=program.sbc        # embed pre-compiled bytecode
```

## Examples

```bash
# REPL
kaappi

# Run a file
kaappi program.scm

# Compile to native binary
kaappi compile program.scm -o program
./program

# Compile to native binary with custom lib path
KAAPPI_LIB_DIR=/opt/kaappi/lib kaappi compile program.scm -o program

# Run with additional library paths
kaappi --lib-path ./vendor/libs --lib-path ./mylibs program.scm

# Compile to bytecode only
kaappi --compile mylib.scm

# Pipe input
echo '(+ 1 2)' | kaappi

# Profile a program
kaappi --profile program.scm

# Lint without running (KP4xxx findings; add --deny-warnings for CI)
kaappi check program.scm

# Run all SRFI-64 test suites under tests/
kaappi test tests/

# Check formatting without writing (exit 1 if anything needs reformatting)
kaappi fmt --check src/

# Look up a diagnostic code
kaappi explain KP3001

# Verify the installation and environment
kaappi doctor

# See where the pipeline spends time, and whether the bytecode cache hit
kaappi --timings program.scm
```

---

Next: [Debugging](debugging.md)
