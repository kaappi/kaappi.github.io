# Debugging

Kaappi provides several tools for understanding what your code is doing:
REPL inspection commands for quick exploration, a stepping debugger for
tracing execution, profiling for performance analysis, and bytecode
disassembly for seeing what the compiler produces.

## Reading error messages

Errors include the source location, a stable diagnostic code, and the
offending line:

```
program.scm:5:12: error[KP3002]: type error in 'arithmetic': expected number, got #<string>
    (+ 1 "hello")
```

The format is `source:line:column: category[KPnnnn]: message`. Error
categories:

- **read error** (`KP1xxx`) — malformed syntax (unclosed parentheses, bad escapes)
- **compile error** (`KP2xxx`) — invalid forms or undefined variables at compile time
- **error** (`KP3xxx`) — runtime type errors, arity mismatches, out-of-bounds access

When errors occur in nested calls, Kaappi prints a backtrace:

```
program.scm:1:20: error[KP3002]: type error in 'arithmetic': expected number, got #<string>
    (define (helper x) (+ x "bad"))
  called from program.scm:3
```

### Diagnostic codes

Every diagnostic carries a stable `KP` code (`KP1xxx` read, `KP2xxx`
compile, `KP3xxx` runtime, `KP4xxx` lint, `KP9xxx` internal). Codes never
change meaning between releases, so they are safe to match on in scripts and
tooling.

Look up any code — its meaning, a minimal example, and how to fix it —
straight from the binary:

```
$ kaappi explain KP3002
KP3002  type-error
runtime · error

type error

A procedure was applied to an argument of the wrong type — for example
'car' on a non-pair or '+' on a non-number. The message names the
procedure, the type it expected, and the value it got.

Example:
    (car 5)
```

The [Diagnostic Reference](diagnostics.md) documents every code on one page.
For machine-readable output, `kaappi explain <code> --json` emits a single
JSON object, and `--diagnostics=json` makes the interpreter itself report
errors as [LSP `Diagnostic`](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic)
objects.

## Catching errors before running

