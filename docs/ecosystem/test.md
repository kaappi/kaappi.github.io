# kaappi-test — Test Framework

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

Output:

```
arithmetic
  ok: 2+2
  ok: positive
errors
  ok: type error

3 tests: 3 passed
```

## API

### Groups

```scheme
(test-group "name" body ...)
```

### Assertions

```scheme
(test-assert "name" expr)                      ; truthy?
(test-equal "name" expected actual)            ; equal?
(test-eqv "name" expected actual)              ; eqv?
(test-approximate "name" expected actual tol)  ; within tolerance
(test-not "name" expr)                         ; falsy?
(test-error "name" thunk)                      ; raises error?
```

### Reporting

```scheme
(test-exit)           ; print summary, exit 1 on failure
(test-verbose! #f)    ; suppress pass messages
```
