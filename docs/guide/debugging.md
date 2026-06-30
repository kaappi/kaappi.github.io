# Debugging

Kaappi provides several tools for understanding what your code is doing:
REPL inspection commands for quick exploration, a stepping debugger for
tracing execution, profiling for performance analysis, and bytecode
disassembly for seeing what the compiler produces.

## Reading error messages

Errors include the source location and a clear diagnostic:

```
program.scm:5:12: error: type error in '+': expected number, got "hello"
```

The format is `source:line:column: category: message`. Error categories:

- **read error** — malformed syntax (unclosed parentheses, bad escapes)
- **compile error** — invalid forms or undefined variables at compile time
- **error** — runtime type errors, arity mismatches, out-of-bounds access

When errors occur in nested calls, Kaappi prints a backtrace:

```
error: type error in '+': expected number, got "hello"
  called from helpers.scm:12
  called from program.scm:5
```

## REPL introspection

The REPL has several comma commands for exploring values and bindings
without stopping execution.

**`,type <expr>`** — show the type of a result:

```
kaappi> ,type (+ 1 2)
; integer
kaappi> ,type "hello"
; string
kaappi> ,type '(1 2 3)
; pair
```

**`,describe <name>`** — show binding details including arity and source:

```
kaappi> ,describe map
  map
    type: procedure
    arity: 2+
kaappi> (define (greet name) (string-append "hello " name))
kaappi> ,describe greet
  greet
    type: procedure
    arity: 1, locals: 0
    source: <repl>:1
```

**`,apropos <string>`** — search bindings by substring:

```
kaappi> ,apropos vector
  vector-append, vector-copy, vector-fill!, vector-for-each,
  vector-length, vector-map, vector-ref, vector-set!, ...
; 18 matches
```

**`,env [prefix]`** — list global bindings, optionally filtered:

```
kaappi> ,env string-
  string-append, string-copy, string-length, string-ref, ...
; 24 bindings
```

**`,expand <expr>`** — show macro expansion:

```
kaappi> ,expand (when #t (display "yes"))
(if #t (begin (display "yes")))
```

**`_` variable** — the last evaluation result, useful for incremental exploration:

```
kaappi> (filter odd? '(1 2 3 4 5))
(1 3 5)
kaappi> (length _)
3
```

## Stepping debugger

The REPL includes a built-in stepping debugger for tracing execution
frame by frame.

### Setting breakpoints

```
kaappi> (define (factorial n) (if (<= n 1) 1 (* n (factorial (- n 1)))))
kaappi> ,break factorial
Breakpoint set on factorial
```

Manage breakpoints with:

```
,breakpoints       -- list all breakpoints
,delete all        -- remove all breakpoints
```

### Hitting a breakpoint

When execution reaches a breakpointed function, Kaappi pauses and shows
a `debug>` prompt:

```
kaappi> (factorial 5)
Break at factorial (<repl>:1)
debug>
```

### Debugger commands

| Command | Short | Action |
|---------|-------|--------|
| `step` | `s` | Step into the next expression |
| `next` | `n` | Step over (stay in current frame) |
| `finish` | `out` | Step out — run until current frame returns |
| `continue` | `c` | Continue to next breakpoint or end |
| `locals` | `l` | Show local variable bindings |
| `backtrace` | `bt` | Print the call stack (marks inspected frame with `>`) |
| `up` | | Move inspection up to the caller frame |
| `down` | | Move inspection down to the callee frame |
| `watch VAR` | | Break when a local variable's value changes |
| `unwatch VAR` | | Stop watching a variable |
| `quit` | `q` | Exit the debugger |

### Conditional breakpoints

Break only when a condition is true:

```
kaappi> ,break factorial
Breakpoint set on factorial
kaappi> ,condition 0 (> n 10)
Condition set
```

The expression is evaluated each time the breakpoint is hit. The debugger
only pauses when the result is truthy.

### Watch expressions

Watch a variable and break when its value changes:

```
debug> watch n
Watching n
debug> continue
Watch: n = 2
Break at factorial
```

Use `unwatch n` to remove the watch.

### Frame navigation

Use `up` and `down` to inspect locals at different stack levels:

```
debug> backtrace
> [2] factorial
  [1] factorial
  [0] <top-level>
debug> up
[1] factorial
debug> locals
  n = 3
debug> down
[2] factorial
```

### Walkthrough

```
kaappi> (factorial 3)
Break at factorial (<repl>:1)
debug> locals
  n = 3
debug> continue
Break at factorial (<repl>:1)
debug> locals
  n = 2
debug> backtrace
> [1] factorial
  [0] factorial
debug> continue
Break at factorial (<repl>:1)
debug> locals
  n = 1
debug> continue
6
```

