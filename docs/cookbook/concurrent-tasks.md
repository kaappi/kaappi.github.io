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

Channels are synchronous (Go-style): `channel-send` blocks until a
receiver is ready, `channel-receive` blocks until a value arrives. That
makes a producer/consumer pipeline naturally self-pacing:

```scheme
(define ch (make-channel))

(spawn (lambda ()
  (for-each (lambda (x) (channel-send ch x)) '(1 2 3))
  (channel-send ch 'done)))

(let loop ((total 0))
  (let ((v (channel-receive ch)))
    (if (eq? v 'done)
        total
        (loop (+ total v)))))
;=> 6
```

The `'done` sentinel tells the consumer when to stop — synchronous
channels have no built-in close operation.

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
parallel. For CPU-bound work across cores, use
[SRFI-18 OS threads](../procedures/threads.md) — each thread gets its
own VM and heap, and values are deep-copied across thread boundaries.
The trade-offs are covered in the
[Concurrency guide](../guide/concurrency.md#choosing-a-model).

## Going further

- Fiber and channel API: [Kaappi Extensions reference](../procedures/extensions.md#spawn)
- Concurrency models compared: [Concurrency guide](../guide/concurrency.md)
- Multi-process serving for web apps: [Deployment](../guide/deployment.md#multi-process-serving)
