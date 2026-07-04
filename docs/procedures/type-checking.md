# Type Checking and Equivalence

These procedures test the type of a value or compare values for equality.
Available from `(scheme base)`.

---

## Equivalence Predicates

### `eq?` { #eq }
<!-- index: 2 | Pointer identity -->

**Syntax:** `(eq? obj1 obj2)`

Tests whether *obj1* and *obj2* are the same object in memory (pointer
identity). This is the fastest comparison but only reliable for symbols,
booleans, the empty list, and pairs/vectors whose identity (not content)
you want to test. Its behavior on numbers, characters, and strings is
implementation-dependent -- use `eqv?` or `equal?` when comparing values.

```scheme
kaappi> (eq? 'a 'a)
;=> #t
kaappi> (eq? '() '())
;=> #t
kaappi> (eq? #t #t)
;=> #t
kaappi> (define x (list 1 2))
kaappi> (eq? x x)
;=> #t
kaappi> (eq? (list 1 2) (list 1 2))
;=> #f
```

**See also:** [`eqv?`](#eqv), [`equal?`](#equal)

---

### `eqv?` { #eqv }
<!-- index: 2 | Value equivalence (numbers, chars, booleans) -->

**Syntax:** `(eqv? obj1 obj2)`

Extends `eq?` with reliable value comparisons for numbers and characters.
Two numbers are `eqv?` if they are both exact or both inexact, have the
same value, and (for complex numbers) have `eqv?` real and imaginary
parts. Two characters are `eqv?` if they represent the same Unicode
codepoint. For all other types, `eqv?` behaves like `eq?`.

```scheme
kaappi> (eqv? 42 42)
;=> #t
kaappi> (eqv? 42 42.0)
;=> #f
kaappi> (eqv? #\a #\a)
;=> #t
kaappi> (eqv? "abc" "abc")
;=> #f
kaappi> (eqv? '() '())
;=> #t
```

**See also:** [`eq?`](#eq), [`equal?`](#equal)

---

### `equal?` { #equal }
<!-- index: 2 | Deep structural equality -->

**Syntax:** `(equal? obj1 obj2)`

Performs deep structural comparison. Two pairs are `equal?` if their
`car` and `cdr` fields are recursively `equal?`. Two vectors are `equal?`
if they have the same length and all corresponding elements are `equal?`.
Strings and bytevectors are compared element-by-element. For numbers and
characters, `equal?` delegates to `eqv?`. This is the most general
equality predicate but also the slowest for large structures.

```scheme
kaappi> (equal? '(1 2 3) '(1 2 3))
;=> #t
kaappi> (equal? "hello" "hello")
;=> #t
kaappi> (equal? '#(1 2) '#(1 2))
;=> #t
kaappi> (equal? 42 42.0)
;=> #f
kaappi> (equal? '(1 (2 3)) '(1 (2 3)))
;=> #t
```

**See also:** [`eq?`](#eq), [`eqv?`](#eqv)

---

## Boolean Operations

### `not` { #not }
<!-- index: 1 | Boolean negation -->

**Syntax:** `(not obj)`

Returns `#t` if *obj* is `#f`, and returns `#f` for every other value.
In Scheme, only `#f` is considered false -- all other values, including
`0`, `""`, and `'()`, are true.

```scheme
kaappi> (not #f)
;=> #t
kaappi> (not #t)
;=> #f
kaappi> (not 0)
;=> #f
kaappi> (not '())
;=> #f
kaappi> (not "")
;=> #f
```

**See also:** [`boolean?`](#boolean)

---

### `boolean=?` { #boolean-equal }
<!-- index: 2+ | True if all arguments are the same boolean -->

**Syntax:** `(boolean=? b1 b2 b3 ...)`

Returns `#t` if all arguments are booleans and have the same truth value.
It is an error if any argument is not a boolean. This is stricter than
comparing with `eqv?` because it enforces that every argument is a
boolean rather than silently accepting non-boolean values.

```scheme
kaappi> (boolean=? #t #t)
;=> #t
kaappi> (boolean=? #f #f)
;=> #t
kaappi> (boolean=? #t #f)
;=> #f
kaappi> (boolean=? #t #t #t)
;=> #t
```

**See also:** [`not`](#not), [`boolean?`](#boolean)

---

### `symbol=?` { #symbol-equal }
<!-- index: 2+ | True if all arguments are the same symbol -->

**Syntax:** `(symbol=? s1 s2 s3 ...)`

Returns `#t` if all arguments are symbols and are the same symbol. It is
an error if any argument is not a symbol. Because symbols are interned,
this is equivalent to `eq?` on symbols but includes the type check.

```scheme
kaappi> (symbol=? 'foo 'foo)
;=> #t
kaappi> (symbol=? 'foo 'bar)
;=> #f
kaappi> (symbol=? 'a 'a 'a)
;=> #t
```

**See also:** [`symbol?`](#symbol), [`eq?`](#eq)

---

## Type Predicates

### `pair?` { #pair }
<!-- index: 1 | True if argument is a pair -->

**Syntax:** `(pair? obj)`

Returns `#t` if *obj* is a pair (created by `cons` or a list literal),
and `#f` otherwise. Note that the empty list is *not* a pair.

```scheme
kaappi> (pair? '(1 2))
;=> #t
kaappi> (pair? (cons 1 2))
;=> #t
kaappi> (pair? '())
;=> #f
kaappi> (pair? 42)
;=> #f
```

**See also:** [`null?`](#null), [`list?`](#list),
[Pairs and Lists](./pairs-and-lists.md)

---

### `null?` { #null }
<!-- index: 1 | True if argument is the empty list -->

**Syntax:** `(null? obj)`

Returns `#t` if *obj* is the empty list `'()`, and `#f` otherwise. This
is the standard way to test for the end of a list when recursing down its
spine.

```scheme
kaappi> (null? '())
;=> #t
kaappi> (null? '(1))
;=> #f
kaappi> (null? #f)
;=> #f
kaappi> (null? 0)
;=> #f
```

**See also:** [`pair?`](#pair), [`list?`](#list),
[Pairs and Lists](./pairs-and-lists.md)

---

### `list?` { #list }
<!-- index: 1 | True if argument is a proper list -->

**Syntax:** `(list? obj)`

Returns `#t` if *obj* is a proper list -- either the empty list or a chain
of pairs terminated by the empty list. Dotted pairs and circular
structures return `#f`. Kaappi uses the tortoise-and-hare algorithm to
detect cycles without unbounded traversal.

```scheme
kaappi> (list? '(1 2 3))
;=> #t
kaappi> (list? '())
;=> #t
kaappi> (list? (cons 1 2))
;=> #f
kaappi> (list? 42)
;=> #f
```

**See also:** [`pair?`](#pair), [`null?`](#null),
[Pairs and Lists](./pairs-and-lists.md)

---

### `number?` { #number }
<!-- index: 1 | True if argument is a number -->

**Syntax:** `(number? obj)`

Returns `#t` if *obj* is a number of any type in the numeric tower:
fixnum, bignum, exact rational, flonum, or complex. This is the broadest
numeric predicate.

```scheme
kaappi> (number? 42)
;=> #t
kaappi> (number? 3.14)
;=> #t
kaappi> (number? 2/3)
;=> #t
kaappi> (number? 1+2i)
;=> #t
kaappi> (number? "42")
;=> #f
```

**See also:** [`integer?`](#integer), [`real?`](#real), [`complex?`](#complex),
[Numbers and Arithmetic](./numbers.md)

---

### `integer?` { #integer }
<!-- index: 1 | True if argument is an integer -->

**Syntax:** `(integer? obj)`

Returns `#t` if *obj* is an integer. This includes exact integers
(fixnums and bignums) as well as flonums whose value is an integer (e.g.,
`3.0`). Rationals whose denominator is 1 also satisfy this predicate.

```scheme
kaappi> (integer? 42)
;=> #t
kaappi> (integer? 3.0)
;=> #t
kaappi> (integer? 3.5)
;=> #f
kaappi> (integer? 2/3)
;=> #f
kaappi> (integer? "42")
;=> #f
```

**See also:** [`number?`](#number), [`real?`](#real),
[Numbers and Arithmetic](./numbers.md)

---

### `real?` { #real }
<!-- index: 1 | True if argument is a real number -->

**Syntax:** `(real? obj)`

Returns `#t` if *obj* is a real number -- any number that is not complex.
This includes fixnums, bignums, exact rationals, and flonums (even
`+inf.0`, `-inf.0`, and `+nan.0`).

```scheme
kaappi> (real? 42)
;=> #t
kaappi> (real? 3.14)
;=> #t
kaappi> (real? 2/3)
;=> #t
kaappi> (real? 1+2i)
;=> #f
kaappi> (real? +inf.0)
;=> #t
```

**See also:** [`number?`](#number), [`complex?`](#complex), [`rational?`](#rational),
[Numbers and Arithmetic](./numbers.md)

---

### `complex?` { #complex }
<!-- index: 1 | True if argument is a complex number -->

**Syntax:** `(complex? obj)`

Returns `#t` if *obj* is a complex number. In R7RS, every real number is
also a complex number (with zero imaginary part), so `complex?` returns
`#t` for all numbers. This predicate is therefore equivalent to
`number?`.

```scheme
kaappi> (complex? 1+2i)
;=> #t
kaappi> (complex? 42)
;=> #t
kaappi> (complex? 3.14)
;=> #t
kaappi> (complex? "hello")
;=> #f
```

**See also:** [`number?`](#number), [`real?`](#real),
[Numbers and Arithmetic](./numbers.md)

---

### `rational?` { #rational }
<!-- index: 1 | True if argument is rational -->

**Syntax:** `(rational? obj)`

Returns `#t` if *obj* is a rational number. This includes all exact
integers, exact rationals, and finite flonums (since every finite float
can be represented as a ratio of integers). Infinite and NaN flonums
return `#f`.

```scheme
kaappi> (rational? 42)
;=> #t
kaappi> (rational? 2/3)
;=> #t
kaappi> (rational? 3.14)
;=> #t
kaappi> (rational? +inf.0)
;=> #f
kaappi> (rational? +nan.0)
;=> #f
```

**See also:** [`number?`](#number), [`real?`](#real), [`integer?`](#integer),
[Numbers and Arithmetic](./numbers.md)

---

### `symbol?` { #symbol }
<!-- index: 1 | True if argument is a symbol -->

**Syntax:** `(symbol? obj)`

Returns `#t` if *obj* is a symbol, and `#f` otherwise. Symbols are
interned identifiers -- two symbols with the same name are always `eq?`.

```scheme
kaappi> (symbol? 'hello)
;=> #t
kaappi> (symbol? (string->symbol "hello"))
;=> #t
kaappi> (symbol? "hello")
;=> #f
kaappi> (symbol? 42)
;=> #f
```

**See also:** [`symbol=?`](#symbol-equal), [`eq?`](#eq)

---

### `string?` { #string }
<!-- index: 1 | True if argument is a string -->

**Syntax:** `(string? obj)`

Returns `#t` if *obj* is a string, and `#f` otherwise. Strings in Kaappi
are sequences of Unicode characters, internally encoded as UTF-8.

```scheme
kaappi> (string? "hello")
;=> #t
kaappi> (string? "")
;=> #t
kaappi> (string? 'hello)
;=> #f
kaappi> (string? #\a)
;=> #f
```

**See also:** [Strings](./strings.md)

---

### `boolean?` { #boolean }
<!-- index: 1 | True if argument is a boolean -->

**Syntax:** `(boolean? obj)`

Returns `#t` if *obj* is a boolean (`#t` or `#f`), and `#f` otherwise.

```scheme
kaappi> (boolean? #t)
;=> #t
kaappi> (boolean? #f)
;=> #t
kaappi> (boolean? 0)
;=> #f
kaappi> (boolean? '())
;=> #f
```

**See also:** [`not`](#not), [`boolean=?`](#boolean-equal)

---

### `char?` { #char }
<!-- index: 1 | True if argument is a character -->

**Syntax:** `(char? obj)`

Returns `#t` if *obj* is a character, and `#f` otherwise. Characters in
Kaappi represent individual Unicode codepoints.

```scheme
kaappi> (char? #\a)
;=> #t
kaappi> (char? #\space)
;=> #t
kaappi> (char? "a")
;=> #f
kaappi> (char? 65)
;=> #f
```

**See also:** [`string?`](#string)

---

### `procedure?` { #procedure }
<!-- index: 1 | True if argument is a procedure -->

**Syntax:** `(procedure? obj)`

Returns `#t` if *obj* is a procedure (a lambda, a built-in primitive, or
a continuation), and `#f` otherwise.

```scheme
kaappi> (procedure? car)
;=> #t
kaappi> (procedure? (lambda (x) x))
;=> #t
kaappi> (procedure? +)
;=> #t
kaappi> (procedure? 42)
;=> #f
kaappi> (procedure? '(1 2))
;=> #f
```

**See also:** [`eq?`](#eq)

---

### `vector?` { #vector }
<!-- index: 1 | True if argument is a vector -->

**Syntax:** `(vector? obj)`

Returns `#t` if *obj* is a vector, and `#f` otherwise. Vectors are
fixed-length, indexed sequences of arbitrary Scheme values.

```scheme
kaappi> (vector? '#(1 2 3))
;=> #t
kaappi> (vector? (vector 'a 'b))
;=> #t
kaappi> (vector? '(1 2 3))
;=> #f
kaappi> (vector? "abc")
;=> #f
```

**See also:** [Vectors](./vectors.md)

---

### `bytevector?` { #bytevector }
<!-- index: 1 | True if argument is a bytevector -->

**Syntax:** `(bytevector? obj)`

Returns `#t` if *obj* is a bytevector, and `#f` otherwise. Bytevectors
are fixed-length sequences of exact integers in the range 0 to 255.

```scheme
kaappi> (bytevector? #u8(1 2 3))
;=> #t
kaappi> (bytevector? (make-bytevector 5))
;=> #t
kaappi> (bytevector? '#(1 2 3))
;=> #f
kaappi> (bytevector? "abc")
;=> #f
```

**See also:** [Bytevectors](./bytevectors.md)

---

### `port?` { #port }
<!-- index: 1 | True if argument is a port -->

**Syntax:** `(port? obj)`

Returns `#t` if *obj* is a port (input port, output port, or
input/output port), and `#f` otherwise.

```scheme
kaappi> (port? (current-input-port))
;=> #t
kaappi> (port? (current-output-port))
;=> #t
kaappi> (port? "not-a-port")
;=> #f
```

**See also:** [`input-port?`](./ports-and-io.md#input-port),
[`output-port?`](./ports-and-io.md#output-port)

---

### `hash-table?` { #hash-table }
<!-- index: 1 | True if argument is a hash table -->

**Syntax:** `(hash-table? obj)`

Returns `#t` if *obj* is a hash table, and `#f` otherwise. Hash tables
in Kaappi are available via SRFI-69 and SRFI-125.

```scheme
kaappi> (hash-table? (make-hash-table))
;=> #t
kaappi> (hash-table? '((a . 1) (b . 2)))
;=> #f
kaappi> (hash-table? '#(1 2))
;=> #f
```

---

### `promise?` { #promise }
<!-- index: 1 | True if argument is a promise -->

**Syntax:** `(promise? obj)`

Returns `#t` if *obj* is a promise created by `delay` or
`delay-force` (also called `make-promise`), and `#f` otherwise.
Promises represent deferred computations that are forced with `force`.

```scheme
kaappi> (promise? (delay 42))
;=> #t
kaappi> (promise? (make-promise 42))
;=> #t
kaappi> (promise? 42)
;=> #f
```

**See also:** [`force`](./other.md#force),
[`delay`](./syntax-forms.md#delay)

---

### `error-object?` { #error-object }
<!-- index: 1 | True if argument is an error object -->

**Syntax:** `(error-object? obj)`

Returns `#t` if *obj* is an error object created by `error` or
`error-object`, and `#f` otherwise. Error objects carry a message, an
irritant list, and optionally a type tag. They are typically caught with
`guard` or `with-exception-handler`.

```scheme
kaappi> (guard (e (#t (error-object? e)))
          (error "boom" 'details))
;=> #t
kaappi> (error-object? "not an error")
;=> #f
kaappi> (error-object? 42)
;=> #f
```

**See also:** [`error`](./control-flow.md#error),
[`error-object-message`](./control-flow.md#error-object-message),
[Control Flow](./control-flow.md#error-object-pred)
