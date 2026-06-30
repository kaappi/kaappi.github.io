# Troubleshooting

Common errors and how to resolve them. Errors in Kaappi fall into three
categories: read-time (parsing), compile-time, and runtime.

---

## Read-Time Errors

Read-time errors occur when the reader cannot parse your input into valid
Scheme data. They are reported with a source location in the format
`<source>:<line>:<col>: read error: <error>`.

### UnexpectedEof

**Message:** `read error: error.UnexpectedEof`

**Cause:** The reader reached the end of input while still inside an
unterminated list, string, or block comment. Usually a missing closing
parenthesis.

**Example:**
```scheme
kaappi> (define (square x)
  (* x x)
;; read error: error.UnexpectedEof
```

**Fix:** Add the missing closing delimiter. In the REPL, count your
parentheses -- every `(` needs a matching `)`.

---

### UnterminatedString

**Message:** `read error: error.UnterminatedString`

**Cause:** A string literal is missing its closing double quote. This also
triggers if a backslash escape appears at the very end of the string without
a closing `"`.

**Example:**
```scheme
kaappi> (display "hello)
;; read error: error.UnterminatedString
```

**Fix:** Close the string with a matching `"`.

---

### InvalidEscape

**Message:** `read error: error.InvalidEscape`

**Cause:** A string or symbol contains an escape sequence that Kaappi does
not recognize. Valid escapes are `\n`, `\r`, `\t`, `\a`, `\b`, `\\`, `\"`,
`\|`, and `\x<hex>;`. Anything else (like `\q` or a `\x` without a valid
hex scalar and semicolon) is rejected.

**Example:**
```scheme
kaappi> (display "hello\q")
;; read error: error.InvalidEscape
```

**Fix:** Use a supported escape sequence. For hex escapes, use the format
`\x41;` (hex digits followed by a semicolon).

---

### DotNotInList

**Message:** `read error: error.DotNotInList`

**Cause:** The dot (`.`) used for dotted-pair notation appeared in an invalid
position, such as more than one dot in a list or a dot outside of a list
context.

**Example:**
```scheme
kaappi> (1 . 2 . 3)
;; read error: error.DotNotInList
```

**Fix:** A dotted pair has exactly one dot separating two elements:
`(1 . 2)`. To build a longer improper list, nest the pairs:
`(1 2 . 3)`.

---

### NestingTooDeep

**Message:** `read error: error.NestingTooDeep`

**Cause:** Block comments (`#| ... |#`) are nested beyond 256 levels. This
limit prevents pathological inputs from consuming unbounded stack space.

**Example:**
```scheme
kaappi> #| #| #| ... 257 levels ... |# |# |#
;; read error: error.NestingTooDeep
```

**Fix:** Reduce the nesting depth of block comments. In practice this error
is only triggered by adversarial input -- normal code never approaches this
limit.

---

## Compile-Time Errors

Compile-time errors are reported when the compiler translates Scheme
expressions into bytecode. They are printed as
`compile error: error.<name>`.

### InvalidSyntax

**Message:** `compile error: error.InvalidSyntax`

**Cause:** A special form is malformed. Common triggers include `let` with
no bindings or body, `lambda` with no parameter list or body, `if` with no
branches, `define` with no value, or bare `syntax-rules` outside
`define-syntax`.

**Example:**
```scheme
kaappi> (lambda)
;; compile error: error.InvalidSyntax

kaappi> (let)
;; compile error: error.InvalidSyntax

kaappi> (if)
;; compile error: error.InvalidSyntax
```

**Fix:** Supply all required sub-expressions. For example, `lambda` needs at
least a parameter list and a body: `(lambda (x) x)`.

---

### UndefinedVariable (compile-time)

**Message:** `compile error: error.UndefinedVariable`

**Cause:** The compiler detected a reference to a variable that is not
defined in any reachable scope. This check applies at compile time for
variables that can be statically resolved.

**Example:**
```scheme
kaappi> (set! nonexistent 42)
;; compile error: error.UndefinedVariable
```

