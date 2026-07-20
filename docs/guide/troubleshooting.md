# Troubleshooting

Common errors and how to resolve them. Errors in Kaappi fall into three
categories -- read-time (parsing), compile-time, and runtime -- and every
diagnostic carries a stable `KP` code:

```
program.scm:1:1: error[KP3002]: type error in 'car': expected pair, got 42
    (car 42)
```

The format is `source:line:col: category[KPnnnn]: message`. Runtime
errors additionally echo the offending source line and, when the error
occurred in a nested call, a backtrace of `called from` frames. In the
interactive REPL the location prefix is `<repl>` for read and compile
errors and omitted for runtime errors.

Each section below links to the code's entry in the
[Diagnostic Reference](diagnostics.md), and `kaappi explain <code>`
prints the same explanation in the terminal.

---

## First: `kaappi doctor`

For anything that smells like a setup problem — `kaappi` not found,
libraries that won't import, native compilation failing, FFI libraries
not loading — start with the built-in environment check:

```console
$ kaappi doctor

binary
  PASS  version: v0.15.0
  PASS  on-PATH: /home/user/.local/bin/kaappi (same as running binary)

library
  PASS  ~/.kaappi/lib: /home/user/.kaappi/lib
...
native-backend
  PASS  c-compiler: zig: /usr/local/bin/zig (links via 'zig cc')
  PASS  libkaappi_rt.a: found in /home/user/.local/lib
  PASS  smoke-link: zig linked a test program against libkaappi_rt.a in /home/user/.local/lib
...
package-manager
  WARN  lockfile: 1 of 3 locked package(s) missing from ~/.kaappi/src (first: kaappi-json)
        → run 'thottam update' to restore missing package sources
...
Summary: 15 pass, 1 warn, 0 fail — usable, but some checks need attention.
```

Six groups are checked — binary, library path, package manager, native
backend, REPL, and FFI — each reported PASS/WARN/FAIL with a suggested
fix for every failure. `kaappi doctor --json` emits the same report for
tooling.

---

## Read-Time Errors

Read-time errors occur when the reader cannot parse your input into valid
Scheme data. They are reported as
`<source>:<line>:<col>: read error[KP1xxx]: <message>`.

### Unexpected end of input (KP1001)

**Message:** `read error[KP1001]: unexpected end of input`

**Cause:** The reader reached the end of input while still inside an
unterminated list, string, or block comment. Usually a missing closing
parenthesis.

**Example** -- `program.scm`:

```scheme
(define (square x)
  (* x x)
```

```console
$ kaappi program.scm
program.scm:3:1: read error[KP1001]: unexpected end of input
```

**Fix:** Add the missing closing delimiter -- every `(` needs a matching
`)`. The interactive REPL never reports this error: while input is
incomplete it shows the `  ... ` continuation prompt and waits for the
rest.

