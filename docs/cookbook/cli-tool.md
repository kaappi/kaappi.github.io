# Build a CLI Tool

This recipe builds a command-line tool with argument parsing, subcommands,
flags, and auto-generated help.

## Setup

```bash
thottam install kaappi-cli
thottam install kaappi-json   # used in the example
```

## A simple tool

A tool that greets someone, with a `--loud` flag and a `--times` option:

```scheme
(import (scheme base) (scheme write) (scheme char) (kaappi cli))

(define app
  (cli "greet" "A greeting tool"
    (flag "-l" "--loud" "Shout the greeting")
    (option "-n" "--times" "Repeat N times" 1)
    (argument "name" "Name to greet")))

(run-cli app
  `((#f . ,(lambda (result)
             (let ((name (cdr (car (parsed-args result))))
                   (loud? (parsed-flag? result "loud"))
                   (n (parsed-ref result "times")))
               (do ((i 0 (+ i 1))) ((= i n))
                 (let ((msg (string-append "Hello, " name "!")))
                   (display (if loud? (string-upcase msg) msg))
                   (newline))))))))
```

```bash
$ kaappi greet.scm Alice
Hello, Alice!

$ kaappi greet.scm --loud -n 3 Alice
HELLO, ALICE!
HELLO, ALICE!
HELLO, ALICE!

$ kaappi greet.scm --help
greet — A greeting tool

Usage: greet [options] <name>

Options:
  -l, --loud                Shout the greeting
  -n, --times <value>       Repeat N times (default: 1)
  -h, --help                Show this help

Arguments:
  <name>                    Name to greet
```

`--help` and `-h` are handled automatically.

## Subcommands

Build a tool with multiple commands, like `git` or `docker`:

```scheme
(import (scheme base) (scheme write) (scheme file)
        (kaappi cli) (kaappi json))

(define app
  (cli "tasks" "A task manager"
    (command "add" "Add a new task"
      (option "-p" "--priority" "Priority (low/med/high)" "med")
      (argument "title" "Task title"))
    (command "list" "List all tasks"
      (flag "-a" "--all" "Show completed tasks too"))
    (command "done" "Mark a task as completed"
      (argument "id" "Task ID"))))

(define tasks-file "tasks.json")

(define (load-tasks)
  (if (file-exists? tasks-file)
      (call-with-input-file tasks-file json-read)
      '()))

(define (save-tasks tasks)
  (call-with-output-file tasks-file
    (lambda (port) (json-write tasks port))))

(run-cli app
  `(("add" . ,(lambda (r)
                (let* ((sub (parsed-sub r))
                       (title (cdr (car (parsed-args sub))))
                       (priority (parsed-ref sub "priority"))
                       (tasks (load-tasks))
                       (id (+ 1 (length tasks)))
                       (task `(("id" . ,id)
                               ("title" . ,title)
                               ("priority" . ,priority)
                               ("done" . #f))))
                  (save-tasks (append tasks (list task)))
                  (display (string-append "Added task #"
                             (number->string id) ": " title))
                  (newline))))

    ("list" . ,(lambda (r)
                 (let* ((sub (parsed-sub r))
                        (show-all? (parsed-flag? sub "all"))
                        (tasks (load-tasks)))
                   (for-each
                     (lambda (task)
                       (let ((done? (cdr (assoc "done" task))))
                         (when (or show-all? (not done?))
                           (display
                             (string-append
                               (if done? "[x] " "[ ] ")
                               "#" (number->string (cdr (assoc "id" task)))
                               " " (cdr (assoc "title" task))
                               " (" (cdr (assoc "priority" task)) ")"))
                           (newline))))
                     tasks))))

    ("done" . ,(lambda (r)
                 (let* ((sub (parsed-sub r))
                        (id (string->number (cdr (car (parsed-args sub)))))
                        (tasks (load-tasks))
                        (updated (map (lambda (t)
                                        (if (= (cdr (assoc "id" t)) id)
                                            (cons '("done" . #t)
                                                  (filter (lambda (p)
                                                            (not (string=? (car p) "done")))
                                                          t))
                                            t))
                                      tasks)))
                   (save-tasks updated)
                   (display (string-append "Completed task #"
                              (number->string id)))
                   (newline))))))
```

```bash
$ kaappi tasks.scm add --priority high "Fix login bug"
Added task #1: Fix login bug

$ kaappi tasks.scm add "Write docs"
Added task #2: Write docs

$ kaappi tasks.scm list
[ ] #1 Fix login bug (high)
[ ] #2 Write docs (med)

$ kaappi tasks.scm done 1
Completed task #1

$ kaappi tasks.scm list --all
[x] #1 Fix login bug (high)
[ ] #2 Write docs (med)

$ kaappi tasks.scm add --help
add — Add a new task

Usage: add [options] <title>

Options:
  -p, --priority <value>    Priority (low/med/high) (default: med)
  -h, --help                Show this help

Arguments:
  <title>                   Task title
```

## Type coercion

Option types are inferred from the default value:

```scheme
;; String default → value stays a string
(option "-o" "--output" "Output file" "out.txt")
(parsed-ref result "output")  ;=> "report.txt"

;; Number default → value is parsed as a number
(option "-n" "--count" "Item count" 10)
(parsed-ref result "count")  ;=> 42

;; No default → string
(option "-f" "--format" "Output format")
(parsed-ref result "format")  ;=> "json" or #f if not provided
```

## Build a standalone binary

For distributing your CLI tool without requiring a Kaappi installation:

```bash
zig build -Dbundle-src=tasks.scm
# produces zig-out/bin/kaappi — rename to your tool name
cp zig-out/bin/kaappi tasks
./tasks add "Ship the binary"
```

See [Standalone Binaries](../guide/advanced.md#standalone-binaries) for
cross-compilation.
