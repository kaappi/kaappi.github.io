# Other Primitives

Miscellaneous procedures that do not fit into the main categories.

---

## Lazy Evaluation

### `promise?` { #promise-pred }
<!-- index: 1 | True if argument is a promise -->

**Syntax:** `(promise? obj)`

Returns `#t` if *obj* is a promise (created by `delay`, `delay-force`,
or `make-promise`), `#f` otherwise.

```scheme
kaappi> (promise? (delay 42))
;=> #t
kaappi> (promise? (make-promise 42))
;=> #t
kaappi> (promise? 42)
;=> #f
kaappi> (promise? (lambda () 42))
;=> #f
```

**See also:** [`make-promise`](#make-promise), [`force`](#force),
[`delay`](./syntax-forms.md#delay)

---

### `make-promise` { #make-promise }
<!-- index: 1 | Wrap a value as an already-forced promise -->

**Syntax:** `(make-promise value)`

Wraps an already-computed *value* as a forced promise. When `force` is
called on the result, it returns *value* immediately without any further
evaluation. This is useful when an API expects a promise but you already
have the value on hand.

```scheme
kaappi> (define p (make-promise 42))
kaappi> (promise? p)
;=> #t
kaappi> (force p)
;=> 42
kaappi> (force (make-promise '(a b c)))
;=> (a b c)
```

!!! note
    `make-promise` is idempotent: if *value* is already a promise, it is
    returned unchanged. `(make-promise (delay 42))` is the same as
    `(delay 42)`.

**See also:** [`force`](#force), [`delay`](./syntax-forms.md#delay)

---

### `force` { #force }
<!-- index: 1 | Force a promise, memoizing the result -->

**Syntax:** `(force promise)`

Evaluates a *promise* and memoizes the result. On the first call, the
thunk stored in the promise is invoked and its result is cached.
Subsequent calls to `force` on the same promise return the cached value
without re-evaluating the thunk. If the promise was created with
`make-promise`, the value is returned immediately.

```scheme
kaappi> (define p (delay (begin (display "computing\n") (* 6 7))))
kaappi> (force p)
computing
;=> 42
kaappi> (force p)
;=> 42
kaappi> (define count 0)
kaappi> (define lazy-count (delay (begin (set! count (+ count 1)) count)))
kaappi> (force lazy-count)
;=> 1
kaappi> (force lazy-count)
;=> 1
```

**See also:** [`make-promise`](#make-promise),
[`delay`](./syntax-forms.md#delay),
[`delay-force`](./syntax-forms.md#delay-force)

---

## Records (Internal Primitives)

### `%make-record-type` { #make-record-type }
<!-- index: 2 | Create a record type descriptor -->

**Syntax:** `(%make-record-type name field-count)`

Creates a record type descriptor with the given *name* (a symbol) and
*field-count* (a non-negative integer). This is the internal primitive
used by the `define-record-type` macro; users rarely call it directly.

```scheme
kaappi> (define point-type (%make-record-type 'point 2))
kaappi> point-type
;=> #<record-type point>
```

!!! note
    Prefer `define-record-type` for defining records. These `%`-prefixed
    primitives are implementation internals exposed for advanced use cases
    such as meta-programming.

**See also:** [`%make-record`](#make-record), [`%record?`](#record-pred),
[`define-record-type`](./syntax-forms.md#define-record-type)

---

### `%make-record` { #make-record }
<!-- index: 1+ | Construct a record instance -->

**Syntax:** `(%make-record type field-value ...)`

Constructs a new record instance of the given *type* (a record type
descriptor from `%make-record-type`). The number of *field-value*
arguments must match the field count of the type.

```scheme
kaappi> (define point-type (%make-record-type 'point 2))
kaappi> (define p (%make-record point-type 3 4))
kaappi> p
;=> #<record point>
kaappi> (%record-ref p 0)
;=> 3
kaappi> (%record-ref p 1)
;=> 4
```

**See also:** [`%make-record-type`](#make-record-type),
[`%record-ref`](#record-ref), [`%record-set!`](#record-set)

---

### `%record?` { #record-pred }
<!-- index: 2 | Check if value is instance of record type -->

**Syntax:** `(%record? obj type)`

Returns `#t` if *obj* is a record instance of the given *type*, `#f`
otherwise. The *type* must be a record type descriptor.

```scheme
kaappi> (define point-type (%make-record-type 'point 2))
kaappi> (define p (%make-record point-type 3 4))
kaappi> (%record? p point-type)
;=> #t
kaappi> (%record? 42 point-type)
;=> #f
kaappi> (define vec-type (%make-record-type 'vec 2))
kaappi> (%record? p vec-type)
;=> #f
```

**See also:** [`%make-record`](#make-record),
[`%make-record-type`](#make-record-type)

---

### `%record-ref` { #record-ref }
<!-- index: 2 | Access field by index -->

**Syntax:** `(%record-ref record index)`

Returns the value of the field at *index* (zero-based) in *record*.
It is an error if *index* is out of range.

```scheme
kaappi> (define point-type (%make-record-type 'point 2))
kaappi> (define p (%make-record point-type 10 20))
kaappi> (%record-ref p 0)
;=> 10
kaappi> (%record-ref p 1)
;=> 20
```

**See also:** [`%record-set!`](#record-set), [`%make-record`](#make-record)

---

### `%record-set!` { #record-set }
<!-- index: 3 | Mutate field by index -->

**Syntax:** `(%record-set! record index value)`

Sets the field at *index* (zero-based) in *record* to *value*.
It is an error if *index* is out of range.

```scheme
kaappi> (define point-type (%make-record-type 'point 2))
kaappi> (define p (%make-record point-type 0 0))
kaappi> (%record-set! p 0 42)
kaappi> (%record-set! p 1 99)
kaappi> (%record-ref p 0)
;=> 42
kaappi> (%record-ref p 1)
;=> 99
```

**See also:** [`%record-ref`](#record-ref), [`%make-record`](#make-record)

---

## Random Numbers (SRFI-27)

### `random-integer` { #random-integer }
<!-- index: 1 | Random integer in [0, n) -->

**Syntax:** `(random-integer n)`

Returns a uniformly distributed random exact integer in the range
[0, *n*), where *n* must be a positive exact integer. The distribution
is uniform over the range.

```scheme
kaappi> (random-integer 6)
;=> 3
kaappi> (random-integer 100)
;=> 57
kaappi> (map (lambda (_) (random-integer 2)) '(1 2 3 4 5))
;=> (0 1 1 0 1)
```

**See also:** [`random-real`](#random-real)

---

### `random-real` { #random-real }
<!-- index: 0 | Random real in [0, 1) -->

**Syntax:** `(random-real)`

Returns a uniformly distributed random inexact real number in the range
[0.0, 1.0). The result is always non-negative and strictly less than 1.0.

```scheme
kaappi> (random-real)
;=> 0.7312456789
kaappi> (random-real)
;=> 0.1284930156
kaappi> (< (random-real) 1.0)
;=> #t
```

**See also:** [`random-integer`](#random-integer)

---
