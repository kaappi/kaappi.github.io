# Diagnostic reference

Every diagnostic Kaappi prints carries a stable `KP` code. This page documents
every registered code: what it means, a minimal example that triggers it, and
how to fix it. The same content is available offline from the binary itself with
[`kaappi explain <code>`](../guide/debugging.md) (e.g. `kaappi explain KP3001`).

!!! note "Generated page"

    This page is generated from the compiler's diagnostic registry by
    `tools/gen_diagnostics_reference.py` in the core repo. Do not edit it by
    hand — regenerate it after a release instead.


## Read / lexical (`KP1xxx`)

### `KP1001` — unexpected-eof

_unexpected end of input_

The reader reached the end of the input while a datum was still open —
most often an unclosed '(' or an unterminated string or block comment.
Check that every '(' has a matching ')' and every '"' is closed.

**Example**

```scheme
(+ 1 2
```

### `KP1002` — unexpected-char

_unexpected character_

The reader encountered a character that cannot begin or continue a datum
at this position. A common cause is a malformed '#'-syntax such as an
unknown '#\name' character literal or a stray '#'.

**Example**

```scheme
#z
```

### `KP1003` — unexpected-right-paren

_unexpected ')'_

A ')' appeared with no matching '(' still open. Usually there is one
closing parenthesis too many, or an earlier '(' was already closed.

**Example**

```scheme
(cons 1 2))
```

### `KP1004` — invalid-number

_invalid number literal_