**Reference:** [`KP1001`](diagnostics.md#kp1001-unexpected-eof) · `kaappi explain KP1001`

---

### Unterminated string literal (KP1006)

**Message:** `read error[KP1006]: unterminated string literal`

**Cause:** A string literal is missing its closing double quote. Because
a string may legally span multiple lines, the reader only knows it is
unterminated when the input ends -- the reported position is the end of
the input, not the opening quote.

**Example** -- `program.scm`:

```scheme
(display "hello)
```

```console
$ kaappi program.scm
program.scm:2:1: read error[KP1006]: unterminated string literal
```

**Fix:** Close the string with a matching `"`.

**Reference:** [`KP1006`](diagnostics.md#kp1006-unterminated-string) · `kaappi explain KP1006`

---

### Invalid escape sequence (KP1007)

**Message:** `read error[KP1007]: invalid escape sequence`

**Cause:** A string or symbol contains an escape sequence that Kaappi does
not recognize. Valid escapes are `\n`, `\r`, `\t`, `\a`, `\b`, `\\`, `\"`,
`\|`, and `\x<hex>;`. Anything else (like `\q` or a `\x` without a valid
hex scalar and semicolon) is rejected. The position points at the
offending escape.

**Example:**

```scheme
kaappi> (display "hello\q")
<repl>:1:17: read error[KP1007]: invalid escape sequence
```

**Fix:** Use a supported escape sequence. For hex escapes, use the format
`\x41;` (hex digits followed by a semicolon).

**Reference:** [`KP1007`](diagnostics.md#kp1007-invalid-escape) · `kaappi explain KP1007`

---

### Misplaced dot (KP1008)

**Message:** `read error[KP1008]: '.' outside of a list`

**Cause:** The dot (`.`) used for dotted-pair notation appeared where the
reader does not allow one -- at the top level, or inside a vector
literal. A second dot *inside* a list, as in `(1 . 2 . 3)`, is reported
at the second dot as
[`KP1002`](diagnostics.md#kp1002-unexpected-char) `unexpected character`.

**Example:**

```scheme
kaappi> #(1 . 2)
<repl>:1:6: read error[KP1008]: '.' outside of a list

kaappi> (1 . 2 . 3)
<repl>:1:8: read error[KP1002]: unexpected character
```

**Fix:** A dotted pair has exactly one dot separating two elements:
`(1 . 2)`. To build a longer improper list, nest the pairs:
`(1 2 . 3)`. Vectors have no dotted form.

**Reference:** [`KP1008`](diagnostics.md#kp1008-dot-outside-list) · `kaappi explain KP1008`

---

### Nesting too deep (KP1009)

**Message:** `read error[KP1009]: nesting too deep`

**Cause:** Block comments (`#| ... |#`) are nested beyond 256 levels. This
limit prevents pathological inputs from consuming unbounded stack space.

**Example** -- `program.scm`:

```scheme
#|#|#| ... 257 levels ... |#|#|#
```

```console
$ kaappi program.scm
program.scm:1:513: read error[KP1009]: nesting too deep
```

**Fix:** Reduce the nesting depth of block comments. In practice this error
is only triggered by adversarial input -- normal code never approaches this
limit.

**Reference:** [`KP1009`](diagnostics.md#kp1009-nesting-too-deep) · `kaappi explain KP1009`

---

## Compile-Time Errors

Compile-time errors are reported when the compiler translates Scheme
expressions into bytecode. They are printed as
`<source>:<line>:<col>: compile error[KP2xxx]: <message>`.

### Invalid syntax (KP2001)

**Message:** `compile error[KP2001]: invalid syntax`

**Cause:** A special form is malformed. Common triggers include `let` with
no bindings or body, `lambda` with no parameter list or body, `if` with no
branches, `define` with no value, or bare `syntax-rules` outside
`define-syntax`.

**Example:**

```scheme
kaappi> (lambda)
<repl>:1:1: compile error[KP2001]: invalid syntax

kaappi> (let)
<repl>:1:1: compile error[KP2001]: invalid syntax

kaappi> (if)
<repl>:1:1: compile error[KP2001]: invalid syntax
```

**Fix:** Supply all required sub-expressions. For example, `lambda` needs at
least a parameter list and a body: `(lambda (x) x)`.

**Reference:** [`KP2001`](diagnostics.md#kp2001-invalid-syntax) · `kaappi explain KP2001`

!!! note "Undefined variables are not compile-time errors"

    R7RS permits top-level forward references (a variable may be defined
    by a later `define`), so an undefined variable is reported at run
    time as [`KP3001`](#undefined-variable-kp3001). To catch likely
    mistakes before running, use `kaappi check`, which reports unknown
    top-level variables as
    [`KP4001`](diagnostics.md#kp4001-unknown-toplevel-variable) warnings.

---

## Runtime Errors

Runtime errors occur during execution. They are reported as
`<source>:<line>: error[KP3xxx]: <message>` (with a column when one is
known), followed by the offending source line. When the error occurred
in a nested call, a backtrace of `called from` frames follows. In the
REPL the location prefix and source echo are omitted.

### Type error (KP3002)

**Message:** `error[KP3002]: type error in '<procedure>': expected <type>, got <value>`

**Cause:** A primitive procedure received an argument of the wrong type.
Kaappi checks types at the point of use and reports the procedure name,
the expected type, and the offending value. Arithmetic primitives such
as `+` and `*` report under the shared name `arithmetic`.

**Example:**

```scheme
kaappi> (+ "a" 1)
error[KP3002]: type error in 'arithmetic': expected number, got #<string>

kaappi> (car 42)
error[KP3002]: type error in 'car': expected pair, got 42
```

**Fix:** Pass the correct type. Use predicates like `number?`, `string?`,
or `pair?` to validate inputs when needed.

**Reference:** [`KP3002`](diagnostics.md#kp3002-type-error) · `kaappi explain KP3002`

---

### Wrong number of arguments (KP3003)

**Message:** `error[KP3003]: '<procedure>': expected <n> arguments, got <m>`

**Cause:** A procedure was called with the wrong number of arguments.
For variadic procedures, the message reads
`expected at least <n> arguments, got <m>`.

**Example:**

```scheme
kaappi> (cons 1)
error[KP3003]: 'cons': expected 2 arguments, got 1

kaappi> (cons 1 2 3)
error[KP3003]: 'cons': expected 2 arguments, got 3
```

**Fix:** Pass the correct number of arguments. Check the procedure's
signature in the [Procedure Reference](../procedures/index.md).

**Reference:** [`KP3003`](diagnostics.md#kp3003-arity-mismatch) · `kaappi explain KP3003`

---

### Not a procedure (KP3005)

**Message:** `error[KP3005]: not a procedure`

**Cause:** The expression in the operator position of a call evaluated to
something that is not callable (not a closure, native function, continuation,
or parameter object). A common mistake is putting a number or string where a
function is expected.

**Example:**

```scheme
kaappi> (42 1 2)
error[KP3005]: not a procedure

kaappi> ("hello" 1)
error[KP3005]: not a procedure
```

**Fix:** Make sure the first element of the call expression is a procedure.
Check for accidental extra parentheses: `((+ 1 2))` tries to call `3`.

**Reference:** [`KP3005`](diagnostics.md#kp3005-not-a-procedure) · `kaappi explain KP3005`

---

### Division by zero (KP3004)

**Message:** `error[KP3004]: division by zero`

**Cause:** An arithmetic operation attempted to divide by zero. This applies
to `/`, `quotient`, `remainder`, and `modulo`.

**Example:**

```scheme
kaappi> (/ 1 0)
error[KP3004]: division by zero

kaappi> (quotient 5 0)
error[KP3004]: division by zero
```

**Fix:** Guard division with a zero check:
`(if (zero? d) (error "divisor is zero") (/ n d))`.

**Reference:** [`KP3004`](diagnostics.md#kp3004-division-by-zero) · `kaappi explain KP3004`

---

### Index out of bounds (KP3006)

**Message:** `error[KP3006]: <procedure>: index <i> out of range for length <n>`

**Cause:** An index argument exceeded the valid range of a vector, string,
or bytevector. Valid indices are `0` to `(- (length obj) 1)`.

**Example:**

```scheme
kaappi> (vector-ref #(1 2 3) 5)
error[KP3006]: vector-ref: index 5 out of range for length 3

kaappi> (string-ref "abc" 10)
error[KP3006]: string-ref: index 10 out of range for length 3
```

**Fix:** Check the length before indexing:
`(when (< i (vector-length v)) (vector-ref v i))`.

**Reference:** [`KP3006`](diagnostics.md#kp3006-index-out-of-bounds) · `kaappi explain KP3006`

---

### Stack overflow (KP3008)

**Message:** `error[KP3008]: stack overflow`

**Cause:** The call stack exceeded 32768 frames or exhausted available
memory. The frame stack grows automatically (starting at 480 frames), so
this error only occurs with extremely deep non-tail recursion. Tail calls
do not consume stack frames.

**Example** -- `program.scm`:

```scheme
(define (forever n) (+ 1 (forever (+ n 1))))
(forever 0)
```

```console
$ kaappi program.scm
program.scm:2: error[KP3008]: stack overflow
    (forever 0)
  called from program.scm:2
```

**Fix:** Rewrite the recursion in tail position. The example above can be
converted to a tail-recursive form:

```scheme
(define (forever n) (forever (+ n 1)))
```

Kaappi optimizes tail calls, so tail-recursive functions run in constant
stack space. Non-tail-recursive code (e.g., `(cons x (f (cdr lst)))`)
works fine for thousands of elements.

**Reference:** [`KP3008`](diagnostics.md#kp3008-stack-overflow) · `kaappi explain KP3008`

---

### Undefined variable (KP3001)

**Message:** `error[KP3001]: undefined variable '<name>'`

**Cause:** A variable was referenced but no binding exists in the current
environment or the global scope. Usually a typo, a missing `import`, or
a `define` that has not run yet. When a similarly named binding exists,
the message suggests it. `set!` on an undefined variable reports the
variant `set!: unbound variable '<name>'`.

**Example:**

```scheme
kaappi> (dispaly "hi")
error[KP3001]: undefined variable 'dispaly'. Did you mean 'display'?

kaappi> (set! y 10)
error[KP3001]: set!: unbound variable 'y'
```

**Fix:** Define the variable before use: `(define x 42)`. For `set!`,
the variable must already be defined -- use `define` for the initial
binding. To catch undefined top-level variables before running, use
`kaappi check` (see the note under
[Compile-Time Errors](#compile-time-errors)).

**Reference:** [`KP3001`](diagnostics.md#kp3001-undefined-variable) · `kaappi explain KP3001`

---

### Out of memory (KP9002)

**Message:** `error[KP9002]: out of memory`

**Cause:** A memory allocation failed: the program (or a single data
structure within it) is too large for the available heap, and the
garbage collector could not free enough memory to satisfy the request.

**Example:**

```scheme
kaappi> (make-bytevector 100000000000000)
error[KP9002]: out of memory
```

Runaway recursion does not trigger this error -- it exhausts the call
stack first and reports [`KP3008`](#stack-overflow-kp3008).

**Fix:** Reduce live data by releasing references to objects you no longer
need. Restructure code to process data in a streaming fashion rather than
building large intermediate structures. If the program is legitimately
memory-bound, consider breaking the work into smaller batches.

**Reference:** [`KP9002`](diagnostics.md#kp9002-out-of-memory) · `kaappi explain KP9002`

---

## Library and Import Errors

### Library not found

**Message:** `error[KP2001]: library not found: (<name>)`

**Cause:** The library is not built-in and no `.sld` file was found in
the library search path. The library name is printed with dots joining
its parts: `(import (kaappi json))` reports `(kaappi.json)`.

**Example:**

```scheme
kaappi> (import (kaappi jsonx))
error[KP2001]: library not found: (kaappi.jsonx)
```

**Fix:** Check the library name for typos. For ecosystem libraries,
install with `thottam install kaappi-json`. For your own libraries, pass
the path with `--lib-path`:

```bash
kaappi --lib-path ./lib program.scm
```

Libraries installed via thottam are auto-discovered from `~/.kaappi/lib/`.

---

### Export not found

**Message:** `error[KP2001]: import only: identifier '<name>' not found in import set`

**Cause:** An `only` import filter named an identifier the library does
not export. Referencing a procedure a library does not export *without*
an `only` filter is not an import error -- it surfaces later as an
undefined variable ([`KP3001`](#undefined-variable-kp3001)).

**Example:**

```scheme
kaappi> (import (only (scheme base) frobnicate))
error[KP2001]: import only: identifier 'frobnicate' not found in import set
```

**Fix:** Check the library's `define-library` form for the `export`
clause. Use `,apropos` in the REPL to search for the procedure name.

---

## FFI Errors

### Shared library not found

**Message:** `error[KP3002]: ffi-open: dlopen(...): ... (no such file)`

**Cause:** The `.dylib` (macOS), `.so` (Linux), or `.dll` (Windows) file
was not found in the library search path. The message includes the system
loader's report of every path it tried.

**Example:**

```scheme
kaappi> (ffi-open "libmissing")
error[KP3002]: ffi-open: dlopen(/home/user/.kaappi/lib/libmissing.so, 0x0001): tried: '/home/user/.kaappi/lib/libmissing.so' (no such file), ...
```

**Fix:** Make sure the native library is built (`make` in the library's
directory) and either:

- Install via thottam (copies to `~/.kaappi/lib/`)
- Pass the path: `--lib-path /path/to/dir`
- Set `DYLD_LIBRARY_PATH` (macOS) or `LD_LIBRARY_PATH` (Linux)
- On Windows, place `.dll` files in `%USERPROFILE%\.kaappi\lib\` or add
  the directory to `PATH`

---

### Symbol not found

**Message:** `error[KP3002]: ffi-fn: dlsym(...): symbol not found`

**Cause:** The shared library was loaded but does not contain the
requested function symbol.

**Example:**

```scheme
kaappi> (ffi-fn lib "no_such_symbol" '(double) 'double)
error[KP3002]: ffi-fn: dlsym(0x36d56d670, no_such_symbol): symbol not found
```

**Fix:** Check the function name for typos. Verify the library was
compiled with the expected function (use `nm -gU library.dylib` on macOS
or `nm -D library.so` on Linux to list exported symbols).

---

## Common Pitfalls

Not errors, but behavior that often surprises newcomers.

- **`eq?` doesn't compare numbers reliably.** Use `=` for numeric
  equality, `eqv?` for numbers and characters, `equal?` for deep
  structural comparison. `eq?` tests pointer identity -- two equal numbers
  may not be `eq?`:

  ```scheme
  (eq? 42 42)           ;=> #t (fixnums are immediate)
  (eq? 3.14 3.14)       ;=> #f (flonums are heap-allocated)
  (= 3.14 3.14)         ;=> #t (use = for numbers)
  ```

- **`set!` changes the binding, not the value.** If you pass a variable to
  a function and `set!` it inside, the caller's variable is unaffected:

  ```scheme
  (define x 10)
  (define (change! v) (set! v 99))
  (change! x)
  x  ;=> 10  (unchanged -- set! modified the local binding v)
  ```

- **`string-set!` requires mutable strings.** String literals are
  immutable. Use `string-copy` to get a mutable copy first:

  ```scheme
  (define s (string-copy "hello"))
  (string-set! s 0 #\H)
  s  ;=> "Hello"
  ```

- **`map` and `for-each` stop at the shortest list.** When given multiple
  lists of different lengths, extra elements are silently ignored:

  ```scheme
  (map + '(1 2 3) '(10 20))  ;=> (11 22)
  ```

- **`begin` in a definition context defines, not sequences.** At the top
  level or in a library body, `begin` splices definitions rather than
  sequencing expressions:

  ```scheme
  (begin
    (define a 1)
    (define b 2))
  ;; a and b are now top-level definitions
  ```

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

**Fix on Windows:** Add the directory containing `kaappi.exe` to your
`PATH` via System Settings > Environment Variables, or in PowerShell:

```powershell
$env:PATH = "C:\path\to\kaappi;$env:PATH"
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

### Windows SmartScreen warning

**Message:** *"Windows protected your PC — Microsoft Defender SmartScreen
prevented an unrecognized app from starting."*

**Cause:** The Windows binaries are not code-signed. SmartScreen flags
unsigned executables downloaded from the internet.

**Fix:** Click **More info** → **Run anyway**. This is a one-time prompt
per binary — subsequent runs will not show the warning. Alternatively,
unblock the file from PowerShell before running it:

```powershell
Unblock-File .\kaappi-aarch64-windows.exe
```

Or right-click the `.exe` in File Explorer → Properties → check
**Unblock** → OK.

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
