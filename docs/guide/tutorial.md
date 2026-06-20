# Scheme Tutorial

A hands-on introduction to Scheme for programmers coming from Python,
JavaScript, or similar languages. Open a REPL with `kaappi` and follow
along.

```bash
kaappi
```

The REPL imports `(scheme base)` automatically, so you can start typing
expressions right away.


## Expressions, Not Statements

In most languages you write *statements* that do things and *expressions*
that produce values. In Scheme, there is only one category: everything is
an expression, and every expression returns a value.

The syntax is uniform: open parenthesis, operator, operands, close
parenthesis. The operator always comes first.

```scheme
kaappi> (+ 2 3)
;=> 5
kaappi> (* 6 7)
;=> 42
```

There is no operator precedence to memorize. You nest expressions
explicitly:

```scheme
kaappi> (+ 2 (* 3 4))
;=> 14
kaappi> (* (+ 1 2) (- 10 4))
;=> 18
```

In Python you would write `2 + 3 * 4` and need to remember that `*` binds
tighter than `+`. In Scheme the parentheses *are* the precedence, and they
are always unambiguous.

There is no `return` keyword. The value of the last expression in a body
is the result. There are no semicolons and no curly braces. Parentheses
are the only grouping mechanism, and you will grow to appreciate their
regularity.


## Atoms

Scheme has several kinds of atomic (indivisible) values.

**Numbers** come in many flavors:

```scheme
kaappi> 42
;=> 42
kaappi> 3.14
;=> 3.14
kaappi> 1/3
;=> 1/3
kaappi> (+ 1/3 1/6)
;=> 1/2
kaappi> 3+4i
;=> 3+4i
```

Integers, rationals, floating-point, and complex numbers are all
first-class. Exact rationals like `1/3` stay exact -- no floating-point
drift.

**Strings** use double quotes:

```scheme
kaappi> "hello, world"
;=> "hello, world"
kaappi> (string-length "hello")
;=> 5
```

Single quotes mean something else in Scheme (see below), so strings are
always double-quoted.

**Booleans** are `#t` (true) and `#f` (false). The critical rule: only
`#f` is false. Everything else -- including `0`, `""`, and `'()` -- is
true.

```scheme
kaappi> (if 0 "truthy" "falsy")
;=> "truthy"
kaappi> (if "" "truthy" "falsy")
;=> "truthy"
kaappi> (if #f "truthy" "falsy")
;=> "falsy"
```

This surprises Python programmers, where `0` and `""` are falsy.

