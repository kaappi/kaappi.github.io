export const EXAMPLES = {
  hello: `(display "Hello from Kaappi!")
(newline)`,
  fib: `(define (fib n)
  (if (<= n 1)
      n
      (+ (fib (- n 1))
         (fib (- n 2)))))

(display "fib(30) = ")
(display (fib 30))
(newline)`,
  higher: `(import (srfi 1))

(define nums '(1 2 3 4 5 6 7 8 9 10))

(display "Squares of odds: ")
(display
  (map (lambda (x) (* x x))
       (filter odd? nums)))
(newline)

(display "Sum: ")
(display (fold + 0 nums))
(newline)

(display "Product: ")
(display (fold * 1 nums))
(newline)`,
  macros: `(define-syntax swap!
  (syntax-rules ()
    ((_ a b)
     (let ((tmp a))
       (set! a b)
       (set! b tmp)))))

(define x 1)
(define y 2)
(display "Before: x=") (display x) (display " y=") (display y) (newline)
(swap! x y)
(display "After:  x=") (display x) (display " y=") (display y) (newline)

(define-syntax my-cond
  (syntax-rules (else)
    ((_ (else e ...)) (begin e ...))
    ((_ (test e ...) rest ...)
     (if test (begin e ...) (my-cond rest ...)))))

(display (my-cond
  ((> 1 2) "no")
  ((< 1 2) "yes")
  (else "maybe")))
(newline)`,
  callcc: `; Coroutine with call/cc
(define saved-k #f)

(define (producer)
  (display "Producing 1\\n")
  (call/cc (lambda (k) (set! saved-k k) 1))
  (display "Producing 2\\n")
  (call/cc (lambda (k) (set! saved-k k) 2))
  (display "Producing 3\\n")
  3)

(display "Result: ")
(display (producer))
(newline)

; Non-local exit
(display "Early exit: ")
(display
  (call-with-current-continuation
    (lambda (exit)
      (for-each (lambda (x)
                  (if (negative? x)
                      (exit x)))
                '(54 0 37 -3 245 19))
      #t)))
(newline)`,
  tail: `; Tail-recursive loop — 1 million iterations, constant stack
(define (loop n acc)
  (if (= n 0)
      acc
      (loop (- n 1) (+ acc 1))))

(display "1,000,000 iterations: ")
(display (loop 1000000 0))
(newline)

; Ackermann (small args — deeply recursive)
(define (ack m n)
  (cond ((= m 0) (+ n 1))
        ((= n 0) (ack (- m 1) 1))
        (else (ack (- m 1) (ack m (- n 1))))))

(display "ack(3,7) = ")
(display (ack 3 7))
(newline)`,
  library: `(define-library (geometry shapes)
  (import (scheme base) (scheme write))
  (export circle-area rect-area describe)
  (begin
    (define pi 3.141592653589793)

    (define (circle-area r)
      (* pi r r))

    (define (rect-area w h)
      (* w h))

    (define (describe shape . args)
      (display shape)
      (display ": ")
      (display
        (cond
          ((equal? shape "circle")
           (circle-area (car args)))
          ((equal? shape "rect")
           (rect-area (car args) (cadr args)))
          (else "unknown")))
      (newline))))

(import (geometry shapes))
(describe "circle" 5)
(describe "rect" 3 4)`,
};
