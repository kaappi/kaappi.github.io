# Hash Tables (SRFI-69)

Hash tables provide efficient key-value storage with average O(1) lookup.
Import with `(import (srfi 69))`.

## Performance characteristics

| Operation | Average | Worst case |
|-----------|:-------:|:----------:|
| `hash-table-ref` | O(1) | O(n) |
| `hash-table-set!` | O(1) | O(n) |
| `hash-table-delete!` | O(1) | O(n) |
| `hash-table-size` | O(1) | O(1) |
| `hash-table->alist` | O(n) | O(n) |
| `hash-table-keys` | O(n) | O(n) |

Kaappi uses open-addressing with linear probing. The table resizes
automatically when the load factor exceeds a threshold.

**When to use hash tables vs. alists:**

- Use hash tables when you have more than ~10 key-value pairs or when
  lookup performance matters — `hash-table-ref` is O(1) vs. `assoc` O(n)
- Use [alists](pairs-and-lists.md#assoc) for small, short-lived mappings
  or when you need the data as a list (e.g., JSON serialization)
- Hash tables are mutable; alists are persistent (the original is unchanged
  when you `cons` a new pair onto the front)

---

## Construction

### `make-hash-table` { #make-hash-table }

**Syntax:** `(make-hash-table)` | `(make-hash-table equal-proc)` | `(make-hash-table equal-proc hash-proc)`

Returns a newly allocated empty hash table. The optional *equal-proc*
specifies the equality predicate used to compare keys (default is
`equal?`). The optional *hash-proc* specifies the hash function used
to compute bucket indices; it must be consistent with the equality
predicate. When using `eq?` or `eqv?` as the equality predicate,
provide a matching hash function for correct behavior.

```scheme
kaappi> (define ht (make-hash-table))
kaappi> (hash-table? ht)
;=> #t
kaappi> (hash-table-size ht)
;=> 0
kaappi> (define ht2 (make-hash-table string=? string-hash))
kaappi> (hash-table-set! ht2 "key" 42)
kaappi> (hash-table-ref ht2 "key")
;=> 42
```

**See also:** [`hash-table?`](#hash-table-pred),
[`alist->hash-table`](#alist-to-hash-table)

---

### `alist->hash-table` { #alist-to-hash-table }

**Syntax:** `(alist->hash-table alist)` | `(alist->hash-table alist equal-proc)` | `(alist->hash-table alist equal-proc hash-proc)`

Creates a new hash table and populates it from the association list
*alist*. Each element of *alist* should be a pair `(key . value)`. If
*alist* contains duplicate keys, the first occurrence takes precedence.
The optional *equal-proc* and *hash-proc* arguments work as in
`make-hash-table`.

```scheme
kaappi> (define ht (alist->hash-table '((a . 1) (b . 2) (c . 3))))
kaappi> (hash-table-ref ht 'a)
;=> 1
kaappi> (hash-table-ref ht 'c)
;=> 3
kaappi> (hash-table-size ht)
;=> 3
kaappi> (alist->hash-table '((x . 10) (x . 20)))
kaappi> (hash-table-ref (alist->hash-table '((x . 10) (x . 20))) 'x)
;=> 10
```

**See also:** [`hash-table->alist`](#hash-table-to-alist),
[`make-hash-table`](#make-hash-table)

---

### `hash-table-copy` { #hash-table-copy }

**Syntax:** `(hash-table-copy ht)`

Returns a shallow copy of hash table *ht*. The new table has the same
equality and hash procedures, and contains the same key-value
associations. Mutating the copy does not affect the original, and vice
versa. Values are not recursively copied -- the copy shares the same
value objects.

```scheme
kaappi> (define ht (alist->hash-table '((a . 1) (b . 2))))
kaappi> (define ht2 (hash-table-copy ht))
kaappi> (hash-table-set! ht2 'a 99)
kaappi> (hash-table-ref ht 'a)
;=> 1
kaappi> (hash-table-ref ht2 'a)
;=> 99
```

**See also:** [`make-hash-table`](#make-hash-table),
[`hash-table->alist`](#hash-table-to-alist)

---

## Type Predicate

### `hash-table?` { #hash-table-pred }

**Syntax:** `(hash-table? obj)`

Returns `#t` if *obj* is a hash table, `#f` otherwise.

```scheme
kaappi> (hash-table? (make-hash-table))
;=> #t
kaappi> (hash-table? '((a . 1) (b . 2)))
;=> #f
kaappi> (hash-table? '#(1 2 3))
;=> #f
kaappi> (hash-table? "hello")
;=> #f
```

**See also:** [`make-hash-table`](#make-hash-table),
[`hash-table?`](./type-checking.md#hash-table)

---

## Lookup and Mutation

### `hash-table-ref` { #hash-table-ref }

**Syntax:** `(hash-table-ref ht key)` | `(hash-table-ref ht key default)`

Returns the value associated with *key* in hash table *ht*. If *key*
is not found and a *default* is provided, returns *default* (if it is
a thunk, it is called and the result is returned). If *key* is not
found and no default is provided, an error is raised. Keys are compared
using the hash table's equality predicate (`equal?` by default).

```scheme
kaappi> (define ht (alist->hash-table '((a . 1) (b . 2) (c . 3))))
kaappi> (hash-table-ref ht 'a)
;=> 1
kaappi> (hash-table-ref ht 'b)
;=> 2
kaappi> (hash-table-ref ht 'z #f)
;=> #f
kaappi> (hash-table-ref ht 'z 0)
;=> 0
```

**See also:** [`hash-table-exists?`](#hash-table-exists),
[`hash-table-set!`](#hash-table-set)

---

### `hash-table-set!` { #hash-table-set }

**Syntax:** `(hash-table-set! ht key value)`

Associates *key* with *value* in hash table *ht*. If *key* already
exists, its value is replaced. Returns void.

```scheme
kaappi> (define ht (make-hash-table))
kaappi> (hash-table-set! ht 'x 10)
kaappi> (hash-table-set! ht 'y 20)
kaappi> (hash-table-ref ht 'x)
;=> 10
kaappi> (hash-table-set! ht 'x 99)
kaappi> (hash-table-ref ht 'x)
;=> 99
kaappi> (hash-table-size ht)
;=> 2
```

**See also:** [`hash-table-ref`](#hash-table-ref),
[`hash-table-delete!`](#hash-table-delete),
[`hash-table-update!/default`](#hash-table-update-default)

---

### `hash-table-delete!` { #hash-table-delete }

**Syntax:** `(hash-table-delete! ht key)`

Removes the association for *key* from hash table *ht*. If *key* is
not present, the table is unchanged. Returns void.

```scheme
kaappi> (define ht (alist->hash-table '((a . 1) (b . 2) (c . 3))))
kaappi> (hash-table-size ht)
;=> 3
kaappi> (hash-table-delete! ht 'b)
kaappi> (hash-table-size ht)
;=> 2
kaappi> (hash-table-exists? ht 'b)
;=> #f
kaappi> (hash-table-delete! ht 'z)
kaappi> (hash-table-size ht)
;=> 2
```

**See also:** [`hash-table-set!`](#hash-table-set),
[`hash-table-exists?`](#hash-table-exists)

---

### `hash-table-exists?` { #hash-table-exists }

**Syntax:** `(hash-table-exists? ht key)`

Returns `#t` if *key* is associated with a value in hash table *ht*,
`#f` otherwise.

```scheme
kaappi> (define ht (alist->hash-table '((a . 1) (b . 2))))
kaappi> (hash-table-exists? ht 'a)
;=> #t
kaappi> (hash-table-exists? ht 'z)
;=> #f
kaappi> (hash-table-delete! ht 'a)
kaappi> (hash-table-exists? ht 'a)
;=> #f
```

**See also:** [`hash-table-ref`](#hash-table-ref),
[`hash-table-size`](#hash-table-size)

---

### `hash-table-update!/default` { #hash-table-update-default }

**Syntax:** `(hash-table-update!/default ht key proc default)`

Updates the value associated with *key* in *ht* by applying *proc* to
the current value. If *key* does not exist, *proc* is applied to
*default* and the result is stored. This is equivalent to:

```scheme
(hash-table-set! ht key (proc (hash-table-ref ht key default)))
```

but may be implemented more efficiently.

```scheme
kaappi> (define ht (make-hash-table))
kaappi> (hash-table-update!/default ht 'count add1 0)
kaappi> (hash-table-ref ht 'count)
;=> 1
kaappi> (hash-table-update!/default ht 'count add1 0)
kaappi> (hash-table-ref ht 'count)
;=> 2
kaappi> (define counts (make-hash-table))
kaappi> (for-each (lambda (word)
                    (hash-table-update!/default counts word add1 0))
                  '(the cat sat on the mat))
kaappi> (hash-table-ref counts 'the)
;=> 2
kaappi> (hash-table-ref counts 'cat)
;=> 1
```

**See also:** [`hash-table-set!`](#hash-table-set),
[`hash-table-ref`](#hash-table-ref)

---

## Size and Inspection

### `hash-table-size` { #hash-table-size }

**Syntax:** `(hash-table-size ht)`

Returns the number of key-value associations in hash table *ht*.

```scheme
kaappi> (hash-table-size (make-hash-table))
;=> 0
kaappi> (hash-table-size (alist->hash-table '((a . 1) (b . 2) (c . 3))))
;=> 3
```

**See also:** [`hash-table-keys`](#hash-table-keys),
[`hash-table-exists?`](#hash-table-exists)

---

### `hash-table-keys` { #hash-table-keys }

**Syntax:** `(hash-table-keys ht)`

Returns a list of all keys in hash table *ht*. The order of keys is
unspecified.

```scheme
kaappi> (define ht (alist->hash-table '((a . 1) (b . 2) (c . 3))))
kaappi> (sort (hash-table-keys ht) symbol<?)
;=> (a b c)
kaappi> (hash-table-keys (make-hash-table))
;=> ()
```

**See also:** [`hash-table-values`](#hash-table-values),
[`hash-table-size`](#hash-table-size)

---

### `hash-table-values` { #hash-table-values }

**Syntax:** `(hash-table-values ht)`

Returns a list of all values in hash table *ht*. The order of values is
unspecified but corresponds to the order of `hash-table-keys`.

```scheme
kaappi> (define ht (alist->hash-table '((a . 1) (b . 2) (c . 3))))
kaappi> (sort (hash-table-values ht) <)
;=> (1 2 3)
kaappi> (hash-table-values (make-hash-table))
;=> ()
```

**See also:** [`hash-table-keys`](#hash-table-keys),
[`hash-table->alist`](#hash-table-to-alist)

---

## Iteration and Conversion

### `hash-table-walk` { #hash-table-walk }

**Syntax:** `(hash-table-walk ht proc)`

Calls `(proc key value)` for each key-value association in hash table
*ht*. The order of iteration is unspecified. The return value is void.
It is an error to mutate *ht* during the walk (add or remove keys).

```scheme
kaappi> (define ht (alist->hash-table '((a . 1) (b . 2) (c . 3))))
kaappi> (define sum 0)
kaappi> (hash-table-walk ht (lambda (k v) (set! sum (+ sum v))))
kaappi> sum
;=> 6
kaappi> (hash-table-walk ht
         (lambda (k v) (display k) (display ": ") (display v) (newline)))
a: 1
b: 2
c: 3
```

!!! note
    The output order above is illustrative. Hash table iteration order
    is not guaranteed and may differ between runs.

**See also:** [`hash-table-keys`](#hash-table-keys),
[`hash-table->alist`](#hash-table-to-alist),
[`for-each`](./pairs-and-lists.md#for-each)

---

### `hash-table->alist` { #hash-table-to-alist }

**Syntax:** `(hash-table->alist ht)`

Returns an association list containing the key-value pairs of hash
table *ht*. Each element is a pair `(key . value)`. The order of
elements is unspecified.

```scheme
kaappi> (define ht (make-hash-table))
kaappi> (hash-table-set! ht 'x 10)
kaappi> (hash-table-set! ht 'y 20)
kaappi> (sort (hash-table->alist ht)
              (lambda (a b) (symbol<? (car a) (car b))))
;=> ((x . 10) (y . 20))
kaappi> (hash-table->alist (make-hash-table))
;=> ()
```

**See also:** [`alist->hash-table`](#alist-to-hash-table),
[`hash-table-keys`](#hash-table-keys),
[`hash-table-values`](#hash-table-values)
