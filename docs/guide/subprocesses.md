# Running External Programs

Kaappi can start other programs, talk to them over pipes, and wait for them
to finish — without blocking anything else your program is doing. The
library is `(kaappi process)`.

!!! note "Availability"
    `(kaappi process)` arrived after v0.25.0. On an older binary the
    `(library (kaappi process))` gate below is simply false, and
    `kaappi features` reports what your build has.

```scheme
(import (scheme base) (kaappi process))

(call-with-values
    (lambda () (run-process '("git" "rev-parse" "HEAD")))
  (lambda (status commit err)
    (if (= status 0)
        (display commit)
        (display err (current-error-port)))))
```

Two entry points, and most programs only need the first:

- **[`run-process`](../procedures/processes.md#run-process)** runs a program
  to completion and hands you its exit status and its output.
- **[`spawn-process`](../procedures/processes.md#spawn-process)** starts a
  program and returns immediately, so you can stream to and from it.

## The command is a list, not a command line

Every procedure here takes a **list of strings**. The first is the program,
the rest are its arguments, and they reach the program exactly as written.

```scheme
(run-process (list "rm" filename))
```

If `filename` is `"my file; rm -rf ~"`, that deletes a single oddly-named
file. Nothing is word-split, nothing is glob-expanded, and no shell is
involved — the string is one argument because you put it in one list
element.

You can still ask for a shell, but you have to say so, and then the quoting
is your problem:

```scheme
(run-process (list "sh" "-c" "ls *.scm | wc -l"))
```

Prefer the list form. Reach for `sh -c` only when you actually want shell
features like pipelines or globbing.

## Capturing output

`run-process` returns three values: the exit status, standard output, and
standard error.

```scheme
kaappi> (call-with-values (lambda () (run-process '("echo" "hello"))) list)
;=> (0 "hello\n" "")
```

A non-zero exit code is a value, not an error — programs signal failure
that way routinely, and it is up to you what to do about it:

```scheme
(define (git . args)
  (call-with-values (lambda () (run-process (cons "git" args)))
    (lambda (status out err)
      (if (= status 0)
          out
          (error "git failed" args status err)))))
```

On POSIX a child killed by a signal reports the pair `(signaled . n)`
instead of an integer. Windows has no signal delivery, so a status there is
always an integer.

Failing to *start* the program is different from the program failing. A
missing or non-executable file raises a file error, catchable with
`file-error?`:

```scheme
(guard (e ((file-error? e) (display "no such program\n")))
  (run-process '("definitely-not-installed")))
```

## Feeding input

`'input:` writes a string (or a bytevector) to the child's stdin and then
closes it:

```scheme
kaappi> (call-with-values
          (lambda () (run-process '("sort") 'input: "pear\napple\n"))
          list)
;=> (0 "apple\npear\n" "")
```

Without `'input:`, the child's stdin is empty rather than inherited — a
program that reads stdin sees end-of-file immediately instead of blocking
on your terminal.

**This is the part that is hard to get right by hand.** Writing to a child's
stdin and then reading its stdout deadlocks as soon as either side fills a
pipe buffer: you are blocked writing, the child is blocked writing to a
stdout nobody is reading, and neither of you will move again. Reading
stdout to end-of-file before touching stderr has the same failure. Other
languages solve this with a thread per stream; `run-process` does it with
fibers, inside the call, so it simply does not happen:

```scheme
;; child reads 1 MB, writes 1 MB to stdout and 1 MB to stderr — no deadlock
(run-process '("sh" "-c" "cat >/dev/null; yes o | head -c 1000000; yes e | head -c 1000000 1>&2")
             'input: (make-string 1000000 #\i))
```

If you build your own loop with `spawn-process`, this hazard is yours to
handle — read each pipe in its own fiber.

## Binary output

`run-process` decodes output as UTF-8 by default. For a program that emits
something else, ask for bytes:

```scheme
(call-with-values
    (lambda () (run-process '("gzip" "-c") 'input: "text" 'output: 'bytevector))
  (lambda (status out err) (bytevector-length out)))
```

## Timeouts

`'timeout:` bounds the whole call in seconds. If the program has not
finished by then it is killed, along with anything it started, and a
condition is raised carrying whatever it managed to write:

```scheme
(guard (e ((process-timeout? e)
           (display "gave up; it had said: ")
           (display (process-timeout-stdout e))
           (newline)))
  (run-process '("./slow-report") 'timeout: 30))
```

The kill is unconditional (`SIGKILL`), because a timeout is a bound and not
a request, and it goes to the whole process group so a child's own children
die with it. The partial output lives only on the condition — the normal
three-value return never happens.

## Environment and working directory

`'directory:` sets the child's working directory. `'env:` **replaces** its
environment rather than adding to it, so build on
`(process-environment)` when you mean "the same, plus one":

```scheme
(run-process '("make" "test")
             'directory: "/src/project"
             'env: (cons (cons "CI" "1") (process-environment)))
```

Replacing wholesale is occasionally what you want — a deliberately minimal
environment for an untrusted program — but dropping the platform's own
variables will stop many programs from starting at all, especially on
Windows.

## Streaming: a long-lived child

When the program is a server, a REPL, or anything you exchange messages
with over time, `spawn-process` gives you the pipes directly.

```scheme
(import (scheme base) (kaappi process) (kaappi fibers))

(define p (spawn-process '("sort") 'stdin: 'pipe 'stdout: 'pipe))

(spawn (lambda ()                       ; a fiber owns the reading side
         (let loop ()
           (let ((line (read-line (process-stdout p))))
             (unless (eof-object? line)
               (display line) (newline)
               (loop))))))

(write-string "pear\napple\ncherry\n" (process-stdin p))
(close-port (process-stdin p))          ; sort produces nothing until EOF
(process-wait p)
```

`process-stdin`, `process-stdout` and `process-stderr` are ordinary ports —
every port procedure works on them. A read or write that would block parks
only the calling fiber; the rest of your program keeps running. That is the
same behavior socket ports already have, and it is why
[`process-wait`](../procedures/processes.md#process-wait) can wait for a
five-minute child without freezing anything.

`'stderr: 'stdout` merges the two streams onto the stdout pipe when you do
not care which one a line came from. `'null` discards a stream entirely.

To stop a child, [`process-kill`](../procedures/processes.md#process-kill)
sends `SIGTERM` by default; `'group: #t` reaches its descendants, which
requires having spawned it with `'new-group: #t`.

```scheme
(define p (spawn-process '("./watcher") 'new-group: #t))
...
(process-kill p 'group: #t)
(process-wait p)
```

## Where the library is not available

`(kaappi process)` is absent in two places:

- **The WebAssembly build**, including the browser playground and tour.
  WASI has no process model at all.
- **`--sandbox` mode**, which excludes it deliberately along with the
  filesystem, `(kaappi ffi)` and OS threads.

Portable code checks for the library rather than for a platform:

```scheme
(cond-expand
  ((library (kaappi process))
   (import (kaappi process))
   (define (version-of prog)
     (call-with-values (lambda () (run-process (list prog "--version")))
       (lambda (status out err) (and (= status 0) out)))))
  (else
   (define (version-of prog) #f)))
```

There is no `kaappi-process` feature identifier — the `(library ...)`
requirement above is the check, and it answers correctly under `--sandbox`
as well. See [Conformance](../conformance.md#detecting-subsystems-from-code).

## Safety notes

- **Never build a command line by string concatenation.** The list form
  exists so that a filename, a branch name, or a user-supplied search term
  cannot become an argument you did not intend — or a second command.
- **The child inherits only stdin, stdout and stderr.** Every other file,
  socket and pipe Kaappi holds is closed before the program starts, so a
  child cannot reach your database connection or your listening socket.
- **A process object belongs to the thread that spawned it.** Using one
  from another SRFI-18 thread raises; pass results over a channel instead.
- **`--sandbox` blocks the whole library**, so a sandboxed script cannot
  escape through a subprocess. See [Security](./security.md).

## See also

- [Subprocess procedures](../procedures/processes.md) — the full reference
- [Run External Programs](../cookbook/external-programs.md) — a worked recipe
- [Concurrency](./concurrency.md) — fibers, channels, and how parking works
