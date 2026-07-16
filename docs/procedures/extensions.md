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
<!-- index: 0 | Create a new channel -->

**Syntax:** `(make-channel)`

Creates a new synchronous channel for inter-fiber communication.
Channels are Go-style: a send blocks until a receiver is ready, and a
receive blocks until a value is available. This provides a safe way to
pass data between fibers without shared mutable state.

```scheme
kaappi> (define ch (make-channel))
kaappi> ch
;=> #<channel>
```

**See also:** [`channel-send`](#channel-send),
[`channel-receive`](#channel-receive), [`channel?`](#channel-pred)

---

### `channel-send` { #channel-send }
<!-- index: 2 | Send a value on a channel -->

**Syntax:** `(channel-send channel value)`

Sends *value* on *channel*. If no fiber is currently waiting to receive,
the sending fiber blocks until a receiver is ready. This ensures
synchronous hand-off of values between fibers.

```scheme
kaappi> (define ch (make-channel))
kaappi> (spawn (lambda () (channel-send ch 42)))
;=> #<fiber>
kaappi> (channel-receive ch)
;=> 42
```

**See also:** [`channel-receive`](#channel-receive),
[`make-channel`](#make-channel)

---

### `channel-receive` { #channel-receive }
<!-- index: 1 | Receive a value from a channel -->

**Syntax:** `(channel-receive channel)`

Receives a value from *channel*. If no value is currently available,
the receiving fiber blocks until a sender provides one. Returns the
sent value.

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
```

**See also:** [`channel-send`](#channel-send),
[`make-channel`](#make-channel)

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
