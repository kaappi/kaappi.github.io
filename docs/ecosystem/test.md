# Testing

`(kaappi test)` — test framework with groups, assertions, and reporting.

```bash
thottam install kaappi-test
```

Pure Scheme — no dependencies. SRFI-64 inspired.

## Quick start

```scheme
(import (kaappi test))

(test-group "arithmetic"
  (test-equal "2+2" 4 (+ 2 2))
  (test-assert "positive" (> 5 0)))

(test-group "errors"
  (test-error "type error" (lambda () (+ 1 "two"))))

(test-exit)
```

Run it:

```bash
kaappi tests/test-math.scm
```

Output:

```
arithmetic
  ok: 2+2
  ok: positive
errors
  ok: type error

3 tests: 3 passed
```

`test-exit` prints the summary and exits with code 1 if any test failed.

## Assertions

### `test-equal` — deep structural equality

Uses `equal?` to compare. Works with lists, vectors, strings, numbers:

```scheme
(test-equal "lists match" '(1 2 3) (list 1 2 3))
(test-equal "strings" "hello" (string-append "hel" "lo"))
(test-equal "vectors" #(1 2) (vector 1 2))
(test-equal "nested" '((a . 1)) (list (cons 'a 1)))
```

On failure, shows expected and actual values:

```
  FAIL: lists match
    expected: (1 2 3)
    actual:   (1 2 4)
```

### `test-eqv` — value identity

Uses `eqv?`. Best for numbers, characters, and booleans:

```scheme
(test-eqv "exact number" 42 (* 6 7))
(test-eqv "character" #\a (string-ref "abc" 0))
(test-eqv "boolean" #t (pair? '(1)))
```

### `test-assert` — truthiness

Passes if the expression is any non-`#f` value:

```scheme
(test-assert "positive" (> 5 0))
(test-assert "string check" (string? "hello"))
(test-assert "list is pair" (pair? '(1 2 3)))
```

### `test-not` — falsiness

Passes if the expression is `#f`:

```scheme
(test-not "empty is not pair" (pair? '()))
(test-not "zero is not positive" (> 0 5))
```

### `test-approximate` — floating point tolerance

Passes if `|expected - actual| <= tolerance`:

```scheme
(test-approximate "pi" 3.14159 (acos -1) 0.001)
(test-approximate "sqrt2" 1.414 (sqrt 2) 0.001)
```

### `test-error` — expected errors

Passes if the thunk raises an error:

```scheme
(test-error "division by zero" (lambda () (/ 1 0)))
(test-error "type error" (lambda () (+ 1 "two")))
(test-error "out of range" (lambda () (vector-ref #(1 2) 5)))
```

The thunk must be a zero-argument lambda — it is called inside a `guard`
that catches the error.

## Test groups

Groups organize tests into labeled sections. They nest:

```scheme
(test-group "parser"
  (test-group "numbers"
    (test-equal "integer" 42 (parse-int "42"))
    (test-equal "negative" -7 (parse-int "-7")))

  (test-group "strings"
    (test-equal "simple" "hello" (parse-str "\"hello\""))
    (test-equal "empty" "" (parse-str "\"\""))))
```

Output:

```
parser
  numbers
    ok: integer
    ok: negative
  strings
    ok: simple
    ok: empty

4 tests: 4 passed
```

## Controlling output

### Suppress passing tests

For large suites, show only failures and the summary:

```scheme
(test-verbose! #f)
```

### Get test counts

```scheme
(test-pass-count)   ;=> number of passed tests
(test-fail-count)   ;=> number of failed tests
(test-skip-count)   ;=> number of skipped tests
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
(import (scheme base)
        (kaappi test)
        (my-lib parser))

(test-group "parser"
  (test-equal "parse integer" 42 (parse "42"))
  (test-error "bad input" (lambda () (parse "???"))))

(test-exit)
```

Run from the project root:

```bash
kaappi tests/test-parser.scm
```

## Setup and teardown

Use `let` bindings inside groups for per-group setup:

```scheme
(import (kaappi test) (kaappi sqlite))

(test-group "database"
  (let ((db (sqlite-open ":memory:")))
    (sqlite-exec db "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")

    (test-equal "insert"
      1 (sqlite-exec db "INSERT INTO users (name) VALUES (?)" "Alice"))

    (test-equal "query"
      '#(1 "Alice")
      (car (sqlite-query db "SELECT * FROM users")))

    (sqlite-close db)))
```

## Checking procedure coverage

After writing tests, verify all exported procedures are exercised:

```bash
kaappi --coverage --lib-path ./lib tests/test-parser.scm
```

```
Coverage:
  (my-lib parser)    5/5  100.0%
  Overall: 5/5 procedures covered (100.0%)
```

Uncalled procedures are listed by name. For CI, generate Cobertura XML:

```bash
kaappi --coverage-xml coverage.xml --lib-path ./lib tests/test-parser.scm
```

## Running in CI

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Kaappi
        run: curl -fsSL https://kaappi-lang.org/install.sh | bash
      - name: Install dependencies
        run: thottam install kaappi-test
      - name: Run tests
        run: kaappi tests/test-all.scm
```

## Running multiple test files

Create a runner that loads all test files:

```scheme
;; tests/test-all.scm
(import (kaappi test))

(load "tests/test-parser.scm")
(load "tests/test-validator.scm")

(test-exit)
```

Or aggregate in the shell:

```bash
kaappi tests/test-parser.scm && kaappi tests/test-validator.scm
```

## API reference

### Groups

| Procedure | Description |
|-----------|-------------|
| `(test-group name body ...)` | Labeled test group |
| `(test-begin name)` | Start group (low-level) |
| `(test-end)` | End group (low-level) |

### Assertions

| Procedure | Description |
|-----------|-------------|
| `(test-equal name expected actual)` | Deep equality (`equal?`) |
| `(test-eqv name expected actual)` | Value identity (`eqv?`) |
| `(test-assert name expr)` | Truthy check |
| `(test-not name expr)` | Falsy check |
| `(test-approximate name expected actual tol)` | Within tolerance |
| `(test-error name thunk)` | Expects error |

### Reporting

| Procedure | Description |
|-----------|-------------|
| `(test-exit)` | Print summary, exit 1 on failure |
| `(test-verbose! bool)` | Show/hide passing tests |
| `(test-pass-count)` | Number of passed tests |
| `(test-fail-count)` | Number of failed tests |
| `(test-skip-count)` | Number of skipped tests |
