export const LESSONS = [
  {
    title: "Hello, Scheme!",
    prose: `<h3>Hello, Scheme!</h3>
<p>In Scheme, everything is an <strong>expression</strong> that produces a value. There are no statements — even <code>if</code> returns a result.</p>
<p>The syntax is uniform: <code>(operator operand ...)</code>. The first element is always the function, and parentheses are never optional.</p>
<p>Try running this program. Then change the message or try an arithmetic expression like <code>(+ 2 (* 3 4))</code>.</p>`,
    code: `; Your first Scheme program!
(display "Hello from Kaappi!")
(newline)

; Arithmetic — everything is an expression
(display (+ 2 (* 3 4)))
(newline)

; Nesting is explicit — no precedence rules
(display (/ (+ 10 20) 3))
(newline)`,
    challenge: "Try replacing the arithmetic with (- 100 (* 7 13)). What do you get?",
  },
  {
    title: "Numbers",
    prose: `<h3>Numbers</h3>
<p>Kaappi supports the full <strong>numeric tower</strong>: integers of any size, exact rationals like <code>1/3</code>, floating-point, and complex numbers like <code>3+4i</code>.</p>
<p>Integers and rationals are <strong>exact</strong> — no rounding, no overflow. Floating-point numbers are <strong>inexact</strong>. Kaappi tracks this distinction and never silently loses precision.</p>
<p>Arithmetic operators work across all types: <code>+</code>, <code>-</code>, <code>*</code>, <code>/</code> handle mixed exact/inexact automatically.</p>`,
    code: `; Exact integers — no size limit
(display (* 100000000000 100000000000))
(newline)

; Exact rationals — no rounding
(display (+ 1/3 1/6))
(newline)

; Floating point (inexact)
(display (sqrt 2))
(newline)

; Complex numbers
(display (+ 3+4i 1-2i))
(newline)

; Mixing exact and inexact
(display (exact? (* 2 1/3)))
(newline)
(display (inexact? (+ 1 0.5)))
(newline)`,
    challenge: "What does (/ 1 3) give? How about (* 1/3 3)? Try both.",
  },
  {
    title: "Strings & Booleans",
    prose: `<h3>Strings & Booleans</h3>
<p>Strings are <strong>UTF-8</strong> sequences enclosed in double quotes. You can index them by codepoint, concatenate, split, and search.</p>
<p>Booleans are <code>#t</code> (true) and <code>#f</code> (false). In Scheme, <strong>only <code>#f</code> is false</strong> — everything else is true, including <code>0</code>, <code>""</code>, and the empty list <code>'()</code>. This differs from most languages.</p>`,
    code: `; String operations
(display (string-append "Hello" ", " "world!"))
(newline)
(display (string-length "Kaappi"))
(newline)
(display (substring "Hello, world!" 7 12))
(newline)

; Booleans — only #f is false
(display (if 0 "zero is true!" "zero is false"))
(newline)
(display (if "" "empty string is true!" "empty string is false"))
(newline)
(display (if '() "empty list is true!" "empty list is false"))
(newline)

; Predicates
(display (string? "hello"))
(newline)
(display (number? 42))
(newline)`,
    challenge: "What does (if #f \"yes\" \"no\") return? What about (if #t \"yes\" \"no\")?",
  },
  {
    title: "Lists",
    prose: `<h3>Lists</h3>
<p>Lists are Scheme's fundamental data structure. A list is a chain of <strong>pairs</strong> — each pair holds a value (<code>car</code>) and a pointer to the next pair (<code>cdr</code>). The empty list <code>'()</code> terminates the chain.</p>
<p>The quote <code>'</code> prevents evaluation: <code>'(1 2 3)</code> is a list, while <code>(1 2 3)</code> would try to call <code>1</code> as a function.</p>
<p><code>cons</code> builds a pair, <code>car</code> extracts the first element, and <code>cdr</code> extracts the rest.</p>`,
    code: `; Quoted lists
(display '(1 2 3))
(newline)

; Building with cons
(display (cons 1 (cons 2 (cons 3 '()))))
(newline)

; Extracting elements
(display (car '(a b c)))    ; first element
(newline)
(display (cdr '(a b c)))    ; rest of the list
(newline)
(display (cadr '(a b c)))   ; second element (car of cdr)
(newline)

; list builds a list directly
(display (list 'x 'y 'z))
(newline)

; length, append, reverse
(display (length '(1 2 3 4 5)))
(newline)
(display (reverse '(1 2 3)))
(newline)`,
    challenge: "What does (cons 'a '(b c)) produce? What about (cons '(a) '(b c))?",
  },
  {
    title: "Defining Functions",
    prose: `<h3>Defining Functions</h3>
<p><code>define</code> binds a name to a value. For functions, there's a convenient shorthand: <code>(define (name params) body)</code> is equivalent to <code>(define name (lambda (params) body))</code>.</p>
<p><code>lambda</code> creates an anonymous function — a value you can pass around, store, or call. Functions are <strong>first-class</strong>: they're values like any other.</p>`,
    code: `; Define a function
(define (square x)
  (* x x))

(display (square 5))
(newline)

; Lambda — anonymous function
(define cube (lambda (x) (* x x x)))
(display (cube 4))
(newline)

; Functions are values — pass them around
(define (apply-twice f x)
  (f (f x)))

(display (apply-twice square 3))   ; (3^2)^2 = 81
(newline)
(display (apply-twice add1 10))    ; 10 + 1 + 1 = 12
(newline)

; Multiple parameters
(define (greet name greeting)
  (string-append greeting ", " name "!"))

(display (greet "world" "Hello"))
(newline)`,
    challenge: "Define a function (double x) that doubles a number. Then try (apply-twice double 3).",
  },
  {
    title: "Conditionals",
    prose: `<h3>Conditionals</h3>
<p><code>if</code> is an expression with three parts: <code>(if test then else)</code>. It always returns a value.</p>
<p><code>cond</code> handles multiple branches — each clause is <code>(test expression)</code>, with an optional <code>(else ...)</code> fallback. <code>and</code> and <code>or</code> short-circuit and return the deciding value, not just <code>#t</code>/<code>#f</code>.</p>`,
    code: `; if is an expression — it returns a value
(display (if (> 3 2) "yes" "no"))
(newline)

; cond for multiple branches
(define (classify n)
  (cond
    ((negative? n) "negative")
    ((zero? n)     "zero")
    ((even? n)     "even")
    (else          "odd")))

(display (classify -5))  (newline)
(display (classify 0))   (newline)
(display (classify 4))   (newline)
(display (classify 7))   (newline)

; and/or return values, not just #t/#f
(display (or #f #f 42))       ; first truthy value
(newline)
(display (and 1 2 3))         ; last value if all true
(newline)
(display (and 1 #f 3))        ; #f — short-circuits
(newline)`,
    challenge: "Write a FizzBuzz: if n is divisible by 15, print \"FizzBuzz\"; by 3, \"Fizz\"; by 5, \"Buzz\"; else the number.",
  },
  {
    title: "Recursion",
    prose: `<h3>Recursion</h3>
<p>Scheme has no <code>for</code> or <code>while</code> loops. Iteration happens through <strong>recursion</strong>: a function that calls itself with a smaller problem until it reaches a base case.</p>
<p>Every recursive function needs two parts: the <strong>base case</strong> (when to stop) and the <strong>recursive step</strong> (how to break the problem down).</p>`,
    code: `; Factorial: n! = n * (n-1) * ... * 1
(define (factorial n)
  (if (<= n 1)
      1
      (* n (factorial (- n 1)))))

(display (factorial 10))
(newline)

; List length — recursion over lists
(define (my-length lst)
  (if (null? lst)
      0
      (+ 1 (my-length (cdr lst)))))

(display (my-length '(a b c d e)))
(newline)

; Sum of a list
(define (my-sum lst)
  (if (null? lst)
      0
      (+ (car lst) (my-sum (cdr lst)))))

(display (my-sum '(1 2 3 4 5)))
(newline)`,
    challenge: "Write (my-reverse lst) that reverses a list using recursion and append.",
  },
  {
    title: "Tail Calls",
    prose: `<h3>Tail Calls</h3>
<p>A <strong>tail call</strong> is a call in the last position of a function — nothing happens after it returns. Scheme guarantees that tail calls reuse the current stack frame, so <strong>tail-recursive functions use constant stack space</strong>.</p>
<p>The trick: use an <strong>accumulator</strong> parameter to carry the result, so the recursive call is the very last thing the function does.</p>
<p>Named <code>let</code> is the idiomatic way to write loops in Scheme.</p>`,
    code: `; Naive recursion — builds stack frames
; (define (sum-naive n)
;   (if (= n 0) 0 (+ n (sum-naive (- n 1)))))
; This would overflow for large n!

; Tail-recursive with accumulator — constant stack
(define (sum n)
  (define (loop i acc)
    (if (= i 0) acc (loop (- i 1) (+ acc i))))
  (loop n 0))

(display (sum 1000000))  ; 1 million — no stack overflow
(newline)

; Named let — idiomatic Scheme loop
(define (sum-named n)
  (let loop ((i n) (acc 0))
    (if (= i 0) acc
        (loop (- i 1) (+ acc i)))))

(display (sum-named 100))
(newline)

; Fibonacci with accumulator
(define (fib n)
  (let loop ((i n) (a 0) (b 1))
    (if (= i 0) a (loop (- i 1) b (+ a b)))))

(display (fib 50))
(newline)`,
    challenge: "The naive sum would crash at 1M. Try changing (sum 1000000) to see it work instantly.",
  },
  {
    title: "Higher-Order Functions",
    prose: `<h3>Higher-Order Functions</h3>
<p>Functions that take or return other functions are <strong>higher-order</strong>. The big three for lists: <code>map</code> applies a function to each element, <code>filter</code> keeps elements matching a predicate, and <code>fold</code> reduces a list to a single value.</p>
<p>Use <code>lambda</code> for one-off functions you don't need to name.</p>`,
    code: `(import (srfi 1))

; map — transform each element
(display (map (lambda (x) (* x x)) '(1 2 3 4 5)))
(newline)

; filter — keep elements matching a predicate
(display (filter even? '(1 2 3 4 5 6 7 8)))
(newline)

; fold — reduce to a single value
(display (fold + 0 '(1 2 3 4 5)))   ; sum
(newline)
(display (fold * 1 '(1 2 3 4 5)))   ; product
(newline)

; Compose operations — pipeline style
(let ((nums '(1 2 3 4 5 6 7 8 9 10)))
  (display "Squares of odds: ")
  (display
    (map (lambda (x) (* x x))
         (filter odd? nums)))
  (newline)

  (display "Sum of evens: ")
  (display
    (fold + 0 (filter even? nums)))
  (newline))`,
    challenge: "Use map and filter to get the lengths of strings longer than 3 characters from '(\"hi\" \"hello\" \"hey\" \"greetings\").",
  },
  {
    title: "Let & Closures",
    prose: `<h3>Let & Closures</h3>
<p><code>let</code> introduces local bindings: <code>(let ((x 1) (y 2)) body)</code>. The bindings are parallel — <code>y</code> can't see <code>x</code>. Use <code>let*</code> for sequential bindings where each can reference the previous.</p>
<p>A <strong>closure</strong> is a function that captures variables from its enclosing scope. The classic example: a counter function that remembers its state.</p>`,
    code: `; let — parallel bindings
(let ((x 10)
      (y 20))
  (display (+ x y))
  (newline))

; let* — sequential (each sees the previous)
(let* ((x 10)
       (y (* x 2)))
  (display y)
  (newline))

; Closures — functions that capture state
(define (make-counter)
  (let ((count 0))
    (lambda ()
      (set! count (+ count 1))
      count)))

(define c1 (make-counter))
(define c2 (make-counter))

(display (c1)) (newline)   ; 1
(display (c1)) (newline)   ; 2
(display (c1)) (newline)   ; 3
(display (c2)) (newline)   ; 1 — independent counter
(display (c2)) (newline)   ; 2`,
    challenge: "Modify make-counter to take a start value and a step size.",
  },
  {
    title: "Macros",
    prose: `<h3>Macros</h3>
<p>Scheme macros transform code at compile time using <code>define-syntax</code> and <code>syntax-rules</code>. Unlike text macros, they're <strong>hygienic</strong> — introduced variables never clash with user code.</p>
<p>A macro takes a code pattern and rewrites it. The <code>...</code> ellipsis matches zero or more repetitions.</p>`,
    code: `; swap! — a macro that swaps two variables
(define-syntax swap!
  (syntax-rules ()
    ((_ a b)
     (let ((tmp a))
       (set! a b)
       (set! b tmp)))))

(define x 1)
(define y 2)
(swap! x y)
(display x) (display " ") (display y)
(newline)

; my-when — like 'when' in other languages
(define-syntax my-when
  (syntax-rules ()
    ((_ test body ...)
     (if test (begin body ...)))))

(my-when (> 3 2)
  (display "3 > 2 is true")
  (newline))

; unless — the opposite
(define-syntax unless
  (syntax-rules ()
    ((_ test body ...)
     (if (not test) (begin body ...)))))

(unless (= 1 2)
  (display "1 is not 2")
  (newline))`,
    challenge: "Write a (repeat n body ...) macro that executes body n times. Hint: use a named let inside.",
  },
  {
    title: "Libraries",
    prose: `<h3>Libraries</h3>
<p><code>define-library</code> creates a module with explicit <code>export</code> and <code>import</code> declarations. Only exported names are visible to importers — everything else is private.</p>
<p>Libraries are Scheme's module system. They let you organize code into reusable, encapsulated units.</p>`,
    code: `; Define a library inline
(define-library (math utils)
  (import (scheme base))
  (export square cube average)
  (begin
    (define (square x) (* x x))
    (define (cube x) (* x x x))
    (define (average . nums)
      (/ (apply + nums) (length nums)))))

; Import and use it
(import (math utils))

(display "square(7) = ")
(display (square 7))
(newline)

(display "cube(3) = ")
(display (cube 3))
(newline)

(display "average(2,4,6,8) = ")
(display (average 2 4 6 8))
(newline)

; Can't access internal helpers (they're private)
; (display (helper)) ; would error`,
    challenge: "Add a (factorial n) function to the library, export it, and call it.",
  },
];
