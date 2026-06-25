# Glossary

Terms used throughout the Kaappi documentation.

---

### Alist { #alist }

**Association list.** A list of pairs where each pair maps a key to a value.
Used throughout Kaappi's ecosystem for JSON objects, HTTP headers, query
parameters, and configuration.

```scheme
'(("name" . "Alice") ("age" . 30))
```

Look up values with `assoc`:

```scheme
(cdr (assoc "name" '(("name" . "Alice"))))  ;=> "Alice"
```

### Bignum { #bignum }

An arbitrary-precision integer. When a [fixnum](#fixnum) operation would
overflow 63 bits, the result is automatically promoted to a bignum. Bignums
can represent any integer, limited only by available memory.

```scheme
(expt 2 100)  ;=> 1267650600228229401496703205376
```

### Bytecode { #bytecode }

The intermediate representation produced by the [compiler](#compiler). Kaappi
uses a register-based bytecode format. Bytecode is executed by the
[VM](#vm) or compiled to native code by the [JIT](#jit).

### Call/cc { #callcc }

Short for `call-with-current-continuation`. Captures the current
[continuation](#continuation) and passes it to a procedure. The most
powerful control flow primitive in Scheme — enables coroutines, exceptions,
backtracking, and more. See also [call/ec](#callec).

### Call/ec { #callec }

Short for `call-with-escape-continuation`. Like [call/cc](#callcc) but the
continuation can only be used during the dynamic extent of the call. Much
cheaper than call/cc because it doesn't copy the stack. Use call/ec for
non-local exits (early return, loop break).

```scheme
(call/ec (lambda (exit)
  (for-each (lambda (x) (when (< x 0) (exit x)))
            '(1 2 -3 4))))
;=> -3
```

### Compiler { #compiler }

The stage that transforms expanded S-expressions into [bytecode](#bytecode).
Kaappi's compiler handles lexical scoping, closure capture, tail call
optimization, and pattern matching for syntax forms.

### Continuation { #continuation }

The "rest of the computation" at any point in a program. When you call
[call/cc](#callcc), the current continuation is packaged as a procedure
that, when invoked, resumes execution from that point. Continuations are
a fundamental concept in Scheme that enable advanced control flow.

### Expander { #expander }

The macro expansion stage. Transforms `syntax-rules` macros into core forms
before compilation. Kaappi uses hygienic macro expansion, which prevents
accidental variable capture.

### Fiber { #fiber }

A lightweight, cooperatively scheduled green thread. Fibers run within a
single OS thread and communicate via [channels](#channel). Much cheaper to
create than OS threads.

```scheme
(import (kaappi fibers))
(define ch (make-channel))
(spawn (lambda () (channel-send ch "hello")))
(channel-receive ch)  ;=> "hello"
```

### Fixnum { #fixnum }

A 63-bit signed integer stored directly in a [tagged value](#tagged-value)
word (no heap allocation). Fixnums are the fastest numeric type. Arithmetic
that overflows is automatically promoted to a [bignum](#bignum).

### Flonum { #flonum }

An IEEE 754 double-precision floating-point number. Since v0.6.0, flonums
are packed directly into the value word via [NaN-boxing](#nan-boxing),
eliminating heap allocation.

```scheme
3.14159        ;; flonum
(inexact 1/3)  ;=> 0.3333333333333333
```

### GC { #gc }

**Garbage collector.** Kaappi uses a mark-and-sweep collector that traces
live objects from roots (stack, globals) and frees unreachable memory.

### Hygienic macros { #hygienic-macros }

Macro expansion that preserves lexical scoping — variables introduced by a
macro don't accidentally capture or shadow user variables. Kaappi implements
this via `syntax-rules` as specified in R7RS.

### JIT { #jit }

**Just-in-time compiler.** Compiles hot [bytecode](#bytecode) functions to
native machine code (ARM64 or x86_64) after 100 calls. JIT-compiled
functions inline fixnum arithmetic, comparisons, `car`/`cdr`, `cons`, and
function calls.

### NaN-boxing { #nan-boxing }

A value representation technique that packs [flonums](#flonum) directly
into the 64-bit value word by exploiting the structure of IEEE 754 NaN
values. Eliminates heap allocation for floating-point numbers.

### Pair { #pair }

The fundamental compound data type in Scheme. A pair holds two values: the
`car` (first element) and the `cdr` (second element). Lists are built from
chains of pairs terminated by the empty list `'()`.

```scheme
(cons 1 2)       ;=> (1 . 2)     — a dotted pair
(cons 1 '(2 3))  ;=> (1 2 3)     — a proper list
```

### Port { #port }

An abstraction for I/O streams. Input ports read data, output ports write
data. Files, strings, stdin, and stdout are all accessed through ports.

```scheme
(call-with-input-file "data.txt" read-line)
```

### Proper list { #proper-list }

A chain of [pairs](#pair) where the final `cdr` is the empty list `'()`.
Most list operations require proper lists.

```scheme
'(1 2 3)         ;; proper list: (1 . (2 . (3 . ())))
'(1 2 . 3)       ;; improper list (dotted pair at the end)
```

### R7RS { #r7rs }

**Revised^7 Report on the Algorithmic Language Scheme.** The language
standard that Kaappi implements. "R7RS-small" is the core language; there
is also an R7RS-large effort (which Kaappi does not target).

### Reader { #reader }

The stage that converts source text into S-expressions (Scheme data
structures). Handles parentheses, quoting, numbers, strings, characters,
booleans, vectors, and bytevectors.

### REPL { #repl }

**Read-Eval-Print Loop.** The interactive prompt (`kaappi>`). Type
expressions, see results immediately. Kaappi's REPL supports line editing,
history, tab completion, and [comma commands](guide/repl.md).

### SRFI { #srfi }

**Scheme Requests for Implementation.** Community-authored library
specifications with reference implementations. Kaappi supports 72 SRFIs
(8 built-in, 64 portable). See [SRFI Support](guide/srfi-support.md) for
the full list.

Example: SRFI-1 provides extended list operations (`fold`, `filter`,
`partition`, etc.).

### Syntax-rules { #syntax-rules }

The R7RS pattern-based macro system. Defines macros by specifying patterns
and their expansions. [Hygienic](#hygienic-macros) by design.

```scheme
(define-syntax when
  (syntax-rules ()
    ((when test body ...)
     (if test (begin body ...)))))
```

### Tagged value { #tagged-value }

Kaappi's internal representation of Scheme values. Each value is a 64-bit
word with tag bits that encode the type ([fixnum](#fixnum), pointer,
immediate boolean/char/nil, or [NaN-boxed](#nan-boxing) flonum). This
allows type checking without dereferencing a pointer.

### Tail call { #tail-call }

A function call in tail position — the last thing a function does before
returning. Kaappi optimizes tail calls to reuse the current stack frame,
enabling unbounded recursion without stack overflow.

```scheme
(define (loop n) (loop (+ n 1)))  ;; runs forever, O(1) stack
```

### Thottam { #thottam }

Kaappi's package manager. Installs, updates, and removes ecosystem
libraries. Named after the Tamil word for "garden." See
[thottam docs](ecosystem/thottam.md).

### Thunk { #thunk }

A zero-argument procedure. Used to delay evaluation:

```scheme
(define my-thunk (lambda () (+ 1 2)))
(my-thunk)  ;=> 3
```

Common in error testing (`test-error "name" thunk`), lazy evaluation, and
`dynamic-wind`.

### VM { #vm }

**Virtual machine.** Kaappi's register-based bytecode interpreter. Executes
[bytecode](#bytecode) instructions, manages the call stack, and coordinates
with the [GC](#gc). Hot functions are compiled to native code by the
[JIT](#jit).

### Channel { #channel }

A communication primitive for [fibers](#fiber). Channels provide
synchronized message passing between green threads.

```scheme
(define ch (make-channel))
(spawn (lambda () (channel-send ch 42)))
(channel-receive ch)  ;=> 42
```
