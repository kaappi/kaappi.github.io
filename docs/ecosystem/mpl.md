# Symbolic Math (MPL)

`(mpl all)` — computer algebra: automatic simplification, algebraic and
trigonometric expansion/contraction, symbolic differentiation, polynomial
division and GCD, and an infix expression parser. Pure Scheme, no build
step — an R7RS port of
[dharmatech/mpl](https://github.com/dharmatech/mpl), implementing
algorithms from Joel S. Cohen's *Computer Algebra and Symbolic
Computation* books.

```bash
thottam install kaappi-mpl
```

Requires Kaappi >= 0.15.0.

!!! note "Imports shadow arithmetic"
    MPL replaces `+`, `-`, `*`, `/`, and `sqrt` with symbolic versions,
    so import `(scheme base)` with `except`:

    ```scheme
    (import (except (scheme base) + - * / sqrt)
            (mpl all))
    ```

    On plain numbers the symbolic operators still compute numeric
    results — `(+ 1 2)` is `3` — so ordinary arithmetic keeps working.

## Quick start

```scheme
(import (except (scheme base) + - * / sqrt)
        (mpl all))

(vars a b x y z)

(* z y x 2)                              ;=> (* 2 x y z)
(+ x y x 5)                              ;=> (+ 5 (* 2 x) y)
(algebraic-expand (alge "(x+2)*(x+3)"))  ;=> (+ 6 (* 5 x) (^ x 2))
(derivative (alge "a x^2 + b x") 'x)     ;=> (+ b (* 2 a x))
```

## Declaring variables

`vars` defines each name as a self-evaluating symbol (it expands to
`(define x 'x) ...`), so expressions can be written without quoting:

```scheme
(vars a b x y z)
```

## Symbolic arithmetic

The operators auto-simplify as they build expressions — terms are
sorted, like terms combined, and identities applied:

```scheme
(* z y x 2)          ;=> (* 2 x y z)      — sorted, coefficient first
(+ x y x z 5 z)      ;=> (+ 5 (* 2 x) y (* 2 z))
(^ (^ x 1/2) 4)      ;=> (^ x 2)
(/ x x)              ;=> 1
(- (/ (* x y) 3))    ;=> (* -1/3 x y)
```

Expressions are ordinary s-expressions (`+`, `*`, `^` trees), so the
result of one operation feeds directly into the next.

## Infix parser

`alge` parses an infix string into a (simplified) symbolic expression —
handy for anything a human types:

```scheme
(alge "(x+2)*(x+3)")          ;=> (* (+ 2 x) (+ 3 x))
(alge "a x^2 + b x")          ;=> (+ (* b x) (* a (^ x 2)))
(alge "sin(x)^2 + cos(x)^2")  ;=> (+ (^ (cos x) 2) (^ (sin x) 2))
```

## Expansion and substitution

```scheme
(algebraic-expand (alge "(x+2)*(x+3)"))
;=> (+ 6 (* 5 x) (^ x 2))

(substitute (alge "x^2 + x") 'x 3)
;=> 12

(collect-terms (alge "a x + b x + c y") '(x y))
;=> (+ (* (+ a b) x) (* c y))
```

`expand-exp` / `contract-exp` and `expand-trig` / `contract-trig` apply
the exponential and trigonometric identities in each direction.

## Calculus

`derivative` differentiates symbolically with respect to a variable:

```scheme
(derivative (alge "a x^2 + b x") 'x)   ;=> (+ b (* 2 a x))
(derivative (alge "sin(x)") 'x)        ;=> (cos x)
```

## Polynomials

`polynomial-division` returns the quotient and remainder as a two-element
list:

```scheme
(polynomial-division (alge "x^2 + 5 x + 6") (alge "x + 2") 'x)
;=> ((+ 3 x) 0)
```

Further operations — GCD, the extended Euclidean algorithm, division over
algebraic number fields, partial fractions — live in individual
`(mpl ...)` modules.

## Individual modules

`(mpl all)` re-exports the common surface. Each component is also its
own library (56 modules mirroring upstream), importable piecemeal:

```scheme
(import (except (scheme base) + - * /)
        (mpl sum-product-power)   ; + * ^
        (mpl sub)                 ; -
        (mpl div)                 ; /
        (mpl derivative))
```

See the repo's [docs/](https://github.com/kaappi/kaappi-mpl/tree/main/docs)
for the full guides (getting started, simplification, algebra,
trigonometry, calculus, exponentials) and the complete API reference.

## API reference

The `(mpl all)` exports:

| Procedure | Description |
|-----------|-------------|
| `+` `-` `*` `/` `^` | Symbolic arithmetic with auto-simplification |
| `(sqrt expr)` | Symbolic square root |
| `(vars name ...)` | Define names as self-evaluating symbolic variables |
| `(alge string)` | Parse an infix string to a simplified expression |
| `(substitute expr from to)` | Replace a subexpression, then simplify |
| `(collect-terms expr vars)` | Collect coefficients of the given variables |
| `(algebraic-expand expr)` | Expand products and integer powers |
| `(expand-exp expr)` / `(contract-exp expr)` | Exponential identities, each direction |
| `(expand-trig expr)` / `(contract-trig expr)` | Trigonometric identities, each direction |
| `(derivative expr var)` | Symbolic derivative |
| `(polynomial-division u v x)` | Quotient and remainder in *x* |
| `(polynomial-expansion u v x t)` | Expansion of *u* in terms of *v* |

!!! note "License"
    kaappi-mpl is Apache-2.0 (inherited from the upstream mpl project),
    unlike the rest of the ecosystem, which is MIT.