**Characters** are written with `#\` prefix:

```scheme
kaappi> #\a
;=> #\a
kaappi> #\space
;=> #\space
kaappi> (char-alphabetic? #\Z)
;=> #t
```

**Symbols** are interned names. A symbol is not a string -- it is a
lightweight identifier that is compared by identity, not by character
content.

```scheme
kaappi> 'hello
;=> hello
kaappi> (symbol? 'hello)
;=> #t
kaappi> (eq? 'abc 'abc)
;=> #t
```

The `'` (single quote) is called *quote*. It prevents the expression that
follows from being evaluated. Without it, `hello` would be looked up as a
variable name.


## Lists

Lists are Scheme's universal data structure. A quoted list looks like this:

```scheme
kaappi> '(1 2 3)
;=> (1 2 3)
kaappi> '(red green blue)
;=> (red green blue)
```

Under the hood, a list is a chain of *pairs*. Each pair holds one element
and a pointer to the next pair. The chain ends with the empty list `'()`.

```scheme
kaappi> (cons 1 (cons 2 (cons 3 '())))
;=> (1 2 3)
```

Here is the structure as a box-and-pointer diagram:

```
(cons 1 (cons 2 (cons 3 '())))

  [1|*]-->[2|*]-->[3|/]
```

Each box is a pair. The left half holds the element, the right half points
to the next pair. The `/` represents `'()`, the end of the list.

`car` extracts the first element, `cdr` extracts the rest:

```scheme
kaappi> (car '(a b c))
;=> a
kaappi> (cdr '(a b c))
;=> (b c)
kaappi> (car (cdr '(a b c)))
;=> b
```

The `list` procedure is shorthand for the `cons` chain:

```scheme
kaappi> (list 10 20 30)
;=> (10 20 30)
```

Lists serve double duty: they are data, and they are also how Scheme code
is represented. The expression `(+ 1 2)` is a list of three elements.
This property -- code is data -- is what makes Lisps uniquely powerful,
but you do not need to exploit it yet.


## Defining Things

Use `define` to bind a name to a value:

```scheme
kaappi> (define pi 3.14159)
kaappi> (* pi 10 10)
;=> 314.159
```

To define a function, put the name and parameters in a list:

```scheme
kaappi> (define (square x) (* x x))
kaappi> (square 7)
;=> 49
kaappi> (square 1.5)
;=> 2.25
```

This is shorthand for the more explicit form using `lambda`, which creates
an anonymous function:

```scheme
kaappi> (define square (lambda (x) (* x x)))
```

`lambda` is like `=>` in JavaScript or `lambda` in Python, but it can
contain multiple expressions in its body. Functions are ordinary values --
you can pass them as arguments, return them from other functions, and
store them in data structures.

```scheme
kaappi> (define (apply-twice f x) (f (f x)))
kaappi> (apply-twice square 3)
;=> 81
```

`(square 3)` gives `9`, then `(square 9)` gives `81`.


## Conditionals

`if` is an expression with three parts: test, then, else.

```scheme
kaappi> (if (> 5 3) "yes" "no")
;=> "yes"
kaappi> (define (abs x) (if (< x 0) (- x) x))
kaappi> (abs -7)
;=> 7
```

Compare to Python's ternary: `"yes" if 5 > 3 else "no"`. The Scheme
version puts the condition first and does not need keywords between the
branches.

For multiple branches, use `cond`. It works like an if/elif/else chain:

```scheme
kaappi> (define (classify n)
  ...     (cond
  ...       ((< n 0) "negative")
  ...       ((= n 0) "zero")
  ...       (else "positive")))
kaappi> (classify -3)
;=> "negative"
kaappi> (classify 0)
;=> "zero"
kaappi> (classify 42)
;=> "positive"
```

`and` and `or` short-circuit and return the deciding value, not just
`#t`/`#f`:

```scheme
kaappi> (and 1 2 3)
;=> 3
kaappi> (and 1 #f 3)
;=> #f
kaappi> (or #f #f 42)
;=> 42
kaappi> (or #f #f #f)
;=> #f
```

This is useful for defaults: `(or (get-config "port") 8080)` returns
the configured port or `8080` if the config returns `#f`.

`when` and `unless` are for side-effect-only conditionals where you do
not need an else branch:

```scheme
kaappi> (when (> 5 3) (display "big\n"))
big
```


## Recursion

Scheme has no `for` or `while` loops. Repetition is expressed through
recursion, and the language is designed to make this efficient.

Start with factorial:

```scheme
kaappi> (define (factorial n)
  ...     (if (= n 0)
  ...         1
  ...         (* n (factorial (- n 1)))))
kaappi> (factorial 5)
;=> 120
kaappi> (factorial 20)
;=> 2432902008176640000
```

Here is a function that computes the length of a list by walking the `cdr`
chain:

```scheme
kaappi> (define (my-length lst)
  ...     (if (null? lst)
  ...         0
  ...         (+ 1 (my-length (cdr lst)))))
kaappi> (my-length '(a b c d))
;=> 4
```

Named `let` is the idiomatic way to write a loop. It defines a local
function and calls it immediately:

```scheme
kaappi> (let loop ((i 1))
  ...     (when (<= i 5)
  ...       (display i)
  ...       (display " ")
  ...       (loop (+ i 1))))
1 2 3 4 5
```

`loop` is just a name you choose -- it is bound to a function with
parameter `i`, and calling `(loop (+ i 1))` recurses with the next value.

**Tail calls.** When a recursive call is the last thing a function does
(it is in *tail position*), Scheme reuses the current stack frame instead
of allocating a new one. This means tail-recursive functions run in
constant space, like a loop.

The factorial above is *not* tail-recursive because it still needs to
multiply after the recursive call. Here is a tail-recursive version using
an accumulator:

```scheme
kaappi> (define (factorial n)
  ...     (let loop ((i n) (acc 1))
  ...       (if (= i 0)
  ...           acc
  ...           (loop (- i 1) (* acc i)))))
kaappi> (factorial 100)
;=> 93326215443944152681699238856266700490715968264381621468592963895217599993229915608941463976156518286253697920827223758251185210916864000000000000000000000000
```

The call to `loop` is the last expression -- nothing wraps it -- so it
runs without growing the stack, even for `(factorial 100000)`.


## Higher-Order Functions

A higher-order function takes a function as an argument or returns one.
This is where Scheme starts to feel powerful.

`map` applies a function to every element of a list:

```scheme
kaappi> (map square '(1 2 3 4 5))
;=> (1 4 9 16 25)
kaappi> (map string-length '("cat" "elephant" "ox"))
;=> (3 8 2)
```

`filter` keeps elements that satisfy a predicate (requires
`(import (srfi 1))` in a file; the REPL has it available):

```scheme
kaappi> (import (srfi 1))
kaappi> (filter even? '(1 2 3 4 5 6))
;=> (2 4 6)
```

`fold` reduces a list to a single value by combining elements left to
right:

```scheme
kaappi> (fold + 0 '(1 2 3 4 5))
;=> 15
kaappi> (fold max 0 '(3 7 2 9 4))
;=> 9
```

You can use `lambda` inline when you need a one-off function:

```scheme
kaappi> (map (lambda (x) (+ x 10)) '(1 2 3))
;=> (11 12 13)
kaappi> (filter (lambda (s) (> (string-length s) 3))
  ...           '("hi" "hello" "hey" "good morning"))
;=> ("hello" "good morning")
```

If you come from Python, `map` is like a list comprehension
`[f(x) for x in lst]`, and `filter` is the `if` clause. In JavaScript,
these are `.map()` and `.filter()`. Scheme had them first -- in 1975.

`for-each` is like `map` but discards the results. Use it for side
effects:

```scheme
kaappi> (for-each (lambda (name) (display "Hello, ")
  ...                             (display name)
  ...                             (newline))
  ...             '("Alice" "Bob" "Carol"))
Hello, Alice
Hello, Bob
Hello, Carol
```


## Local Bindings

`let` binds names inside a limited scope. The bindings exist only within
the body.

```scheme
kaappi> (let ((x 10)
  ...         (y 20))
  ...     (+ x y))
;=> 30
```

The bindings are parallel: `x` and `y` are computed before either is
visible. If you need sequential bindings where each can refer to the
previous ones, use `let*`:

```scheme
kaappi> (let* ((x 3)
  ...          (y (* x x))
  ...          (z (+ x y)))
  ...     z)
;=> 12
```

`letrec` allows mutual recursion. Here is a classic example:

```scheme
kaappi> (letrec ((my-even? (lambda (n)
  ...                        (if (= n 0) #t (my-odd? (- n 1)))))
  ...            (my-odd? (lambda (n)
  ...                       (if (= n 0) #f (my-even? (- n 1))))))
  ...     (my-even? 10))
;=> #t
```

Scope in Scheme is *lexical*: a name is resolved where the function is
defined, not where it is called. This is the same as Python and
JavaScript (but not Emacs Lisp or Bash).

Under the hood, `let` is syntactic sugar for an immediately-called
`lambda`:

```scheme
;; These two are equivalent:
(let ((x 5)) (* x x))
((lambda (x) (* x x)) 5)
```


## Closures

A closure is a function that captures variables from its enclosing scope.
When the enclosing scope exits, those variables live on inside the
closure.

Here is a function that creates a counter:

```scheme
kaappi> (define (make-counter)
  ...     (let ((n 0))
  ...       (lambda ()
  ...         (set! n (+ n 1))
  ...         n)))
kaappi> (define c (make-counter))
kaappi> (c)
;=> 1
kaappi> (c)
;=> 2
kaappi> (c)
;=> 3
```

Each call to `make-counter` creates a fresh `n`. The returned `lambda`
closes over that `n` and updates it on every call. This is the same
mechanism as closures in JavaScript:

```javascript
// JavaScript equivalent
function makeCounter() {
  let n = 0;
  return () => ++n;
}
```

Closures give you encapsulation without classes. The variable `n` is
completely private -- no code outside the closure can access it.

You can return multiple closures that share the same state:

```scheme
kaappi> (define (make-account balance)
  ...     (define (deposit amount) (set! balance (+ balance amount)) balance)
  ...     (define (withdraw amount) (set! balance (- balance amount)) balance)
  ...     (define (check) balance)
  ...     (list deposit withdraw check))
kaappi> (define acct (make-account 100))
kaappi> ((first acct) 50)
;=> 150
kaappi> ((second acct) 30)
;=> 120
kaappi> ((third acct))
;=> 120
```


## Mutation and Why It's Rare

Scheme *can* mutate variables and data structures. The convention is that
mutating operations end with `!` (pronounced "bang").

`set!` changes an existing binding:

```scheme
kaappi> (define x 1)
kaappi> (set! x 2)
kaappi> x
;=> 2
```

`set-car!` and `set-cdr!` modify the contents of a pair in place:

```scheme
kaappi> (define p (list 1 2 3))
kaappi> (set-car! p 99)
kaappi> p
;=> (99 2 3)
```

However, idiomatic Scheme prefers building new values over mutating
existing ones. Instead of changing a list, you construct a new list with
the desired shape:

```scheme
kaappi> (define (replace-first lst val)
  ...     (cons val (cdr lst)))
kaappi> (replace-first '(1 2 3) 99)
;=> (99 2 3)
```

Why avoid mutation? Pure functions -- those that depend only on their
inputs and produce no side effects -- are easier to test, easier to reason
about, and safer in concurrent programs. Save mutation for things that are
inherently stateful: counters, caches, I/O buffers.


## Input and Output

`display` writes a value in human-readable form. Strings appear without
quotes, characters without the `#\` prefix.

```scheme
kaappi> (display "The answer is ")
The answer is
kaappi> (display 42)
42
kaappi> (newline)

```

`write` produces machine-readable output that can be read back with
`read`. Strings include quotes, characters include `#\`:

```scheme
kaappi> (write "hello")
"hello"
kaappi> (write #\a)
#\a
```

`read-line` reads a line of text from standard input:

```scheme
kaappi> (display "Name: ")
Name:
kaappi> (define name (read-line))
Alice
kaappi> (string-append "Hello, " name "!")
;=> "Hello, Alice!"
```

`read` reads and parses a complete Scheme datum:

```scheme
kaappi> (define x (read))
(1 2 3)
kaappi> (car x)
;=> 1
```

String ports let you capture output as a string without writing to the
console:

```scheme
kaappi> (define port (open-output-string))
kaappi> (write 42 port)
kaappi> (write " bottles" port)
kaappi> (get-output-string port)
;=> "42\" bottles\""
```

For file I/O, `with-input-from-file` redirects standard input to read
from a file:

```scheme
(with-input-from-file "data.txt"
  (lambda ()
    (let loop ((line (read-line)))
      (unless (eof-object? line)
        (display line)
        (newline)
        (loop (read-line))))))
```


## Where to Go Next

This tutorial covered the core of Scheme: expressions, data types, lists,
functions, recursion, higher-order functions, closures, and I/O. There is
more to explore.

- [Language Reference](language.md) -- quick syntax lookup for everything
  shown here plus macros, continuations, records, exceptions, and lazy
  evaluation
- [Procedure Reference](../procedures/index.md) -- detailed documentation
  for every built-in procedure, organized by category
- [Libraries](libraries.md) -- how to import SRFIs and write your own
  libraries
- [Tips](tips.md) -- performance tips, common pitfalls, and REPL workflow

---

Next: [Language Reference](language.md)
