# Command-Line Reference

```
kaappi [OPTIONS] [FILE]
```

| Option | Description |
|--------|-------------|
| *(no arguments)* | Launch the REPL |
| `FILE` | Run a Scheme source file |
| `-h`, `--help` | Show usage and available flags |
| `--version` | Show version string |
| `--compile FILE` | Compile to bytecode (.sbc) without running |
| `-o FILE` | Output path for `--compile` |
| `--lib-path DIR` | Add a directory to the library search path (repeatable, up to 16) |
| `--profile` | Profile execution (per-function timing, call counts, allocations) |
| `--sandbox` | Sandbox mode — blocks FFI, file I/O, `eval`, `load`, env access |
| `--no-jit` | Disable JIT compilation |
| `--no-cache` | Disable bytecode caching |
| `--disassemble FILE` | Show compiled bytecode without running |
| `--gc-stats` | Print GC statistics on exit |
| `--experimental-threads` | Enable OS threads (SRFI-18 `thread-start!`) |

## Build-Time Options

These are passed to `zig build` (not the `kaappi` CLI) and control
compile-time settings:

| Option | Default | Description |
|--------|---------|-------------|
| `-Dmax-frames=N` | 512 | Maximum call frame depth |
| `-Dmax-registers=N` | 2048 | Maximum register count |
| `-Dgc-threshold=N` | 8192 | Initial GC object threshold |
| `-Doptimize=MODE` | ReleaseSafe | Optimization mode (Debug, ReleaseSafe, ReleaseFast) |

```bash
# Build with deeper recursion limit
zig build -Dmax-frames=1024

# Build with larger GC threshold for allocation-heavy programs
zig build -Dgc-threshold=32768
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

# Run with additional library paths
kaappi --lib-path ./vendor/libs --lib-path ./mylibs program.scm

# Compile only
kaappi --compile mylib.scm

# Pipe input
echo '(+ 1 2)' | kaappi

# Profile a program
kaappi --profile program.scm
```

---

Next: [Tips](tips.md)