`kaappi check` reads, expands, and compiles a file without executing it,
reporting read and compile errors plus
[`KP4xxx` lint findings](diagnostics.md#static-analysis-kp4xxx) for
mistakes that are guaranteed to fail at run time:

```console
$ kaappi check program.scm
1:1: warning[KP4001]: unknown variable 'undefined-name' at top level
2:1: error[KP4002]: 'car' expects 1 argument, but 2 were given
3:1: error[KP4003]: 'vector-ref' expects a vector as argument 1, but a string literal was given
check: 2 errors, 1 warning
```

The exit code is non-zero when any error is found. Findings that are
only warnings — like KP4001, since R7RS permits top-level forward
references — leave the exit code at 0 unless you pass `--deny-warnings`;
`kaappi check` never rejects a program R7RS permits:

```bash
kaappi check --deny-warnings program.scm   # CI: warnings fail too
```

Like the interpreter, `check` honors `--diagnostics=json` for tooling.

## REPL introspection

The REPL has several comma commands for exploring values and bindings
without stopping execution.

**`,type <expr>`** — show the type of a result:

```scheme
kaappi> ,type (+ 1 2)
; integer
kaappi> ,type "hello"
; string
kaappi> ,type '(1 2 3)
; pair
```

**`,describe <name>`** — show binding details including arity and source:

```scheme
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

```scheme
kaappi> ,apropos vector
  vector-append, vector-copy, vector-fill!, vector-for-each,
  vector-length, vector-map, vector-ref, vector-set!, ...
; 18 matches
```

**`,env [prefix]`** — list global bindings, optionally filtered:

```scheme
kaappi> ,env string-
  string-append, string-copy, string-length, string-ref, ...
; 24 bindings
```

**`,expand <expr>`** — show macro expansion:

```scheme
kaappi> ,expand (when #t (display "yes"))
(if #t (begin (display "yes")))
```

**`_` variable** — the last evaluation result, useful for incremental exploration:

```scheme
kaappi> (filter odd? '(1 2 3 4 5))
(1 3 5)
kaappi> (length _)
3
```

## Stepping debugger

The REPL includes a built-in stepping debugger for tracing execution
frame by frame.

### Setting breakpoints

```scheme
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

```scheme
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

```scheme
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

```scheme
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

```scheme
kaappi> ,step (* 2 (+ 3 4))
```

## Profiling

### In the REPL

```scheme
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

```scheme
kaappi> ,time (fib 30)
832040
; 0.025 seconds
```

### Per-stage pipeline timings

To see where startup time goes — reading, expansion, compilation, or
execution — and whether the bytecode cache was used:

```console
$ kaappi --timings program.scm
3
timings: read 0.0ms | expand 0.0ms | lower 0.0ms | optimize 0.0ms | emit 0.0ms | execute 0.0ms
cache: MISS (wrote /home/user/.kaappi/cache/7f6d8fd16240bf92.sbc)
```

Both lines go to stderr. On a second run of an unchanged program the
compile stages disappear — the cache line reports `HIT` and only
`execute` remains. `--timings=json` emits the same data as JSON.

## Performance tips

- **Prefer vectors over lists for random access.** `vector-ref` is O(1);
  `list-ref` is O(n) because it walks the chain of pairs. Use lists for
  sequential processing, vectors when you need indexing:

  ```scheme
  ;; Fast: O(1) lookup
  (define v (vector 10 20 30 40 50))
  (vector-ref v 3)         ;=> 40

  ;; Slow: O(n) traversal
  (define ls (list 10 20 30 40 50))
  (list-ref ls 3)          ;=> 40
  ```

- **For maximum performance, compile to native.** Use
  `zig build native -Dnative-src=program.scm` to compile your program
  via the LLVM backend. Simple functions compile to native LLVM functions
  with direct calls, bypassing the bytecode interpreter.

- **Use `for-each` instead of `map` when you don't need results.** `map`
  allocates a new list for its return value; `for-each` just applies the
  procedure for side effects:

  ```scheme
  ;; Allocates a list you throw away -- wasteful
  (map display '(1 2 3))

  ;; No allocation
  (for-each display '(1 2 3))
  ```

- **Hash tables are O(1) for lookup.** Kaappi uses open-addressing with
  linear probing. For key-value associations that grow beyond a handful of
  entries, `hash-table-ref` is much faster than `assoc` on an alist:

  ```scheme
  (import (srfi 69))
  (define ht (alist->hash-table '((a . 1) (b . 2) (c . 3))))
  (hash-table-ref ht 'b)  ;=> 2
  ```

## Pipeline stage dumps

Three read-only subcommands print a program at successive stages of the
compile pipeline — useful for macro debugging and for seeing what the
optimizer does:

- `kaappi ast file.scm` — the datums exactly as the reader produced
  them, before any expansion
- `kaappi expand file.scm` — the program after full macro expansion; the
  output is valid source and round-trips through the reader
- `kaappi ir file.scm` — the compiler's IR tree after the optimization
  passes (`--no-opt` shows it before them)

Macro expansion makes hygiene visible — template-introduced bindings
show up under their renamed `__hyg_...` identities:

```console
$ cat swap.scm
(define-syntax swap!
  (syntax-rules ()
    ((_ a b) (let ((tmp a)) (set! a b) (set! b tmp)))))
(define x 1)
(define y 2)
(swap! x y)

$ kaappi expand swap.scm
(define-syntax swap! (syntax-rules () ((_ a b) (let ((tmp a)) (set! a b) (set! b tmp)))))
(define x 1)
(define y 2)
(__hyg_1_let ((__hyg_2_tmp x)) (set! x y) (set! y __hyg_2_tmp))
```

The REPL's `,expand` command does the same for a single expression.

## Bytecode inspection

### Disassembling a procedure

Use the `,dis` REPL command or the `(disassemble)` procedure:

```scheme
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

```scheme
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

To branch on *which* error occurred, dispatch on its stable diagnostic
code with `error-object-code` from `(kaappi diagnostics)` instead of
matching message text — wording may change between releases; codes never
do:

```scheme
(import (kaappi diagnostics))

(guard (e ((eq? (error-object-code e) 'KP3004)   ; division by zero
           'undefined))
  (/ 1 0))
;=> undefined
```

`error-object-code` never raises — it returns `#f` for any value that
carries no code — so it is safe as the first test in a `guard` clause.
See the [reference entry](../procedures/extensions.md#error-object-code).

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

**Use `write-shared` for circular structures** — `write` will hang on
circular lists or vectors. `write-shared` prints them with datum labels:

```scheme
(define x (list 1 2 3))
(set-cdr! (cddr x) x)
(write-shared x)  ;; prints: #0=(1 2 3 . #0#)
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

Next: [Editor Support](editors.md)
