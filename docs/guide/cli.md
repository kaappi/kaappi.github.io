# Command-Line Reference

```
kaappi [OPTIONS] [FILE]
```

| Option | Description |
|--------|-------------|
| *(no arguments)* | Launch the REPL |
| `FILE` | Run a Scheme source file |
| `--compile FILE` | Compile to bytecode (.sbc) without running |
| `--lib-path DIR` | Add a directory to the library search path (repeatable) |
| `--profile` | Profile execution (per-function timing, call counts, allocations) |
| `--sandbox` | Sandbox mode — blocks FFI, file I/O, `eval`, `load`, env access |
| `--no-jit` | Disable JIT compilation |
| `--no-cache` | Disable bytecode caching |
| `--disassemble FILE` | Show compiled bytecode without running |
| `--gc-stats` | Print GC statistics on exit |

**Standalone binaries:**

```bash
zig build -Dbundle-src=program.scm    # compile + embed in one step
zig build -Dbundle=program.sbc        # embed pre-compiled bytecode
```

### Examples

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
