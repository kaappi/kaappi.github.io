# Syntax Forms

These are special forms handled by the compiler, not procedure dispatch.
They cannot be passed as arguments or stored in variables. Available from
`(scheme base)`.

---

## Definitions

### `define` { #define }
<!-- index: - | Variable and function definition -->

`(define var expr)` | `(define (name params ...) body ...)`

Binds *var* to the result of evaluating *expr*, or defines a procedure
named *name* with the given *params* and *body*. The procedure shorthand
`(define (f x) ...)` is equivalent to `(define f (lambda (x) ...))`.
At the top level, `define` creates a new binding. Inside a `lambda`,
`let`, or other body, `define` creates an internal definition (equivalent
to `letrec*`).

```scheme
kaappi> (define pi 3.14159)
kaappi> pi
;=> 3.14159
kaappi> (define (square x) (* x x))
kaappi> (square 5)
;=> 25
kaappi> (define (fact n)
         (if (<= n 1) 1 (* n (fact (- n 1)))))
kaappi> (fact 10)
;=> 3628800
```

**See also:** [`lambda`](#lambda), [`set!`](#set),
[`define-syntax`](#define-syntax)

---

### `lambda` { #lambda }
<!-- index: - | Anonymous function -->

`(lambda (params ...) body ...)`  
`(lambda (params ... . rest) body ...)`  
`(lambda rest body ...)`

Creates an anonymous procedure. The *params* list specifies the formal
parameters. A dotted tail parameter collects extra arguments into a
list. A bare symbol instead of a parameter list collects all arguments
into a list.

```scheme
kaappi> ((lambda (x y) (+ x y)) 3 4)
;=> 7
kaappi> (define add1 (lambda (x) (+ x 1)))
kaappi> (add1 41)
;=> 42
kaappi> ((lambda (x . rest) rest) 1 2 3 4)
;=> (2 3 4)
kaappi> ((lambda args (length args)) 'a 'b 'c)
;=> 3
```

**See also:** [`define`](#define), [`case-lambda`](#case-lambda)

---

## Conditionals

### `if` { #if }
<!-- index: - | Conditional -->

`(if test consequent)` | `(if test consequent alternate)`

Evaluates *test*. If the result is true (anything other than `#f`),
evaluates and returns *consequent*. Otherwise, evaluates and returns
*alternate*. If *test* is false and no *alternate* is provided, the
result is unspecified.

```scheme
kaappi> (if (> 3 2) 'yes 'no)
;=> yes
kaappi> (if (< 3 2) 'yes 'no)
;=> no
kaappi> (if #f 'yes)
kaappi> (if 0 'yes 'no)
;=> yes
```

**See also:** [`cond`](#cond), [`when`](#when), [`unless`](#unless)

---

### `cond` { #cond }
<!-- index: - | Multi-branch conditional -->

`(cond (test expr ...) ... (else expr ...))`

Evaluates each *test* in order until one returns true, then evaluates
the corresponding *expr* sequence and returns the last result. An
`else` clause matches if no previous test succeeded. A clause of the
form `(test => proc)` passes the test result to *proc*.

A clause of the form `(test guard => receiver)` (SRFI-61) first
evaluates *test*, then applies *guard* to the result. If *guard*
returns true, *receiver* is called with the test result. This allows
filtering the test value before accepting the clause.

```scheme
kaappi> (cond ((> 3 2) 'greater)
              ((< 3 2) 'less)
              (else 'equal))
;=> greater
kaappi> (cond ((assv 2 '((1 one) (2 two) (3 three)))
               => cadr)
              (else 'not-found))
;=> two
kaappi> (cond ((assv 2 '((1 one) (2 two) (3 three)))
               pair?
               => cadr)
              (else 'not-found))
;=> two
```

**See also:** [`if`](#if), [`case`](#case), [`guard`](#guard),
[SRFI-61](../guide/srfi-support.md)

---

### `case` { #case }
<!-- index: - | Dispatch on datum equality -->

`(case key ((datum ...) expr ...) ... (else expr ...))`

Evaluates *key*, then compares its value (using `eqv?`) against each
list of *datums*. The *expr* sequence of the first matching clause is
evaluated and its result returned. An `else` clause matches when no
datum matches. A clause of the form `((datum ...) => proc)` calls
*proc* with the key value.

```scheme
kaappi> (case (* 2 3)
         ((2 3 5 7) 'prime)
         ((1 4 6 8 9) 'composite)
         (else 'unknown))
;=> composite
kaappi> (case (car '(c d))
         ((a e i o u) 'vowel)
         ((w y) 'semivowel)
         (else 'consonant))
;=> consonant
```

**See also:** [`cond`](#cond), [`if`](#if)

---

### `and` { #and }
<!-- index: - | Short-circuit logical and -->

`(and test ...)`

Evaluates each *test* from left to right. If any evaluates to `#f`,
returns `#f` immediately without evaluating the rest. If all tests
are true, returns the value of the last test. `(and)` with no
arguments returns `#t`.

```scheme
kaappi> (and 1 2 3)
;=> 3
kaappi> (and 1 #f 3)
;=> #f
kaappi> (and)
;=> #t
kaappi> (and (> 3 2) (< 5 10) 'yes)
;=> yes
```

**See also:** [`or`](#or), [`if`](#if)

---

### `or` { #or }
<!-- index: - | Short-circuit logical or -->

`(or test ...)`

Evaluates each *test* from left to right. If any evaluates to a true
value, returns that value immediately. If all tests are `#f`, returns
`#f`. `(or)` with no arguments returns `#f`.

```scheme
kaappi> (or #f #f 3)
;=> 3
kaappi> (or #f #f #f)
;=> #f
kaappi> (or)
;=> #f
kaappi> (or (memq 'b '(a b c)) 'not-found)
;=> (b c)
```

**See also:** [`and`](#and), [`if`](#if)

---

### `when` { #when }
<!-- index: - | One-armed conditional with implicit begin -->

`(when test expr ...)`

If *test* is true, evaluates each *expr* in sequence and returns the
value of the last one (like an implicit `begin`). If *test* is false,
the result is unspecified. `when` is a one-armed `if` with implicit
`begin`.

```scheme
kaappi> (when (> 3 2)
         (display "3 is greater")
         (newline)
         'done)
3 is greater
;=> done
kaappi> (when #f (error "never reached"))
```

**See also:** [`unless`](#unless), [`if`](#if)

---

### `unless` { #unless }
<!-- index: - | Negated one-armed conditional -->

`(unless test expr ...)`

The opposite of `when`. If *test* is false, evaluates each *expr* in
sequence and returns the value of the last one. If *test* is true, the
result is unspecified.

```scheme
kaappi> (unless (> 3 5)
         (display "3 is not greater than 5")
         (newline)
         'done)
3 is not greater than 5
;=> done
kaappi> (unless #t (error "never reached"))
```

**See also:** [`when`](#when), [`if`](#if)

---

## Binding Forms

### `let` { #let }
<!-- index: - | Local bindings -->

`(let ((var expr) ...) body ...)`  
`(let name ((var expr) ...) body ...)`

Binds each *var* to the value of its corresponding *expr* (evaluated
in an unspecified order), then evaluates *body* in the extended
environment. Named `let` binds *name* to a procedure that can be called
recursively from *body*, enabling loop constructs.

```scheme
kaappi> (let ((x 2) (y 3))
         (+ x y))
;=> 5
kaappi> (let loop ((i 0) (sum 0))
         (if (> i 10)
             sum
             (loop (+ i 1) (+ sum i))))
;=> 55
```

**See also:** [`let*`](#let-star), [`letrec`](#letrec),
[`let-values`](#let-values)

---

### `let*` { #let-star }
<!-- index: - | Sequential local bindings -->

`(let* ((var expr) ...) body ...)`

Like `let`, but each binding is evaluated sequentially, and each
subsequent binding can refer to earlier ones. This is equivalent to
nested `let` forms.

```scheme
kaappi> (let* ((x 1) (y (+ x 1)) (z (+ x y)))
         (list x y z))
;=> (1 2 3)
kaappi> (let* ((path "/tmp")
               (file (string-append path "/data.txt")))
         file)
;=> "/tmp/data.txt"
```

**See also:** [`let`](#let), [`letrec*`](#letrec-star)

---

### `letrec` { #letrec }
<!-- index: - | Mutually recursive bindings -->

`(letrec ((var expr) ...) body ...)`

Binds each *var*, then evaluates each *expr* in the extended environment
where all variables are visible (but not yet assigned). This allows
mutually recursive definitions. It is an error to reference a variable
before its initializer has completed, except inside a `lambda`.

```scheme
kaappi> (letrec ((even? (lambda (n)
                          (if (= n 0) #t (odd? (- n 1)))))
                 (odd? (lambda (n)
                         (if (= n 0) #f (even? (- n 1))))))
         (list (even? 4) (odd? 3)))
;=> (#t #t)
```

**See also:** [`letrec*`](#letrec-star), [`let`](#let),
[`define`](#define)

---

### `letrec*` { #letrec-star }
<!-- index: - | Sequential mutually recursive bindings -->

`(letrec* ((var expr) ...) body ...)`

Like `letrec`, but each *expr* is evaluated sequentially from left to
right. Each initializer can refer to the values of previously
initialized variables. This is equivalent to internal `define` at the
top of a body.

```scheme
kaappi> (letrec* ((x 1)
                  (y (+ x 1)))
         (+ x y))
;=> 3
```

**See also:** [`letrec`](#letrec), [`let*`](#let-star)

---

### `let-values` { #let-values }
<!-- index: - | Destructure multiple values -->

`(let-values (((var ...) expr) ...) body ...)`

Like `let`, but each *expr* can return multiple values (via `values`),
which are bound to the corresponding *vars*. The bindings are
evaluated in an unspecified order.

```scheme
kaappi> (let-values (((a b) (values 1 2))
                     ((c d e) (values 3 4 5)))
         (list a b c d e))
;=> (1 2 3 4 5)
kaappi> (let-values (((q r) (floor/ 17 5)))
         (list q r))
;=> (3 2)
```

**See also:** [`let*-values`](#let-star-values),
[`values`](./control-flow.md#values)

---

### `let*-values` { #let-star-values }
<!-- index: - | Sequential destructure multiple values -->

`(let*-values (((var ...) expr) ...) body ...)`

Like `let-values`, but bindings are evaluated sequentially. Each
*expr* can refer to variables bound by previous clauses.

```scheme
kaappi> (let*-values (((a b) (values 1 2))
                      ((c) (+ a b)))
         c)
;=> 3
```

**See also:** [`let-values`](#let-values), [`let*`](#let-star)

---

## Iteration

### `do` { #do }
<!-- index: - | Iteration with step expressions -->

`(do ((var init step) ...) (test expr ...) command ...)`

Iterative construct. Each *var* is bound to *init*, then repeatedly:
*test* is evaluated; if true, the *expr* sequence is evaluated and its
last value returned; otherwise the *command* sequence is evaluated for
side effects, each *var* is updated to its *step* value, and iteration
continues.

```scheme
kaappi> (do ((i 0 (+ i 1))
             (sum 0 (+ sum i)))
            ((= i 5) sum))
;=> 10
kaappi> (do ((vec (make-vector 5))
             (i 0 (+ i 1)))
            ((= i 5) vec)
         (vector-set! vec i (* i i)))
;=> #(0 1 4 9 16)
```

**See also:** [`let`](#let) (named let for loops),
[`for-each`](./pairs-and-lists.md#for-each)

---

### `case-lambda` { #case-lambda }
<!-- index: - | Arity-dispatched lambda -->

`(case-lambda (formals body ...) ...)`

Creates a procedure that dispatches on the number of arguments. Each
clause has its own *formals* list and *body*. When the procedure is
called, the first clause whose formals match the argument count is
selected.

```scheme
kaappi> (define add
         (case-lambda
           ((x) x)
           ((x y) (+ x y))
           ((x y z) (+ x y z))))
kaappi> (add 1)
;=> 1
kaappi> (add 1 2)
;=> 3
kaappi> (add 1 2 3)
;=> 6
kaappi> (define optarg
         (case-lambda
           ((x) (optarg x 10))
           ((x y) (+ x y))))
kaappi> (optarg 5)
;=> 15
kaappi> (optarg 5 20)
;=> 25
```

**See also:** [`lambda`](#lambda), [`define`](#define)

---

## Sequencing and Mutation

### `quote` { #quote }
<!-- index: - | Literal datum -->

`(quote datum)` | `'datum`

Returns *datum* without evaluating it. The shorthand `'datum` is
equivalent to `(quote datum)`. The returned value is immutable.

```scheme
kaappi> (quote (1 2 3))
;=> (1 2 3)
kaappi> '(a b c)
;=> (a b c)
kaappi> 'hello
;=> hello
kaappi> '#(1 2 3)
;=> #(1 2 3)
```

**See also:** [`quasiquote`](#quasiquote)

---

### `set!` { #set }
<!-- index: - | Variable mutation -->

`(set! var expr)`

Assigns the value of *expr* to the existing binding of *var*. It is
an error if *var* has not been defined. Unlike `define`, `set!` does
not create a new binding -- it mutates an existing one.

```scheme
kaappi> (define x 1)
kaappi> x
;=> 1
kaappi> (set! x 42)
kaappi> x
;=> 42
kaappi> (define count 0)
kaappi> (set! count (+ count 1))
kaappi> count
;=> 1
```

#### Generalized `set!` (SRFI-17)

`(set! (accessor args ...) expr)`

When the first argument to `set!` is a procedure call form, Kaappi applies the
*setter* associated with *accessor*. This allows mutation through accessors
without separate mutator names. Import `(srfi 17)` to use this form.

Pre-defined setters:

| Accessor | Equivalent to |
|----------|---------------|
| `car` | `set-car!` |
| `cdr` | `set-cdr!` |
| `vector-ref` | `vector-set!` |
| `string-ref` | `string-set!` |
| `hashtable-ref` | `hashtable-set!` |
| `slot-ref` | `slot-set!` |

```scheme
kaappi> (import (srfi 17))
kaappi> (define p (list 1 2 3))
kaappi> (set! (car p) 10)
kaappi> p
;=> (10 2 3)
kaappi> (define v (vector 'a 'b 'c))
kaappi> (set! (vector-ref v 1) 'x)
kaappi> v
;=> #(a x c)
```

**See also:** [`define`](#define), [SRFI-17](../guide/srfi-support.md)

---

### `begin` { #begin }
<!-- index: - | Sequence of expressions -->

`(begin expr ...)`

Evaluates each *expr* in sequence from left to right and returns the
value of the last expression. At the top level of a program or library
body, `begin` splices its contents into the enclosing body.

```scheme
kaappi> (begin
         (define x 1)
         (set! x (+ x 1))
         x)
;=> 2
kaappi> (begin (display "hello ") (display "world") (newline) 42)
hello world
;=> 42
```

**See also:** [`when`](#when), [`unless`](#unless), [`lambda`](#lambda)

---

### `quasiquote` { #quasiquote }
<!-- index: - | Template with unquote and unquote-splicing -->

`` `template `` | `(quasiquote template)`

Like `quote`, but allows *unquoting* inside the template. An `unquote`
expression `,expr` evaluates *expr* and inserts its value. An
`unquote-splicing` expression `,@expr` evaluates *expr* (which must
produce a list) and splices its elements into the surrounding list.

```scheme
kaappi> (let ((x 1) (y 2))
         `(sum is ,(+ x y)))
;=> (sum is 3)
kaappi> (let ((items '(a b c)))
         `(begin ,@items end))
;=> (begin a b c end)
kaappi> `(list ,(+ 1 2) 4)
;=> (list 3 4)
```

**See also:** [`quote`](#quote)

---

## Macros

### `define-syntax` { #define-syntax }
<!-- index: - | Define a macro -->

`(define-syntax name transformer-spec)`

Binds *name* as a macro. The *transformer-spec* is typically a
`syntax-rules` form that specifies how to rewrite calls to *name*.

```scheme
kaappi> (define-syntax swap!
         (syntax-rules ()
           ((swap! a b)
            (let ((tmp a))
              (set! a b)
              (set! b tmp)))))
kaappi> (let ((x 1) (y 2))
         (swap! x y)
         (list x y))
;=> (2 1)
```

**See also:** [`syntax-rules`](#syntax-rules),
[`let-syntax`](#let-syntax)

---

### `syntax-rules` { #syntax-rules }
<!-- index: - | Pattern-based macro transformer -->

`(syntax-rules (literal ...) (pattern template) ...)`

Defines a pattern-based macro transformer. Each *pattern* is matched
against the macro call; the first matching pattern determines the
*template* used to produce the expansion. Identifiers listed as
*literals* are matched by binding rather than treated as pattern
variables. Patterns support `...` (ellipsis) for matching zero or
more subforms.

```scheme
kaappi> (define-syntax my-if
         (syntax-rules (then else)
           ((my-if test then consequent else alternate)
            (cond (test consequent)
                  (#t alternate)))))
kaappi> (my-if (> 3 2) then 'yes else 'no)
;=> yes
kaappi> (define-syntax my-and
         (syntax-rules ()
           ((my-and) #t)
           ((my-and x) x)
           ((my-and x rest ...)
            (if x (my-and rest ...) #f))))
kaappi> (my-and 1 2 3)
;=> 3
```

**See also:** [`define-syntax`](#define-syntax),
[`let-syntax`](#let-syntax)

---

### `let-syntax` { #let-syntax }
<!-- index: - | Local macro bindings -->

`(let-syntax ((name transformer) ...) body ...)`

Introduces local macro bindings. Each *name* is bound to its
*transformer* (typically `syntax-rules`) for the scope of *body*. The
transformers are evaluated in the enclosing environment -- they cannot
reference each other.

```scheme
kaappi> (let-syntax ((double (syntax-rules ()
                               ((double x) (+ x x)))))
         (double 21))
;=> 42
```

**See also:** [`letrec-syntax`](#letrec-syntax),
[`define-syntax`](#define-syntax)

---

### `letrec-syntax` { #letrec-syntax }
<!-- index: - | Mutually recursive local macro bindings -->

`(letrec-syntax ((name transformer) ...) body ...)`

Like `let-syntax`, but the *transformers* can reference each other,
enabling mutually recursive macro definitions within *body*.

```scheme
kaappi> (letrec-syntax
          ((my-or (syntax-rules ()
                    ((my-or) #f)
                    ((my-or e1 e2 ...)
                     (let ((t e1))
                       (if t t (my-or e2 ...)))))))
         (my-or #f #f 42))
;=> 42
```

**See also:** [`let-syntax`](#let-syntax),
[`define-syntax`](#define-syntax)

---

## Modules

### `define-library` { #define-library }
<!-- index: - | Define a library -->

`(define-library (lib-name ...) declaration ...)`

Defines a library (module) with the given hierarchical name. Library
declarations include `export`, `import`, `begin` (for definitions),
`include`, and `cond-expand`. Libraries provide separate namespaces
and explicit interfaces.

```scheme
(define-library (mylib utils)
  (export factorial fibonacci)
  (import (scheme base))
  (begin
    (define (factorial n)
      (if (<= n 1) 1 (* n (factorial (- n 1)))))
    (define (fibonacci n)
      (let loop ((i 0) (a 0) (b 1))
        (if (= i n) a (loop (+ i 1) b (+ a b)))))))
```

**See also:** [`import`](#import),
[`cond-expand`](#cond-expand)

---

### `import` { #import }
<!-- index: - | Import library bindings -->

`(import import-set ...)`

Imports bindings from one or more libraries into the current
environment. Import sets can be plain library names or modified with
`only`, `except`, `prefix`, and `rename` to control which bindings
are brought in and under what names.

```scheme
kaappi> (import (scheme base))
kaappi> (import (scheme write))
kaappi> (import (only (srfi 1) fold filter))
kaappi> (import (prefix (srfi 69) ht:))
kaappi> (import (rename (scheme base) (define def)))
```

**See also:** [`define-library`](#define-library),
[`environment`](./system.md#environment)

---

## Exceptions and Control

### `guard` { #guard }
<!-- index: - | Exception handling with cond clauses -->

`(guard (var (test expr ...) ...) body ...)`

Structured exception handling. Evaluates *body*; if an exception is
raised, it is bound to *var* and the `cond`-style clauses are tested
in order. If a clause's *test* is true, its *expr* sequence is
evaluated and the result returned. An `else` clause catches all
exceptions. If no clause matches, the exception is re-raised.

```scheme
kaappi> (guard (e ((string? e) (string-append "caught: " e))
                  ((number? e) (* e 2)))
         (raise "oops"))
;=> "caught: oops"
kaappi> (guard (e ((number? e) (* e 10)))
         (raise 5))
;=> 50
kaappi> (guard (e (#t (error-object-message e)))
         (error "something failed" 'details))
;=> "something failed"
```

**See also:** [`raise`](./control-flow.md#raise),
[`with-exception-handler`](./control-flow.md#with-exception-handler),
[`cond`](#cond)

---

### `define-record-type` { #define-record-type }
<!-- index: - | Define a record type -->

`(define-record-type name (constructor field-name ...) predicate (field-name accessor) ... (field-name accessor mutator) ...)`

Defines a new record type with a constructor, predicate, and field
accessors (and optional mutators). This is the standard way to define
structured data types in R7RS.

```scheme
kaappi> (define-record-type <point>
         (make-point x y)
         point?
         (x point-x)
         (y point-y))
kaappi> (define p (make-point 3 4))
kaappi> (point? p)
;=> #t
kaappi> (point-x p)
;=> 3
kaappi> (point-y p)
;=> 4
kaappi> (point? '(3 4))
;=> #f
```

**See also:** [`define`](#define)

---

## Lazy Evaluation

### `delay` { #delay }
<!-- index: - | Create a promise (lazy thunk) -->

`(delay expr)`

Creates a promise that, when forced, evaluates *expr* and caches the
result. Subsequent calls to `force` on the same promise return the
cached value without re-evaluating *expr*.

```scheme
kaappi> (define p (delay (begin (display "computing...") (newline) 42)))
kaappi> (force p)
computing...
;=> 42
kaappi> (force p)
;=> 42
```

**See also:** [`delay-force`](#delay-force),
[`force`](./other.md#force),
[`promise?`](./type-checking.md#promise)

---

### `delay-force` { #delay-force }
<!-- index: - | Create an iterative promise -->

`(delay-force expr)`

Creates an iterative promise. When forced, *expr* is evaluated and
must return another promise, which is then forced iteratively (not
recursively). This avoids stack overflow when chaining lazy
computations. Also known as `lazy` in SRFI-45.

```scheme
kaappi> (define (lazy-range n limit)
         (if (>= n limit)
             (delay '())
             (delay-force
               (delay (cons n (lazy-range (+ n 1) limit))))))
kaappi> (force (lazy-range 0 5))
;=> (0 . #<promise>)
kaappi> (define (force-list p)
         (let ((v (force p)))
           (if (null? v) '()
               (cons (car v) (force-list (cdr v))))))
kaappi> (force-list (lazy-range 0 5))
;=> (0 1 2 3 4)
```

**See also:** [`delay`](#delay),
[`force`](./other.md#force)

---

### `parameterize` { #parameterize }
<!-- index: - | Dynamically bind parameters -->

`(parameterize ((param value) ...) body ...)`

Dynamically rebinds each parameter object *param* to *value* for the
duration of *body*. When control leaves *body* (normally or via
continuation), the parameters are restored to their previous values.
If the parameter was created with a converter procedure, the converter
is applied to *value* before binding.

```scheme
kaappi> (define radix (make-parameter 10))
kaappi> (radix)
;=> 10
kaappi> (parameterize ((radix 16))
         (radix))
;=> 16
kaappi> (radix)
;=> 10
kaappi> (parameterize ((current-output-port (open-output-string)))
         (display "captured")
         (get-output-string (current-output-port)))
;=> "captured"
```

**See also:** [`make-parameter`](./system.md#make-parameter),
[`dynamic-wind`](./control-flow.md#dynamic-wind)

---

### `cond-expand` { #cond-expand }
<!-- index: - | Feature-based conditional expansion -->

`(cond-expand (feature-requirement expr ...) ... (else expr ...))`

Compile-time conditional expansion based on implementation features.
Each *feature-requirement* is tested against the features returned by
`(features)`. The first matching clause's *expr* sequence is expanded
into the program; other clauses are discarded entirely. Feature
requirements can use `and`, `or`, `not`, and `library` to compose
tests.

```scheme
kaappi> (cond-expand
         (kaappi (display "Running on Kaappi") (newline))
         (else (display "Unknown implementation") (newline)))
Running on Kaappi
kaappi> (cond-expand
         ((library (srfi 1))
          (import (srfi 1))
          (display "SRFI-1 available"))
         (else
          (display "No SRFI-1")))
SRFI-1 available
```

**See also:** [`features`](./system.md#features),
[`define-library`](#define-library)
