# Migrating from Other Schemes

If you already know Scheme from another implementation, this guide covers
the differences. Kaappi follows R7RS-small closely, so standard code should
work with minimal changes.

## Coming from Racket

### Module system

Racket uses `#lang racket` and `(require ...)`. Kaappi uses R7RS
`define-library` and `import`:

```scheme
;; Racket
#lang racket
(require racket/list)

;; Kaappi
(import (scheme base) (srfi 1))
```

Libraries are defined in `.sld` files:

```scheme
;; Racket (my-lib.rkt)
#lang racket
(provide my-func)
(define (my-func x) (* x x))

;; Kaappi (my-lib/utils.sld)
(define-library (my-lib utils)
  (export my-func)
  (import (scheme base))
  (begin
    (define (my-func x) (* x x))))
```

### Contracts and types

Racket's contract system (`->`, `provide/contract`) has no Kaappi equivalent.
Use `guard` and explicit checks:

```scheme
;; Racket
(provide/contract [add1 (-> number? number?)])

;; Kaappi
(define (add1 x)
  (unless (number? x) (error "add1: expected number" x))
  (+ x 1))
```

### Hash tables

Racket's `hash` is immutable by default. Kaappi uses SRFI-69 mutable
hash tables:

```scheme
;; Racket
(define h (hash "a" 1 "b" 2))
(hash-ref h "a")

;; Kaappi
(import (srfi 69))
(define h (alist->hash-table '((a . 1) (b . 2))))
(hash-table-ref h 'a)
```

### Pattern matching

Racket's `match` uses a different syntax. Kaappi provides `match` via
SRFI 257, which supports non-linear patterns, backtracking, and
user-extensible pattern forms:

```scheme
;; Racket
(match x
  [(list a b) (+ a b)]
  [(? number?) (* x 2)]
  [_ 0])

;; Kaappi (SRFI 257)
(import (srfi 257))
(match x
  ((a b) (+ a b))
  ((? number?) (* x 2))
  (_ 0))
```

The `(srfi 257 rx)` sublibrary adds regexp match patterns, and
`(srfi 257 misc)` adds catamorphism and `syntax-rules`-style matchers.

### Sequences and for loops

Racket's `for/list`, `for/fold` become `map`, `fold` (SRFI-1):

```scheme
;; Racket
(for/list ([x '(1 2 3)]) (* x x))

;; Kaappi
(import (srfi 1))
(map (lambda (x) (* x x)) '(1 2 3))
```

### What works unchanged

- `lambda`, `define`, `let`, `let*`, `letrec`
- `if`, `cond`, `case`, `when`, `unless`
- `map`, `filter`, `for-each`, `apply`
- `cons`, `car`, `cdr`, `list`, `append`
- `string-append`, `number->string`, `string->number`
- `call/cc`, `dynamic-wind`, `values`, `call-with-values`

## Coming from Guile

### Module system

Guile uses `define-module` and `use-modules`. Kaappi uses R7RS
`define-library`:

```scheme
;; Guile
(define-module (my-lib utils)
  #:export (my-func))

;; Kaappi
(define-library (my-lib utils)
  (export my-func)
  (import (scheme base))
  (begin ...))
```

### GOOPS (object system)

Guile's GOOPS has no Kaappi equivalent. Use records (SRFI-9):

```scheme
;; Guile
(define-class <point> ()
  (x #:init-keyword #:x)
  (y #:init-keyword #:y))

;; Kaappi
(import (srfi 9))
(define-record-type <point>
  (make-point x y)
  point?
  (x point-x)
  (y point-y))
```

### Foreign function interface

Guile's dynamic FFI is different from Kaappi's:

```scheme
;; Guile
(use-modules (system foreign))
(define sqrt (pointer->procedure double
               (dynamic-func "sqrt" (dynamic-link "libm"))
               (list double)))

;; Kaappi
(import (kaappi ffi))
(define libm (ffi-open "libm.dylib"))
(define c-sqrt (ffi-fn libm "sqrt" '(double) 'double))
(c-sqrt 2.0)  ;=> 1.4142135623730951
(ffi-close libm)
```

### What works unchanged

Most R7RS code works directly. Key Guile extensions that need translation:

| Guile | Kaappi equivalent |
|-------|-------------------|
| `use-modules` | `import` |
| `define-module` | `define-library` |
| `format` | `display` + `number->string` |
| `hash-set!` / `hash-ref` | SRFI-69 `hash-table-set!` / `hash-table-ref` |
| `throw` / `catch` | `raise` / `guard` |

