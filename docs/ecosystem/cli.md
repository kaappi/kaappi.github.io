# CLI Parsing

`(kaappi cli)` — declarative command-line argument parsing with subcommands,
type coercion, and auto-generated help.

```bash
thottam install kaappi-cli
```

Pure Scheme — no dependencies.

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

### `cli` — define the app

```scheme
(cli name description spec ...)
```

### `flag` — boolean switch

```scheme
(flag "-v" "--verbose" "Enable verbose output")
(flag "-q" "--quiet" "Suppress output")
```

Flags are `#f` by default, `#t` when present.

### `option` — value parameter

```scheme
(option "-o" "--output" "Output file" "out.txt")
(option "-n" "--count" "Number of items" 10)
(option "-f" "--format" "Output format")
```

The default value determines type coercion:
- Number default (`10`) — input is parsed as a number
- String default (`"out.txt"`) — input stays as a string
- No default — string, `#f` when not provided

### `argument` — positional parameter

```scheme
(argument "file" "Input file")
(argument "output" "Output path")
```

### `command` — subcommand

```scheme
(command "init" "Initialize a project"
  (argument "name" "Project name"))
```

Subcommands have their own specs — flags, options, arguments, and nested
subcommands.

## Parsing and result access

### Automatic dispatch

```scheme
(run-cli app handlers)
```

`handlers` is an alist mapping command names to handler functions. Use `#f`
for the default (no subcommand) handler:

```scheme
(run-cli app
  `((#f      . ,main-handler)
    ("build" . ,build-handler)
    ("test"  . ,test-handler)))
```

### Manual parsing

For testing or custom dispatch:

```scheme
(define result (run-cli-parse app '("--verbose" "-n" "5" "input.txt")))
```

### Result accessors

```scheme
(parsed-ref result "output")       ;=> option value by long name, or default
(parsed-flag? result "verbose")    ;=> #t if flag was set
(parsed-args result)               ;=> positional args as (("name" . "value") ...)
(parsed-command result)            ;=> subcommand name or #f
(parsed-sub result)                ;=> parsed result for the subcommand
```

## Subcommands

Build tools with multiple commands:

```scheme
(define app
  (cli "deploy" "Deployment tool"
    (flag "-v" "--verbose" "Verbose output")

    (command "push" "Push to production"
      (option "-t" "--target" "Deploy target" "production")
      (flag "-f" "--force" "Skip confirmation"))

    (command "rollback" "Roll back last deploy"
      (argument "version" "Version to roll back to"))

    (command "status" "Show deploy status")))

(run-cli app
  `(("push" . ,(lambda (r)
                 (let ((sub (parsed-sub r)))
                   (display "Pushing to ")
                   (display (parsed-ref sub "target"))
                   (when (parsed-flag? sub "force")
                     (display " (forced)"))
                   (newline))))

    ("rollback" . ,(lambda (r)
                     (let ((sub (parsed-sub r)))
                       (display "Rolling back to ")
                       (display (cdr (car (parsed-args sub))))
                       (newline))))

    ("status" . ,(lambda (r)
                   (display "All systems operational\n")))))
```

```
$ kaappi deploy.scm push --target staging
Pushing to staging

$ kaappi deploy.scm push --force
Pushing to production (forced)

$ kaappi deploy.scm rollback v1.2.3
Rolling back to v1.2.3

$ kaappi deploy.scm --help
deploy — Deployment tool

Usage: deploy [options] <command>

Options:
  -v, --verbose             Verbose output
  -h, --help                Show this help

Commands:
  push                      Push to production
  rollback                  Roll back last deploy
  status                    Show deploy status
```

### Subcommand help

Each subcommand has its own help:

```
$ kaappi deploy.scm push --help
push — Push to production

Usage: push [options]

Options:
  -t, --target <value>      Deploy target (default: production)
  -f, --force               Skip confirmation
  -h, --help                Show this help
```

## Argument parsing details

### Option syntax

All of these are equivalent:

```bash
kaappi app.scm --output file.txt    # long form, separate value
kaappi app.scm --output=file.txt    # long form, = syntax
kaappi app.scm -o file.txt          # short form
```

### Flag combining

Flags can be combined in short form:

```bash
kaappi app.scm -vq     # sets both --verbose and --quiet
```

### Positional arguments

Positional arguments are collected after all flags and options:

```bash
kaappi app.scm --verbose input.txt output.txt
```

## Help generation

Help is generated automatically from the spec. You can also generate it
programmatically:

```scheme
(generate-help app)            ;; print main help
(generate-help app "push")     ;; print help for a subcommand
```

## Building a standalone CLI

Compile your CLI tool into a single binary:

```bash
zig build -Dbundle-src=deploy.scm
cp zig-out/bin/kaappi deploy
./deploy push --target staging
```

See [Standalone Binaries](../guide/advanced.md#standalone-binaries).

## API reference

### Spec builders

| Procedure | Description |
|-----------|-------------|
| `(cli name desc spec ...)` | Define CLI app |
| `(flag short long desc)` | Boolean flag |
| `(option short long desc [default])` | Option with value |
| `(argument name desc)` | Positional argument |
| `(command name desc spec ...)` | Subcommand |

### Parsing

| Procedure | Description |
|-----------|-------------|
| `(run-cli app handlers)` | Parse and dispatch |
| `(run-cli-parse app argv)` | Parse explicit argv |

### Result access

| Procedure | Description |
|-----------|-------------|
| `(parsed-ref result name)` | Option value by long name |
| `(parsed-flag? result name)` | Check if flag is set |
| `(parsed-args result)` | Positional args as alist |
| `(parsed-command result)` | Subcommand name or `#f` |
| `(parsed-sub result)` | Parsed result for subcommand |

### Help

| Procedure | Description |
|-----------|-------------|
| `(generate-help app [command])` | Print formatted help |
