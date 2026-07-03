# Control Flow

Procedures for managing program flow including continuations, multiple
values, exceptions, and dynamic binding. Available from `(scheme base)`.

## Choosing the right control flow

| Need | Use | Cost |
|------|-----|------|
| Apply a function to a list of args | `apply` | Minimal |
| Return multiple values | `values` + `call-with-values` | Minimal |
| Structured error handling | `guard` + `raise` | Minimal when no error |
| Non-local exit (early return, loop break) | `call/ec` | Cheap — no stack copy |
| Coroutines, backtracking, advanced flow | `call/cc` | Expensive — copies full stack |
| Cleanup on exit (like `finally`) | `dynamic-wind` | Moderate |

**Key guidance:**

- Prefer `call/ec` over `call/cc` unless you need to reinvoke the
  continuation after the procedure returns. `call/ec` is significantly
  faster because it doesn't snapshot the stack
- Use `guard` for error handling — it combines exception catching with
  pattern matching and is the R7RS standard approach
- Tail calls are optimized automatically. Write loops as recursive calls
  in tail position and they use O(1) stack

---

## Procedure Application

### `apply` { #apply }

**Syntax:** `(apply proc arg1 ... args)`

Calls *proc* with the given arguments. The last argument must be a list;
its elements are spread as individual arguments. Any arguments before
the final list are prepended as individual arguments.

```scheme
kaappi> (apply + '(1 2 3))
;=> 6
kaappi> (apply + 1 2 '(3 4))
;=> 10
kaappi> (apply list 'a 'b '(c d))
;=> (a b c d)
kaappi> (apply string #\h #\i '())
;=> "hi"
```

!!! note
    `apply` requires at least two arguments: the procedure and the trailing
    list. The trailing list is always spread, so `(apply + '(1 2 3))` is
    equivalent to `(+ 1 2 3)`.

