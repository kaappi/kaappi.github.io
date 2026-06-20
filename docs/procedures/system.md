# System and Environment

Procedures for interacting with the operating system, evaluating code,
and managing parameter objects. Available from `(scheme base)`,
`(scheme process-context)`, `(scheme time)`, `(scheme eval)`,
and `(scheme load)`.

---

## Process Control

### `exit` { #exit }

**Syntax:** `(exit)` | `(exit status)`

Exits the Scheme process. If *status* is omitted or `#t`, the process
exits with a success status code (0). If *status* is `#f`, the process
exits with a failure status code. If *status* is an exact integer, it
is used directly as the exit code. Before exiting, `exit` runs all
outstanding `dynamic-wind` *after* thunks and flushes all output ports.

```scheme
kaappi> (exit)         ; exits with status 0
kaappi> (exit 0)       ; exits with status 0
kaappi> (exit 1)       ; exits with status 1
kaappi> (exit #f)      ; exits with failure status
```

!!! note
    Unlike `emergency-exit`, `exit` runs cleanup code installed by
    `dynamic-wind`. Use `exit` for normal program termination and
    `emergency-exit` only when cleanup must be skipped.

**See also:** [`emergency-exit`](#emergency-exit),
[`dynamic-wind`](./control-flow.md#dynamic-wind)

---

### `emergency-exit` { #emergency-exit }

**Syntax:** `(emergency-exit)` | `(emergency-exit status)`

Immediately terminates the process without running `dynamic-wind`
cleanup thunks or flushing output ports. The *status* argument works
as in `exit`. This is appropriate when the process is in an
unrecoverable state and cleanup code might hang or cause further
damage.

```scheme
kaappi> (emergency-exit)    ; immediate exit, status 0
kaappi> (emergency-exit 2)  ; immediate exit, status 2
```

**See also:** [`exit`](#exit)

---

## Command Line and Environment

### `command-line` { #command-line }

**Syntax:** `(command-line)`

Returns a list of strings representing the command-line arguments.
The first element is the program name (or an implementation-defined
string if not available). Subsequent elements are the arguments passed
to the program. Available from `(scheme process-context)`.

```scheme
;; Running: kaappi script.scm foo bar
kaappi> (command-line)
;=> ("script.scm" "foo" "bar")
kaappi> (car (command-line))
;=> "script.scm"
kaappi> (cdr (command-line))
;=> ("foo" "bar")
```

**See also:** [`get-environment-variable`](#get-environment-variable)

---

### `get-environment-variable` { #get-environment-variable }

**Syntax:** `(get-environment-variable name)`

Returns the value of the environment variable *name* as a string, or
`#f` if the variable is not set. Available from
`(scheme process-context)`.

```scheme
kaappi> (get-environment-variable "HOME")
;=> "/home/user"
kaappi> (get-environment-variable "PATH")
;=> "/usr/bin:/bin:/usr/local/bin"
kaappi> (get-environment-variable "NONEXISTENT")
;=> #f
```

**See also:** [`get-environment-variables`](#get-environment-variables),
[`command-line`](#command-line)

---

### `get-environment-variables` { #get-environment-variables }

**Syntax:** `(get-environment-variables)`

Returns the entire environment as an association list of string pairs.
Each element is `(name . value)` where both are strings. Available
from `(scheme process-context)`.

```scheme
kaappi> (assoc "HOME" (get-environment-variables))
;=> ("HOME" . "/home/user")
kaappi> (length (get-environment-variables))
;=> 42
kaappi> (map car (take (get-environment-variables) 3))
;=> ("HOME" "PATH" "SHELL")
```

**See also:** [`get-environment-variable`](#get-environment-variable)

---

## Time

### `current-second` { #current-second }

**Syntax:** `(current-second)`

Returns the current time as an inexact real number representing TAI
(International Atomic Time) seconds since midnight on January 1, 1970.
TAI does not skip or repeat seconds (unlike UTC, which has leap
seconds), so the value increases monotonically. Available from
`(scheme time)`.

```scheme
kaappi> (current-second)
;=> 1718900000.123456
kaappi> (let ((start (current-second)))
         ;; ... do some work ...
         (- (current-second) start))
;=> 0.002345
```

!!! note
    TAI is approximately 37 seconds ahead of UTC (as of 2024). The
    exact offset changes when a leap second is added.

**See also:** [`current-jiffy`](#current-jiffy),
[`jiffies-per-second`](#jiffies-per-second)

---

### `current-jiffy` { #current-jiffy }

**Syntax:** `(current-jiffy)`

Returns the number of *jiffies* (implementation-defined time units)
elapsed since an arbitrary, fixed epoch. This provides high-resolution
timing suitable for performance measurement. The resolution is given
by `jiffies-per-second`. Available from `(scheme time)`.

```scheme
kaappi> (current-jiffy)
;=> 1234567890123
kaappi> (let ((start (current-jiffy)))
         ;; ... do some work ...
         (let ((elapsed (- (current-jiffy) start)))
           (/ elapsed (jiffies-per-second))))
;=> 0.000042
```

**See also:** [`jiffies-per-second`](#jiffies-per-second),
[`current-second`](#current-second)

---

### `jiffies-per-second` { #jiffies-per-second }

**Syntax:** `(jiffies-per-second)`

Returns the number of jiffies per second. This is a constant for a
given implementation. Divide elapsed jiffies by this value to convert
to seconds. Available from `(scheme time)`.

```scheme
kaappi> (jiffies-per-second)
;=> 1000000000
kaappi> (exact (/ (jiffies-per-second) 1000))
;=> 1000000
```

**See also:** [`current-jiffy`](#current-jiffy),
[`current-second`](#current-second)

---

## Feature Detection

### `features` { #features }

**Syntax:** `(features)`

Returns a list of symbols representing the features supported by this
implementation. These are the same identifiers tested by `cond-expand`.
Typical features include `r7rs`, `kaappi`, the operating system, and
the machine architecture.

```scheme
kaappi> (features)
;=> (r7rs kaappi zig ieee-float full-numeric-tower posix
     macosx x86-64 little-endian)
kaappi> (memq 'r7rs (features))
;=> (r7rs kaappi zig ...)
kaappi> (memq 'windows (features))
;=> #f
```

**See also:** [`cond-expand`](./syntax-forms.md#cond-expand)

---

## Evaluation

### `eval` { #eval }

**Syntax:** `(eval expr environment)`

Evaluates *expr* in the given *environment* and returns the result.
The expression is a Scheme datum (typically constructed with `quote` or
`read`). Available from `(scheme eval)`.

```scheme
kaappi> (eval '(+ 1 2 3) (environment '(scheme base)))
;=> 6
kaappi> (eval '(map car '((a 1) (b 2) (c 3)))
              (environment '(scheme base)))
;=> (a b c)
kaappi> (eval '(string-append "hello" " " "world")
              (environment '(scheme base)))
;=> "hello world"
```

!!! warning
    `eval` is significantly slower than compiled code and prevents
    many optimizations. Prefer macros or higher-order functions when
    possible.

**See also:** [`environment`](#environment),
[`interaction-environment`](#interaction-environment)

---

### `environment` { #environment }

**Syntax:** `(environment import-set ...)`

Creates an immutable environment from the given import sets. Each
*import-set* follows the same syntax as `import` declarations. The
returned environment is suitable for use as the second argument to
`eval`. Available from `(scheme eval)`.

```scheme
kaappi> (define env (environment '(scheme base) '(scheme write)))
kaappi> (eval '(begin (display "hello") (newline)) env)
hello
kaappi> (eval '(+ 1 2) (environment '(scheme base)))
;=> 3
```

**See also:** [`eval`](#eval),
[`interaction-environment`](#interaction-environment),
[`import`](./syntax-forms.md#import)

---

### `interaction-environment` { #interaction-environment }

**Syntax:** `(interaction-environment)`

Returns the environment used by the REPL, which contains all bindings
that have been defined interactively. Unlike environments created by
`environment`, the interaction environment is mutable -- new bindings
can be added to it. Available from `(scheme repl)`.

```scheme
kaappi> (define x 42)
kaappi> (eval 'x (interaction-environment))
;=> 42
kaappi> (eval '(define y 99) (interaction-environment))
kaappi> y
;=> 99
```

**See also:** [`environment`](#environment), [`eval`](#eval)

---

## Loading

### `load` { #load }

**Syntax:** `(load filename)`

Reads and evaluates the Scheme source file *filename* in the
interaction environment. Definitions and side effects from the loaded
file take effect as if they were typed at the REPL. Available from
`(scheme load)`.

```scheme
;; Assuming utils.scm contains: (define (square x) (* x x))
kaappi> (load "utils.scm")
kaappi> (square 5)
;=> 25
```

!!! note
    `load` is intended for interactive use. For modular programs, use
    `define-library` and `import` instead.

**See also:** [`eval`](#eval),
[`define-library`](./syntax-forms.md#define-library),
[`import`](./syntax-forms.md#import)

---

## Parameters

### `make-parameter` { #make-parameter }

**Syntax:** `(make-parameter init)` | `(make-parameter init converter)`

Creates a parameter object with initial value *init*. When called with
no arguments, a parameter object returns its current value. When called
with one argument, it sets the value (applying the *converter* first,
if one was provided). The *converter* is a one-argument procedure that
validates or transforms values before they are stored; it is also
applied to *init*.

Parameter objects are used with `parameterize` to establish dynamic
bindings that are automatically restored when control leaves the
`parameterize` body.

```scheme
kaappi> (define verbose (make-parameter #f))
kaappi> (verbose)
;=> #f
kaappi> (parameterize ((verbose #t))
         (verbose))
;=> #t
kaappi> (verbose)
;=> #f
kaappi> (define max-depth (make-parameter 10
                            (lambda (v)
                              (if (and (integer? v) (positive? v))
                                  v
                                  (error "max-depth must be a positive integer" v)))))
kaappi> (max-depth)
;=> 10
kaappi> (parameterize ((max-depth 5))
         (max-depth))
;=> 5
```

**See also:** [`parameterize`](./syntax-forms.md#parameterize),
[`current-input-port`](./ports-and-io.md#current-input-port),
[`current-output-port`](./ports-and-io.md#current-output-port)
