# Advanced Features

## Concurrency

Kaappi offers two concurrency models: green threads (fibers) for cooperative
multitasking and OS threads (SRFI-18) for true parallelism.

### Green threads (fibers)

Fibers run cooperatively within a single OS thread. They are lightweight
and communicate via channels:

```scheme
(import (kaappi fibers))

(define ch (make-channel))

(spawn (lambda ()
  (channel-send ch "hello from fiber")))

(display (channel-receive ch))  ;=> hello from fiber
```

Use fibers for concurrent I/O, event loops, and cooperative task
scheduling. See the [Fibers reference](../procedures/extensions.md#spawn)
for the full API.

### OS threads (SRFI-18)

Real OS threads via `pthread_create`. Each thread gets its own VM and GC
with an independent heap. No special flag is needed -- just run your
program:

```bash
kaappi program.scm
```

OS threads are unavailable in `--sandbox` mode and in the WebAssembly
build (including the browser playground); use fibers there.

```scheme
(import (srfi 18))

(define t (thread-start!
  (make-thread
    (lambda ()
      (* 6 7)))))

(thread-join! t)  ;=> 42
```

Values are **deep-copied** when crossing thread boundaries:

- At `thread-start!`: the thunk closure is deep-copied from parent to child
- At `thread-join!`: the result is deep-copied from child to parent

Threads cannot share mutable heap state directly -- use return values or
channels to communicate. See the [SRFI-18 reference](../procedures/threads.md)
for mutexes, condition variables, and the full threading API.

## FFI (Foreign Function Interface)

Call C library functions directly from Scheme:

```scheme
(import (kaappi ffi))

;; Open a shared library
(define libm (ffi-open "libm.dylib"))  ;; macOS
;; (define libm (ffi-open "libm.so.6"))  ;; Linux

;; Bind a C function: (ffi-fn lib "name" (param-types ...) return-type)
(define c-sqrt (ffi-fn libm "sqrt" '(double) 'double))
(define c-pow  (ffi-fn libm "pow"  '(double double) 'double))

(c-sqrt 2.0)     ;=> 1.4142135623730951
(c-pow 2.0 10.0) ;=> 1024.0

;; Clean up
(ffi-close libm)
```

Supported C types: `int`, `long`, `double`, `float`, `string`, `pointer`,
`void`, `bool`, `uint8`, `int8`, `int16`, `int32`, `int64`, `uint16`,
`uint32`, `uint64`, `size_t`, `char`.

**FFI callbacks** — pass Scheme procedures to C functions that expect function pointers:

```scheme
(define cb (ffi-callback (lambda (a b) (- a b)) '(pointer pointer) 'int))
;; Pass cb to a C function like qsort
(ffi-callback-release cb)  ;; free when done
```

## REPL Commands

The REPL supports meta-commands prefixed with `,` (comma). Type `,help`
to see the full list:

| Command | Description |
|---------|-------------|
| `,time <expr>` | Measure execution time of an expression |
| `,type <expr>` | Show the type of the result |
| `,expand <expr>` | Show the result of macro expansion |
| `,profile <expr>` | Profile timing, call counts, and allocations |
| `,dis <expr>` | Disassemble a procedure |
| `,describe <sym>` | Show procedure arity and type |
| `,apropos <str>` | Search bindings by substring |
| `,env [prefix]` | List global bindings (optional prefix filter) |
| `,break <name>` | Set a breakpoint on a function (see [Debugging](debugging.md)) |
| `,gc` | Show garbage collector statistics |
| `,version` | Show Kaappi version |
| `,load <file>` | Load and run a Scheme file |
| `,import <lib>` | Import a library (e.g. `,import (srfi 1)`) |
| `,quit` | Exit the REPL |
| `,help` | Show all available commands |

```
kaappi> ,time (fib 30)
832040
; 0.173 seconds
kaappi> ,import (srfi 1)
kaappi> (iota 5)
(0 1 2 3 4)
```

## Bytecode Caching

Kaappi automatically caches compiled bytecode to `.sbc` files next to the
source. On subsequent runs, if the source hasn't changed, the cached bytecode
is loaded directly -- skipping the reader, expander, and compiler stages.

```bash
# Explicitly compile to bytecode
kaappi --compile program.scm
# Output: Compiled program.scm -> program.sbc

# Subsequent runs use the cache automatically
kaappi program.scm
```

## Standalone Binaries

Kaappi can compile a Scheme program into a single standalone executable
that requires no runtime or source files to run.

**One-step build** — compile and embed in one command:

```bash
zig build -Dbundle-src=app.scm
# produces zig-out/bin/kaappi with app.scm embedded
```

The resulting binary includes the full Kaappi runtime and your compiled
program. Distribute it as a single file — no Zig or Kaappi installation
needed on the target machine.

**Two-step build** — pre-compile to bytecode, then embed:

```bash
kaappi --compile app.scm -o app.sbc    # compile to bytecode
zig build -Dbundle=app.sbc             # embed in binary
```

The two-step workflow is useful when you want to inspect or cache the
bytecode separately.

**Cross-compilation** — build for a different platform:

```bash
zig build -Dbundle-src=app.scm -Dtarget=x86_64-linux
zig build -Dbundle-src=app.scm -Dtarget=aarch64-linux
zig build -Dbundle-src=app.scm -Dtarget=riscv64-linux
```

## WebAssembly (WASM)

Kaappi can be compiled to WebAssembly for use in browsers or WASI
runtimes:

```bash
zig build wasm    # produces zig-out/bin/kaappi.wasm
```

The WASM build runs the same bytecode interpreter but with several
limitations:

- **No REPL** — WASM mode takes a source file, not interactive input
- **Interpreter only** — no LLVM native compilation
- **No FFI** — `ffi-open`, `ffi-fn` are unavailable
- **No file I/O** — limited to WASI-compatible stdin/stdout
- **No profiling or coverage** — `--profile`, `--coverage` flags are not available
- **No library paths** — `--lib-path` is not supported; only built-in libraries
- **No OS threads** — SRFI-18 is disabled (green fibers still work)

The [playground](../playground.md) and [interactive tour](../tour.md) use
the WASM build to run Scheme directly in the browser.

---

For the stepping debugger, profiling, bytecode inspection, and other
debugging tools, see the [Debugging](debugging.md) guide.

Next: [CLI Reference](cli.md)