A token that looked like a number could not be parsed as one — for
example a malformed radix prefix (#x, #o, #b, #e, #i), a bad exponent,
or a rational with a zero denominator.

**Example**

```scheme
1/0
```

### `KP1005` — invalid-character-name

_invalid character name_

A '#\...' character literal named something the reader does not know.
Valid forms are a single character (#\a), a named character
(#\newline, #\space, #\tab, ...), or a hex escape (#\x41).

**Example**

```scheme
#\foo
```

### `KP1006` — unterminated-string

_unterminated string literal_

A string opened with '"' was never closed before end of input. Add the
closing '"', or escape any literal '"' inside the string as '\"'.

**Example**

```scheme
(display "abc
```

### `KP1007` — invalid-escape

_invalid escape sequence_

A '\' inside a string was followed by a character that is not a valid
escape. R7RS allows \a \b \t \n \r \" \\ \x<hex>; and a line-continuation
'\' followed by whitespace and a newline.

**Example**

```scheme
(display "\q")
```

### `KP1008` — dot-outside-list

_'.' outside of a list_

A '.' (dotted-pair marker) appeared where it is not allowed. It is legal
only before the final element inside a list, as in (a . b) or (a b . c).

**Example**

```scheme
(. 5)
```

### `KP1009` — nesting-too-deep

_nesting too deep_

The datum nests more deeply than the reader's fixed limit. This usually
means unbalanced parentheses producing runaway nesting rather than a
genuinely deep literal.

**Example**

```scheme
((((( ...nested past the reader's depth limit... )))))
```

### `KP1010` — token-too-long

_token too long_

A single token (identifier, number, or string) exceeded the reader's
maximum token length. Split the input or shorten the token.

**Example**

```scheme
aaaaaaaa...  ; a single token longer than the reader's limit
```


## Expand / compile (`KP2xxx`)

### `KP2001` — invalid-syntax

_invalid syntax_

A special form was written incorrectly — for example an 'if' with no
test, a 'define' with no body, or a 'lambda' whose parameter list is not
a proper list of identifiers. Check the form against its expected shape.

**Example**

```scheme
(if)
```

### `KP2002` — syntax-error

_syntax error_

A macro rejected its use, either via the R7RS 'syntax-error' keyword or
because no 'syntax-rules' pattern matched the form. The accompanying
message describes what the macro expected.

**Example**

```scheme
(syntax-error "must be a pair" 1)
```

### `KP2003` — macro-expansion-limit

_macro expansion limit exceeded_

Macro expansion did not terminate within the implementation's step
limit, which almost always indicates a macro that expands into itself
without a base case.

**Example**

```scheme
(define-syntax loop (syntax-rules () ((_ x) (loop x))))
(loop 1)
```


## Runtime (`KP3xxx`)

### `KP3000` — uncaught-exception

_uncaught exception_

An object was raised (via 'raise', 'error', 'assert', or a library) and
reached the top level without being caught. Wrap the code in 'guard' or
'with-exception-handler' to handle it. The message shown is the payload
of the raised object.

**Example**

```scheme
(raise 'boom)
```

### `KP3001` — undefined-variable

_undefined variable_

A variable was referenced that has no binding in scope. Check for a typo
(Kaappi suggests the nearest defined name), a missing 'import', or a
'define' that has not run yet because it appears after the reference.

**Example**

```scheme
(display undefined-name)
```

### `KP3002` — type-error

_type error_

A procedure was applied to an argument of the wrong type — for example
'car' on a non-pair or '+' on a non-number. The message names the
procedure, the type it expected, and the value it got.

**Example**

```scheme
(car 5)
```

### `KP3003` — arity-mismatch

_wrong number of arguments_

A procedure was called with a number of arguments its parameter list
cannot accept. The message shows how many arguments were expected versus
how many were supplied.

**Example**

```scheme
(cons 1)
```

### `KP3004` — division-by-zero

_division by zero_

An exact division, 'modulo', 'remainder', or 'quotient' had a zero
divisor. Guard the divisor, or use inexact arithmetic where the result
is a floating-point infinity or NaN instead of an error.

**Example**

```scheme
(/ 1 0)
```

### `KP3005` — not-a-procedure

_attempt to call a non-procedure_

The operator position of a call evaluated to something that is not a
procedure, as in (5 6). Check for an extra pair of parentheses or a name
that is bound to a value rather than a procedure.

**Example**

```scheme
(5 6)
```

### `KP3006` — index-out-of-bounds

_index out of bounds_

An index passed to a sequence operation (vector-ref, string-ref,
list-ref, bytevector-u8-ref, ...) was negative or not less than the
length of the sequence.

**Example**

```scheme
(vector-ref (vector 1 2) 5)
```

### `KP3007` — invalid-argument

_invalid argument_

An argument was of an acceptable type but outside the range or shape the
procedure allows — for example a start index greater than an end index,
or a value a procedure explicitly rejects.

**Example**

```scheme
(import (srfi 13))
(string-join '() "," 'strict-infix)
```

### `KP3008` — stack-overflow

_stack overflow_

The call stack grew past its limit, almost always from unbounded
non-tail recursion. Rewrite the recursion to be in tail position, or use
an explicit accumulator or loop.

**Example**

```scheme
(define (sum n) (+ n (sum (+ n 1))))
(sum 0)
```

### `KP3009` — execution-timeout

_execution timed out_

Execution exceeded a configured time budget and was interrupted. This is
a sandbox / watchdog limit, not a fault in the program's logic per se.

**Example**

```scheme
(let loop () (loop))   ; run with --timeout 500
```


## Static analysis (`KP4xxx`)

### `KP4001` — unknown-toplevel-variable

_unknown variable at top level_

`kaappi check` found a free reference to a top-level variable that is
neither a built-in, an imported binding, nor defined anywhere in the
file. This is a WARNING, never an error: R7RS permits top-level forward
references (a variable may be defined by a later top-level `define`, or
a mutual recursion), so rejecting the program would deviate from the
standard. Check for a typo, a missing `import`, or a missing `define`.

**Example**

```scheme
(display undefined-name)
```

### `KP4002` — primitive-arity-mismatch

_wrong number of arguments to a built-in procedure_

`kaappi check` found a direct call to a known built-in procedure with a
number of arguments the procedure cannot accept. The argument count is a
static fact for every built-in, so this call is guaranteed to raise an
arity error (KP3003) at run time. Only direct, unshadowed calls to
built-ins are checked — a call through a variable, or to a name you have
redefined, is left alone.

**Example**

```scheme
(car 1 2)
```

### `KP4003` — primitive-type-mismatch

_wrong type of literal argument to a built-in procedure_

`kaappi check` found a literal argument whose type a known built-in
cannot accept in that position — for example a number where a pair is
required (`(car 5)`) or a string where a vector is required
(`(vector-ref "s" 0)`). Only self-evaluating and quoted literals are
checked: there is no type inference and no way to annotate types, so a
value computed at run time is never flagged. Such a call is guaranteed
to raise a type error (KP3002) at run time.

**Example**

```scheme
(car 5)
```


## Internal / resource (`KP9xxx`)

### `KP9000` — uncategorized

_error_

A diagnostic that has not yet been assigned a specific code. Seeing this
code is itself a gap worth reporting: the underlying condition should get
its own registry entry.

**Example**

```scheme
(no specific trigger — a catch-all for uncoded conditions)
```

### `KP9001` — internal-error

_internal compiler error_

Kaappi hit a condition that should not be reachable — a corrupt bytecode
stream or an internal limit. This indicates a bug in Kaappi itself;
please report it with the program that triggered it.

**Example**

```scheme
(no trigger from correct input — signals a bug in Kaappi)
```

### `KP9002` — out-of-memory

_out of memory_

Memory allocation failed. The program (or a single datum, program text,
or data structure within it) is too large for the available heap.

**Example**

```scheme
(make-bytevector 100000000000000)
```
