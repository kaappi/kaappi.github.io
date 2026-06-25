# Vectors

Vectors are fixed-length arrays with constant-time indexed access. Unlike
lists, vectors support efficient random access and mutation. Available from
`(scheme base)`. For extended operations, see
[SRFI-133 Vector Library](./srfi-133.md).

## Performance characteristics

| Operation | Complexity | Notes |
|-----------|:----------:|-------|
| `vector-ref` | O(1) | Constant time — direct index |
| `vector-set!` | O(1) | Constant time |
| `vector-length` | O(1) | Stored in the object header |
| `vector->list` | O(n) | Allocates n pairs |
| `list->vector` | O(n) | One pass |
| `vector-copy` | O(n) | Full copy |
| `vector-fill!` | O(n) | Fills all elements |
| `vector-for-each` | O(n) | One pass |

**When to use vectors vs. lists:**

- Use vectors when you need random access by index — `vector-ref` is O(1),
  `list-ref` is O(n)
- Use vectors for fixed-size collections where the length is known up front
- Use [lists](pairs-and-lists.md) when you build data incrementally with
  `cons` and process it sequentially
- Database query results in the ecosystem (kaappi-pg, kaappi-sqlite) return
  rows as vectors for efficient column access

---

## Construction

### `vector` { #vector }

**Syntax:** `(vector obj ...)`

Returns a newly allocated vector whose elements are the given arguments. When
called with no arguments, returns the empty vector.

```scheme
kaappi> (vector 1 2 3)
;=> #(1 2 3)
kaappi> (vector 'a 'b 'c)
;=> #(a b c)
kaappi> (vector)
;=> #()
```