**See also:** [`map`](./pairs-and-lists.md#map),
[`for-each`](./pairs-and-lists.md#for-each),
[`call-with-values`](#call-with-values)

---

## Continuations

### `call-with-current-continuation` { #call-with-current-continuation }

**Syntax:** `(call-with-current-continuation proc)`

Captures the current continuation and passes it as an escape procedure
to *proc*. The escape procedure, when called with a value, abandons the
current computation and returns that value to the point where
`call-with-current-continuation` was called. The continuation can be
invoked multiple times and from outside the dynamic extent of the
original call.

```scheme
kaappi> (call-with-current-continuation
         (lambda (k) (k 42)))
;=> 42
kaappi> (call-with-current-continuation
         (lambda (k) (+ 1 (k 42))))
;=> 42
kaappi> (let ((saved #f))
         (let ((result (call-with-current-continuation
                         (lambda (k) (set! saved k) 0))))
           (if (< result 3)
               (saved (+ result 1))
               result)))
;=> 3
```

**See also:** [`call/cc`](#callcc), [`call/ec`](#callec),
[`dynamic-wind`](#dynamic-wind)

---

### `call/cc` { #callcc }

**Syntax:** `(call/cc proc)`

An alias for `call-with-current-continuation`. The captured continuation
can be called any number of times and from any dynamic context. This is
the most powerful form of continuation but also the most expensive, as
the runtime must preserve the full call stack.

```scheme
kaappi> (call/cc (lambda (k) (k 42)))
;=> 42
kaappi> (+ 1 (call/cc (lambda (k) (+ 2 (k 3)))))
;=> 4
```

**See also:** [`call-with-current-continuation`](#call-with-current-continuation),
[`call/ec`](#callec)

---

### `call-with-escape-continuation` { #call-with-escape-continuation }

**Syntax:** `(call-with-escape-continuation proc)`

Like `call-with-current-continuation`, but the continuation can only be
called during the dynamic extent of *proc*. After *proc* returns
normally, invoking the escape continuation raises an error. Because the
runtime knows the continuation will not be used after *proc* returns, it
can be implemented more efficiently than a full continuation.

```scheme
kaappi> (call-with-escape-continuation
         (lambda (exit) (exit 42)))
;=> 42
kaappi> (call-with-escape-continuation
         (lambda (exit)
           (for-each (lambda (x)
                       (when (negative? x) (exit x)))
                     '(3 1 -4 1 5))
           'all-positive))
;=> -4
```

**See also:** [`call/ec`](#callec),
[`call-with-current-continuation`](#call-with-current-continuation)

---

### `call/ec` { #callec }

**Syntax:** `(call/ec proc)`

An alias for `call-with-escape-continuation`. The escape continuation
is a one-shot exit: it can only be called within the dynamic extent of
*proc*. Much cheaper than `call/cc` because no stack snapshot is needed.

**Prefer `call/ec` over `call/cc`** unless you need to reinvoke the
continuation after the procedure returns.

```scheme
kaappi> (call/ec (lambda (exit) (exit 'done)))
;=> done
kaappi> (call/ec
         (lambda (return)
           (let loop ((i 0))
             (when (= i 5) (return i))
             (loop (+ i 1)))))
;=> 5
```

**Common pattern** — early return from iteration:

```scheme
(define (find-negative lst)
  (call/ec (lambda (return)
    (for-each (lambda (x)
                (when (negative? x) (return x)))
              lst)
    #f)))

(find-negative '(1 2 -3 4))  ;=> -3
(find-negative '(1 2 3))     ;=> #f
```

**See also:** [`call-with-escape-continuation`](#call-with-escape-continuation),
[`call/cc`](#callcc)

---

### `dynamic-wind` { #dynamic-wind }

**Syntax:** `(dynamic-wind before thunk after)`

Calls *thunk*, guaranteeing that *before* is called when control enters
the dynamic extent of *thunk* and *after* is called when control leaves.
If a continuation captured inside *thunk* is invoked from outside,
*before* is called again upon re-entry; if a continuation captured
outside *thunk* is invoked from inside, *after* is called upon exit.
All three arguments are zero-argument procedures (thunks).

```scheme
kaappi> (let ((log '()))
         (dynamic-wind
           (lambda () (set! log (cons 'in log)))
           (lambda () (set! log (cons 'body log)))
           (lambda () (set! log (cons 'out log))))
         (reverse log))
;=> (in body out)
kaappi> (let ((log '())
              (k #f))
         (dynamic-wind
           (lambda () (set! log (cons 'in log)))
           (lambda () (call/cc (lambda (c) (set! k c)))
                      (set! log (cons 'body log)))
           (lambda () (set! log (cons 'out log))))
         (when (< (length log) 6) (k #f))
         (reverse log))
;=> (in body out in body out)
```

**See also:** [`call/cc`](#callcc),
[`with-exception-handler`](#with-exception-handler)

---

## Multiple Values

### `values` { #values }

**Syntax:** `(values obj ...)`

Returns zero or more values. Multiple values are not first-class objects
-- they must be received by a continuation that expects them, typically
`call-with-values` or special forms like `let-values` and
`receive`. A single value passed to `values` is equivalent to
returning that value directly.

```scheme
kaappi> (values 1 2 3)
;=> 1
;=> 2
;=> 3
kaappi> (values)
kaappi> (call-with-values (lambda () (values 1 2)) +)
;=> 3
```

**See also:** [`call-with-values`](#call-with-values)

---

### `call-with-values` { #call-with-values }

**Syntax:** `(call-with-values producer consumer)`

Calls *producer* with no arguments. The values returned by *producer*
(which may use `values` to return multiple values) are passed as
arguments to *consumer*. Returns whatever *consumer* returns.

```scheme
kaappi> (call-with-values (lambda () (values 1 2 3)) list)
;=> (1 2 3)
kaappi> (call-with-values (lambda () (values 4 5)) +)
;=> 9
kaappi> (call-with-values (lambda () 42) (lambda (x) (* x x)))
;=> 1764
```

**See also:** [`values`](#values),
[`apply`](#apply)

---

## Dynamic Binding

### `with-exception-handler` { #with-exception-handler }

**Syntax:** `(with-exception-handler handler thunk)`

Installs *handler* as the current exception handler for the dynamic
extent of the call to *thunk*. If an exception is raised (by `raise` or
`raise-continuable`) during the execution of *thunk*, *handler* is
called with the raised object as its argument. The *handler* is called
with the exception handler that was in effect before
`with-exception-handler` was called.

If *handler* returns (only possible when the exception was raised by
`raise-continuable`), the value returned by *handler* becomes the return
value of the `raise-continuable` call. If the exception was raised by
`raise`, returning from *handler* raises a new exception.

```scheme
kaappi> (with-exception-handler
         (lambda (e) (display "caught: ") (display e) (newline) 42)
         (lambda () (raise-continuable "oops")))
caught: oops
;=> 42
kaappi> (call/cc
         (lambda (exit)
           (with-exception-handler
             (lambda (e) (exit (list 'caught e)))
             (lambda () (raise "boom")))))
;=> (caught "boom")
```

**See also:** [`raise`](#raise), [`raise-continuable`](#raise-continuable),
[`error`](#error), [`dynamic-wind`](#dynamic-wind)

---

## Exceptions

### `raise` { #raise }

**Syntax:** `(raise obj)`

Raises an exception by invoking the current exception handler with *obj*
as its argument. The exception handler is called in the dynamic
environment of the `raise` call, with the exception handler that was in
effect before the current one installed. If the handler returns, a new
exception is raised (it is an error for a `raise` handler to return).

```scheme
kaappi> (call/cc
         (lambda (exit)
           (with-exception-handler
             (lambda (e) (exit (string-append "error: " e)))
             (lambda () (raise "something went wrong")))))
;=> "error: something went wrong"
```

**See also:** [`raise-continuable`](#raise-continuable),
[`with-exception-handler`](#with-exception-handler),
[`error`](#error)

---

### `raise-continuable` { #raise-continuable }

**Syntax:** `(raise-continuable obj)`

Like `raise`, but allows the exception handler to return a value. The
returned value becomes the result of the `raise-continuable` expression.
This is used for conditions where the handler can supply a replacement
value and execution continues normally.

```scheme
kaappi> (with-exception-handler
         (lambda (e) (* e 10))
         (lambda () (+ 1 (raise-continuable 5))))
;=> 51
```

**See also:** [`raise`](#raise),
[`with-exception-handler`](#with-exception-handler)

---

### `error` { #error }

**Syntax:** `(error message obj ...)`

Creates a new error object with the string *message* and zero or more
*irritant* objects, then raises it. This is the standard way to signal
an error in Scheme programs. The *message* should describe what went
wrong, and the irritants provide additional context (typically the
offending values).

**Errors:** Always raises. The error can be caught with `guard`.

```scheme
kaappi> (guard (e (#t (error-object-message e)))
         (error "index out of range" 5 '(0 3)))
;=> "index out of range"
kaappi> (guard (e (#t (error-object-irritants e)))
         (error "bad value" 42 'expected-string))
;=> (42 expected-string)
```

**Common pattern** — input validation:

```scheme
(define (divide a b)
  (when (zero? b) (error "divide: division by zero" a b))
  (/ a b))
```

**Common pattern** — catch and handle:

```scheme
(guard (e
        ((string=? (error-object-message e) "not found")
         (display "using default\n")
         default-value)
        (#t (raise e)))
  (lookup key))
```

**See also:** [`error-object?`](#error-object-pred),
[`error-object-message`](#error-object-message),
[`error-object-irritants`](#error-object-irritants),
[`raise`](#raise)

---

### `error-object?` { #error-object-pred }

**Syntax:** `(error-object? obj)`

Returns `#t` if *obj* is an error object created by `error` or raised by
the implementation, and `#f` otherwise. Error objects carry a message
string and a (possibly empty) list of irritants.

```scheme
kaappi> (guard (e (#t (error-object? e)))
         (error "boom" 'details))
;=> #t
kaappi> (error-object? "not an error")
;=> #f
kaappi> (error-object? 42)
;=> #f
```

**See also:** [`error`](#error),
[`error-object-message`](#error-object-message),
[`error-object-irritants`](#error-object-irritants),
[`port?`](./type-checking.md#port)

---

### `error-object-message` { #error-object-message }

**Syntax:** `(error-object-message error-object)`

Returns the message string from *error-object*. It is an error if the
argument is not an error object.

```scheme
kaappi> (guard (e (#t (error-object-message e)))
         (error "file not found" "/tmp/missing.txt"))
;=> "file not found"
```

**See also:** [`error`](#error), [`error-object?`](#error-object-pred),
[`error-object-irritants`](#error-object-irritants)

---

### `error-object-irritants` { #error-object-irritants }

**Syntax:** `(error-object-irritants error-object)`

Returns the list of irritants from *error-object*. The irritants are the
extra arguments that were passed to `error` after the message string. If
`error` was called with only a message, this returns the empty list. It
is an error if the argument is not an error object.

```scheme
kaappi> (guard (e (#t (error-object-irritants e)))
         (error "bad args" 1 2 3))
;=> (1 2 3)
kaappi> (guard (e (#t (error-object-irritants e)))
         (error "no extras"))
;=> ()
```

**See also:** [`error`](#error), [`error-object?`](#error-object-pred),
[`error-object-message`](#error-object-message)

---

### `file-error?` { #file-error }

**Syntax:** `(file-error? obj)`

Returns `#t` if *obj* is an error object raised by file I/O operations
(such as `open-input-file` when the file does not exist), and `#f`
otherwise. This allows programs to distinguish file-related errors from
other kinds of errors in exception handlers.

```scheme
kaappi> (guard (e (#t (file-error? e)))
         (open-input-file "/nonexistent/file"))
;=> #t
kaappi> (guard (e (#t (file-error? e)))
         (error "not a file error"))
;=> #f
```

**See also:** [`read-error?`](#read-error), [`error-object?`](#error-object-pred),
[`open-input-file`](./ports-and-io.md#open-input-file)

---

### `read-error?` { #read-error }

**Syntax:** `(read-error? obj)`

Returns `#t` if *obj* is an error object raised by `read` or other
parsing operations when the input is malformed, and `#f` otherwise. This
allows programs to distinguish syntax errors from other kinds of errors
in exception handlers.

```scheme
kaappi> (guard (e (#t (read-error? e)))
         (read (open-input-string "(unclosed")))
;=> #t
kaappi> (guard (e (#t (read-error? e)))
         (error "not a read error"))
;=> #f
```

**See also:** [`file-error?`](#file-error), [`error-object?`](#error-object-pred),
[`read`](./ports-and-io.md#read)
