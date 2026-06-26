# BDD Testing

`(kaappi bdd)` — BDD test framework with describe/it blocks, matchers, and
lifecycle hooks.

```bash
thottam install kaappi-bdd
```

Pure Scheme — no dependencies. Inspired by RSpec and Jasmine.

## Quick start

```scheme
(import (scheme base) (kaappi bdd))

(describe "arithmetic"
  (it "adds numbers"
    (expect (+ 2 3) to-equal 5))

  (it "multiplies"
    (expect (* 6 7) to-equal 42))

  (context "division"
    (it "divides evenly"
      (expect (/ 10 2) to-equal 5))

    (it "raises on division by zero"
      (expect-error (/ 1 0)))))

(run-specs)
```

Run it:

```bash
kaappi tests/test-math.scm
```

Output:

```
arithmetic
  adds numbers  ok
  multiplies  ok
  division
    divides evenly  ok
    raises on division by zero  ok

4 examples, 0 failures
```

`run-specs` prints the summary and exits with code 1 if any spec failed.

## Describe, context, and it

`describe` groups related specs. `context` is an alias for `describe`,
conventionally used for "when" or "with" conditions. `it` defines an
individual spec:

```scheme
(describe "string-append"
  (context "with two strings"
    (it "concatenates them"
      (expect (string-append "a" "b") to-equal "ab")))

  (context "with empty strings"
    (it "returns the other string"
      (expect (string-append "" "x") to-equal "x"))))
```

Nesting is unlimited — each level indents in the output.

## Matchers

All matchers are used with `expect`:

```scheme
(expect actual matcher [args ...])
```

### `to-equal` — deep structural equality

Uses `equal?`. Works with lists, vectors, strings, numbers:

```scheme
(expect '(1 2 3) to-equal (list 1 2 3))
(expect "hello" to-equal (string-append "hel" "lo"))
(expect #(1 2) to-equal (vector 1 2))
```

On failure, shows expected and actual values:

```
  adds numbers  FAIL

Failures:

  1) adds numbers
     expected: 5
          got: 4
```

### `to-eqv` — value identity

Uses `eqv?`. Best for numbers, characters, and booleans:

```scheme
(expect 42 to-eqv (* 6 7))
(expect #\a to-eqv (string-ref "abc" 0))
```

### `to-be` — predicate check

Passes if `(pred actual)` returns a truthy value:

```scheme
(expect 42 to-be number?)
(expect "hello" to-be string?)
```

### `to-be-truthy` / `to-be-falsy`

```scheme
(expect (> 5 0) to-be-truthy)
(expect (> 0 5) to-be-falsy)
```

### `to-be-a` — type check

Like `to-be`, reads better for type predicates:

```scheme
(expect '(1 2) to-be-a pair?)
(expect 42 to-be-a number?)
```

### `to-contain` — membership

Works with lists, strings, and vectors:

```scheme
(expect '(a b c) to-contain 'b)
(expect "hello world" to-contain "world")
(expect (vector 1 2 3) to-contain 2)
```

### `to-satisfy` — custom predicate

```scheme
(expect 42 to-satisfy even?)
(expect '(1 2 3) to-satisfy (lambda (l) (= (length l) 3)))
```

### `to-be-close-to` — floating point tolerance

Passes if `|actual - expected| < tolerance`:

```scheme
(expect 3.14 to-be-close-to 3.14159 0.01)
(expect (sqrt 2) to-be-close-to 1.414 0.001)
```

### `to-be-null`

```scheme
(expect '() to-be-null)
```

### `to-be-greater-than` / `to-be-less-than`

```scheme
(expect 10 to-be-greater-than 5)
(expect 3 to-be-less-than 7)
```

### Negated matchers

```scheme
(expect 1 not-to-equal 2)
(expect '(1 2 3) not-to-contain 4)
```

## Error expectations

`expect-error` passes if the body raises any error:

```scheme
(it "raises on bad input"
  (expect-error (/ 1 0)))

(it "catches type errors"
  (expect-error (+ 1 "two")))
```

Multiple expressions in the body are supported — the error can come from any
of them.

