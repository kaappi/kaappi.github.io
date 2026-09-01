# Subprocesses

Spawning and controlling external programs. Import with
`(import (kaappi process))`.

!!! note
    `(kaappi process)` is absent in the WebAssembly build (including the
    browser playground), which has no process model at all, and under
    `--sandbox`, which excludes it deliberately. Portable code branches with
    `(cond-expand ((library (kaappi process)) ...) (else ...))` — see
    [Running External Programs](../guide/subprocesses.md) for the full
    pattern.

!!! note "Availability"
    `(kaappi process)` arrived after v0.25.0. On an older binary the
    `(library (kaappi process))` gate below is simply false, and
    `kaappi features` reports what your build has.

The command is always a **list of strings**, never a shell command line.
Nothing is word-split, glob-expanded, or interpreted; a filename containing
a space or a semicolon is just an argument. Use `sh -c` explicitly if you
want a shell, and then you own the quoting.

---

## One-shot Capture

### `run-process` { #run-process }
<!-- index: 1+ | Run a program to completion; returns status, stdout, stderr -->

**Syntax:** `(run-process argv option ...)`

Spawns *argv*, feeds it optional input, collects everything it writes to
stdout and stderr, waits for it to exit, and returns three values: the exit
*status*, the captured *stdout*, and the captured *stderr*.

All three streams move at the same time, driven by fibers inside the call.
A child that fills its stdin, stdout and stderr buffers simultaneously
completes normally instead of deadlocking.

Options are quoted keyword symbols followed by a value:

