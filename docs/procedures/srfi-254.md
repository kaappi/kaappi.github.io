# Ephemerons and Guardians (SRFI-254)

Weak references and post-mortem finalization, integrated with the garbage
collector. Import with `(import (srfi 254))`.

An **ephemeron** is a key/value pair whose value is kept alive only while
its key is reachable through some path that does not pass through the
value. When the key becomes unreachable, the collector *breaks* the
ephemeron: key and value both read as `#f` afterwards. Unlike a plain
weak-key pair, an ephemeron breaks even when its value references its own
key — the classic leak case that motivates the abstraction.

A **guardian** provides post-mortem finalization: objects registered with
a guardian are *resurrected* by the collector once they become otherwise
unreachable, so cleanup code can run for them after death.

The component libraries `(srfi 254 ephemerons)`,
`(srfi 254 guardians)`, and `(srfi 254 transport-cell-guardians)` export
each slice separately; `(srfi 254 ephemerons-and-guardians)` and
`(srfi 254)` export everything.

!!! note
    Kaappi's collector is non-moving, so `current-hash` is a stable
    identity hash and transport cell guardians are degenerate: a key is
    never transported, a registered cell never breaks, and calling a
    transport cell guardian with no arguments always returns `#f`. The
    API is still provided in full for portability.

---

## Ephemerons

### `make-ephemeron` { #make-ephemeron }
<!-- index: 2 | Create an ephemeron pairing key and value -->

**Syntax:** `(make-ephemeron key value)`

Returns a new ephemeron associating *key* with *value*. The collector
retains *value* only while *key* is reachable through a path that does
not pass through *value*; once *key* becomes unreachable the ephemeron
is broken and both slots read as `#f`.

```scheme
kaappi> (define e (make-ephemeron 'k 'v))
kaappi> (ephemeron-key e)
;=> k
kaappi> (ephemeron-value e)
;=> v
```

### `ephemeron?` { #ephemeron }
<!-- index: 1 | Test whether obj is an ephemeron -->

**Syntax:** `(ephemeron? obj)`

Returns `#t` if *obj* is an ephemeron, `#f` otherwise.

```scheme
kaappi> (ephemeron? (make-ephemeron 'k 'v))
;=> #t
kaappi> (ephemeron? 'x)
;=> #f
```

### `ephemeron-key` { #ephemeron-key }
<!-- index: 1 | Key of an ephemeron, or #f once broken -->

**Syntax:** `(ephemeron-key ephemeron)`

Returns the key of *ephemeron*, or `#f` if the ephemeron has been
broken.

### `ephemeron-value` { #ephemeron-value }
<!-- index: 1 | Value of an ephemeron, or #f once broken -->

**Syntax:** `(ephemeron-value ephemeron)`

Returns the value of *ephemeron*, or `#f` if the ephemeron has been
broken. On break the value slot is cleared, so a broken ephemeron never
retains its value.

### `ephemeron-broken?` { #ephemeron-broken }
<!-- index: 1 | Test whether the collector has broken the ephemeron -->

**Syntax:** `(ephemeron-broken? ephemeron)`

Returns `#t` if the collector has broken *ephemeron* (its key became
unreachable), `#f` otherwise.

```scheme
kaappi> (define e (make-ephemeron 'k 'v))
kaappi> (ephemeron-broken? e)
;=> #f
```

### `ephemeron-ref` { #ephemeron-ref }
<!-- index: 2+ | Value if key matches and unbroken, else default -->

**Syntax:** `(ephemeron-ref ephemeron key)` | `(ephemeron-ref ephemeron key default)`

Returns the value of *ephemeron* if it is unbroken and its key is `eq?`
to *key*; otherwise returns *default* (`#f` when omitted). This is the
lookup shape used when building weak tables out of ephemerons.

```scheme
kaappi> (define e (make-ephemeron 'k 'v))
kaappi> (ephemeron-ref e 'k)
;=> v
kaappi> (ephemeron-ref e 'other 'missing)
;=> missing
```

---

## Guardians

### `make-guardian` { #make-guardian }
<!-- index: 0 | Create a guardian for post-mortem finalization -->

**Syntax:** `(make-guardian)`

Returns a new guardian. A guardian is itself a procedure with three
calling forms:

- `(g obj)` — register *obj* with the guardian
- `(g obj rep)` — register *obj*, with *rep* as the representative to
  hand back in its place
- `(g)` — return one object that has died since the last call (or its
  representative), or `#f` if none is pending

When a registered object becomes unreachable, the collector resurrects
it: subsequent zero-argument calls on the guardian return it (or its
representative) for cleanup. Objects that are still reachable are never
returned.

```scheme
(define g (make-guardian))
(g (open-input-file "data.txt") 'data-port)

;; ... after the port becomes unreachable and a collection runs:
(let loop ()
  (let ((dead (g)))
    (when dead
      ;; run finalization for dead, e.g. log or release resources
      (loop))))
```

### `guardian?` { #guardian }
<!-- index: 1 | Test whether obj is a guardian -->

**Syntax:** `(guardian? obj)`

Returns `#t` if *obj* is a guardian created by `make-guardian`, `#f`
otherwise — including for transport cell guardians, which are a distinct
type.

```scheme
kaappi> (guardian? (make-guardian))
;=> #t
kaappi> (guardian? (make-transport-cell-guardian))
;=> #f
```

---

## Transport cell guardians

Transport cell guardians exist for collectors that move (transport)
objects, letting a program observe when a key is relocated. See the note
at the top of this page: on Kaappi's non-moving collector they are
degenerate but fully present.

### `make-transport-cell-guardian` { #make-transport-cell-guardian }
<!-- index: 0 | Create a transport cell guardian -->

**Syntax:** `(make-transport-cell-guardian)`

Returns a new transport cell guardian — a procedure with two calling
forms:

- `(tcg key value)` — register *key*/*value*, returning a transport cell
- `(tcg)` — return a cell whose key was transported since the last call,
  or `#f` if none (always `#f` on Kaappi's non-moving collector)

```scheme
kaappi> (define tcg (make-transport-cell-guardian))
kaappi> (define c (tcg 'k 'v))
kaappi> (transport-cell? c)
;=> #t
```

### `transport-cell-guardian?` { #transport-cell-guardian }
<!-- index: 1 | Test whether obj is a transport cell guardian -->

**Syntax:** `(transport-cell-guardian? obj)`

Returns `#t` if *obj* is a transport cell guardian, `#f` otherwise.

### `transport-cell?` { #transport-cell }
<!-- index: 1 | Test whether obj is a transport cell -->

**Syntax:** `(transport-cell? obj)`

Returns `#t` if *obj* is a transport cell (the object returned by
registering a key with a transport cell guardian), `#f` otherwise.

### `transport-cell-key` { #transport-cell-key }
<!-- index: 1 | Key of a transport cell, or #f once broken -->

**Syntax:** `(transport-cell-key cell)`

Returns the key registered in *cell*, or `#f` if the cell has been
broken.

### `transport-cell-value` { #transport-cell-value }
<!-- index: 1 | Value of a transport cell, or #f once broken -->

**Syntax:** `(transport-cell-value cell)`

Returns the value registered in *cell*, or `#f` if the cell has been
broken.

### `transport-cell-broken?` { #transport-cell-broken }
<!-- index: 1 | Test whether the transport cell has been broken -->

**Syntax:** `(transport-cell-broken? cell)`

Returns `#t` if *cell* has been broken, `#f` otherwise. Never `#t` on
Kaappi's non-moving collector.

### `current-hash` { #current-hash }
<!-- index: 1 | Stable identity hash of an object -->

**Syntax:** `(current-hash obj)`

Returns an exact non-negative integer identity hash for *obj*. On
Kaappi's non-moving collector the result is stable for the lifetime of
the object — two calls on the same (`eq?`) object always agree, across
collections.

```scheme
kaappi> (define o (list 1 2 3))
kaappi> (= (current-hash o) (current-hash o))
;=> #t
```

---

## Shared

### `reference-barrier` { #reference-barrier }
<!-- index: 1 | Keep an object reachable up to this point -->

**Syntax:** `(reference-barrier obj)`

Guarantees that *obj* is treated as reachable up to this point in the
program, preventing the collector from breaking ephemerons keyed on it
(or resurrecting it through a guardian) any earlier. Returns an
unspecified value.