## Hooks

### `before-each` / `after-each`

Run around every `it` in the enclosing `describe` block. Hooks cascade
through nesting — outer hooks run before inner hooks:

```scheme
(define db '())

(describe "user database"
  (before-each
    (set! db '(("alice" . "admin") ("bob" . "user"))))
  (after-each
    (set! db '()))

  (it "starts with two users"
    (expect (length db) to-equal 2))

  (context "after adding a user"
    (before-each
      (set! db (cons '("carol" . "user") db)))

    (it "has three users"
      (expect (length db) to-equal 3))))
```

Hook execution order for "has three users":

1. Outer `before-each` — reset db to two users
2. Inner `before-each` — add carol
3. Spec body — check length is 3
4. Outer `after-each` — clear db

### `before-all` / `after-all`

Run once per group, not per spec:

```scheme
(describe "expensive setup"
  (before-all (connect-to-database!))
  (after-all (disconnect-database!))

  (it "queries data" ...)
  (it "inserts data" ...))
```

## Pending specs

Mark specs as pending in three ways:

```scheme
;; 1. Skip with xit
(xit "not implemented yet"
  (expect 1 to-equal 2))

;; 2. Skip an entire group with xdescribe
(xdescribe "future feature"
  (it "does something" ...))

;; 3. Mark pending inside a spec
(it "work in progress"
  (pending "waiting on upstream fix"))
```

Pending specs appear in the output and summary:

```
  not implemented yet  (pending)

5 examples, 0 failures, 1 pending
```

## Multiple expects per spec

A spec can contain multiple `expect` calls. The first failure stops the spec:

```scheme
(it "validates all fields"
  (expect name to-be string?)
  (expect age to-be-greater-than 0)
  (expect email to-contain "@"))
```

## Testing a library

Typical project layout:

```
my-lib/
  lib/
    my-lib/
      parser.sld
  tests/
    test-parser.scm
```

`tests/test-parser.scm`:

```scheme
(import (scheme base) (kaappi bdd) (my-lib parser))

(describe "parser"
  (it "parses integers"
    (expect (parse "42") to-equal 42))

  (it "rejects bad input"
    (expect-error (parse "???"))))

(run-specs)
```

Run from the project root:

```bash
kaappi --lib-path ./lib tests/test-parser.scm
```

## API reference

### Structure

| Form | Description |
|------|-------------|
| `(describe name body ...)` | Named test group |
| `(context name body ...)` | Alias for `describe` |
| `(it name body ...)` | Individual spec |
| `(xit name body ...)` | Pending spec (skipped) |
| `(xdescribe name body ...)` | Pending group (skipped) |
| `(pending [reason])` | Mark current spec pending |

### Matchers

| Matcher | Description |
|---------|-------------|
| `(expect val to-equal expected)` | Deep equality (`equal?`) |
| `(expect val to-eqv expected)` | Value identity (`eqv?`) |
| `(expect val to-be pred)` | Predicate check |
| `(expect val to-be-truthy)` | Not `#f` |
| `(expect val to-be-falsy)` | Is `#f` |
| `(expect val to-be-a pred)` | Type check |
| `(expect val to-contain elem)` | Membership (list/string/vector) |
| `(expect val to-satisfy pred)` | Custom predicate |
| `(expect val to-be-close-to exp tol)` | Within tolerance |
| `(expect val to-be-null)` | Empty list |
| `(expect val to-be-greater-than n)` | `(> val n)` |
| `(expect val to-be-less-than n)` | `(< val n)` |
| `(expect val not-to-equal expected)` | Not equal |
| `(expect val not-to-contain elem)` | Not a member |
| `(expect-error body ...)` | Body raises error |

### Hooks

| Form | Description |
|------|-------------|
| `(before-each body ...)` | Run before every spec in scope |
| `(after-each body ...)` | Run after every spec in scope |
| `(before-all body ...)` | Run once at start of group |
| `(after-all body ...)` | Run once at end of group |

### Running

| Procedure | Description |
|-----------|-------------|
| `(run-specs)` | Print summary, exit 1 on failure |
