# Kaappi Extensions

Kaappi-specific features not part of R7RS or standard SRFIs.

---

## FFI (Foreign Function Interface)

### `ffi-open` { #ffi-open }

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

**Syntax:** `(ffi-fn lib "c-name" '(param-types ...) 'return-type)`

Binds a C function from the shared library *lib* and returns a callable
Scheme procedure. The *c-name* is a string naming the C function.
Parameter and return types are specified as symbols: `uint8`, `uint16`,
`uint32`, `uint64`, `int8`, `int16`, `int32`, `int64`, `float`, `double`,
`pointer`, `void`, `bool`.

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
