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

**Cause:** The call stack exceeded 256 frames. This typically happens with
non-tail-recursive functions that recurse deeply. Tail calls do not consume
stack frames, so properly tail-recursive code will not trigger this error.

**Example:**
```scheme
kaappi> (define (forever n) (+ 1 (forever (+ n 1))))
kaappi> (forever 0)
;; runtime error: error.StackOverflow
```

**Fix:** Rewrite the recursion in tail position. The example above can be
converted to a tail-recursive form:

```scheme
(define (forever n) (forever (+ n 1)))
```

Kaappi optimizes tail calls, so tail-recursive functions run in constant
stack space.

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
