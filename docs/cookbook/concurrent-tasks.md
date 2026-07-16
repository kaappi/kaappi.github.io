# Run Concurrent Tasks

This recipe covers structuring concurrent work with Kaappi's built-in
green threads (fibers): fan-out/fan-in, pipelines, and worker pools.
Fibers need no installation — `(kaappi fibers)` ships with Kaappi — and
they work everywhere, including `--sandbox` mode and the browser
playground.

For choosing between fibers and OS threads, see the
[Concurrency guide](../guide/concurrency.md).

## Spawn and join

`spawn` starts a fiber immediately and returns a handle; `fiber-join`
waits for it and returns its result. If the fiber raised an error,
`fiber-join` re-raises it:

```scheme
(import (scheme base) (kaappi fibers))

(define f (spawn (lambda () (* 6 7))))
(fiber-join f)   ;=> 42
```

## Fan out, fan in

Split independent work across fibers, then collect all results in
order:

```scheme
(define (parallel-map f items)
  (map fiber-join
       (map (lambda (item)
              (spawn (lambda () (f item))))
            items)))

(parallel-map (lambda (n) (* n n)) '(1 2 3 4 5))
;=> (1 4 9 16 25)
```

Fibers are cooperative: long-running computations should call `(yield)`
periodically so other fibers get a turn:

```scheme
(define (sum-range lo hi)
  (let loop ((i lo) (acc 0))
    (if (= i hi)
        acc
        (begin
          (when (zero? (modulo i 1000)) (yield))
          (loop (+ i 1) (+ acc i))))))
```

## Pipeline with a channel

A channel is a FIFO queue: `channel-receive` blocks until a value
arrives, so a consumer naturally waits for its producer. Closing the
channel signals end-of-stream — once the queue drains, every receive
returns an eof-object:

```scheme
(define ch (make-channel))

(spawn (lambda ()
  (for-each (lambda (x) (channel-send ch x)) '(1 2 3))
  (channel-close! ch)))

(let loop ((total 0))
  (let ((v (channel-receive ch)))
    (if (eof-object? v)
        total
        (loop (+ total v)))))
;=> 6
```

`channel-send` on a default (unbounded) channel never blocks. To make a
fast producer pace itself to a slow consumer, give the channel a
capacity — `(make-channel 8)` — and sends block whenever 8 values are
already queued.

## Worker pool

Bound concurrency with a fixed number of workers pulling jobs from a
shared channel. Each worker accumulates its results locally and returns
them at `fiber-join`, which avoids result-channel deadlocks:

```scheme
(define (worker jobs process)
  (let loop ((acc '()))
    (let ((job (channel-receive jobs)))
      (if (eq? job 'done)
          (reverse acc)
          (loop (cons (process job) acc))))))

(define (pool-map process items n-workers)
  (let* ((jobs (make-channel))
         (workers
           (let loop ((i 0) (ws '()))
             (if (= i n-workers)
                 ws
                 (loop (+ i 1)
                       (cons (spawn (lambda () (worker jobs process)))
                             ws))))))
    ;; hand out the jobs, then one 'done per worker
    (for-each (lambda (item) (channel-send jobs item)) items)
    (let loop ((i 0))
      (when (< i n-workers)
        (channel-send jobs 'done)
        (loop (+ i 1))))
    ;; gather everything
    (apply append (map fiber-join workers))))

(pool-map (lambda (n) (* n 10)) '(1 2 3 4 5 6 7 8) 3)
;=> results from all workers (order depends on scheduling)
```

## CPU-bound work with a real thread pool

The worker pool above runs every worker on the same OS thread — fine for
I/O-bound work, but CPU-bound computation never actually runs in parallel
that way. `(kaappi parallel)` gives you the same pool shape backed by real
OS threads, with the chunking and shutdown bookkeeping already handled:

```scheme
(import (scheme base) (scheme write) (kaappi parallel))

(parallel-map (lambda (n) (* n n)) '(1 2 3 4 5))
;=> (1 4 9 16 25)
```

For repeated submissions, keep a pool around rather than paying setup cost
per call — `pool-submit` returns a channel immediately, and `task-wait`
blocks for the result (re-raising the task's exception, same contract as
`fiber-join`):

```scheme
(define pool (make-pool (processor-count)))

(define replies (map (lambda (item) (pool-submit pool (lambda () (process item))))
                      items))
(define results (map task-wait replies))

(pool-shutdown! pool)
```

Every task thunk and result crosses the pool boundary **by copy**, the same
rule as `thread-start!`/`thread-join!` — workers don't share heap state with
the caller or each other. `make-pool` degrades to fiber workers (like the
hand-rolled pool above) under `--sandbox` and in the WebAssembly build,
where real threads aren't available, so code written against this API keeps
working unchanged in either environment.

Submitting one task per item (as above, or via `parallel-map`) is reliable
for up to a few hundred items; for larger inputs, chunk the work into one
task per processor instead — see the [Parallel Pools
reference](../procedures/extensions.md#parallel-pools) for why, and
`pool-submit`/`task-wait`/`pool-shutdown!`/`parallel-for-each`'s full API.

## Handle fiber errors

An exception inside a fiber surfaces at `fiber-join` — wrap the join,
not the spawn:

```scheme
(define f (spawn (lambda () (error "boom"))))

(guard (e (#t (display "fiber failed\n") #f))
  (fiber-join f))
;; prints: fiber failed
```

## When to reach for OS threads instead

Fibers run in one OS thread, so they interleave but never run in
parallel. For CPU-bound work across cores, reach for
`(kaappi parallel)`'s `parallel-map`/`make-pool` (above) rather than raw
[SRFI-18 OS threads](../procedures/threads.md) — it handles the
channel/task bookkeeping for you and degrades to fibers automatically
under `--sandbox` and WASM. Each worker still gets its own VM and heap,
and values are deep-copied across thread boundaries either way. The
trade-offs are covered in the
[Concurrency guide](../guide/concurrency.md#choosing-a-model).

## Going further

- Fiber and channel API: [Kaappi Extensions reference](../procedures/extensions.md#spawn)
- Parallel pool API: [Kaappi Extensions reference](../procedures/extensions.md#parallel-pools)
- Concurrency models compared: [Concurrency guide](../guide/concurrency.md)
- Multi-process serving for web apps: [Deployment](../guide/deployment.md#multi-process-serving)