## Coming from Chicken

### Extensions and eggs

Chicken uses `(import ...)` with eggs installed via `chicken-install`. Kaappi
uses `thottam`:

```bash
# Chicken
chicken-install srfi-1

# Kaappi
thottam install kaappi-json
```

Built-in SRFIs don't need installation — just `(import (srfi 1))`.

### Compilation

Chicken compiles to C. Kaappi uses bytecode or LLVM-compiled standalone binaries:

```bash
# Chicken
csc program.scm -o program

# Kaappi
zig build -Dbundle-src=program.scm
```

### Foreign function interface

```scheme
;; Chicken
(import (chicken foreign))
(define sqrt (foreign-lambda double "sqrt" double))

;; Kaappi
(import (kaappi ffi))
(define libm (ffi-open "libm.dylib"))
(define c-sqrt (ffi-fn libm "sqrt" '(double) 'double))
```

### Continuations

Chicken uses a continuation-passing compilation strategy. Kaappi's `call/cc`
captures the full stack. Both support the same R7RS interface, but Kaappi
also offers `call/ec` for cheap escape-only continuations:

```scheme
;; Use call/ec when you only need a non-local exit
(call/ec (lambda (exit)
  (for-each (lambda (x)
              (when (negative? x) (exit x)))
            '(1 2 -3 4))))
;=> -3
```

### What works unchanged

- Most R7RS code
- SRFI imports (Kaappi supports 85 SRFIs, Chicken supports many of the same)
- `define-record-type` (SRFI-9)
- Standard list, string, vector operations

## Coming from Common Lisp

### Key differences

| Common Lisp | Kaappi (Scheme) |
|-------------|-----------------|
| Lisp-2 (separate namespaces) | Lisp-1 (one namespace) |
| `funcall` required | Functions are first-class values |
| `defun` | `define` |
| `setf` / `setq` | `set!` |
| `nil` is false and empty list | `#f` is false, `'()` is empty list |
| `t` is true | `#t` is true (any non-`#f` value is truthy) |
| `progn` | `begin` |
| `loop` macro | Tail recursion or SRFI-1 `fold` |

### Function definition

```scheme
;; Common Lisp
(defun square (x) (* x x))
(funcall #'square 5)

;; Kaappi
(define (square x) (* x x))
(square 5)
```

### nil vs #f vs '()

This is the biggest conceptual change. In CL, `nil` is simultaneously
false, the empty list, and a symbol. In Scheme:

```scheme
(if '() "truthy" "falsy")  ;=> "truthy"  — empty list is truthy!
(if #f  "truthy" "falsy")  ;=> "falsy"   — only #f is falsy
(null? '())                ;=> #t
(null? #f)                 ;=> #f
```

### Iteration

```scheme
;; Common Lisp
(loop for x in '(1 2 3) collect (* x x))

;; Kaappi
(map (lambda (x) (* x x)) '(1 2 3))

;; CL dotimes
(dotimes (i 5) (format t "~a~%" i))

;; Kaappi
(do ((i 0 (+ i 1))) ((= i 5))
  (display i) (newline))
```

### Error handling

```scheme
;; Common Lisp
(handler-case (/ 1 0)
  (division-by-zero (e) (format t "caught: ~a" e)))

;; Kaappi
(guard (e (#t (display "caught") (newline)))
  (/ 1 0))
```

## Summary of key differences

| Feature | Racket | Guile | Chicken | Kaappi |
|---------|--------|-------|---------|--------|
| Module system | `#lang` + `require` | `define-module` | `import` (eggs) | `define-library` (R7RS) |
| File extension | `.rkt` | `.scm` | `.scm` | `.sld` (library), `.scm` (program) |
| FFI | `ffi/unsafe` | `(system foreign)` | `foreign-lambda` | `(kaappi ffi)` |
| Package manager | `raco pkg` | Guix | `chicken-install` | `thottam` |
| Compilation | Bytecode/JIT | Bytecode | C | Bytecode + LLVM native |
| REPL | `racket` | `guile` | `csi` | `kaappi` |

## Getting help

If you hit a difference not covered here, check the
[Troubleshooting](troubleshooting.md) page or ask on
[GitHub Discussions](https://github.com/orgs/kaappi/discussions).

---

Next: [Troubleshooting](troubleshooting.md)