### Step through an expression

Use `,step` to single-step from the start without setting breakpoints:

```
kaappi> ,step (* 2 (+ 3 4))
```

## Profiling

### In the REPL

```
kaappi> ,profile (factorial 20)
2432902008176640000
; Profile Report
;   Self ms  Total ms    Calls  Alloc KB  Function
;      0.1       0.1       20        -    factorial (<repl>:1)
;      0.0       0.0       19        -    * (built-in)
```

Columns:

- **Self ms** — time in this function, excluding callees
- **Total ms** — inclusive time (self + callees)
- **Calls** — number of invocations
- **Alloc KB** — heap memory allocated in this function

### From the command line

```bash
kaappi --profile program.scm
```

Profile an entire program run. The top 20 functions by self time are shown.

### Timing a single expression

For a quick wall-clock measurement without the full profile breakdown:

```
kaappi> ,time (fib 30)
832040
; 0.025 seconds
```

## Bytecode inspection

### Disassembling a procedure

Use the `,dis` REPL command or the `(disassemble)` procedure:

```
kaappi> (define (factorial n) (if (<= n 1) 1 (* n (factorial (- n 1)))))
kaappi> ,dis factorial
; Function: factorial
; Source: <repl>
; Arity: 1, Locals: 7, Upvalues: 0
; Constants: <=, 1, *, factorial, -
;
  0000  move            r2, r0
  0003  load_const      r3, 1
  0007  call_global     r1, <=, 2
  0012  jump_false      r1, -> 0023
  0016  load_const      r1, 1
  0020  jump            -> 0050
  0023  get_global      r1, *
  ...
  0047  tail_call       r1, 2
  0050  return          r1
```

`,dis <expr>` evaluates the expression, then disassembles the resulting
procedure. `(disassemble proc)` does the same from Scheme code. This shows
the register-based bytecode the compiler produces — useful for
understanding tail call optimization, closure captures, and performance.

### Disassembling a file

```bash
kaappi --disassemble program.scm
```

Shows bytecode for all top-level definitions without executing the program.

## GC diagnostics

### In the REPL

```
kaappi> ,gc
GC Statistics:
  Collections:       0
  Live objects:      589 (peak: 589)
  Heap size:         42552 bytes (peak: 42552)
  Freed:             0 objects, 0 bytes
  Mark time:         0.00 ms total
  Sweep time:        0.00 ms total
  Allocations by type:
    native_fn       585  port              3  rng               1
```

### From the command line

```bash
kaappi --gc-stats program.scm
```

Prints GC statistics after the program finishes. Useful for spotting
excessive allocation or frequent collections.

## Error handling in code

Use R7RS `guard` for structured exception handling:

```scheme
(guard (e
        ((string? (condition/message e))
         (display "caught: ")
         (display (condition/message e))
         (newline)))
  (error "something went wrong"))
```

Use `with-exception-handler` for lower-level control:

```scheme
(with-exception-handler
  (lambda (e) (display "error!\n"))
  (lambda () (/ 1 0))
  'replace)
```

Use `call/ec` (escape continuations) for non-local exits:

```scheme
(define (find-negative lst)
  (call/ec
    (lambda (return)
      (for-each (lambda (x)
                  (when (negative? x) (return x)))
                lst)
      #f)))

(find-negative '(3 7 -2 5))  ;=> -2
```

## Tips

**Compare interpreter vs native** — if a native-compiled binary behaves
differently from the interpreter, run both and diff:

```bash
kaappi program.scm > expected.txt
zig build native -Dnative-src=program.scm && ./zig-out/bin/program > actual.txt
diff expected.txt actual.txt
```

**Check library coverage** — see which exported procedures your tests
exercise:

```bash
kaappi --coverage --lib-path ./lib tests/test.scm
```

**Catch runaway programs** — use `--timeout` to kill programs that
take too long, and `--max-memory` to cap heap usage:

```bash
kaappi --timeout 5000 program.scm           # 5-second limit
kaappi --max-memory 10000000 program.scm    # ~10 MB limit
```

**Tune initial stack capacity** — the frame stack and register array grow
automatically during execution. To reduce the number of reallocations for
deeply recursive programs, set a larger initial capacity:

```bash
zig build -Dmax-frames=4096        # default: 480, grows to 32768
zig build -Dmax-registers=8192     # default: 2048, grows to 65536
```

---

Next: [Tips](tips.md)
