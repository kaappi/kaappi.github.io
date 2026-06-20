# SRFI-133 Vector Library

Extended vector operations beyond R7RS base. Import with
`(import (srfi 133))`. For core vector procedures, see
[Vectors](./vectors.md).

---

## Constructors

### `vector-unfold` { #vector-unfold }

**Syntax:** `(vector-unfold f length)` | `(vector-unfold f length seed ...)`

Returns a newly allocated vector of the given *length*. The elements are
produced by calling *f* with the current index and seed values. *f* must
return the element value and the next seed values (via `values`). The
initial seeds are provided as additional arguments.

```scheme
kaappi> (vector-unfold (lambda (i) (* i i)) 5)
;=> #(0 1 4 9 16)
kaappi> (vector-unfold (lambda (i x) (values x (* x 2))) 5 1)
;=> #(1 2 4 8 16)
```

**See also:** [`vector-unfold-right`](#vector-unfold-right),
[`make-vector`](./vectors.md#make-vector)

---

### `vector-unfold-right` { #vector-unfold-right }

**Syntax:** `(vector-unfold-right f length)` | `(vector-unfold-right f length seed ...)`

Like [`vector-unfold`](#vector-unfold), but fills the vector from right to left.
The index passed to *f* counts down from *length* - 1 to 0.

```scheme
kaappi> (vector-unfold-right (lambda (i) (* i i)) 5)
;=> #(0 1 4 9 16)
kaappi> (vector-unfold-right (lambda (i x) (values x (* x 2))) 5 1)
;=> #(16 8 4 2 1)
```

**See also:** [`vector-unfold`](#vector-unfold)

---

### `vector-concatenate` { #vector-concatenate }

**Syntax:** `(vector-concatenate list-of-vectors)`

Returns a newly allocated vector that is the concatenation of all vectors in
*list-of-vectors*. Equivalent to `(apply vector-append list-of-vectors)` but
may be more efficient for large lists.

```scheme
kaappi> (vector-concatenate '(#(1 2) #(3 4) #(5)))
;=> #(1 2 3 4 5)
kaappi> (vector-concatenate '())
;=> #()
```

**See also:** [`vector-append`](./vectors.md#vector-append)

---

## Predicates

### `vector-any` { #vector-any }

**Syntax:** `(vector-any pred vector1 vector2 ...)`

Returns the first true value produced by applying *pred* element-wise to the
given vectors. If *pred* never returns a true value, returns `#f`. When
multiple vectors are given, iteration stops at the length of the shortest.

```scheme
kaappi> (vector-any odd? #(2 4 5 6))
;=> #t
kaappi> (vector-any odd? #(2 4 6 8))
;=> #f
kaappi> (vector-any < #(1 2 3) #(0 3 2))
;=> #t
```

**See also:** [`vector-every`](#vector-every),
[`vector-index`](#vector-index)

---

### `vector-every` { #vector-every }

**Syntax:** `(vector-every pred vector1 vector2 ...)`

Returns `#t` if *pred* returns a true value for every element-wise application
across the given vectors. Returns the value of the last application if all
succeed, or `#f` as soon as *pred* returns false. Returns `#t` for empty
vectors.

```scheme
kaappi> (vector-every even? #(2 4 6 8))
;=> #t
kaappi> (vector-every even? #(2 4 5 8))
;=> #f
kaappi> (vector-every < #(1 2 3) #(4 5 6))
;=> #t
```

**See also:** [`vector-any`](#vector-any),
[`vector-count`](#vector-count)

---

### `vector-empty?` { #vector-empty }

**Syntax:** `(vector-empty? vector)`

Returns `#t` if *vector* has zero length, `#f` otherwise.

```scheme
kaappi> (vector-empty? #())
;=> #t
kaappi> (vector-empty? #(1))
;=> #f
```

**See also:** [`vector-length`](./vectors.md#vector-length)

---

### `vector=` { #vector-equal }

**Syntax:** `(vector= elt=? vector1 vector2 ...)`

Returns `#t` if all given vectors have the same length and their corresponding
elements are equal according to the equality procedure *elt=?*. The first
argument is the element comparator, not a vector.

```scheme
kaappi> (vector= eq? #(a b c) #(a b c))
;=> #t
kaappi> (vector= eq? #(a b c) #(a b d))
;=> #f
kaappi> (vector= = #(1 2 3) #(1 2 3) #(1 2 3))
;=> #t
kaappi> (vector= eq? #(a b) #(a b c))
;=> #f
```

**See also:** [`equal?`](./type-checking.md#equal)

---

## Searching

### `vector-index` { #vector-index }

**Syntax:** `(vector-index pred vector1 vector2 ...)`

Returns the index of the first element-wise application of *pred* that returns
a true value. Returns `#f` if no element satisfies *pred*. When multiple
vectors are given, *pred* receives one element from each.

```scheme
kaappi> (vector-index odd? #(2 4 5 6 7))
;=> 2
kaappi> (vector-index even? #(1 3 5 7))
;=> #f
kaappi> (vector-index < #(1 5 3) #(2 3 4))
;=> 0
```

**See also:** [`vector-index-right`](#vector-index-right),
[`vector-skip`](#vector-skip)

---

### `vector-index-right` { #vector-index-right }

**Syntax:** `(vector-index-right pred vector1 vector2 ...)`

Like [`vector-index`](#vector-index), but searches from right to left, returning
the index of the last element satisfying *pred*. Returns `#f` if no element
matches.

```scheme
kaappi> (vector-index-right odd? #(2 4 5 6 7))
;=> 4
kaappi> (vector-index-right even? #(1 3 5 7))
;=> #f
```

**See also:** [`vector-index`](#vector-index),
[`vector-skip-right`](#vector-skip-right)

---

### `vector-skip` { #vector-skip }

**Syntax:** `(vector-skip pred vector1 vector2 ...)`

Returns the index of the first element that does *not* satisfy *pred*. This is
the complement of [`vector-index`](#vector-index). Returns `#f` if every element
matches.

```scheme
kaappi> (vector-skip even? #(2 4 5 6 7))
;=> 2
kaappi> (vector-skip even? #(2 4 6 8))
;=> #f
```

**See also:** [`vector-skip-right`](#vector-skip-right),
[`vector-index`](#vector-index)

---

### `vector-skip-right` { #vector-skip-right }

**Syntax:** `(vector-skip-right pred vector1 vector2 ...)`

Like [`vector-skip`](#vector-skip), but searches from right to left, returning
the index of the last element that does *not* satisfy *pred*.

```scheme
kaappi> (vector-skip-right even? #(2 4 5 6 7))
;=> 4
kaappi> (vector-skip-right odd? #(1 3 5 7))
;=> #f
```

**See also:** [`vector-skip`](#vector-skip),
[`vector-index-right`](#vector-index-right)

---

### `vector-binary-search` { #vector-binary-search }

**Syntax:** `(vector-binary-search vector value cmp)`

Performs a binary search on a sorted *vector* for *value*, using the three-way
comparator *cmp*. The comparator `(cmp a b)` must return a negative integer if
*a* < *b*, zero if *a* = *b*, or a positive integer if *a* > *b*. Returns the
index of the matching element, or `#f` if not found. The vector must be sorted
according to *cmp*.

```scheme
kaappi> (vector-binary-search #(1 3 5 7 9) 5
                              (lambda (a b) (- a b)))
;=> 2
kaappi> (vector-binary-search #(1 3 5 7 9) 4
                              (lambda (a b) (- a b)))
;=> #f
```

**See also:** [`vector-index`](#vector-index)

---

## Mutation

### `vector-swap!` { #vector-swap }

**Syntax:** `(vector-swap! vector i j)`

Swaps the elements at indices *i* and *j* in *vector*. Both *i* and *j* must
be valid indices. Returns void.

```scheme
kaappi> (let ((v (vector 'a 'b 'c 'd)))
         (vector-swap! v 0 3)
         v)
;=> #(d b c a)
kaappi> (let ((v (vector 1 2 3)))
         (vector-swap! v 0 2)
         v)
;=> #(3 2 1)
```

**See also:** [`vector-set!`](./vectors.md#vector-set),
[`vector-reverse!`](#vector-reverse-mut)

---

### `vector-reverse!` { #vector-reverse-mut }

**Syntax:** `(vector-reverse! vector)` | `(vector-reverse! vector start)` | `(vector-reverse! vector start end)`

Reverses the elements of *vector* in place. The optional *start* and *end*
arguments restrict the reversal to a subrange. Returns void.

```scheme
kaappi> (let ((v (vector 1 2 3 4 5)))
         (vector-reverse! v)
         v)
;=> #(5 4 3 2 1)
kaappi> (let ((v (vector 1 2 3 4 5)))
         (vector-reverse! v 1 4)
         v)
;=> #(1 4 3 2 5)
```

**See also:** [`vector-reverse-copy`](#vector-reverse-copy),
[`vector-swap!`](#vector-swap)

---

## Copying

### `vector-reverse-copy` { #vector-reverse-copy }

**Syntax:** `(vector-reverse-copy vector)` | `(vector-reverse-copy vector start)` | `(vector-reverse-copy vector start end)`

Returns a newly allocated vector containing the elements of *vector* in reverse
order. The optional *start* and *end* arguments select a subrange to reverse
and copy. Unlike [`vector-reverse!`](#vector-reverse-mut), this does not modify
the original.

```scheme
kaappi> (vector-reverse-copy #(1 2 3 4 5))
;=> #(5 4 3 2 1)
kaappi> (vector-reverse-copy #(1 2 3 4 5) 1 4)
;=> #(4 3 2)
```

**See also:** [`vector-copy`](./vectors.md#vector-copy),
[`vector-reverse!`](#vector-reverse-mut)

---

## Folding

### `vector-fold` { #vector-fold }

**Syntax:** `(vector-fold f seed vector1 vector2 ...)`

Left fold over one or more vectors. *f* is called as `(f index state elt ...)`
where *index* is the current position and *state* is the accumulated value.
Returns the final accumulated value.

```scheme
kaappi> (vector-fold (lambda (i sum x) (+ sum x)) 0 #(1 2 3 4 5))
;=> 15
kaappi> (vector-fold (lambda (i acc x) (cons x acc)) '() #(a b c))
;=> (c b a)
```

**See also:** [`vector-fold-right`](#vector-fold-right),
[`fold`](./srfi-1.md#fold)

---

### `vector-fold-right` { #vector-fold-right }

**Syntax:** `(vector-fold-right f seed vector1 vector2 ...)`

Right fold over one or more vectors. Like [`vector-fold`](#vector-fold), but
processes elements from right to left. *f* is called as
`(f index state elt ...)`.

```scheme
kaappi> (vector-fold-right (lambda (i acc x) (cons x acc)) '() #(a b c))
;=> (a b c)
kaappi> (vector-fold-right (lambda (i s x) (+ s x)) 0 #(1 2 3))
;=> 6
```

**See also:** [`vector-fold`](#vector-fold),
[`fold-right`](./srfi-1.md#fold-right)

---

### `vector-cumulate` { #vector-cumulate }

**Syntax:** `(vector-cumulate f seed vector)`

Returns a newly allocated vector of the same length as *vector*, where each
element is the cumulative result of applying *f* to the previous accumulated
value and the current element. This is sometimes called a prefix sum or scan.
*f* is called as `(f state elt)`.

```scheme
kaappi> (vector-cumulate + 0 #(1 2 3 4 5))
;=> #(1 3 6 10 15)
kaappi> (vector-cumulate * 1 #(1 2 3 4))
;=> #(1 2 6 24)
```

**See also:** [`vector-fold`](#vector-fold)

---

### `vector-count` { #vector-count }

**Syntax:** `(vector-count pred vector1 vector2 ...)`

Returns the number of elements for which *pred* returns a true value when
applied element-wise to the given vectors.

```scheme
kaappi> (vector-count even? #(1 2 3 4 5 6))
;=> 3
kaappi> (vector-count < #(1 5 3) #(2 3 4))
;=> 2
```

**See also:** [`vector-any`](#vector-any),
[`vector-index`](#vector-index)

---

### `vector-partition` { #vector-partition }

**Syntax:** `(vector-partition pred vector)`

Partitions the elements of *vector* by *pred*, returning two values: a vector
of elements for which *pred* returned true, and a vector of elements for which
*pred* returned false. The relative order of elements is preserved.

```scheme
kaappi> (let-values (((yes no) (vector-partition even? #(1 2 3 4 5 6))))
         (list yes no))
;=> (#(2 4 6) #(1 3 5))
kaappi> (let-values (((yes no) (vector-partition positive? #(-1 2 -3 4))))
         (list yes no))
;=> (#(2 4) #(-1 -3))
```

**See also:** [`partition`](./srfi-1.md#partition),
[`vector-fold`](#vector-fold)

---

## Transformation

### `vector-map!` { #vector-map-mut }

**Syntax:** `(vector-map! f vector1 vector2 ...)`

Applies *f* element-wise to the given vectors and stores each result back into
*vector1*. When multiple vectors are given, *f* receives one element from each.
Iteration stops at the length of the shortest vector. Returns void.

```scheme
kaappi> (let ((v (vector 1 2 3 4)))
         (vector-map! (lambda (x) (* x x)) v)
         v)
;=> #(1 4 9 16)
kaappi> (let ((v (vector 1 2 3)))
         (vector-map! + v #(10 20 30))
         v)
;=> #(11 22 33)
```

**See also:** [`vector-map`](./vectors.md#vector-map),
[`vector-for-each`](./vectors.md#vector-for-each)

---
