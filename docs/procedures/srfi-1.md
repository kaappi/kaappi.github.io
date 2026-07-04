# SRFI-1 List Library

Extended list operations beyond R7RS base. Import with `(import (srfi 1))`.
For core list procedures, see [Pairs and Lists](./pairs-and-lists.md).

---

## Constructors

### `cons*` { #cons-star }
<!-- index: 1+ | Like `list` but last arg is the tail -->

**Syntax:** `(cons* obj1 obj2 ...)`

Like `list`, but the last argument becomes the tail of the result instead of
being wrapped in a pair. With a single argument, returns that argument
unchanged. Equivalent to `list*` in some other Scheme implementations.

```scheme
kaappi> (cons* 1 2 3)
;=> (1 2 . 3)
kaappi> (cons* 'a 'b '(c d))
;=> (a b c d)
kaappi> (cons* 42)
;=> 42
```

**See also:** [`cons`](./pairs-and-lists.md#cons), [`list`](./pairs-and-lists.md#list)

---

### `xcons` { #xcons }
<!-- index: 2 | `(cons cdr car)` — reversed cons -->

**Syntax:** `(xcons d a)`

"eXchanged cons" -- returns `(cons a d)`. The arguments are reversed compared
to `cons`, which is convenient for passing to higher-order procedures.

```scheme
kaappi> (xcons '(b c) 'a)
;=> (a b c)
kaappi> (xcons 2 1)
;=> (1 . 2)
```

**See also:** [`cons`](./pairs-and-lists.md#cons)

---

### `list-tabulate` { #list-tabulate }
<!-- index: 2 | Build list of k elements from init procedure -->

**Syntax:** `(list-tabulate n init-proc)`

Returns a list of *n* elements, where each element is the result of calling
*init-proc* with its index (0 to *n*-1). Raises a type error if *n* is not
a non-negative integer.

```scheme
kaappi> (list-tabulate 5 (lambda (i) (* i i)))
;=> (0 1 4 9 16)
kaappi> (list-tabulate 3 values)
;=> (0 1 2)
kaappi> (list-tabulate 0 values)
;=> ()
```

**See also:** [`iota`](#iota), [`make-list`](./pairs-and-lists.md#make-list)

---

### `circular-list` { #circular-list }
<!-- index: 1+ | Build a circular list from arguments -->

**Syntax:** `(circular-list obj1 obj2 ...)`

Returns a circular list containing the given elements, with the last pair's
`cdr` pointing back to the first pair. With no arguments, returns `()`.

```scheme
kaappi> (take (circular-list 1 2 3) 7)
;=> (1 2 3 1 2 3 1)
kaappi> (circular-list? (circular-list 'a 'b))
;=> #t
```

**See also:** [`circular-list?`](#circular-list-pred), [`list`](./pairs-and-lists.md#list)

---

### `iota` { #iota }
<!-- index: 1+ | Generate list of integers (count, optional start and step) -->

**Syntax:** `(iota count)` | `(iota count start)` | `(iota count start step)`

Returns a list of *count* numbers. With one argument, produces `(0 1 2 ... count-1)`.
With *start*, begins from that value. With *step*, increments by that amount.
Uses exact arithmetic when all arguments are exact, otherwise inexact.

```scheme
kaappi> (iota 5)
;=> (0 1 2 3 4)
kaappi> (iota 5 1)
;=> (1 2 3 4 5)
kaappi> (iota 5 0 2)
;=> (0 2 4 6 8)
kaappi> (iota 3 1.0 0.5)
;=> (1.0 1.5 2.0)
```

**See also:** [`list-tabulate`](#list-tabulate)

---

## Predicates

### `proper-list?` { #proper-list }
<!-- index: 1 | True if argument is a proper list -->

**Syntax:** `(proper-list? obj)`

Returns `#t` if *obj* is a proper list -- a chain of pairs ending with the
empty list. Returns `#f` for dotted lists, circular lists, and non-pair
values (including `()`  returns `#t` since the empty list is a proper list).
Uses Floyd's tortoise-and-hare algorithm for cycle detection.

```scheme
kaappi> (proper-list? '(1 2 3))
;=> #t
kaappi> (proper-list? '())
;=> #t
kaappi> (proper-list? (cons 1 2))
;=> #f
kaappi> (proper-list? (circular-list 1 2))
;=> #f
```

**See also:** [`dotted-list?`](#dotted-list), [`circular-list?`](#circular-list-pred)

---

### `dotted-list?` { #dotted-list }
<!-- index: 1 | True if argument is a dotted (improper) list -->

**Syntax:** `(dotted-list? obj)`

Returns `#t` if *obj* is a dotted (improper) list -- a chain of pairs ending
with a non-nil value rather than `()`. A non-pair, non-nil value is also
considered dotted. Returns `#f` for proper lists and circular lists.

```scheme
kaappi> (dotted-list? (cons 1 2))
;=> #t
kaappi> (dotted-list? '(1 2 . 3))
;=> #t
kaappi> (dotted-list? '(1 2 3))
;=> #f
kaappi> (dotted-list? 42)
;=> #t
```

**See also:** [`proper-list?`](#proper-list), [`circular-list?`](#circular-list-pred)

---

### `circular-list?` { #circular-list-pred }
<!-- index: 1 | True if argument is a circular list -->

**Syntax:** `(circular-list? obj)`

Returns `#t` if *obj* is a circular list -- a chain of pairs that forms a
cycle. Uses Floyd's tortoise-and-hare algorithm. Returns `#f` for proper
lists, dotted lists, and non-pair values.

```scheme
kaappi> (circular-list? (circular-list 1 2 3))
;=> #t
kaappi> (circular-list? '(1 2 3))
;=> #f
kaappi> (circular-list? 42)
;=> #f
```

**See also:** [`proper-list?`](#proper-list), [`dotted-list?`](#dotted-list), [`circular-list`](#circular-list)

---

### `not-pair?` { #not-pair }
<!-- index: 1 | True if argument is not a pair -->

**Syntax:** `(not-pair? obj)`

Returns `#t` if *obj* is not a pair. Equivalent to `(not (pair? obj))` but
can be more convenient as a predicate argument to higher-order procedures.

```scheme
kaappi> (not-pair? 42)
;=> #t
kaappi> (not-pair? '())
;=> #t
kaappi> (not-pair? '(1 2))
;=> #f
```

**See also:** [`pair?`](./type-checking.md#pair)

---

### `null-list?` { #null-list }
<!-- index: 1 | True if argument is the empty list (error on non-list) -->

**Syntax:** `(null-list? obj)`

Like `null?`, but raises a type error if *obj* is not a proper list or pair.
Returns `#t` for `()`, `#f` for pairs.

```scheme
kaappi> (null-list? '())
;=> #t
kaappi> (null-list? '(1 2))
;=> #f
```

**See also:** [`null?`](./type-checking.md#null)

---

### `list=` { #list-equal }
<!-- index: 2+ | Compare lists element-wise with a given equality predicate -->

**Syntax:** `(list= elt= list1 ...)`

Returns `#t` if all given lists have equal length and corresponding elements
are equal according to the *elt=* procedure. With zero or one list argument,
returns `#t`.

```scheme
kaappi> (list= eq? '(a b c) '(a b c))
;=> #t
kaappi> (list= eq? '(a b) '(a b c))
;=> #f
kaappi> (list= = '(1 2 3) '(1 2 3) '(1 2 3))
;=> #t
```

**See also:** [`equal?`](./type-checking.md#equal), [`lset=`](#lset-equal)

---

## Selectors

### `take` { #take }
<!-- index: 2 | First k elements -->

**Syntax:** `(take list k)`

Returns a freshly allocated list of the first *k* elements of *list*.
Raises a type error if *k* is negative or greater than the length of the list.

```scheme
kaappi> (take '(a b c d e) 3)
;=> (a b c)
kaappi> (take '(a b c d) 2)
;=> (a b)
kaappi> (take '(a b c) 0)
;=> ()
```

**See also:** [`drop`](#drop), [`take-right`](#take-right), [`split-at`](#split-at)

---

### `drop` { #drop }
<!-- index: 2 | All but first k elements -->

**Syntax:** `(drop list k)`

Returns the suffix of *list* obtained by skipping the first *k* elements.
This is the list's *k*-th `cdr`. The result shares structure with *list*.

```scheme
kaappi> (drop '(a b c d e) 2)
;=> (c d e)
kaappi> (drop '(a b c d) 2)
;=> (c d)
kaappi> (drop '(a b c) 0)
;=> (a b c)
```

**See also:** [`take`](#take), [`drop-right`](#drop-right), [`split-at`](#split-at)

---

### `take-right` { #take-right }
<!-- index: 2 | Last k elements -->

**Syntax:** `(take-right list k)`

Returns the last *k* elements of *list*. The result shares structure with
the original list.

```scheme
kaappi> (take-right '(a b c d e) 3)
;=> (c d e)
kaappi> (take-right '(a b c d e) 0)
;=> ()
```

**See also:** [`drop-right`](#drop-right), [`take`](#take)

---

### `drop-right` { #drop-right }
<!-- index: 2 | All but last k elements -->

**Syntax:** `(drop-right list k)`

Returns a freshly allocated list containing all but the last *k* elements
of *list*.

```scheme
kaappi> (drop-right '(a b c d e) 2)
;=> (a b c)
kaappi> (drop-right '(a b c d e) 0)
;=> (a b c d e)
```

**See also:** [`take-right`](#take-right), [`drop`](#drop)

---

### `split-at` { #split-at }
<!-- index: 2 | Split list at index k into two values -->

**Syntax:** `(split-at list k)`

Returns two values: the first *k* elements as a freshly allocated list,
and the remaining tail. Equivalent to `(values (take list k) (drop list k))`
but only traverses the list once.

```scheme
kaappi> (call-with-values
         (lambda () (split-at '(a b c d e) 3))
         list)
;=> ((a b c) (d e))
```

**See also:** [`take`](#take), [`drop`](#drop), [`partition`](#partition)

---

### `last` { #last }
<!-- index: 1 | Last element of a non-empty list -->

**Syntax:** `(last list)`

Returns the last element of the non-empty proper list *list*. Raises a type
error if the argument is not a pair.

```scheme
kaappi> (last '(a b c))
;=> c
kaappi> (last '(x))
;=> x
```

**See also:** [`last-pair`](#last-pair), [`first`](#first)

---

### `last-pair` { #last-pair }
<!-- index: 1 | Last pair of a non-empty list -->

**Syntax:** `(last-pair list)`

Returns the last pair in the non-empty list *list*. For a proper list this
is the pair whose `cdr` is `()`.

```scheme
kaappi> (last-pair '(a b c))
;=> (c)
kaappi> (last-pair '(a b . c))
;=> (b . c)
```

**See also:** [`last`](#last)

---

## Accessors (first through tenth)

`first` through `tenth` extract elements by position from a list. Each is
equivalent to the corresponding chain of `car`/`cdr` calls.

| Procedure | Position | Equivalent |
|-----------|----------|------------|
| `(first pair)` { #first } | 1st | `(car pair)` |  <!-- index: 1 | First element (same as `car`) -->
| `(second pair)` { #second } | 2nd | `(cadr pair)` |  <!-- index: 1 | Second element -->
| `(third pair)` { #third } | 3rd | `(caddr pair)` |  <!-- index: 1 | Third element -->
| `(fourth pair)` { #fourth } | 4th | `(cadddr pair)` |  <!-- index: 1 | Fourth element -->
| `(fifth pair)` { #fifth } | 5th | 5th element |  <!-- index: 1 | Fifth element -->
| `(sixth pair)` { #sixth } | 6th | 6th element |  <!-- index: 1 | Sixth element -->
| `(seventh pair)` { #seventh } | 7th | 7th element |  <!-- index: 1 | Seventh element -->
| `(eighth pair)` { #eighth } | 8th | 8th element |  <!-- index: 1 | Eighth element -->
| `(ninth pair)` { #ninth } | 9th | 9th element |  <!-- index: 1 | Ninth element -->
| `(tenth pair)` { #tenth } | 10th | 10th element |  <!-- index: 1 | Tenth element -->

All raise a type error if the list is shorter than the requested position.

```scheme
kaappi> (first '(a b c d e f g h i j))
;=> a
kaappi> (third '(a b c d e f g h i j))
;=> c
kaappi> (seventh '(a b c d e f g h i j))
;=> g
kaappi> (tenth '(a b c d e f g h i j))
;=> j
```

**See also:** [`car`](./pairs-and-lists.md#car), [`list-ref`](./pairs-and-lists.md#list-ref)

---

### `car+cdr` { #carcdr }
<!-- index: 1 | Return car and cdr as multiple values -->

**Syntax:** `(car+cdr pair)`

Returns two values: `(car pair)` and `(cdr pair)`. Useful for
destructuring a pair in a single call with `receive` or
`call-with-values`.

```scheme
kaappi> (call-with-values
         (lambda () (car+cdr '(a b c)))
         list)
;=> (a (b c))
```

**See also:** [`car`](./pairs-and-lists.md#car), [`cdr`](./pairs-and-lists.md#cdr)

---

## Folding and Mapping

### `fold` { #fold }
<!-- index: 3+ | Left fold over one or more lists -->

**Syntax:** `(fold kons knil list1 list2 ...)`

The fundamental left-fold operation. Applies *kons* across the list(s) from
left to right, threading an accumulator that starts at *knil*.

For one list: `(fold kons knil '(e1 e2 e3))` computes
`(kons e3 (kons e2 (kons e1 knil)))`.

With multiple lists, *kons* receives corresponding elements from each list
plus the accumulator. Iteration stops when the shortest list is exhausted.

```scheme
kaappi> (fold + 0 '(1 2 3 4 5))
;=> 15
kaappi> (fold cons '() '(a b c d))
;=> (d c b a)
kaappi> (fold + 0 '(1 2 3) '(10 20 30))
;=> 66
```

**See also:** [`fold-right`](#fold-right), [`reduce`](#reduce)

---

### `fold-right` { #fold-right }
<!-- index: 3+ | Right fold over one or more lists -->

**Syntax:** `(fold-right kons knil list1 list2 ...)`

The fundamental right-fold operation. Applies *kons* across the list(s) from
right to left. Collects all elements first, then folds from the rightmost
element.

For one list: `(fold-right kons knil '(e1 e2 e3))` computes
`(kons e1 (kons e2 (kons e3 knil)))`.

```scheme
kaappi> (fold-right cons '() '(a b c d))
;=> (a b c d)
kaappi> (fold-right + 0 '(1 2 3 4 5))
;=> 15
kaappi> (fold-right list '() '(a b c))
;=> (a (b (c ())))
```

**See also:** [`fold`](#fold), [`reduce-right`](#reduce-right)

---

### `reduce` { #reduce }
<!-- index: 3 | Like fold with identity element -->

**Syntax:** `(reduce f ridentity list)`

Like `fold`, but uses the first element of *list* as the initial accumulator
value. Returns *ridentity* if *list* is empty. The combining function *f*
receives `(f element accumulator)`.

This is useful when there is no natural "right identity" separate from the
list elements, such as computing a maximum.

```scheme
kaappi> (reduce + 0 '(1 2 3 4 5))
;=> 15
kaappi> (reduce max 0 '(3 1 4 1 5 9))
;=> 9
kaappi> (reduce + 0 '())
;=> 0
```

**See also:** [`fold`](#fold), [`reduce-right`](#reduce-right)

---

### `reduce-right` { #reduce-right }
<!-- index: 3 | Like fold-right with identity element -->

**Syntax:** `(reduce-right f ridentity list)`

Like `fold-right`, but uses the last element of *list* as the initial
accumulator. Returns *ridentity* if *list* is empty.

```scheme
kaappi> (reduce-right append '() '((1 2) (3 4) (5 6)))
;=> (1 2 3 4 5 6)
kaappi> (reduce-right + 0 '())
;=> 0
```

**See also:** [`fold-right`](#fold-right), [`reduce`](#reduce)

---

### `pair-fold` { #pair-fold }
<!-- index: 3+ | Fold over pairs (not elements) -->

**Syntax:** `(pair-fold kons knil list1 list2 ...)`

Like `fold`, but *kons* receives the successive pairs (tails) of the list(s)
rather than the successive elements. Iteration stops when the shortest list
is exhausted.

```scheme
kaappi> (pair-fold (lambda (pair acc) (+ (car pair) acc)) 0 '(1 2 3))
;=> 6
```

**See also:** [`fold`](#fold), [`pair-fold-right`](#pair-fold-right), [`pair-for-each`](#pair-for-each)

---

### `pair-fold-right` { #pair-fold-right }
<!-- index: 3+ | Right fold over pairs -->

**Syntax:** `(pair-fold-right kons knil list1 list2 ...)`

Like `fold-right`, but *kons* receives the successive pairs (tails) from
right to left rather than the successive elements.

```scheme
kaappi> (pair-fold-right (lambda (pair acc) (cons (car pair) acc)) '() '(a b c))
;=> (a b c)
```

**See also:** [`fold-right`](#fold-right), [`pair-fold`](#pair-fold)

---

### `unfold` { #unfold }
<!-- index: 4+ | Unfold a list from a seed value -->

**Syntax:** `(unfold pred mapper successor seed)` | `(unfold pred mapper successor seed tail-gen)`

The fundamental recursive list constructor. Builds a list from a seed value:

1. If `(pred seed)` is true, stop. Return `(tail-gen seed)` or `()` if
   *tail-gen* is not provided.
2. Otherwise, cons `(mapper seed)` onto the result of unfolding
   `(successor seed)`.

```scheme
kaappi> (unfold (lambda (x) (> x 5)) values (lambda (x) (+ x 1)) 1)
;=> (1 2 3 4 5)
kaappi> (unfold null? car cdr '(a b c))
;=> (a b c)
kaappi> (unfold (lambda (x) (> x 3))
               (lambda (x) (* x x))
               (lambda (x) (+ x 1))
               1)
;=> (1 4 9)
```

**See also:** [`unfold-right`](#unfold-right), [`list-tabulate`](#list-tabulate)

---

### `unfold-right` { #unfold-right }
<!-- index: 4+ | Unfold a list in reverse from a seed value -->

**Syntax:** `(unfold-right pred mapper successor seed)` | `(unfold-right pred mapper successor seed tail)`

Builds a list from right to left. Starts with *tail* (or `()`) and repeatedly
conses `(mapper seed)` onto the front until `(pred seed)` is true.

```scheme
kaappi> (unfold-right zero? values (lambda (x) (- x 1)) 5)
;=> (1 2 3 4 5)
kaappi> (unfold-right null? car cdr '(a b c))
;=> (c b a)
```

**See also:** [`unfold`](#unfold)

---

### `map-in-order` { #map-in-order }
<!-- index: 2+ | Map with guaranteed left-to-right evaluation -->

**Syntax:** `(map-in-order proc list1 list2 ...)`

Like `map`, but guarantees left-to-right evaluation order. The standard
`map` does not specify evaluation order; use `map-in-order` when the
mapping procedure has side effects that depend on order.

```scheme
kaappi> (map-in-order (lambda (x) (* x x)) '(1 2 3 4))
;=> (1 4 9 16)
```

**See also:** [`map`](./pairs-and-lists.md#map), [`for-each`](./pairs-and-lists.md#for-each)

---

### `filter-map` { #filter-map }
<!-- index: 2+ | Map then filter false values -->

**Syntax:** `(filter-map proc list1 list2 ...)`

Maps *proc* over the list(s) and collects only the truthy results, discarding
`#f` values. Combines `map` and `filter` in a single pass.

```scheme
kaappi> (filter-map (lambda (x) (and (even? x) (* x x))) '(1 2 3 4 5 6))
;=> (4 16 36)
kaappi> (filter-map (lambda (x) (if (positive? x) x #f)) '(-1 2 -3 4 -5))
;=> (2 4)
```

**See also:** [`filter`](#filter), [`map`](./pairs-and-lists.md#map)

---

### `append-map` { #append-map }
<!-- index: 2+ | Map then append results -->

**Syntax:** `(append-map proc list1 list2 ...)`

Maps *proc* over the list(s) -- each call must return a list -- then appends
all the result lists together. Equivalent to
`(concatenate (map proc list1 ...))` but done in a single pass.

```scheme
kaappi> (append-map (lambda (x) (list x (- x))) '(1 2 3))
;=> (1 -1 2 -2 3 -3)
kaappi> (append-map (lambda (x) (if (odd? x) (list x) '())) '(1 2 3 4 5))
;=> (1 3 5)
```

**See also:** [`map`](./pairs-and-lists.md#map), [`concatenate`](#concatenate), [`append`](./pairs-and-lists.md#append)

---

### `pair-for-each` { #pair-for-each }
<!-- index: 2+ | For-each over pairs -->

**Syntax:** `(pair-for-each proc list1 list2 ...)`

Like `for-each`, but *proc* receives the successive pairs (tails) of the
list(s) rather than the successive elements. Return value is unspecified.

```scheme
kaappi> (pair-for-each (lambda (p) (display (car p)) (display " ")) '(a b c))
a b c
```

**See also:** [`for-each`](./pairs-and-lists.md#for-each), [`pair-fold`](#pair-fold)

---

## Filtering and Partitioning

### `filter` { #filter }
<!-- index: 2 | Keep elements satisfying predicate -->

**Syntax:** `(filter pred list)`

Returns a freshly allocated list containing only the elements of *list*
for which `(pred element)` returns true. The order of elements is preserved.

```scheme
kaappi> (filter even? '(1 2 3 4 5 6))
;=> (2 4 6)
kaappi> (filter symbol? '(a 1 b 2 c 3))
;=> (a b c)
kaappi> (filter even? '())
;=> ()
```

**See also:** [`remove`](#remove), [`partition`](#partition), [`filter-map`](#filter-map)

---

### `remove` { #remove }
<!-- index: 2 | Remove elements satisfying predicate -->

**Syntax:** `(remove pred list)`

The complement of `filter`: returns a freshly allocated list containing only
the elements of *list* for which `(pred element)` returns false.
Equivalent to `(filter (lambda (x) (not (pred x))) list)`.

```scheme
kaappi> (remove even? '(1 2 3 4 5 6))
;=> (1 3 5)
kaappi> (remove symbol? '(a 1 b 2 c 3))
;=> (1 2 3)
```

**See also:** [`filter`](#filter), [`partition`](#partition)

---

### `partition` { #partition }
<!-- index: 2 | Split list by predicate into two lists -->

**Syntax:** `(partition pred list)`

Returns two values: a list of elements satisfying *pred*, and a list of
elements not satisfying *pred*. Equivalent to
`(values (filter pred list) (remove pred list))` but traverses the list
only once.

```scheme
kaappi> (call-with-values
         (lambda () (partition even? '(1 2 3 4 5 6)))
         list)
;=> ((2 4 6) (1 3 5))
kaappi> (call-with-values
         (lambda () (partition symbol? '(a 1 b 2)))
         list)
;=> ((a b) (1 2))
```

**See also:** [`filter`](#filter), [`remove`](#remove), [`span`](#span)

---

### `take-while` { #take-while }
<!-- index: 2 | Leading elements satisfying predicate -->

**Syntax:** `(take-while pred list)`

Returns a freshly allocated list of the longest initial prefix of *list*
whose elements all satisfy *pred*.

```scheme
kaappi> (take-while even? '(2 4 6 1 3 5))
;=> (2 4 6)
kaappi> (take-while even? '(1 2 3))
;=> ()
```

**See also:** [`drop-while`](#drop-while), [`span`](#span), [`take`](#take)

---

### `drop-while` { #drop-while }
<!-- index: 2 | Drop leading elements satisfying predicate -->

**Syntax:** `(drop-while pred list)`

Returns the suffix of *list* starting from the first element that does not
satisfy *pred*. The result shares structure with *list*.

```scheme
kaappi> (drop-while even? '(2 4 6 1 3 5))
;=> (1 3 5)
kaappi> (drop-while even? '(1 2 3))
;=> (1 2 3)
```

**See also:** [`take-while`](#take-while), [`break`](#break), [`drop`](#drop)

---

### `span` { #span }
<!-- index: 2 | Split list at first element not satisfying predicate -->

**Syntax:** `(span pred list)`

Returns two values: the longest initial prefix of *list* whose elements all
satisfy *pred*, and the remaining tail. Equivalent to
`(values (take-while pred list) (drop-while pred list))` but traverses
the list only once.

```scheme
kaappi> (call-with-values
         (lambda () (span even? '(2 4 6 1 3 5)))
         list)
;=> ((2 4 6) (1 3 5))
```

**See also:** [`break`](#break), [`take-while`](#take-while), [`drop-while`](#drop-while), [`partition`](#partition)

---

### `break` { #break }
<!-- index: 2 | Split list at first element satisfying predicate -->

**Syntax:** `(break pred list)`

Returns two values: the longest initial prefix of *list* whose elements all
*fail* to satisfy *pred*, and the remaining tail. The complement of `span`:
splits the list at the first element where *pred* succeeds.

```scheme
kaappi> (call-with-values
         (lambda () (break even? '(1 3 5 2 4 6)))
         list)
;=> ((1 3 5) (2 4 6))
```

**See also:** [`span`](#span), [`take-while`](#take-while), [`drop-while`](#drop-while)

---

## Searching

### `find` { #find }
<!-- index: 2 | First element satisfying predicate, or `#f` -->

**Syntax:** `(find pred list)`

Returns the first element of *list* for which `(pred element)` returns true.
Returns `#f` if no element satisfies *pred*. Note that `#f` is
indistinguishable from an element that happens to be `#f`; use `find-tail`
if this matters.

```scheme
kaappi> (find even? '(1 3 5 8 9))
;=> 8
kaappi> (find even? '(1 3 5 7))
;=> #f
kaappi> (find char-alphabetic? (string->list "123abc"))
;=> a
```

**See also:** [`find-tail`](#find-tail), [`any`](#any)

---

### `find-tail` { #find-tail }
<!-- index: 2 | Tail starting at first element satisfying predicate -->

**Syntax:** `(find-tail pred list)`

Returns the first pair (tail) of *list* whose `car` satisfies *pred*.
Returns `#f` if no element satisfies *pred*. Unlike `find`, the result
is the entire sublist, not just the matching element.

```scheme
kaappi> (find-tail even? '(1 3 4 5 6))
;=> (4 5 6)
kaappi> (find-tail even? '(1 3 5))
;=> #f
```

**See also:** [`find`](#find), [`list-index`](#list-index)

---

### `any` { #any }
<!-- index: 2+ | True if predicate holds for any element -->

**Syntax:** `(any pred list1 list2 ...)`

Applies *pred* element-wise across the list(s) and returns the first true
value produced by *pred*. Returns the actual predicate result, not just `#t`.
Returns `#f` if no application of *pred* returns true. Stops at the shortest
list.

```scheme
kaappi> (any even? '(1 2 3))
;=> #t
kaappi> (any even? '(1 3 5))
;=> #f
kaappi> (any (lambda (x) (and (> x 3) x)) '(1 2 5 6))
;=> 5
```

**See also:** [`every`](#every), [`find`](#find)

---

### `every` { #every }
<!-- index: 2+ | True if predicate holds for every element -->

**Syntax:** `(every pred list1 list2 ...)`

Applies *pred* element-wise across the list(s). If all applications return
true, returns the last true value. Returns `#f` as soon as any application
returns false. Returns `#t` for empty lists.

```scheme
kaappi> (every even? '(2 4 6))
;=> #t
kaappi> (every even? '(2 4 5))
;=> #f
kaappi> (every (lambda (x) (and (positive? x) x)) '(1 2 3))
;=> 3
```

**See also:** [`any`](#any)

---

### `count` { #count }
<!-- index: 2+ | Count elements satisfying predicate -->

**Syntax:** `(count pred list1 list2 ...)`

Returns the number of elements in the list(s) that satisfy *pred*. With
multiple lists, applies *pred* element-wise and counts truthy results.
Stops at the shortest list.

```scheme
kaappi> (count even? '(1 2 3 4 5 6))
;=> 3
kaappi> (count < '(1 2 3) '(2 1 4))
;=> 2
```

**See also:** [`filter`](#filter), [`any`](#any), [`length`](./pairs-and-lists.md#length)

---

### `list-index` { #list-index }
<!-- index: 2+ | Index of first element satisfying predicate -->

**Syntax:** `(list-index pred list1 list2 ...)`

Returns the index (zero-based) of the first element in the list(s) that
satisfies *pred*. Returns `#f` if no element satisfies *pred*.
With multiple lists, applies *pred* element-wise.

```scheme
kaappi> (list-index even? '(1 3 4 5 6))
;=> 2
kaappi> (list-index even? '(1 3 5))
;=> #f
kaappi> (list-index < '(1 5 3) '(2 1 4))
;=> 0
```

**See also:** [`find`](#find), [`find-tail`](#find-tail)

---

### `delete` { #delete }
<!-- index: 2+ | Remove all occurrences equal to element -->

**Syntax:** `(delete x list)` | `(delete x list =)`

Returns a freshly allocated list with all elements equal to *x* removed.
Uses `equal?` by default, or the provided equality predicate *=*.

```scheme
kaappi> (delete 3 '(1 2 3 4 3 5))
;=> (1 2 4 5)
kaappi> (delete 'b '(a b c b d))
;=> (a c d)
kaappi> (delete 2 '(1 2 3 4) =)
;=> (1 3 4)
```

**See also:** [`remove`](#remove), [`delete-duplicates`](#delete-duplicates)

---

### `delete-duplicates` { #delete-duplicates }
<!-- index: 1+ | Remove duplicate elements -->

**Syntax:** `(delete-duplicates list)` | `(delete-duplicates list =)`

Returns a freshly allocated list with duplicate elements removed. The first
occurrence of each element is kept. Uses `equal?` by default, or the
provided equality predicate *=*.

```scheme
kaappi> (delete-duplicates '(a b a c b a))
;=> (a b c)
kaappi> (delete-duplicates '(1 2 1 3 2 4))
;=> (1 2 3 4)
kaappi> (delete-duplicates '(1 1.0 2 2.0) =)
;=> (1 2)
```

**See also:** [`delete`](#delete)

---

## Association Lists

### `alist-cons` { #alist-cons }
<!-- index: 3 | `(cons (cons key value) alist)` -->

**Syntax:** `(alist-cons key datum alist)`

Cons a new entry onto the front of an association list. Equivalent to
`(cons (cons key datum) alist)`.

```scheme
kaappi> (alist-cons 'x 1 '((y . 2) (z . 3)))
;=> ((x . 1) (y . 2) (z . 3))
kaappi> (alist-cons 'a 10 '())
;=> ((a . 10))
```

**See also:** [`assoc`](./pairs-and-lists.md#assoc), [`alist-delete`](#alist-delete)

---

### `alist-copy` { #alist-copy }
<!-- index: 1 | Shallow copy of an association list -->

**Syntax:** `(alist-copy alist)`

Returns a freshly allocated shallow copy of *alist*. Each entry pair is
copied (so mutating an entry in the copy does not affect the original),
but the keys and values themselves are shared.

```scheme
kaappi> (define al '((a . 1) (b . 2) (c . 3)))
kaappi> (alist-copy al)
;=> ((a . 1) (b . 2) (c . 3))
```

**See also:** [`alist-cons`](#alist-cons), [`list-copy`](./pairs-and-lists.md#list-copy)

---

### `alist-delete` { #alist-delete }
<!-- index: 2+ | Remove entries with matching key -->

**Syntax:** `(alist-delete key alist)` | `(alist-delete key alist =)`

Returns a freshly allocated association list with all entries whose key
matches *key* removed. Uses `equal?` by default, or the provided equality
predicate *=*.

```scheme
kaappi> (alist-delete 'b '((a . 1) (b . 2) (c . 3)))
;=> ((a . 1) (c . 3))
kaappi> (alist-delete 2 '((1 . a) (2 . b) (3 . c) (2 . d)))
;=> ((1 . a) (3 . c))
```

**See also:** [`alist-cons`](#alist-cons), [`assoc`](./pairs-and-lists.md#assoc)

---

## Set Operations

All `lset-*` procedures take an equality predicate as their first argument.
Elements are compared using this predicate; results do not depend on the
order of elements in the input lists.

### `lset=` { #lset-equal }
<!-- index: 2+ | Set equality -->

**Syntax:** `(lset= = list1 list2 ...)`

Returns `#t` if all the given lists represent the same set of elements
(without regard to order or duplicates), using *=* for comparison. With
zero or one list argument, returns `#t`.

```scheme
kaappi> (lset= eq? '(a b c) '(c b a))
;=> #t
kaappi> (lset= eq? '(a b) '(a b c))
;=> #f
kaappi> (lset= = '(1 2 3) '(3 1 2) '(2 3 1))
;=> #t
```

**See also:** [`list=`](#list-equal)

---

### `lset-adjoin` { #lset-adjoin }
<!-- index: 2+ | Add elements to a set -->

**Syntax:** `(lset-adjoin = list elt ...)`

Adds each *elt* to *list* unless it is already present (according to *=*).
Returns the augmented list.

```scheme
kaappi> (lset-adjoin eq? '(a b c) 'd 'b 'e)
;=> (e d a b c)
kaappi> (lset-adjoin eq? '() 'a 'b)
;=> (b a)
```

**See also:** [`lset-union`](#lset-union)

---

### `lset-union` { #lset-union }
<!-- index: 2+ | Set union -->

**Syntax:** `(lset-union = list1 list2 ...)`

Returns the union of all the given lists. Each element appears at least once
in the result. With zero list arguments, returns `()`.

```scheme
kaappi> (lset-union eq? '(a b) '(b c) '(c d))
;=> (d a b c)
kaappi> (lset-union eq? '(a b) '(a b))
;=> (a b)
```

**See also:** [`lset-intersection`](#lset-intersection), [`lset-difference`](#lset-difference)

---

### `lset-intersection` { #lset-intersection }
<!-- index: 2+ | Set intersection -->

**Syntax:** `(lset-intersection = list1 list2 ...)`

Returns a list of elements that appear in *all* of the given lists. With
one list argument, returns that list.

```scheme
kaappi> (lset-intersection eq? '(a b c d) '(b c e))
;=> (b c)
kaappi> (lset-intersection eq? '(a b c) '(b c d) '(c d e))
;=> (c)
```

**See also:** [`lset-union`](#lset-union), [`lset-difference`](#lset-difference)

---

### `lset-difference` { #lset-difference }
<!-- index: 2+ | Set difference -->

**Syntax:** `(lset-difference = list1 list2 ...)`

Returns a list of elements from *list1* that do not appear in any of the
other lists. With one list argument, returns that list.

```scheme
kaappi> (lset-difference eq? '(a b c d) '(b c e))
;=> (a d)
kaappi> (lset-difference eq? '(a b c d) '(b) '(d))
;=> (a c)
```

**See also:** [`lset-union`](#lset-union), [`lset-intersection`](#lset-intersection), [`lset-xor`](#lset-xor)

---

### `lset-xor` { #lset-xor }
<!-- index: 2+ | Set symmetric difference -->

**Syntax:** `(lset-xor = list1 list2 ...)`

Returns the symmetric difference of the given lists -- elements that appear
in exactly one of the lists. With zero list arguments, returns `()`.
With one list argument, returns that list.

```scheme
kaappi> (lset-xor eq? '(a b c) '(b c d))
;=> (a d)
kaappi> (lset-xor eq? '(a b) '(b c) '(c d))
;=> (a d)
```

**See also:** [`lset-difference`](#lset-difference), [`lset-union`](#lset-union)

---

## Other

### `concatenate` { #concatenate }
<!-- index: 1 | Append a list of lists -->

**Syntax:** `(concatenate list-of-lists)`

Appends all the lists in *list-of-lists* together. Equivalent to
`(apply append list-of-lists)` but does not require a variadic call.
The last element of *list-of-lists* is used directly as the tail.

```scheme
kaappi> (concatenate '((a b) (c d) (e f)))
;=> (a b c d e f)
kaappi> (concatenate '((1 2) (3 4)))
;=> (1 2 3 4)
kaappi> (concatenate '())
;=> ()
```

**See also:** [`append`](./pairs-and-lists.md#append), [`append-map`](#append-map)

---

### `zip` { #zip }
<!-- index: 1+ | Transpose lists into list of lists -->

**Syntax:** `(zip list1 list2 ...)`

Returns a list of lists, where the *i*-th sublist contains the *i*-th
elements of all the argument lists. Stops at the shortest list.
`(zip list1 list2 ...)` is equivalent to `(map list list1 list2 ...)`.

```scheme
kaappi> (zip '(a b c) '(1 2 3))
;=> ((a 1) (b 2) (c 3))
kaappi> (zip '(a b c) '(1 2 3) '(x y z))
;=> ((a 1 x) (b 2 y) (c 3 z))
kaappi> (zip '(a b) '(1 2 3))
;=> ((a 1) (b 2))
```

**See also:** [`unzip1`](#unzip1), [`unzip2`](#unzip2), [`map`](./pairs-and-lists.md#map)

---

### `unzip1` { #unzip1 }
<!-- index: 1 | Unzip list of lists (first elements) -->

**Syntax:** `(unzip1 list-of-lists)`

Takes a list of lists and returns a list of the first elements.
Equivalent to `(map car list-of-lists)`.

```scheme
kaappi> (unzip1 '((a b) (c d) (e f)))
;=> (a c e)
```

**See also:** [`unzip2`](#unzip2), [`zip`](#zip)

---

### `unzip2` { #unzip2 }
<!-- index: 1 | Unzip list of lists (first two elements as values) -->

**Syntax:** `(unzip2 list-of-lists)`

Takes a list of lists and returns two values: a list of first elements
and a list of second elements.

```scheme
kaappi> (call-with-values
         (lambda () (unzip2 '((a b) (c d) (e f))))
         list)
;=> ((a c e) (b d f))
```

**See also:** [`unzip1`](#unzip1), [`zip`](#zip)

---

### `append-reverse` { #append-reverse }
<!-- index: 2 | `(append (reverse list1) list2)` -->

**Syntax:** `(append-reverse rev-head tail)`

Appends the reverse of *rev-head* onto *tail*. Equivalent to
`(append (reverse rev-head) tail)` but more efficient since it does not
allocate an intermediate reversed list.

```scheme
kaappi> (append-reverse '(3 2 1) '(4 5 6))
;=> (1 2 3 4 5 6)
kaappi> (append-reverse '(a b) '())
;=> (b a)
```

**See also:** [`reverse`](./pairs-and-lists.md#reverse), [`append`](./pairs-and-lists.md#append)

---

### `length+` { #length-plus }
<!-- index: 1 | Length or `#f` for circular lists -->

**Syntax:** `(length+ list)`

Returns the length of *list* as a non-negative integer, or `#f` if *list*
is circular. Unlike `length`, this procedure does not loop forever on
circular lists. Uses Floyd's cycle detection algorithm.

```scheme
kaappi> (length+ '(a b c))
;=> 3
kaappi> (length+ '())
;=> 0
kaappi> (length+ (circular-list 1 2 3))
;=> #f
```

**See also:** [`length`](./pairs-and-lists.md#length), [`circular-list?`](#circular-list-pred)
