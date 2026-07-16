# Kaappi Extensions

Kaappi-specific features not part of R7RS or standard SRFIs.

---

## FFI (Foreign Function Interface)

### `ffi-open` { #ffi-open }
<!-- index: 1 | Open a shared library by path -->

**Syntax:** `(ffi-open path)`

Opens a shared library (`.so` on Linux, `.dylib` on macOS) and returns a
library handle. The *path* is a string specifying the library file.
The handle is used with `ffi-fn` to bind C functions and must be closed
with `ffi-close` when no longer needed.

```scheme
kaappi> (define lib (ffi-open "libm.so"))
kaappi> lib
;=> #<ffi-lib libm.so>
```

**See also:** [`ffi-fn`](#ffi-fn), [`ffi-close`](#ffi-close)

---

### `ffi-fn` { #ffi-fn }
<!-- index: 4 | Bind a C function: `(ffi-fn lib "name" '(param-types) 'return-type)` -->

**Syntax:** `(ffi-fn lib "c-name" '(param-types ...) 'return-type)`

Binds a C function from the shared library *lib* and returns a callable
Scheme procedure. The *c-name* is a string naming the C function.
Parameter and return types are specified as symbols: `int`, `long`,
`double`, `float`, `string`, `pointer`, `void`, `bool`, `uint8`, `int8`,
`int16`, `int32`, `int64`, `uint16`, `uint32`, `uint64`, `size_t`, `char`.

```scheme
kaappi> (define lib (ffi-open "libm.so"))
kaappi> (define c-sqrt (ffi-fn lib "sqrt" '(double) 'double))
kaappi> (c-sqrt 16.0)
;=> 4.0
kaappi> (define c-pow (ffi-fn lib "pow" '(double double) 'double))
kaappi> (c-pow 2.0 10.0)
;=> 1024.0
```

!!! note
    Type annotations must match the C function signature exactly.
    Passing a mismatched type causes undefined behavior.

**See also:** [`ffi-open`](#ffi-open), [`ffi-close`](#ffi-close)

---

### `ffi-close` { #ffi-close }
<!-- index: 1 | Close a shared library handle -->

**Syntax:** `(ffi-close lib)`

Closes the shared library handle *lib*, releasing the associated
resources. Any procedures previously bound with `ffi-fn` from this
library become invalid and must not be called after closing.

```scheme
kaappi> (define lib (ffi-open "libm.so"))
kaappi> (ffi-close lib)
```

**See also:** [`ffi-open`](#ffi-open), [`ffi-fn`](#ffi-fn)

---

### `fd->port` { #fd-to-port }
<!-- index: 1 | Wrap a raw file descriptor as a reactor-integrated binary port -->

**Syntax:** `(fd->port fd)`

Wraps *fd* — a raw OS file descriptor obtained through the FFI, such as
a socket — as a bidirectional binary port. Reads and writes on the port
go through the same non-blocking, reactor-integrated path as Kaappi's
file ports: an operation that would block suspends the calling fiber
instead of the OS thread, and the descriptor is switched to non-blocking
mode the first time it is touched under the fiber scheduler. Writes are
buffered; use `flush-output-port` to force them out.

The port **takes ownership** of the descriptor: `close-port` closes the
fd, wakes any fiber parked on it, and unregisters it from the reactor.
Don't also close the fd through your own FFI path — the number could be
recycled onto an unrelated port.

The standard streams (fd 0, 1, 2) are rejected, since their blocking
semantics are relied on elsewhere. Not available under `--sandbox`
(where the whole `(kaappi ffi)` library is blocked) or on WebAssembly.

This is the bridge that gives FFI socket libraries fiber-friendly I/O
with no C changes — kaappi-net wraps every connected socket exactly
like this:

```scheme
(define (socket-port fd) (fd->port fd))

(define conn (socket-port (c-accept listener)))  ; fd from an FFI call
(spawn (lambda ()
  (let ((request (read-bytevector 4096 conn)))   ; parks this fiber only
    (write-bytevector (handle request) conn)
    (flush-output-port conn)
    (close-port conn))))                         ; closes the fd too
```

**See also:** [`ffi-fn`](#ffi-fn), [`spawn`](#spawn),
[`flush-output-port`](./ports-and-io.md#flush-output-port),
[Concurrency guide](../guide/concurrency.md#fiber-io-is-non-blocking)

---

## Green Threads (Fibers)

### `spawn` { #spawn }
<!-- index: 1 | Create and start a fiber running a thunk -->

**Syntax:** `(spawn thunk)`

Creates and immediately starts a new fiber that executes *thunk* (a
procedure of zero arguments). Fibers are cooperatively scheduled green
threads that run on the VM's event loop. Returns a fiber object that can
be passed to `fiber-join` to retrieve the result.

```scheme
kaappi> (define f (spawn (lambda () (* 6 7))))
kaappi> (fiber-join f)
;=> 42
kaappi> (define f2 (spawn (lambda ()
                            (display "fiber running\n")
                            'done)))
fiber running
kaappi> (fiber-join f2)
;=> done
```

**See also:** [`fiber-join`](#fiber-join), [`yield`](#yield),
[`thread-start!`](./threads.md#thread-start) (OS thread equivalent)

---

### `yield` { #yield }
<!-- index: 0 | Yield to the fiber scheduler -->

**Syntax:** `(yield)`

Voluntarily gives up the current fiber's time slice, allowing the
scheduler to run other ready fibers. Returns an unspecified value.
Since fibers are cooperatively scheduled, long-running computations
should call `yield` periodically to avoid starving other fibers.

```scheme
kaappi> (spawn (lambda ()
         (let loop ((i 0))
           (when (< i 5)
             (display i) (display " ")
             (yield)
             (loop (+ i 1))))))
;=> #<fiber>
kaappi> 0 1 2 3 4
```

**See also:** [`spawn`](#spawn),
[`thread-yield!`](./threads.md#thread-yield) (OS thread equivalent)

---

### `fiber?` { #fiber-pred }
<!-- index: 1 | True if argument is a fiber -->

**Syntax:** `(fiber? obj)`

Returns `#t` if *obj* is a fiber, `#f` otherwise.

```scheme
kaappi> (fiber? (spawn (lambda () 42)))
;=> #t
kaappi> (fiber? (current-thread))
;=> #f
kaappi> (fiber? 'not-a-fiber)
;=> #f
```

**See also:** [`spawn`](#spawn)

---

### `fiber-join` { #fiber-join }
<!-- index: 1 | Wait for fiber completion, return its result -->

**Syntax:** `(fiber-join fiber)`

Blocks until *fiber* completes and returns its result value. If the
fiber raised an exception, `fiber-join` re-raises it in the calling
context.

```scheme
kaappi> (define f (spawn (lambda () (+ 10 20))))
kaappi> (fiber-join f)
;=> 30
kaappi> (define f2 (spawn (lambda ()
                            (let loop ((i 0) (acc 0))
                              (if (= i 100)
                                  acc
                                  (begin (yield) (loop (+ i 1) (+ acc i))))))))
kaappi> (fiber-join f2)
;=> 4950
```

**See also:** [`spawn`](#spawn),
[`thread-join!`](./threads.md#thread-join) (OS thread equivalent)

---

## Channels

### `make-channel` { #make-channel }
<!-- index: 0+ | Create a channel, optionally bounded to a capacity -->

**Syntax:** `(make-channel)` | `(make-channel capacity)`

Creates a new channel for passing values between fibers — and, when
handed to an OS thread through its `thread-start!` thunk, between
threads (see the [Concurrency
guide](../guide/concurrency.md#os-threads-srfi-18)). Values are
delivered first-in, first-out, without shared mutable state.

With no argument the channel is unbounded: `channel-send` queues the
value and returns immediately. With *capacity* (a non-negative exact
integer), at most *capacity* values may be queued: a send on a full
channel blocks until a receive frees a slot, so a bounded channel
applies backpressure to a producer that outpaces its consumer. A
*capacity* of `0` creates a channel that is permanently full — every
send blocks (or times out).

```scheme
kaappi> (define ch (make-channel))    ; unbounded
kaappi> (define bd (make-channel 8))  ; at most 8 queued values
kaappi> ch
;=> #<channel>
```

**See also:** [`channel-send`](#channel-send),
[`channel-receive`](#channel-receive), [`channel-close!`](#channel-close),
[`channel?`](#channel-pred)

---

### `channel-send` { #channel-send }
<!-- index: 2+ | Send a value: `(channel-send ch value [timeout [timeout-val]])` -->

**Syntax:** `(channel-send channel value)` | `(channel-send channel value timeout)` | `(channel-send channel value timeout timeout-val)`

Sends *value* on *channel*. On an unbounded channel (the default) the
value is queued and the send returns immediately; on a bounded channel a
send blocks while the channel is full, resuming when a receive frees a
slot. Returns an unspecified value.

If *timeout* is given (a time object or number of seconds) and the send
cannot complete within that time, returns *timeout-val* if supplied, or
raises an error otherwise.

Sending on a closed channel raises an error, as does sending an
eof-object — at the receiving end it would be indistinguishable from the
end-of-stream marker `channel-close!` produces. A send that can never
complete raises a deadlock error instead of hanging.

```scheme
kaappi> (define ch (make-channel))
kaappi> (channel-send ch 42)            ; unbounded: returns immediately
kaappi> (channel-receive ch)
;=> 42
kaappi> (define bd (make-channel 1))
kaappi> (channel-send bd 'a)
kaappi> (channel-send bd 'b 0.1 'full)  ; full for 100 ms -> timeout value
;=> full
```

**See also:** [`channel-receive`](#channel-receive),
[`channel-close!`](#channel-close), [`make-channel`](#make-channel)

---

### `channel-receive` { #channel-receive }
<!-- index: 1+ | Receive a value: `(channel-receive ch [timeout [timeout-val]])` -->

**Syntax:** `(channel-receive channel)` | `(channel-receive channel timeout)` | `(channel-receive channel timeout timeout-val)`

Receives the oldest queued value from *channel*. If the channel is
empty, the receiving fiber blocks until a sender provides a value. If
the channel has been closed and all queued values have been received,
returns an eof-object.

If *timeout* is given (a time object or number of seconds) and no value
arrives within that time, returns *timeout-val* if supplied, or raises
an error otherwise. A receive that can never be satisfied raises a
deadlock error instead of hanging.

```scheme
kaappi> (define ch (make-channel))
kaappi> (spawn (lambda ()
         (channel-send ch 'hello)
         (channel-send ch 'world)))
;=> #<fiber>
kaappi> (channel-receive ch)
;=> hello
kaappi> (channel-receive ch)
;=> world
kaappi> (channel-receive ch 0.1 'nothing)  ; empty for 100 ms -> timeout value
;=> nothing
```

**See also:** [`channel-send`](#channel-send),
[`channel-close!`](#channel-close), [`make-channel`](#make-channel)

---

### `channel-close!` { #channel-close }
<!-- index: 1 | Close a channel, signalling end-of-stream to receivers -->

**Syntax:** `(channel-close! channel)`

Closes *channel*, signalling end-of-stream: subsequent sends raise an
error, values already queued are still delivered, and once the channel
is drained every `channel-receive` returns an eof-object. Receivers
already blocked on an empty channel are woken and get the eof-object
immediately. Closing an already-closed channel has no effect. Returns
an unspecified value.

Closing replaces ad-hoc sentinel values as the way a producer tells
consumers no more data is coming:

```scheme
kaappi> (define ch (make-channel))
kaappi> (spawn (lambda ()
         (for-each (lambda (x) (channel-send ch x)) '(1 2 3))
         (channel-close! ch)))
;=> #<fiber>
kaappi> (let loop ((total 0))
         (let ((v (channel-receive ch)))
           (if (eof-object? v) total (loop (+ total v)))))
;=> 6
```

**See also:** [`channel-closed?`](#channel-closed),
[`channel-send`](#channel-send), [`channel-receive`](#channel-receive)

---

### `channel-closed?` { #channel-closed }
<!-- index: 1 | True if a channel has been closed -->

**Syntax:** `(channel-closed? channel)`

Returns `#t` if *channel* has been closed with `channel-close!`, `#f`
otherwise. A closed channel may still hold queued values —
`channel-closed?` answering `#t` does not mean the stream has been fully
consumed; only a `channel-receive` returning an eof-object does.

```scheme
kaappi> (define ch (make-channel))
kaappi> (channel-closed? ch)
;=> #f
kaappi> (channel-send ch 1)
kaappi> (channel-close! ch)
kaappi> (channel-closed? ch)
;=> #t
kaappi> (channel-receive ch)   ; queued value still delivered
;=> 1
kaappi> (eof-object? (channel-receive ch))
;=> #t
```

**See also:** [`channel-close!`](#channel-close), [`channel?`](#channel-pred)

---

### `channel?` { #channel-pred }
<!-- index: 1 | True if argument is a channel -->

**Syntax:** `(channel? obj)`

Returns `#t` if *obj* is a channel, `#f` otherwise.

```scheme
kaappi> (channel? (make-channel))
;=> #t
kaappi> (channel? (make-mutex))
;=> #f
kaappi> (channel? 'not-a-channel)
;=> #f
```

**See also:** [`make-channel`](#make-channel)

---

## Parallel Pools

`(kaappi parallel)` — worker pools and parallel map/for-each over
`(srfi 18)` threads (fiber workers under `--sandbox` and WASM, where real
threads are unavailable). See the [Concurrency
guide](../guide/concurrency.md#multi-core-parallelism-with-kaappi-parallel)
for a walkthrough and the cross-thread-copy semantics shared with raw
`thread-start!`/`thread-join!`.

### `make-pool` { #make-pool }
<!-- index: 1 | Create a fixed-size pool of workers draining a shared task queue -->

**Syntax:** `(make-pool n)`

Creates a pool of *n* workers (a positive exact integer), each pulling
tasks from a shared queue until the pool is shut down. Workers are real
OS threads when available, or fiber workers on the calling thread's
scheduler under `--sandbox` and in the WebAssembly build.

```scheme
kaappi> (import (kaappi parallel))
kaappi> (define pool (make-pool 4))
kaappi> (pool-shutdown! pool)
```

**See also:** [`pool-submit`](#pool-submit), [`pool-shutdown!`](#pool-shutdown),
[`processor-count`](#processor-count)

---

### `pool-submit` { #pool-submit }
<!-- index: 2 | Submit a thunk to a pool, returning a reply channel -->

**Syntax:** `(pool-submit pool thunk)`

Submits *thunk* (a procedure of zero arguments) to *pool* and returns a
reply channel immediately — it does not wait for the task to run. Pass the
reply channel to `task-wait` to block for the result. Raises if *pool* has
already been shut down. Like `thread-start!`, *thunk* and its eventual
result cross to and from the worker **by copy**.

```scheme
kaappi> (import (kaappi parallel))
kaappi> (define pool (make-pool 2))
kaappi> (define reply (pool-submit pool (lambda () (* 6 7))))
kaappi> (task-wait reply)
;=> 42
kaappi> (pool-shutdown! pool)
```

**See also:** [`task-wait`](#task-wait), [`make-pool`](#make-pool)

---

### `task-wait` { #task-wait }
<!-- index: 1 | Block for a submitted task's result, re-raising its exception -->

**Syntax:** `(task-wait reply)`

Blocks on the reply channel returned by `pool-submit` until the
corresponding task completes, then returns its result. If the task's
thunk raised an exception, `task-wait` re-raises it in the calling
context — the same contract as `fiber-join`/`thread-join!`.

```scheme
kaappi> (import (kaappi parallel))
kaappi> (define pool (make-pool 2))
kaappi> (define reply (pool-submit pool (lambda () (error "boom"))))
kaappi> (guard (e (#t (display "task failed\n"))) (task-wait reply))
task failed
kaappi> (pool-shutdown! pool)
```

**See also:** [`pool-submit`](#pool-submit)

---

### `pool-shutdown!` { #pool-shutdown }
<!-- index: 1 | Drain a pool's queued tasks and join every worker -->

**Syntax:** `(pool-shutdown! pool)`

Closes *pool*'s task queue and waits for every worker to finish. Tasks
already submitted (including one racing this call) all run to
completion; `pool-submit` after shutdown raises.

```scheme
kaappi> (import (kaappi parallel))
kaappi> (define pool (make-pool 2))
kaappi> (pool-shutdown! pool)
kaappi> (pool-submit pool (lambda () 1))
;=> error: send on closed channel
```

**See also:** [`make-pool`](#make-pool), [`pool-submit`](#pool-submit)

---

### `parallel-map` { #parallel-map }
<!-- index: 2 | Apply a procedure to a list in parallel, preserving order -->

**Syntax:** `(parallel-map proc list)`

Applies *proc* to each element of *list*, one task per element, using a
private pool sized `(processor-count)` that's torn down before returning.
Results are returned in the original list order regardless of completion
order. An exception from any element propagates out of `parallel-map`.

```scheme
kaappi> (import (kaappi parallel))
kaappi> (parallel-map (lambda (n) (* n n)) '(1 2 3 4 5))
;=> (1 4 9 16 25)
```

**See also:** [`parallel-for-each`](#parallel-for-each), [`make-pool`](#make-pool)

---

### `parallel-for-each` { #parallel-for-each }
<!-- index: 2 | Apply a procedure to a list in parallel for side effects -->

**Syntax:** `(parallel-for-each proc list)`

Like `parallel-map`, but for side effects: applies *proc* to each element
of *list* using a private pool, waits for every call to finish, and
returns an unspecified value. Since each call runs on a worker with its
own heap, communicate side effects back through a channel rather than a
shared variable.

```scheme
kaappi> (import (kaappi parallel))
kaappi> (define out (make-channel))
kaappi> (parallel-for-each (lambda (n) (channel-send out (* n n))) '(1 2 3))
kaappi> (list (channel-receive out) (channel-receive out) (channel-receive out))
;=> (1 4 9)  ; order depends on scheduling
```

**See also:** [`parallel-map`](#parallel-map)

---

!!! note "Cheap per-element work: chunk manually instead"
    `parallel-map`/`parallel-for-each` submit one task per list element, so
    every element pays a `pool-submit`/`task-wait` round trip plus the copy
    across the worker boundary. That is the right shape when each call does
    real work; for very cheap per-element operations the bookkeeping
    dominates the computation. For those, use
    `make-pool`/`pool-submit`/`task-wait` directly with one task per
    processor, each covering a slice of the input with an ordinary
    sequential loop — see the [Parallel Prime
    Search](https://github.com/kaappi/kaappi-examples/tree/main/parallel-primes)
    example.

### `processor-count` { #processor-count }
<!-- index: 0 | Number of available processors -->

**Syntax:** `(processor-count)`

Returns the number of logical processors available, or `1` under
`--sandbox` or in the WebAssembly build — matching the worker count a pool
degrades to in those environments.

```scheme
kaappi> (processor-count)
;=> 8
```

**See also:** [`make-pool`](#make-pool)

---

## Diagnostics

`(kaappi diagnostics)` — programmatic access to the stable `KP` codes
that Kaappi stamps on the errors it raises. Every code is documented in
the [Diagnostic Reference](../guide/diagnostics.md); codes never change
meaning between releases, so they are safe to dispatch on where message
text is not.

### `error-object-code` { #error-object-code }
<!-- index: 1 | Stable KP diagnostic code of an error object as a symbol, or `#f` -->

**Syntax:** `(error-object-code obj)`

Returns the stable diagnostic code stamped on *obj* as an interned
symbol (for example `KP3004` for a division-by-zero error), or `#f` if
there is none. Because the symbol is interned, codes compare with `eq?`.

Unlike `error-object-message` and `error-object-irritants`, this is a
total accessor that never raises: it returns `#f` both for values that
are not error objects and for error objects carrying no code — such as
those from `error`, since the `KP` namespace is reserved to the
implementation. That makes it safe as the first dispatch check inside a
`guard`, where `raise` may have delivered any value at all.

```scheme
kaappi> (import (kaappi diagnostics))
kaappi> (guard (e (#t (error-object-code e))) (/ 1 0))
;=> KP3004
kaappi> (guard (e (#t (error-object-code e))) (error "boom"))
;=> #f
kaappi> (error-object-code 42)
;=> #f
kaappi> (define (safe-div a b)
         (guard (e ((eq? (error-object-code e) 'KP3004) 'undefined))
           (/ a b)))
kaappi> (safe-div 1 0)
;=> undefined
```

**See also:** [`error-object-message`](./control-flow.md#error-object-message),
[`error-object-irritants`](./control-flow.md#error-object-irritants),
[Diagnostic Reference](../guide/diagnostics.md)

---