| Option | Value | Meaning |
|---|---|---|
| `'input:` | string or bytevector | Written to the child's stdin, which is then closed. Without it the child's stdin is empty (`/dev/null`), never the terminal |
| `'timeout:` | seconds (real) | Kill the child and raise a [`process-timeout`](#process-timeout) condition if it has not exited in time |
| `'output:` | `'string` (default) or `'bytevector` | How *stdout* and *stderr* come back. Use `'bytevector` for a program whose output is not UTF-8 text |
| `'directory:` | string | Working directory for the child |
| `'env:` | alist of `(name . value)` strings | Replaces the child's environment wholesale — see [`process-environment`](#process-environment) |
| `'new-group:` | boolean | Put the child in its own process group. Implied by `'timeout:` |

```scheme
kaappi> (call-with-values
          (lambda () (run-process '("echo" "hello")))
          list)
;=> (0 "hello\n" "")
kaappi> (call-with-values
          (lambda () (run-process '("tr" "a-z" "A-Z") 'input: "shout"))
          list)
;=> (0 "SHOUT" "")
```

The status is an exit code, or the pair `(signaled . n)` on POSIX when the
child died from signal *n*.

Failure to start the program — it does not exist, or is not executable —
raises a file error, not a timeout condition, and carries the underlying
errno so "not found" and "not allowed" stay distinguishable.

**See also:** [`spawn-process`](#spawn-process), [`process-timeout?`](#process-timeout)

---

### `process-timeout?` { #process-timeout }
<!-- index: 1 | True if the object is a run-process timeout condition -->

**Syntax:** `(process-timeout? obj)`

Returns `#t` if *obj* is the condition `run-process` raises when its
`'timeout:` expires. By then the child (and its process group) has been
killed and reaped, so this condition is the only route to what the child
managed to produce.

```scheme
kaappi> (guard (e ((process-timeout? e) (process-timeout-stdout e)))
          (run-process '("sh" "-c" "printf started; sleep 30") 'timeout: 0.5))
;=> "started"
```

It is an ordinary error object as well: `error-object?` is true,
`error-object-message` is `"run-process: timed out"`, and
`error-object-irritants` is `(argv seconds)`. The captured output is
deliberately *not* in the irritants — an uncaught condition prints those,
and a child that wrote megabytes before stalling should not print them.

**See also:** [`process-timeout-stdout`](#process-timeout-stdout), [`run-process`](#run-process)

---

### `process-timeout-stdout` { #process-timeout-stdout }
<!-- index: 1 | Partial stdout captured before a run-process timeout -->

**Syntax:** `(process-timeout-stdout condition)`

Everything the child wrote to stdout before its `'timeout:` expired, in
whatever form `'output:` asked for. Raises a type error if *condition* is
not a `process-timeout` condition.

**See also:** [`process-timeout-stderr`](#process-timeout-stderr), [`process-timeout?`](#process-timeout)

---

### `process-timeout-stderr` { #process-timeout-stderr }
<!-- index: 1 | Partial stderr captured before a run-process timeout -->

**Syntax:** `(process-timeout-stderr condition)`

The stderr counterpart of
[`process-timeout-stdout`](#process-timeout-stdout).

**See also:** [`process-timeout-stdout`](#process-timeout-stdout), [`process-timeout?`](#process-timeout)

---

## Spawning

### `spawn-process` { #spawn-process }
<!-- index: 1+ | Start a program and return a process object -->

**Syntax:** `(spawn-process argv option ...)`

Starts *argv* and returns a process object immediately, without waiting.
Use this when the child is long-lived, when you want to interleave reads
and writes yourself, or when you need its pid.

| Option | Value | Meaning |
|---|---|---|
| `'stdin:` `'stdout:` `'stderr:` | a redirection spec | See below; the default is `'inherit` |
| `'directory:` | string | Working directory for the child |
| `'env:` | alist of `(name . value)` strings | Replaces the child's environment wholesale |
| `'new-group:` | boolean | Put the child in its own process group, so [`process-kill`](#process-kill) can signal the whole tree |

Redirection specs:

| Spec | Meaning |
|---|---|
| `'inherit` | The child shares Kaappi's own stream (the default) |
| `'pipe` | Create a pipe; the Kaappi end is a port on the process object |
| `'null` | `/dev/null` (`NUL` on Windows) |
| `'stdout` | **stderr only** — merge stderr into the same pipe as stdout |
| a port | An open, file-descriptor-backed port |

```scheme
kaappi> (define p (spawn-process '("sort") 'stdin: 'pipe 'stdout: 'pipe))
kaappi> (write-string "pear\napple\n" (process-stdin p))
kaappi> (close-port (process-stdin p))
kaappi> (read-line (process-stdout p))
;=> "apple"
kaappi> (process-wait p)
;=> 0
```

The child inherits exactly three descriptors — 0, 1 and 2. Every other
file, socket and pipe Kaappi holds is closed before the program starts.

**See also:** [`run-process`](#run-process), [`process-wait`](#process-wait)

---

### `process?` { #process }
<!-- index: 1 | True if argument is a process object -->

**Syntax:** `(process? obj)`

Returns `#t` if *obj* is a process object.

```scheme
kaappi> (process? (spawn-process '("true")))
;=> #t
kaappi> (process? 'nope)
;=> #f
```

---

### `process-pid` { #process-pid }
<!-- index: 1 | Operating-system process id of the child -->

**Syntax:** `(process-pid p)`

The child's process id, as the operating system reports it.

Do not use it to signal the child — use [`process-kill`](#process-kill),
which refuses to signal a process that has already been reaped. A reaped
pid may have been reused by an unrelated process.

**See also:** [`process-group`](#process-group), [`process-kill`](#process-kill)

---

### `process-group` { #process-group }
<!-- index: 1 | Process-group id, or #f if the child shares ours -->

**Syntax:** `(process-group p)`

The child's process-group id when it was spawned with `'new-group: #t`, and
`#f` otherwise. On Windows the group is a Job Object, and this reports the
same value a POSIX group leader would.

**See also:** [`spawn-process`](#spawn-process), [`process-kill`](#process-kill)

---

## Pipe Ports

### `process-stdin` { #process-stdin }
<!-- index: 1 | Output port writing to the child's stdin, or #f -->

**Syntax:** `(process-stdin p)`

The port that writes to the child's stdin, if `'stdin:` was `'pipe`, and
`#f` for every other spec.

It is an ordinary binary output port: every port procedure works on it, and
a write that would block parks only the calling fiber. Closing it is what
signals end-of-input to the child.

**See also:** [`process-stdout`](#process-stdout), [`spawn-process`](#spawn-process)

---

### `process-stdout` { #process-stdout }
<!-- index: 1 | Input port reading the child's stdout, or #f -->

**Syntax:** `(process-stdout p)`

The port that reads the child's stdout, if `'stdout:` was `'pipe`, and `#f`
otherwise. A read that would block parks only the calling fiber; sibling
fibers keep running.

**See also:** [`process-stderr`](#process-stderr), [`process-stdin`](#process-stdin)

---

### `process-stderr` { #process-stderr }
<!-- index: 1 | Input port reading the child's stderr, or #f -->

**Syntax:** `(process-stderr p)`

The stderr counterpart of [`process-stdout`](#process-stdout). Also `#f`
when `'stderr:` was `'stdout`, since the merged stream arrives on the
stdout port.

!!! note
    Reading one pipe to end-of-file before touching the other deadlocks the
    moment the child fills the pipe you are not reading. Read them in
    separate fibers, or use [`run-process`](#run-process), which does it for
    you.

**See also:** [`process-stdout`](#process-stdout)

---

## Waiting and Signaling

### `process-status` { #process-status }
<!-- index: 1 | Exit status if the child has exited, else #f -->

**Syntax:** `(process-status p)`

Returns `#f` while the child is still running, and its status once it has
exited: an integer exit code, or the pair `(signaled . n)` on POSIX for a
child killed by signal *n*. Never blocks.

```scheme
kaappi> (define p (spawn-process '("sleep" "5")))
kaappi> (process-status p)
;=> #f
```

**See also:** [`process-wait`](#process-wait)

---

### `process-wait` { #process-wait }
<!-- index: 1+ | Wait for the child to exit; returns its status -->

**Syntax:** `(process-wait p)` | `(process-wait p 'timeout: seconds)`

Waits for the child to exit and returns its status. The calling fiber
parks; every other fiber on the thread keeps running.

With `'timeout:`, returns `#f` if the child is still running when the
deadline passes — the child is left alive, and a later `process-wait` still
reaps it.

```scheme
kaappi> (define p (spawn-process '("sleep" "30")))
kaappi> (process-wait p 'timeout: 0.1)
;=> #f
kaappi> (process-kill p 'signal: 9)
kaappi> (process-wait p)
;=> (signaled . 9)
```

Waiting again on an already-reaped process returns the stored status
immediately.

**See also:** [`process-status`](#process-status), [`process-kill`](#process-kill)

---

### `process-kill` { #process-kill }
<!-- index: 1+ | Signal the child, or its whole process group -->

**Syntax:** `(process-kill p)` | `(process-kill p 'signal: n)` | `(process-kill p 'group: #t)`

Sends a signal to the child — `SIGTERM` (15) by default. With
`'group: #t` the signal goes to the whole process group, which reaches
grandchildren; that requires the child to have been spawned with
`'new-group: #t`, since otherwise the group is Kaappi's own.

Killing an already-reaped process is a quiet no-op, never an error: its pid
may belong to somebody else by now.

!!! note
    Windows has no signal delivery. `process-kill` terminates the process
    (or the Job Object, with `'group: #t`) and folds `'signal:` into the
    exit code it stamps as `128 + n` — so `'signal: 9` reports `137` rather
    than `(signaled . 9)`.

**See also:** [`process-wait`](#process-wait), [`process-group`](#process-group)

---

## Environment

### `process-environment` { #process-environment }
<!-- index: 0 | The current environment as an (name . value) alist -->

**Syntax:** `(process-environment)`

Returns the current process environment as a list of `(name . value)`
string pairs — the exact shape `'env:` accepts.

`'env:` **replaces** the environment rather than extending it, so this is
what you build on to add a variable without dropping everything else:

```scheme
kaappi> (call-with-values
          (lambda ()
            (run-process '("printenv" "GREETING")
                         'env: (cons (cons "GREETING" "hello")
                                     (process-environment))))
          list)
;=> (0 "hello\n" "")
```

A wholesale replacement that dropped the platform's own variables would
leave the child unable to start at all on Windows.

**See also:** [`run-process`](#run-process), [`spawn-process`](#spawn-process)
