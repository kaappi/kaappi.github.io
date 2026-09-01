# Run External Programs

Shelling out is how a Scheme program uses the rest of the machine: `git`,
`ffmpeg`, `pandoc`, a compiler, a deploy script. Kaappi's
[`(kaappi process)`](../procedures/processes.md) library does it without a
shell and without blocking the rest of your program.

No installation is needed — the library is built in. It is absent only in
the WebAssembly build and under `--sandbox`; see
[Running External Programs](../guide/subprocesses.md#where-the-library-is-not-available)
for the portability gate.

## Run a program and read its output

`run-process` returns three values: exit status, stdout, stderr.

```scheme
(import (scheme base) (scheme write) (kaappi process))

(call-with-values (lambda () (run-process '("echo" "hello"))) list)
;=> (0 "hello\n" "")
```

The command is a **list of strings**, never a command line. Arguments reach
the program exactly as written, so a filename with a space or a semicolon
in it is still one argument.

## Turn a failure into an error

A non-zero exit is a value, not an exception — which is right, because
plenty of programs use exit codes to answer questions. Most call sites want
"give me the output or blow up", so write that helper once:

```scheme
(define (run! argv . opts)
  (call-with-values (lambda () (apply run-process argv opts))
    (lambda (status out err)
      (if (= status 0)
          out
          (error "command failed" argv status err)))))

(run! '("echo" "ok"))
;=> "ok\n"
```

Keep `run-process` itself for the cases where the code is the answer:

```scheme
(call-with-values (lambda () (run-process '("sh" "-c" "exit 2"))) list)
;=> (2 "" "")
```

A program that cannot be *started* — missing, or not executable — is a
different thing: that raises a file error, catchable with `file-error?`.

## Send data in

`'input:` writes to the child's stdin and closes it:

```scheme
(run! '("sort") 'input: "pear\napple\ncherry\n")
;=> "apple\ncherry\npear\n"
```

This is the case that is easy to get wrong by hand. Writing to a child and
then reading it back deadlocks the moment either pipe fills: you are
blocked writing, and the child is blocked writing to a stdout nobody is
draining. `run-process` feeds and drains all three streams at once, using
fibers inside the call, so the size of the data never matters.

## Keep stderr separate

```scheme
(call-with-values
    (lambda () (run-process '("sh" "-c" "printf out; printf boom 1>&2; exit 1")))
  list)
;=> (1 "out" "boom")
```

Diagnostics stay out of the data. If you would rather have them
interleaved, use `spawn-process` with `'stderr: 'stdout`.

## Give up on a slow program

```scheme
(guard (e ((process-timeout? e)
           (list 'timed-out (process-timeout-stdout e))))
  (run-process '("sh" "-c" "printf half; sleep 30") 'timeout: 0.5))
;=> (timed-out "half")
```

The child and everything it started are killed, and whatever it wrote
before the deadline is carried on the condition — the normal three-value
return never happens, so that is the only place it can go.

## Set the environment and working directory

`'env:` **replaces** the environment, so build on `(process-environment)`
when you mean "the same, plus one":

```scheme
(run! '("printenv" "GREETING")
      'env: (cons (cons "GREETING" "hello") (process-environment)))
;=> "hello\n"
```

```scheme
(run! '("pwd") 'directory: "/")
;=> "/\n"
```

## Run several programs at once

Each `run-process` parks its fiber while it waits, so a fiber per program
runs the whole batch concurrently on one thread:

```scheme
(import (kaappi fibers))

(define (probe argv)
  (spawn (lambda ()
           (call-with-values (lambda () (run-process argv))
             (lambda (status out err) (cons status out))))))

(map fiber-join (map probe '(("echo" "a") ("echo" "b") ("echo" "c"))))
;=> ((0 . "a\n") (0 . "b\n") (0 . "c\n"))
```

Three programs, one thread, no OS threads involved. Swap `echo` for
anything slow and the batch takes about as long as its slowest member
rather than the sum.

## Talk to a long-lived program

When you exchange messages with a program over time rather than running it
once, `spawn-process` hands you the pipes and gets out of the way. Give the
reading side its own fiber:

```scheme
(define p (spawn-process '("sort") 'stdin: 'pipe 'stdout: 'pipe))

(define reader
  (spawn (lambda ()
           (let loop ((acc '()))
             (let ((line (read-line (process-stdout p))))
               (if (eof-object? line)
                   (reverse acc)
                   (loop (cons line acc))))))))

(write-string "pear\napple\n" (process-stdin p))
(close-port (process-stdin p))          ; sort emits nothing until EOF
(fiber-join reader)
;=> ("apple" "pear")
```

```scheme
(process-wait p)
;=> 0
```

The pipes are ordinary ports: `read-line`, `read-u8`, `write-string` and
the rest all work, and a read that would block parks only that fiber.

## Stop a program and everything it started

Spawn it in its own process group, and the kill reaches its children too:

```scheme
(define w (spawn-process '("sh" "-c" "sleep 30 & sleep 30") 'new-group: #t))
(process-kill w 'group: #t)
(process-wait w)
;=> (signaled . 15)
```

Without `'new-group: #t` there is no group to signal but Kaappi's own, and
`process-kill` refuses rather than signalling your own program. A plain
`(process-kill w)` still terminates the child itself.

On Windows the group is a Job Object and the status is an integer — there
are no signals to report. See
[`process-kill`](../procedures/processes.md#process-kill).

## Safety

The list-of-strings command is the whole defense against injection, and it
is enough as long as you never assemble a shell string yourself:

```scheme
(run! (list "git" "checkout" branch))          ; safe for any branch name
(run! (list "sh" "-c" (string-append "git checkout " branch)))  ; NOT safe
```

Two more things worth knowing:

- The child inherits only stdin, stdout and stderr. Every other descriptor
  Kaappi holds — database connections, listening sockets, the reactor's own
  kernel objects — is closed before the program starts.
- `--sandbox` excludes the library entirely, so a sandboxed script cannot
  escape through a subprocess.

## Next steps

- [Running External Programs](../guide/subprocesses.md) — the guide
- [Subprocess procedures](../procedures/processes.md) — the full reference
- [Run Concurrent Tasks](./concurrent-tasks.md) — fibers and channels
