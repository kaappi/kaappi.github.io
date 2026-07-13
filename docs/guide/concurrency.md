# Concurrency

Kaappi offers two concurrency models: green threads (fibers) for cooperative
multitasking and OS threads (SRFI-18) for true parallelism.

## Green threads (fibers)

Fibers run cooperatively within a single OS thread. They are lightweight
and communicate via channels:

```scheme
(import (kaappi fibers))

(define ch (make-channel))

(spawn (lambda ()
  (channel-send ch "hello from fiber")))

(display (channel-receive ch))  ;=> hello from fiber
```

Use fibers for concurrent I/O, event loops, and cooperative task
scheduling. See the [Fibers reference](../procedures/extensions.md#spawn)
for the full API.

### Fiber I/O is non-blocking

A blocking-looking call like `(read-line port)` only suspends the fiber
that made it. Under the hood, Kaappi runs a per-OS-thread **I/O
reactor**: if the read would block, the fiber parks and the reactor
waits on the underlying file descriptors (via kqueue on macOS/BSD, epoll
on Linux, or `poll_oneoff` under WASI), waking whichever fiber becomes
ready. `thread-sleep!` gets the same treatment — it parks the calling
fiber on the reactor's timer heap instead of blocking the whole thread,
so sleeping fibers and I/O-bound fibers interleave freely:

```scheme
(import (kaappi fibers))

;; Each fiber's (read-line) yields to the scheduler on EAGAIN instead
;; of freezing every other fiber. Thousands of these coexist on one
;; OS thread and one GC heap.
(define (handle conn)
  (spawn (lambda ()
           (let loop ()
             (let ((line (read-line conn)))
               (unless (eof-object? line)
                 (channel-send out (process line))
                 (loop)))))))
```

This is what makes [`http-listen-fiber`](../ecosystem/http.md#server-modes)
practical: it accepts connections in a non-blocking loop and spawns one
fiber per connection, so a slow client trickling in its request never
delays a fast one on a different connection — all on a single OS
thread. Libraries built on `(kaappi net)`'s plain-TCP `tcp-recv`/`tcp-send`
(`kaappi-redis`, `kaappi-email`, `kaappi-http`'s client) work unchanged
under this model; only server accept loops need the explicit
non-blocking treatment `http-listen-fiber` provides.

## OS threads (SRFI-18)

Real OS threads via `pthread_create`. Each thread gets its own VM and GC
with an independent heap. No special flag is needed -- just run your
program:

```bash
kaappi program.scm
```

OS threads are unavailable in `--sandbox` mode and in the WebAssembly
build (including the browser playground); use fibers there.

```scheme
(import (srfi 18))

(define t (thread-start!
  (make-thread
    (lambda ()
      (* 6 7)))))

(thread-join! t)  ;=> 42
```

Both interpreted and native (compiled) procedures are accepted by
`make-thread` and `spawn`:

```scheme
(define (compute) (* 6 7))
(thread-join! (thread-start! (make-thread compute)))  ;=> 42
```

Values are **deep-copied** when crossing thread boundaries:

- At `thread-start!`: the thunk closure is deep-copied from parent to child
- At `thread-join!`: the result is deep-copied from child to parent

Threads cannot share mutable heap state directly -- use return values or
channels to communicate. See the [SRFI-18 reference](../procedures/threads.md)
for mutexes, condition variables, and the full threading API.

!!! note "Cross-thread channels"
    A channel handed to a thread through its thunk works across the thread
    boundary — sends and receives are deep-copied at each end, the same way
    values already are at `thread-start!`/`thread-join!`. This is newer than
    the rest of the threading API and still has open correctness issues in
    its wakeup path; see [Standards Conformance](../conformance.md#extensions-beyond-r7rs-smalls-scope)
    for current status before relying on it for production workloads.

## Choosing a model

| | Fibers | OS threads |
|---|--------|-----------|
| Parallelism | No (cooperative, single thread) | Yes (one VM per thread) |
| Shared state | Yes (same heap) | No (values deep-copied) |
| Works in `--sandbox` | Yes | No |
| Works in WASM / playground | Yes | No |
| Best for | Concurrent I/O, event loops | CPU-bound parallel work |

For multi-process serving in production (`serve-prefork`), see
[Deployment](deployment.md#multi-process-serving). For worked examples
of pipelines and worker pools, see the cookbook recipe
[Run Concurrent Tasks](../cookbook/concurrent-tasks.md).

---

Next: [REPL Guide](repl.md)
