# Future Ideas

Potential improvements, roughly ordered by impact. None are committed.

---

## Performance

- **RISC-V JIT backend** — riscv64 currently runs interpreter-only
- **NaN-boxing** — pack f64 directly into the u64 value to eliminate heap allocation for flonums
- **Inline small functions** at the bytecode level (reduce call overhead for `tak`-style benchmarks)
- **Register window slide** instead of frame push for known-callee simple calls

## Features

- **Async I/O** integration with the fiber scheduler
- **Resource limits** for sandbox mode (max execution time, max memory)

## Tooling

- **REPL improvements** — syntax highlighting, auto-indent