**See also:** [`make-vector`](#make-vector), [`list->vector`](#list-to-vector)

---

### `make-vector` { #make-vector }

**Syntax:** `(make-vector k)` | `(make-vector k fill)`

Returns a newly allocated vector of length *k*. If *fill* is given, every
element is initialized to *fill*; otherwise the elements are unspecified.

```scheme
kaappi> (vector-length (make-vector 5))
;=> 5
kaappi> (make-vector 3 0)
;=> #(0 0 0)
kaappi> (make-vector 4 'x)
;=> #(x x x x)
```

**See also:** [`vector`](#vector), [`vector-fill!`](#vector-fill)

---

## Type Predicate

### `vector?` { #vector-pred }

**Syntax:** `(vector? obj)`

Returns `#t` if *obj* is a vector, `#f` otherwise.

```scheme
kaappi> (vector? #(1 2 3))
;=> #t
kaappi> (vector? '(1 2 3))
;=> #f
kaappi> (vector? "hello")
;=> #f
```

**See also:** [`vector`](#vector)

---

## Access and Mutation

### `vector-length` { #vector-length }

**Syntax:** `(vector-length vector)`

Returns the number of elements in *vector*.

```scheme
kaappi> (vector-length #(1 2 3))
;=> 3
kaappi> (vector-length #())
;=> 0
```

**See also:** [`vector-ref`](#vector-ref)

---

### `vector-ref` { #vector-ref }

**Syntax:** `(vector-ref vector k)`

Returns the element at index *k* in *vector*, using zero-based indexing. It is
an error if *k* is not a valid index. This operation is O(1).

```scheme
kaappi> (vector-ref #(a b c d) 0)
;=> a
kaappi> (vector-ref #(a b c d) 2)
;=> c
```

**See also:** [`vector-set!`](#vector-set), [`vector-length`](#vector-length)

---

### `vector-set!` { #vector-set }

**Syntax:** `(vector-set! vector k obj)`

Stores *obj* into element *k* of *vector*. It is an error if *k* is not a valid
index. This operation is O(1). Returns void.

```scheme
kaappi> (let ((v (vector 1 2 3)))
         (vector-set! v 1 99)
         v)
;=> #(1 99 3)
```

**See also:** [`vector-ref`](#vector-ref), [`vector-fill!`](#vector-fill)

---

## Conversion

### `vector->list` { #vector-to-list }

**Syntax:** `(vector->list vector)` | `(vector->list vector start)` | `(vector->list vector start end)`

Returns a list of the elements in *vector*. The optional *start* and *end*
arguments select a subrange using zero-based indices: *start* is inclusive and
*end* is exclusive. If *end* is omitted it defaults to the length of the vector;
if *start* is also omitted it defaults to 0.

```scheme
kaappi> (vector->list #(a b c))
;=> (a b c)
kaappi> (vector->list #(a b c d e) 1 3)
;=> (b c)
kaappi> (vector->list #())
;=> ()
```

**See also:** [`list->vector`](#list-to-vector),
[`vector->string`](#vector-to-string)

---

### `list->vector` { #list-to-vector }

**Syntax:** `(list->vector list)`

Returns a newly allocated vector whose elements are the elements of *list*.

```scheme
kaappi> (list->vector '(1 2 3))
;=> #(1 2 3)
kaappi> (list->vector '())
;=> #()
```

**See also:** [`vector->list`](#vector-to-list), [`vector`](#vector)

---

### `vector->string` { #vector-to-string }

**Syntax:** `(vector->string vector)` | `(vector->string vector start)` | `(vector->string vector start end)`

Returns a string formed from the characters in *vector*. It is an error if any
element of *vector* is not a character. The optional *start* and *end* arguments
select a subrange.

```scheme
kaappi> (vector->string #(#\a #\b #\c))
;=> "abc"
kaappi> (vector->string #(#\h #\e #\l #\l #\o) 1 4)
;=> "ell"
```

**See also:** [`string->vector`](./strings.md#string-to-vector),
[`list->string`](./strings.md#list-to-string)

---

## Filling and Copying

### `vector-fill!` { #vector-fill }

**Syntax:** `(vector-fill! vector fill)` | `(vector-fill! vector fill start)` | `(vector-fill! vector fill start end)`

Fills the elements of *vector* with *fill* from index *start* (inclusive,
default 0) to *end* (exclusive, default `(vector-length vector)`). Returns void.

```scheme
kaappi> (let ((v (make-vector 4 0)))
         (vector-fill! v 7)
         v)
;=> #(7 7 7 7)
kaappi> (let ((v (vector 1 2 3 4 5)))
         (vector-fill! v 0 1 4)
         v)
;=> #(1 0 0 0 5)
```

**See also:** [`make-vector`](#make-vector), [`vector-set!`](#vector-set)

---

### `vector-copy` { #vector-copy }

**Syntax:** `(vector-copy vector)` | `(vector-copy vector start)` | `(vector-copy vector start end)`

Returns a newly allocated vector containing the elements of *vector* from index
*start* (inclusive, default 0) to *end* (exclusive, default
`(vector-length vector)`).

```scheme
kaappi> (vector-copy #(a b c d e))
;=> #(a b c d e)
kaappi> (vector-copy #(a b c d e) 1 4)
;=> #(b c d)
```

**See also:** [`vector-copy!`](#vector-copy-mut),
[`vector-append`](#vector-append)

---

### `vector-copy!` { #vector-copy-mut }

**Syntax:** `(vector-copy! to at from)` | `(vector-copy! to at from start)` | `(vector-copy! to at from start end)`

Copies elements from vector *from* into vector *to*, starting at index *at* in
*to*. The optional *start* and *end* arguments select a subrange of *from*. The
destination must have enough room for the copied elements. Overlapping ranges
(where *to* and *from* are the same vector) are handled correctly. Returns void.

```scheme
kaappi> (let ((v (vector 1 2 3 4 5)))
         (vector-copy! v 1 #(10 20))
         v)
;=> #(1 10 20 4 5)
kaappi> (let ((v (vector 1 2 3 4 5)))
         (vector-copy! v 0 #(a b c d e) 2 4)
         v)
;=> #(c d 3 4 5)
```

**See also:** [`vector-copy`](#vector-copy), [`vector-fill!`](#vector-fill)

---

### `vector-append` { #vector-append }

**Syntax:** `(vector-append vector ...)`

Returns a newly allocated vector whose elements are the concatenation of the
given vectors. When called with no arguments, returns the empty vector.

```scheme
kaappi> (vector-append #(1 2) #(3 4))
;=> #(1 2 3 4)
kaappi> (vector-append #(a) #(b) #(c))
;=> #(a b c)
kaappi> (vector-append)
;=> #()
```

**See also:** [`vector-copy`](#vector-copy),
[`vector-concatenate`](./srfi-133.md#vector-concatenate)

---

## Iteration

### `vector-for-each` { #vector-for-each }

**Syntax:** `(vector-for-each proc vector1 vector2 ...)`

Applies *proc* element-wise to the elements of the given vectors, in order
from the first element to the last, for its side effects. When multiple
vectors are provided, *proc* receives one element from each vector per call.
Iteration stops at the length of the shortest vector. Returns void.

```scheme
kaappi> (let ((sum 0))
         (vector-for-each (lambda (x) (set! sum (+ sum x)))
                          #(1 2 3 4))
         sum)
;=> 10
kaappi> (let ((pairs '()))
         (vector-for-each (lambda (a b) (set! pairs (cons (list a b) pairs)))
                          #(x y z) #(1 2 3))
         (reverse pairs))
;=> ((x 1) (y 2) (z 3))
```

**See also:** [`vector-map`](#vector-map),
[`for-each`](./pairs-and-lists.md#for-each)

---

### `vector-map` { #vector-map }

**Syntax:** `(vector-map proc vector1 vector2 ...)`

Applies *proc* element-wise to the elements of the given vectors, collecting the
results into a new vector. When multiple vectors are provided, *proc* receives
one element from each vector per call. The result has the length of the shortest
input vector.

```scheme
kaappi> (vector-map + #(1 2 3) #(10 20 30))
;=> #(11 22 33)
kaappi> (vector-map (lambda (x) (* x x)) #(1 2 3 4))
;=> #(1 4 9 16)
kaappi> (vector-map car #(#(a b) #(c d) #(e f)))
;=> #(a c e)
```

**See also:** [`vector-for-each`](#vector-for-each),
[`map`](./pairs-and-lists.md#map)

---