**Fix:** Define the variable before referencing it, or check for typos in the
variable name.

---

## Runtime Errors

Runtime errors occur during execution. When an error detail message is
available, Kaappi prints `error: <detail>`. Otherwise it falls back to
`runtime error: error.<name>`. A stack trace follows when multiple frames
are active.

### TypeError

**Message:** `error: type error in '<procedure>': got <value>`

**Cause:** A primitive procedure received an argument of the wrong type.
Kaappi checks types at the point of use and reports the procedure name and
the offending value.

**Example:**
```scheme
kaappi> (+ "a" 1)
;; error: type error in '+': got "a"

kaappi> (car 42)
;; error: type error in 'car': got 42
```

**Fix:** Pass the correct type. Use predicates like `number?`, `string?`,
or `pair?` to validate inputs when needed.

---

### ArityMismatch

**Message:** `error: expected <n> arguments, got <m>` or
`error: '<procedure>': expected <n> arguments, got <m>`

**Cause:** A procedure was called with the wrong number of arguments.
For variadic procedures, the message reads
`expected at least <n> arguments, got <m>`.

**Example:**
```scheme
kaappi> (cons 1)
;; error: expected 2 arguments, got 1

kaappi> (cons 1 2 3)
;; error: expected 2 arguments, got 3
```

**Fix:** Pass the correct number of arguments. Check the procedure's
signature in the [Procedure Reference](../procedures/index.md).

---

### NotAProcedure

**Message:** `error: not a procedure`

**Cause:** The expression in the operator position of a call evaluated to
something that is not callable (not a closure, native function, continuation,
or parameter object). A common mistake is putting a number or string where a
function is expected.

**Example:**
```scheme
kaappi> (42 1 2)
;; error: not a procedure

kaappi> ("hello" 1)
;; error: not a procedure
```

**Fix:** Make sure the first element of the call expression is a procedure.
Check for accidental extra parentheses: `((+ 1 2))` tries to call `3`.

---

### DivisionByZero

**Message:** `runtime error: error.DivisionByZero`

**Cause:** An arithmetic operation attempted to divide by zero. This applies
to `/`, `quotient`, `remainder`, and `modulo`.

**Example:**
```scheme
kaappi> (/ 1 0)
;; runtime error: error.DivisionByZero

kaappi> (quotient 5 0)
;; runtime error: error.DivisionByZero
```

**Fix:** Guard division with a zero check:
`(if (zero? d) (error "divisor is zero") (/ n d))`.

---

### IndexOutOfBounds

**Message:** `error: index out of bounds in '<procedure>'`

**Cause:** An index argument exceeded the valid range of a vector, string,
or bytevector. Valid indices are `0` to `(- (length obj) 1)`.

**Example:**
```scheme
kaappi> (vector-ref #(1 2 3) 5)
;; error: index out of bounds in 'vector-ref'

kaappi> (string-ref "abc" 10)
;; error: index out of bounds in 'string-ref'
```

**Fix:** Check the length before indexing:
`(when (< i (vector-length v)) (vector-ref v i))`.

---

### StackOverflow

**Message:** `runtime error: error.StackOverflow`

**Cause:** The call stack exceeded 32768 frames or exhausted available
memory. The frame stack grows automatically (starting at 480 frames), so
this error only occurs with extremely deep non-tail recursion. Tail calls
do not consume stack frames.

**Example:**
```scheme
kaappi> (define (forever n) (+ 1 (forever (+ n 1))))
kaappi> (forever 0)
;; runtime error: error.StackOverflow (at ~32768 frames)
```

**Fix:** Rewrite the recursion in tail position. The example above can be
converted to a tail-recursive form:

```scheme
(define (forever n) (forever (+ n 1)))
```

Kaappi optimizes tail calls, so tail-recursive functions run in constant
stack space. Non-tail-recursive code (e.g., `(cons x (f (cdr lst)))`)
works fine for thousands of elements.

---

### UndefinedVariable (runtime)

**Message:** `error: undefined variable '<name>'`

