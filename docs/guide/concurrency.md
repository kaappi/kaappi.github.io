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
