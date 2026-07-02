# SRFI-18 Threads

Multithreading primitives for concurrent programming. Import with
`(import (srfi 18))`. See also [Kaappi Extensions](./extensions.md) for
lightweight green threads (fibers).

!!! note
    SRFI-18 spawns real OS threads -- each thread gets its own VM and GC
    heap, and values are deep-copied when crossing thread boundaries. OS
    threads are unavailable in `--sandbox` mode and in the WebAssembly build
    (including the browser playground); use [fibers](./extensions.md) there.
    See the [Concurrency guide](../guide/concurrency.md) for details.

---

## Thread Operations

### `current-thread` { #current-thread }

**Syntax:** `(current-thread)`

Returns the thread object representing the currently executing thread.

```scheme
kaappi> (current-thread)
;=> #<thread main>
kaappi> (thread-name (current-thread))
;=> main
```

**See also:** [`thread?`](#thread-pred), [`make-thread`](#make-thread)

---

### `thread?` { #thread-pred }

**Syntax:** `(thread? obj)`

Returns `#t` if *obj* is a thread object, `#f` otherwise.

```scheme
kaappi> (thread? (current-thread))
;=> #t
kaappi> (thread? (make-thread (lambda () 42)))
;=> #t
kaappi> (thread? 'not-a-thread)
;=> #f
```

**See also:** [`current-thread`](#current-thread), [`make-thread`](#make-thread)

---

### `make-thread` { #make-thread }

**Syntax:** `(make-thread thunk)` | `(make-thread thunk name)`

Creates a new thread that will execute *thunk* (a procedure of zero
arguments) when started. The optional *name* is a string used for
identification and debugging. The thread is created in a non-started
state; call `thread-start!` to begin execution.

```scheme
kaappi> (define t (make-thread (lambda () (+ 1 2))))
kaappi> t
;=> #<thread>
kaappi> (define t2 (make-thread (lambda () 'done) "worker"))
kaappi> (thread-name t2)
;=> "worker"
```

**See also:** [`thread-start!`](#thread-start), [`thread-join!`](#thread-join)

---

### `thread-name` { #thread-name }

**Syntax:** `(thread-name thread)`

Returns the name associated with *thread*, or `#f` if no name was given
at creation time.

```scheme
kaappi> (thread-name (make-thread (lambda () #f) "my-thread"))
;=> "my-thread"
kaappi> (thread-name (make-thread (lambda () #f)))
;=> #f
```

**See also:** [`make-thread`](#make-thread)

---

### `thread-specific` { #thread-specific }

**Syntax:** `(thread-specific thread)`

Returns the thread-specific value associated with *thread*. Each thread
has a single slot for storing an arbitrary value, initially `#f`.

```scheme
kaappi> (thread-specific (current-thread))
;=> #f
kaappi> (thread-specific-set! (current-thread) '(my data))
kaappi> (thread-specific (current-thread))
;=> (my data)
```

**See also:** [`thread-specific-set!`](#thread-specific-set)

---

### `thread-specific-set!` { #thread-specific-set }

**Syntax:** `(thread-specific-set! thread obj)`

Sets the thread-specific value of *thread* to *obj*. This can be used to
associate per-thread data without using global mutable state.

```scheme
kaappi> (thread-specific-set! (current-thread) 42)
kaappi> (thread-specific (current-thread))
;=> 42
```

**See also:** [`thread-specific`](#thread-specific)

---

### `thread-start!` { #thread-start }

**Syntax:** `(thread-start! thread)`

Starts *thread* and returns the thread object. The thread begins
executing the thunk that was passed to `make-thread`. A thread can only
be started once; starting an already-started thread is an error.

The child thread receives a **deep copy** of the thunk's closure --
mutations in the child are not visible to the parent.

```scheme
kaappi> (define t (make-thread (lambda () (display "hello\n"))))
kaappi> (thread-start! t)
;=> #<thread>
hello
kaappi> (thread-join! t)
```

```bash
# OS threads work out of the box -- no special flag needed
kaappi program.scm
```

**See also:** [`make-thread`](#make-thread), [`thread-join!`](#thread-join)

---

### `thread-yield!` { #thread-yield }

**Syntax:** `(thread-yield!)`

Causes the current thread to voluntarily give up its time slice,
allowing the scheduler to run other ready threads. Returns an
unspecified value.

```scheme
kaappi> (thread-yield!)
```

**See also:** [`thread-sleep!`](#thread-sleep),
[`yield`](./extensions.md#yield) (fiber equivalent)

---

### `thread-sleep!` { #thread-sleep }

**Syntax:** `(thread-sleep! timeout)`

Causes the current thread to sleep until *timeout*. The *timeout* can
be a time object (from `seconds->time`) or a number of seconds as an
inexact real. Other threads continue to run during the sleep.

```scheme
kaappi> (thread-sleep! 0.5)  ; sleep 500ms
kaappi> (thread-sleep! (seconds->time (+ (time->seconds (current-time)) 1)))
```

**See also:** [`thread-yield!`](#thread-yield),
[`current-time`](#current-time), [`seconds->time`](#seconds-to-time)

---

### `thread-terminate!` { #thread-terminate }

**Syntax:** `(thread-terminate! thread)`

Forcefully terminates *thread*. Any thread that subsequently calls
`thread-join!` on the terminated thread will receive a
`terminated-thread-exception`. Use with caution: the terminated thread
does not get a chance to release resources or unlock mutexes.

```scheme
kaappi> (define t (make-thread (lambda () (thread-sleep! 100))))
kaappi> (thread-start! t)
;=> #<thread>
kaappi> (thread-terminate! t)
```

!!! note
    Terminating a thread that holds a mutex leaves the mutex in an
    abandoned state. Subsequent attempts to lock it will raise an
    `abandoned-mutex-exception`.

**See also:** [`thread-join!`](#thread-join),
[`terminated-thread-exception?`](#terminated-thread-exception)

---

### `thread-join!` { #thread-join }

**Syntax:** `(thread-join! thread)` | `(thread-join! thread timeout)` | `(thread-join! thread timeout timeout-val)`

Blocks the current thread until *thread* terminates. Returns the result
value of the thread's thunk (deep-copied from the child's heap to the
caller's heap). If the thread raised an uncaught exception, `thread-join!`
re-raises it wrapped in an `uncaught-exception` object.

If *timeout* is given (a time object or number of seconds) and the thread
has not terminated by then, a `join-timeout-exception` is raised -- unless
*timeout-val* is provided, in which case that value is returned instead.

```scheme
kaappi> (define t (make-thread (lambda () (* 6 7))))
kaappi> (thread-start! t)
;=> #<thread>
kaappi> (thread-join! t)
;=> 42
kaappi> (define t2 (make-thread (lambda () (thread-sleep! 10))))
kaappi> (thread-start! t2)
;=> #<thread>
kaappi> (thread-join! t2 0.1 'timed-out)
;=> timed-out
```

**See also:** [`thread-start!`](#thread-start),
[`join-timeout-exception?`](#join-timeout-exception),
[`uncaught-exception?`](#uncaught-exception)

---

## Mutexes

### `mutex?` { #mutex-pred }

**Syntax:** `(mutex? obj)`

Returns `#t` if *obj* is a mutex, `#f` otherwise.

```scheme
kaappi> (mutex? (make-mutex))
;=> #t
kaappi> (mutex? 'not-a-mutex)
;=> #f
```

**See also:** [`make-mutex`](#make-mutex)

---

### `make-mutex` { #make-mutex }

**Syntax:** `(make-mutex)` | `(make-mutex name)`

Creates a new mutex in the unlocked state. The optional *name* is a
string used for identification and debugging.

```scheme
kaappi> (define m (make-mutex "my-lock"))
kaappi> m
;=> #<mutex my-lock>
kaappi> (mutex-state m)
;=> not-abandoned
```

**See also:** [`mutex-lock!`](#mutex-lock), [`mutex-unlock!`](#mutex-unlock)

---

### `mutex-name` { #mutex-name }

**Syntax:** `(mutex-name mutex)`

Returns the name associated with *mutex*, or `#f` if no name was given.

```scheme
kaappi> (mutex-name (make-mutex "lock-1"))
;=> "lock-1"
kaappi> (mutex-name (make-mutex))
;=> #f
```

**See also:** [`make-mutex`](#make-mutex)

---

### `mutex-specific` { #mutex-specific }

**Syntax:** `(mutex-specific mutex)`

Returns the mutex-specific value associated with *mutex*, initially `#f`.

```scheme
kaappi> (define m (make-mutex))
kaappi> (mutex-specific m)
;=> #f
kaappi> (mutex-specific-set! m 'data)
kaappi> (mutex-specific m)
;=> data
```

**See also:** [`mutex-specific-set!`](#mutex-specific-set)

---

### `mutex-specific-set!` { #mutex-specific-set }

**Syntax:** `(mutex-specific-set! mutex obj)`

Sets the mutex-specific value of *mutex* to *obj*.

```scheme
kaappi> (define m (make-mutex))
kaappi> (mutex-specific-set! m '(resource-info))
kaappi> (mutex-specific m)
;=> (resource-info)
```

**See also:** [`mutex-specific`](#mutex-specific)

---

### `mutex-state` { #mutex-state }

**Syntax:** `(mutex-state mutex)`

Returns the state of *mutex*. Possible return values:

- A thread object -- the mutex is locked and owned by that thread
- The symbol `not-owned` -- the mutex is locked but not owned
- The symbol `abandoned` -- the mutex was abandoned by a terminated thread
- The symbol `not-abandoned` -- the mutex is unlocked

```scheme
kaappi> (define m (make-mutex))
kaappi> (mutex-state m)
;=> not-abandoned
kaappi> (mutex-lock! m)
;=> #t
kaappi> (mutex-state m)
;=> #<thread main>
```

**See also:** [`mutex-lock!`](#mutex-lock), [`mutex-unlock!`](#mutex-unlock)

---

### `mutex-lock!` { #mutex-lock }

**Syntax:** `(mutex-lock! mutex)` | `(mutex-lock! mutex timeout)` | `(mutex-lock! mutex timeout thread)`

Locks *mutex*. If the mutex is already locked, the current thread blocks
until it becomes available. Returns `#t` if the lock was acquired.

If *timeout* is given (a time object or number of seconds) and the mutex
cannot be acquired within that time, returns `#f`. The optional *thread*
argument specifies the new owner of the mutex (defaults to the current
thread); passing `#f` locks the mutex without an owner.

```scheme
kaappi> (define m (make-mutex))
kaappi> (mutex-lock! m)
;=> #t
kaappi> (mutex-state m)
;=> #<thread main>
kaappi> (mutex-unlock! m)
;=> #t
```

**See also:** [`mutex-unlock!`](#mutex-unlock), [`make-mutex`](#make-mutex)

---

### `mutex-unlock!` { #mutex-unlock }

**Syntax:** `(mutex-unlock! mutex)` | `(mutex-unlock! mutex condition-variable)` | `(mutex-unlock! mutex condition-variable timeout)`

Unlocks *mutex* and returns `#t`. If a *condition-variable* is given,
the current thread is blocked on that condition variable and the mutex is
unlocked atomically. If *timeout* is also given, the thread unblocks
after the timeout even if the condition variable was not signaled, and
returns `#f`.

```scheme
kaappi> (define m (make-mutex))
kaappi> (mutex-lock! m)
;=> #t
kaappi> (mutex-unlock! m)
;=> #t
kaappi> (mutex-state m)
;=> not-abandoned
```

**See also:** [`mutex-lock!`](#mutex-lock),
[`condition-variable-signal!`](#condition-variable-signal),
[`condition-variable-broadcast!`](#condition-variable-broadcast)

---

## Condition Variables

### `condition-variable?` { #condition-variable-pred }

**Syntax:** `(condition-variable? obj)`

Returns `#t` if *obj* is a condition variable, `#f` otherwise.

```scheme
kaappi> (condition-variable? (make-condition-variable))
;=> #t
kaappi> (condition-variable? (make-mutex))
;=> #f
```

**See also:** [`make-condition-variable`](#make-condition-variable)

---

### `make-condition-variable` { #make-condition-variable }

**Syntax:** `(make-condition-variable)` | `(make-condition-variable name)`

Creates a new condition variable. The optional *name* is a string used
for identification and debugging.

```scheme
kaappi> (define cv (make-condition-variable "data-ready"))
kaappi> cv
;=> #<condition-variable data-ready>
```

**See also:** [`condition-variable-signal!`](#condition-variable-signal),
[`condition-variable-broadcast!`](#condition-variable-broadcast)

---

### `condition-variable-name` { #condition-variable-name }

**Syntax:** `(condition-variable-name condition-variable)`

Returns the name associated with *condition-variable*, or `#f` if no
name was given.

```scheme
kaappi> (condition-variable-name (make-condition-variable "cv-1"))
;=> "cv-1"
kaappi> (condition-variable-name (make-condition-variable))
;=> #f
```

**See also:** [`make-condition-variable`](#make-condition-variable)

---

### `condition-variable-specific` { #condition-variable-specific }

**Syntax:** `(condition-variable-specific condition-variable)`

Returns the condition-variable-specific value, initially `#f`.

```scheme
kaappi> (define cv (make-condition-variable))
kaappi> (condition-variable-specific cv)
;=> #f
```

**See also:** [`condition-variable-specific-set!`](#condition-variable-specific-set)

---

### `condition-variable-specific-set!` { #condition-variable-specific-set }

**Syntax:** `(condition-variable-specific-set! condition-variable obj)`

Sets the condition-variable-specific value to *obj*.

```scheme
kaappi> (define cv (make-condition-variable))
kaappi> (condition-variable-specific-set! cv 'waiting)
kaappi> (condition-variable-specific cv)
;=> waiting
```

**See also:** [`condition-variable-specific`](#condition-variable-specific)

---

### `condition-variable-signal!` { #condition-variable-signal }

**Syntax:** `(condition-variable-signal! condition-variable)`

Wakes one thread blocked on *condition-variable* (if any). If multiple
threads are waiting, exactly one is selected to be woken. Which thread
is chosen is implementation-dependent. If no threads are waiting, the
signal has no effect.

```scheme
kaappi> (define cv (make-condition-variable))
kaappi> (define m (make-mutex))
kaappi> ;; In a producer/consumer pattern:
kaappi> (condition-variable-signal! cv)
```

**See also:** [`condition-variable-broadcast!`](#condition-variable-broadcast),
[`mutex-unlock!`](#mutex-unlock)

---

### `condition-variable-broadcast!` { #condition-variable-broadcast }

**Syntax:** `(condition-variable-broadcast! condition-variable)`

Wakes all threads blocked on *condition-variable*. If no threads are
waiting, the broadcast has no effect.

```scheme
kaappi> (define cv (make-condition-variable))
kaappi> (condition-variable-broadcast! cv)
```

**See also:** [`condition-variable-signal!`](#condition-variable-signal),
[`mutex-unlock!`](#mutex-unlock)

---

## Time

### `current-time` { #current-time }

**Syntax:** `(current-time)`

Returns the current time as a time object. This is used with
`time->seconds` and `seconds->time` for computing timeouts in threading
operations.

```scheme
kaappi> (current-time)
;=> #<time>
kaappi> (time->seconds (current-time))
;=> 1719000000.123
```

**See also:** [`time?`](#time-pred), [`time->seconds`](#time-to-seconds),
[`seconds->time`](#seconds-to-time)

---

### `time?` { #time-pred }

**Syntax:** `(time? obj)`

Returns `#t` if *obj* is a time object, `#f` otherwise.

```scheme
kaappi> (time? (current-time))
;=> #t
kaappi> (time? 42)
;=> #f
```

**See also:** [`current-time`](#current-time)

---

### `time->seconds` { #time-to-seconds }

**Syntax:** `(time->seconds time)`

Converts a time object to an inexact real number representing seconds
since the epoch.

```scheme
kaappi> (time->seconds (current-time))
;=> 1719000000.123
```

**See also:** [`seconds->time`](#seconds-to-time),
[`current-time`](#current-time)

---

### `seconds->time` { #seconds-to-time }

**Syntax:** `(seconds->time seconds)`

Converts an inexact real number representing seconds since the epoch
to a time object. Useful for constructing absolute timeouts for
`thread-sleep!`, `mutex-lock!`, and `thread-join!`.

```scheme
kaappi> (define later (seconds->time (+ (time->seconds (current-time)) 5)))
kaappi> (time? later)
;=> #t
```

**See also:** [`time->seconds`](#time-to-seconds),
[`thread-sleep!`](#thread-sleep)

---

## Exception Predicates

### `join-timeout-exception?` { #join-timeout-exception }

**Syntax:** `(join-timeout-exception? obj)`

Returns `#t` if *obj* is a join-timeout exception, which is raised by
`thread-join!` when the timeout expires before the thread terminates.

```scheme
kaappi> (define t (make-thread (lambda () (thread-sleep! 100))))
kaappi> (thread-start! t)
;=> #<thread>
kaappi> (guard (e ((join-timeout-exception? e) 'timed-out))
         (thread-join! t (seconds->time (+ (time->seconds (current-time)) 0.1))))
;=> timed-out
```

**See also:** [`thread-join!`](#thread-join)

---

### `abandoned-mutex-exception?` { #abandoned-mutex-exception }

**Syntax:** `(abandoned-mutex-exception? obj)`

Returns `#t` if *obj* is an abandoned-mutex exception, which is raised
when attempting to lock a mutex that was left locked by a thread that
has since been terminated.

```scheme
kaappi> (abandoned-mutex-exception? 'foo)
;=> #f
```

**See also:** [`mutex-lock!`](#mutex-lock),
[`thread-terminate!`](#thread-terminate)

---

### `terminated-thread-exception?` { #terminated-thread-exception }

**Syntax:** `(terminated-thread-exception? obj)`

Returns `#t` if *obj* is a terminated-thread exception, which is raised
by `thread-join!` when the joined thread was terminated with
`thread-terminate!`.

```scheme
kaappi> (terminated-thread-exception? 'foo)
;=> #f
```

**See also:** [`thread-join!`](#thread-join),
[`thread-terminate!`](#thread-terminate)

---

### `uncaught-exception?` { #uncaught-exception }

**Syntax:** `(uncaught-exception? obj)`

Returns `#t` if *obj* is an uncaught-exception object, which wraps the
original exception raised by a thread that terminated abnormally. Use
`uncaught-exception-reason` to extract the original exception.

```scheme
kaappi> (define t (make-thread (lambda () (error "oops"))))
kaappi> (thread-start! t)
;=> #<thread>
kaappi> (guard (e ((uncaught-exception? e)
                   (error-object-message (uncaught-exception-reason e))))
         (thread-join! t))
;=> "oops"
```

**See also:** [`uncaught-exception-reason`](#uncaught-exception-reason),
[`thread-join!`](#thread-join)

---

### `uncaught-exception-reason` { #uncaught-exception-reason }

**Syntax:** `(uncaught-exception-reason exception)`

Returns the original exception object that caused the thread to terminate
abnormally. The *exception* must be an uncaught-exception object (as
tested by `uncaught-exception?`).

```scheme
kaappi> (define t (make-thread (lambda () (error "something broke" 42))))
kaappi> (thread-start! t)
;=> #<thread>
kaappi> (guard (e ((uncaught-exception? e)
                   (let ((reason (uncaught-exception-reason e)))
                     (list (error-object-message reason)
                           (error-object-irritants reason)))))
         (thread-join! t))
;=> ("something broke" (42))
```

**See also:** [`uncaught-exception?`](#uncaught-exception),
[`error-object-message`](./control-flow.md#error-object-message)

---