**Cause:** A variable was referenced at runtime but no binding exists in
the current environment or the global scope. This differs from the
compile-time check because the variable lookup happens dynamically (e.g.,
via `eval` or a global reference loaded at runtime).

**Example:**
```scheme
kaappi> x
;; error: undefined variable 'x'

kaappi> (set! y 10)
;; error: set!: unbound variable 'y'
```

**Fix:** Define the variable before use: `(define x 42)`. For `set!`,
the variable must already be defined -- use `define` for the initial
binding.

---

### OutOfMemory

**Message:** `runtime error: error.OutOfMemory`

**Cause:** The garbage collector could not free enough memory to satisfy an
allocation request. This can happen with very large data structures or
long-running programs that accumulate live data.

**Example:**
```scheme
kaappi> (define (eat) (cons 1 (eat)))
kaappi> (eat)
;; runtime error: error.OutOfMemory
```

**Fix:** Reduce live data by releasing references to objects you no longer
need. Restructure code to process data in a streaming fashion rather than
building large intermediate structures. If the program is legitimately
memory-bound, consider breaking the work into smaller batches.

---

## Library and Import Errors

### Library not found

**Message:** `error: library not found: (some library)`

**Cause:** The library is not built-in and no `.sld` file was found in
the library search path.

**Fix:** Check the library name for typos. For ecosystem libraries,
install with `thottam install kaappi-json`. For your own libraries, pass
the path with `--lib-path`:

```bash
kaappi --lib-path ./lib program.scm
```

Libraries installed via thottam are auto-discovered from `~/.kaappi/lib/`.

---

### Export not found

**Cause:** You imported a library but referenced a procedure that it
does not export.

**Fix:** Check the library's `define-library` form for the `export`
clause. Use `,apropos` in the REPL to search for the procedure name.

---

## FFI Errors

### Shared library not found

**Message:** `error: ffi-open: cannot open shared library`

**Cause:** The `.dylib` (macOS) or `.so` (Linux) file was not found in
the library search path.

**Fix:** Make sure the native library is built (`make` in the library's
directory) and either:

- Install via thottam (copies to `~/.kaappi/lib/`)
- Pass the path: `--lib-path /path/to/dir`
- Set `DYLD_LIBRARY_PATH` (macOS) or `LD_LIBRARY_PATH` (Linux)

---

### Symbol not found

**Message:** `error: ffi-fn: symbol not found`

**Cause:** The shared library was loaded but does not contain the
requested function symbol.

**Fix:** Check the function name for typos. Verify the library was
compiled with the expected function (use `nm -gU library.dylib` on macOS
or `nm -D library.so` on Linux to list exported symbols).

---

## Setup Issues

### command not found: kaappi

**Cause:** The `kaappi` binary is not in your `PATH`.

**Fix for install script:** The install script places binaries in
`~/.local/bin`. Add it to your shell profile:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then restart your terminal or `source` your profile.

**Fix for source build:** The binary is at `zig-out/bin/kaappi`. Either
add `zig-out/bin` to your `PATH` or copy the binary:

```bash
cp zig-out/bin/kaappi ~/.local/bin/
```

---

### macOS Gatekeeper warning

**Message:** *"kaappi" can't be opened because Apple cannot check it for
malicious software.*

**Cause:** The binary is not signed. This only affects binaries built
from source — release binaries are Developer ID signed and Apple
notarized.

**Fix:** Use the install script (`curl -fsSL https://kaappi-lang.org/install.sh | bash`)
which downloads signed binaries. For source builds, remove the quarantine
attribute:

```bash
xattr -d com.apple.quarantine zig-out/bin/kaappi
```

---

## Native Compilation Issues

If a native-compiled binary behaves differently from the interpreter,
compare outputs:

```bash
kaappi program.scm > expected.txt
zig build native -Dnative-src=program.scm
./zig-out/bin/program > actual.txt
diff expected.txt actual.txt
```

If outputs differ, please
[report it](https://github.com/kaappi/kaappi/issues).

---
