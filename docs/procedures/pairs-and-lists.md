# Pairs and Lists

Pairs are the fundamental building block of Scheme data structures. A list is
either the empty list `'()` or a pair whose `cdr` is a list. These procedures
are available from `(scheme base)`.

---

## Core Pairs

### `cons` { #cons }

**Syntax:** `(cons obj1 obj2)`

Returns a newly allocated mutable pair whose `car` is *obj1* and whose `cdr` is
*obj2*. If *obj2* is a proper list the result is a proper list; otherwise the
result is a dotted pair.

```scheme
kaappi> (cons 1 2)
;=> (1 . 2)
kaappi> (cons 'a '(b c))
;=> (a b c)
kaappi> (cons 1 '())
;=> (1)
```

**See also:** [`car`](#car), [`cdr`](#cdr)

---

### `car` { #car }

**Syntax:** `(car pair)`

Returns the contents of the `car` field of *pair*. Raises a type error if
the argument is not a pair.

```scheme
kaappi> (car '(a b c))
;=> a
kaappi> (car (cons 1 2))
;=> 1
```

**See also:** [`cdr`](#cdr), [`caar`](#caar), [`cadr`](#cadr)

---

### `cdr` { #cdr }

**Syntax:** `(cdr pair)`

Returns the contents of the `cdr` field of *pair*. Raises a type error if
the argument is not a pair.

```scheme
kaappi> (cdr '(a b c))
;=> (b c)
kaappi> (cdr (cons 1 2))
;=> 2
```

**See also:** [`car`](#car), [`cdar`](#cdar), [`cddr`](#cddr)

---

### `set-car!` { #set-car }

**Syntax:** `(set-car! pair obj)`

Stores *obj* in the `car` field of *pair*. The return value is unspecified.
Raises a type error if the first argument is not a pair.

```scheme
kaappi> (define p (cons 1 2))
kaappi> (set-car! p 99)
kaappi> p
;=> (99 . 2)
```

**See also:** [`set-cdr!`](#set-cdr), [`car`](#car)

---

### `set-cdr!` { #set-cdr }

**Syntax:** `(set-cdr! pair obj)`

Stores *obj* in the `cdr` field of *pair*. The return value is unspecified.
Raises a type error if the first argument is not a pair.

```scheme
kaappi> (define p (cons 1 2))
kaappi> (set-cdr! p 99)
kaappi> p
;=> (1 . 99)
```

**See also:** [`set-car!`](#set-car), [`cdr`](#cdr)

---

## List Construction

### `list` { #list }

**Syntax:** `(list obj ...)`

Returns a newly allocated proper list whose elements are the arguments.
Called with no arguments it returns the empty list.

```scheme
kaappi> (list 1 2 3)
;=> (1 2 3)
kaappi> (list 'a 'b)
;=> (a b)
kaappi> (list)
;=> ()
```

**See also:** [`make-list`](#make-list), [`cons`](#cons)

---

### `make-list` { #make-list }

**Syntax:** `(make-list k)` | `(make-list k fill)`

Returns a newly allocated list of *k* elements. If *fill* is given, each
element is initialized to *fill*; otherwise the elements are unspecified.
Raises a type error if *k* is not a non-negative integer.

```scheme
kaappi> (make-list 3 0)
;=> (0 0 0)
kaappi> (make-list 0)
;=> ()
```

**See also:** [`list`](#list), [`list-copy`](#list-copy)

---

### `list-copy` { #list-copy }

**Syntax:** `(list-copy obj)`

Returns a newly allocated shallow copy of *obj*. If *obj* is a proper list,
the result is a new list with the same elements. If *obj* is not a pair, it
is returned unchanged. Improper lists are copied faithfully, preserving the
dotted tail.

```scheme
kaappi> (define original (list 1 2 3))
kaappi> (define copy (list-copy original))
kaappi> (list-set! copy 0 99)
kaappi> original
;=> (1 2 3)
kaappi> copy
;=> (99 2 3)
```

**See also:** [`list`](#list), [`make-list`](#make-list)

---

### `append` { #append }

**Syntax:** `(append list ...)`

Returns a list consisting of the elements of the first *list* followed by the
elements of the other *lists*. The last argument may be any object and is used
directly as the tail of the result. All preceding arguments must be proper
lists. Called with no arguments it returns the empty list.

```scheme
kaappi> (append '(a b) '(c d))
;=> (a b c d)
kaappi> (append '(1) '(2) '(3))
;=> (1 2 3)
kaappi> (append '(a b) 'c)
;=> (a b . c)
kaappi> (append)
;=> ()
```

**See also:** [`reverse`](#reverse), [`concatenate`](./srfi-1.md#concatenate)

---

### `reverse` { #reverse }

**Syntax:** `(reverse list)`

Returns a newly allocated list consisting of the elements of *list* in
reverse order. Raises a type error if the argument is an improper list.

```scheme
kaappi> (reverse '(a b c))
;=> (c b a)
kaappi> (reverse '())
;=> ()
```

**See also:** [`append`](#append), [`append-reverse`](./srfi-1.md#append-reverse)

---

### `length` { #length }

**Syntax:** `(length list)`

Returns the number of elements in *list*. Raises a type error if the
argument is an improper or circular list. Uses Floyd's cycle-detection
algorithm internally so circular lists are caught rather than causing an
infinite loop.

```scheme
kaappi> (length '(a b c))
;=> 3
kaappi> (length '())
;=> 0
```

**See also:** [`list?`](./type-checking.md#list), [`length+`](./srfi-1.md#length-plus)

---

## Two-Level CXR

These four compositions of `car` and `cdr` are part of `(scheme base)`.
Each takes exactly one pair argument and applies two accessor operations
from right to left (innermost first).

### `caar` { #caar }

**Syntax:** `(caar pair)`

Equivalent to `(car (car pair))`. Returns the `car` of the `car` of *pair*.

```scheme
kaappi> (caar '((1 2) 3))
;=> 1
```

---

### `cadr` { #cadr }

**Syntax:** `(cadr pair)`

Equivalent to `(car (cdr pair))`. Returns the second element of a list.

```scheme
kaappi> (cadr '(1 2 3))
;=> 2
```

---

### `cdar` { #cdar }

**Syntax:** `(cdar pair)`

Equivalent to `(cdr (car pair))`. Returns the `cdr` of the `car` of *pair*.

```scheme
kaappi> (cdar '((1 2) 3))
;=> (2)
```

---

### `cddr` { #cddr }

**Syntax:** `(cddr pair)`

Equivalent to `(cdr (cdr pair))`. Returns the list after dropping the first
two elements.

```scheme
kaappi> (cddr '(1 2 3))
;=> (3)
```

---

## List Access

### `list-ref` { #list-ref }

**Syntax:** `(list-ref list k)`

Returns the *k*th element of *list* (zero-indexed). Raises `IndexOutOfBounds`
if *k* is out of range and `TypeError` if *k* is not a non-negative integer
or *list* is not a proper list.

```scheme
kaappi> (list-ref '(a b c d) 0)
;=> a
kaappi> (list-ref '(a b c d) 2)
;=> c
kaappi> (list-ref '(a b c d) 3)
;=> d
```

**See also:** [`list-tail`](#list-tail), [`list-set!`](#list-set)

---

### `list-tail` { #list-tail }

**Syntax:** `(list-tail list k)`

Returns the sublist of *list* obtained by omitting the first *k* elements.
Equivalent to applying `cdr` *k* times. Raises `IndexOutOfBounds` if *k*
is out of range.

```scheme
kaappi> (list-tail '(a b c d) 0)
;=> (a b c d)
kaappi> (list-tail '(a b c d) 2)
;=> (c d)
kaappi> (list-tail '(a b c d) 4)
;=> ()
```

**See also:** [`list-ref`](#list-ref), [`drop`](./srfi-1.md#drop)

---

### `list-set!` { #list-set }

**Syntax:** `(list-set! list k obj)`

Stores *obj* in element *k* of *list* (zero-indexed), mutating the pair in
place. The return value is unspecified. Raises `IndexOutOfBounds` if *k* is
out of range and `TypeError` if *k* is not a non-negative integer.

```scheme
kaappi> (define ls (list 1 2 3))
kaappi> (list-set! ls 1 99)
kaappi> ls
;=> (1 99 3)
```

**See also:** [`list-ref`](#list-ref), [`set-car!`](#set-car)

---

## Search

### `member` { #member }

**Syntax:** `(member obj list)` | `(member obj list compare)`

Returns the first sublist of *list* whose `car` is equal to *obj*, or `#f`
if *obj* does not appear. By default elements are compared with `equal?`.
An optional third argument *compare* specifies a two-argument predicate to
use instead.

```scheme
kaappi> (member 3 '(1 2 3 4 5))
;=> (3 4 5)
kaappi> (member 6 '(1 2 3 4 5))
;=> #f
kaappi> (member '(b) '((a) (b) (c)))
;=> ((b) (c))
kaappi> (member 2 '(1 2 3) =)
;=> (2 3)
```

**See also:** [`memq`](#memq), [`memv`](#memv), [`find`](./srfi-1.md#find)

---

### `memq` { #memq }

**Syntax:** `(memq obj list)`

Like `member`, but compares elements using `eq?` (pointer identity). Returns
the first sublist whose `car` is `eq?` to *obj*, or `#f`.

```scheme
kaappi> (memq 'b '(a b c))
;=> (b c)
kaappi> (memq 'd '(a b c))
;=> #f
```

**See also:** [`member`](#member), [`memv`](#memv)

---

### `memv` { #memv }

**Syntax:** `(memv obj list)`

Like `member`, but compares elements using `eqv?` (value equivalence for
numbers and characters). Returns the first sublist whose `car` is `eqv?`
to *obj*, or `#f`. For flonums, comparison is bitwise so `+0.0` and `-0.0`
are distinguished.

```scheme
kaappi> (memv 2 '(1 2 3))
;=> (2 3)
kaappi> (memv 4 '(1 2 3))
;=> #f
```

**See also:** [`member`](#member), [`memq`](#memq)

---

### `assoc` { #assoc }

**Syntax:** `(assoc obj alist)` | `(assoc obj alist compare)`

Searches the association list *alist* (a list of pairs) for the first pair
whose `car` is equal to *obj* using `equal?`. Returns the matching pair, or
`#f` if not found. An optional third argument *compare* specifies a
two-argument predicate to use instead of `equal?`.

```scheme
kaappi> (assoc 'b '((a 1) (b 2) (c 3)))
;=> (b 2)
kaappi> (assoc 'd '((a 1) (b 2) (c 3)))
;=> #f
kaappi> (assoc 2.0 '((1 a) (2 b) (3 c)) =)
;=> (2 b)
```

**See also:** [`assq`](#assq), [`assv`](#assv), [`alist-cons`](./srfi-1.md#alist-cons)

---

### `assq` { #assq }

**Syntax:** `(assq obj alist)`

Like `assoc`, but compares keys using `eq?` (pointer identity). Returns the
first pair whose `car` is `eq?` to *obj*, or `#f`.

```scheme
kaappi> (assq 'b '((a 1) (b 2) (c 3)))
;=> (b 2)
kaappi> (assq 'd '((a 1) (b 2) (c 3)))
;=> #f
```

**See also:** [`assoc`](#assoc), [`assv`](#assv)

---

### `assv` { #assv }

**Syntax:** `(assv obj alist)`

Like `assoc`, but compares keys using `eqv?` (value equivalence for numbers
and characters). Returns the first pair whose `car` is `eqv?` to *obj*, or
`#f`. For flonums, comparison is bitwise.

```scheme
kaappi> (assv 2 '((1 a) (2 b) (3 c)))
;=> (2 b)
kaappi> (assv 4 '((1 a) (2 b) (3 c)))
;=> #f
```

**See also:** [`assoc`](#assoc), [`assq`](#assq)

---

## Iteration

### `map` { #map }

**Syntax:** `(map proc list1 list2 ...)`

Applies *proc* element-wise to the elements of the given lists and returns
a list of the results. When multiple lists are given, *proc* receives one
argument from each list and iteration stops at the shortest list. The order
of application is unspecified by R7RS but Kaappi processes elements left to
right.

```scheme
kaappi> (map car '((1 2) (3 4) (5 6)))
;=> (1 3 5)
kaappi> (map (lambda (x) (* x x)) '(1 2 3))
;=> (1 4 9)
kaappi> (map + '(1 2 3) '(10 20 30))
;=> (11 22 33)
kaappi> (map car '())
;=> ()
```

**See also:** [`for-each`](#for-each), [`filter-map`](./srfi-1.md#filter-map)

---

### `for-each` { #for-each }

**Syntax:** `(for-each proc list1 list2 ...)`

Like `map`, but calls *proc* for its side effects rather than collecting
results. The return value is unspecified. When multiple lists are given,
iteration stops at the shortest. Elements are guaranteed to be processed
left to right.

```scheme
kaappi> (let ((result '()))
         (for-each (lambda (x) (set! result (cons x result)))
                   '(1 2 3))
         (reverse result))
;=> (1 2 3)
kaappi> (let ((sum 0))
         (for-each (lambda (a b) (set! sum (+ sum a b)))
                   '(1 2 3) '(10 20 30))
         sum)
;=> 66
```

**See also:** [`map`](#map), [`pair-for-each`](./srfi-1.md#pair-for-each)

---

### `apply` { #apply }

**Syntax:** `(apply proc arg1 ... args)`

Calls *proc* with the given arguments. The last argument must be a list;
its elements are spread as individual arguments. Any arguments before the
final list are prepended as individual arguments.

```scheme
kaappi> (apply + '(1 2 3))
;=> 6
kaappi> (apply + 1 2 '(3 4))
;=> 10
kaappi> (apply list 'a 'b '(c d))
;=> (a b c d)
```

!!! note
    `apply` requires at least two arguments: the procedure and the trailing
    list. The trailing list is always spread, so `(apply + '(1 2 3))` is
    equivalent to `(+ 1 2 3)`.

**See also:** [`map`](#map), [`call-with-values`](./control-flow.md#call-with-values)

---

## CXR Compositions

The `(scheme cxr)` library provides all 24 compositions of `car` and `cdr`
at three and four levels deep. Each procedure takes exactly one argument and
applies the accessor operations from right to left (innermost first). For
example, `(caddar x)` is equivalent to `(car (cdr (cdr (car x))))`.

The naming convention encodes the operation sequence between `c` and `r`:
each `a` stands for `car` and each `d` stands for `cdr`, read right to left.

### Three-Level Compositions

| Procedure | Expansion | Example |
|-----------|-----------|---------|
| `caaar` | `(car (car (car x)))` | `(caaar '(((1 2) 3) 4))` => `1` |
| `caadr` | `(car (car (cdr x)))` | `(caadr '(1 (2 3) 4))` => `2` |
| `cadar` | `(car (cdr (car x)))` | `(cadar '((1 2 3) 4))` => `2` |
| `caddr` | `(car (cdr (cdr x)))` | `(caddr '(1 2 3 4))` => `3` |
| `cdaar` | `(cdr (car (car x)))` | `(cdaar '(((1 2) 3) 4))` => `(2)` |
| `cdadr` | `(cdr (car (cdr x)))` | `(cdadr '(1 (2 3) 4))` => `(3)` |
| `cddar` | `(cdr (cdr (car x)))` | `(cddar '((1 2 3) 4))` => `(3)` |
| `cdddr` | `(cdr (cdr (cdr x)))` | `(cdddr '(1 2 3 4))` => `(4)` |

### Four-Level Compositions

| Procedure | Expansion |
|-----------|-----------|
| `caaaar` | `(car (car (car (car x))))` |
| `caaadr` | `(car (car (car (cdr x))))` |
| `caadar` | `(car (car (cdr (car x))))` |
| `caaddr` | `(car (car (cdr (cdr x))))` |
| `cadaar` | `(car (cdr (car (car x))))` |
| `cadadr` | `(car (cdr (car (cdr x))))` |
| `caddar` | `(car (cdr (cdr (car x))))` |
| `cadddr` | `(car (cdr (cdr (cdr x))))` |
| `cdaaar` | `(cdr (car (car (car x))))` |
| `cdaadr` | `(cdr (car (car (cdr x))))` |
| `cdadar` | `(cdr (car (cdr (car x))))` |
| `cdaddr` | `(cdr (car (cdr (cdr x))))` |
| `cddaar` | `(cdr (cdr (car (car x))))` |
| `cddadr` | `(cdr (cdr (car (cdr x))))` |
| `cdddar` | `(cdr (cdr (cdr (car x))))` |
| `cddddr` | `(cdr (cdr (cdr (cdr x))))` |

All 24 compositions raise a `TypeError` if any intermediate value along
the access path is not a pair.

```scheme
kaappi> (caddr '(a b c d))
;=> c
kaappi> (cadddr '(a b c d e))
;=> d
```
