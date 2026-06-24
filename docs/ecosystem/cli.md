# CLI

`(kaappi cli)` — declarative command-line argument parsing with
subcommands and auto-generated help. Pure Scheme, no build step.

```bash
thottam install kaappi-cli
```

## Quick start

```scheme
(import (kaappi cli))

(define app
  (cli "greet" "A greeting tool"
    (flag "-l" "--loud" "Use uppercase")
    (option "-n" "--times" "Repeat N times" 1)
    (argument "name" "Name to greet")))

(run-cli app
  `((#f . ,(lambda (result)
             (let ((name (cdr (car (parsed-args result))))
                   (n (parsed-ref result "times")))
               (do ((i 0 (+ i 1))) ((= i n))
                 (display "Hello, ") (display name)
                 (display "!") (newline)))))))
```

```
$ kaappi greet.scm Alice
Hello, Alice!

$ kaappi greet.scm --help
greet — A greeting tool

Usage: greet [options] <name>

Options:
  -l, --loud                Use uppercase
  -n, --times <value>       Repeat N times (default: 1)
  -h, --help                Show this help

Arguments:
  <name>                    Name to greet
```

`--help` and `-h` are handled automatically.

## Spec builders

```scheme
(cli name description spec ...)            ; top-level app
(flag short long description)              ; boolean flag
(option short long description [default])  ; option with value
(argument name description)                ; positional argument
(command name description spec ...)        ; subcommand
```

## Parsing and result access

```scheme
(run-cli app handlers)           ; parse and dispatch
(run-cli-parse app argv)         ; parse explicit argv (for testing)

(parsed-ref result "name")       ; option value by long name
(parsed-flag? result "verbose")  ; check if flag is set
(parsed-args result)             ; positional args as alist
(parsed-command result)          ; subcommand name or #f
(parsed-sub result)              ; parsed result for subcommand
```

## Subcommands

```scheme
(define app
  (cli "mytool" "My tool"
    (command "init" "Initialize"
      (argument "name" "Project name"))
    (command "build" "Build"
      (option "-j" "--jobs" "Parallel jobs" 4))))

(run-cli app
  `(("init"  . ,(lambda (r)
                  (display "Initializing ")
                  (display (cdr (car (parsed-args (parsed-sub r)))))
                  (newline)))
    ("build" . ,(lambda (r)
                  (display "Building with ")
                  (display (parsed-ref (parsed-sub r) "jobs"))
                  (display " jobs") (newline)))))
```

## Type coercion

Option types are inferred from the default value:

- Number default (`10`) — value parsed as number
- String default (`"out.txt"`) — value kept as string
- No default — string

## Help generation

```scheme
(generate-help app)           ; print help for main app
(generate-help app "build")   ; print help for subcommand
```
