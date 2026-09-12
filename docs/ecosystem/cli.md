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

`--help` and `-h` are handled automatically, and a bad invocation is
reported rather than ignored (see [Usage errors](#usage-errors)):

```
$ kaappi greet.scm --lodu Alice
greet: unknown option '--lodu'
Try 'greet --help' for more information.
```

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

Subcommands have their own specs: flags, options, and arguments. A
subcommand may declare an option with the same name as a top-level one;
see [Options after a subcommand](#options-after-a-subcommand) for which
wins.

### Validation

Every builder checks its arguments when the spec is built and raises an
error naming the builder and the offending value, so a mistake fails where
it is written rather than at the first invocation:

```scheme
(option "-n" "count" "Item count" 10)
;; error: option: long name must be "--" followed by a name without "=" "count"

(flag "-H" "--help" "Detail level")
;; error: flag: -h and --help are reserved for the built-in help "-H" "--help"

(cli "t" "T" (option "-a" "--count" "A" 1) (option "-b" "--count" "B" 2))
;; error: cli: duplicate long option name "--count"
```

The rules: a short name is `-` plus one character, a long name is `--` plus
a name without `=`, command and argument names are non-empty and do not
start with `-`, names and descriptions are strings, `-h` and `--help` are
reserved for the built-in help, and option, argument, and command names are
unique within one level. An argument may not share a name with a command at
the same level, since the command would always win.

## Parsing and result access

### Automatic dispatch

```scheme
(run-cli app handlers)
```

`handlers` is an alist mapping command names to handler functions. Use `#f`
for the default (no subcommand) handler, and optionally the symbol `error`
for a usage-error handler:

```scheme
(run-cli app
  `((#f      . ,main-handler)
    ("build" . ,build-handler)
    ("test"  . ,test-handler)
    (error   . ,report-usage-error)))
```

Each handler receives the parsed result. Two mistakes in the program itself
raise an error from `run-cli` rather than reaching a handler: a declared
command with no entry in `handlers`, and an app with no commands and no `#f`
entry.

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
(parsed-errors result)             ;=> usage errors as a list of strings, or ()
```

A positional argument that was not given is present with the value `#f`,
which makes a default a one-liner:

```scheme
(define app (cli "greet" "A greeting tool" (argument "name" "Name to greet")))
(parsed-args (run-cli-parse app '()))
;=> (("name" . #f))
(or (cdr (car (parsed-args (run-cli-parse app '())))) "World")
;=> "World"
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
deploy push — Push to production

Usage: deploy push [options]

Options:
  -t, --target <value>      Deploy target (default: production)
  -f, --force               Skip confirmation
  -h, --help                Show this help
```

## Usage errors

The parser reports input it cannot use instead of silently ignoring it: an
option that is not declared, an option with no value, a command that is
not declared, more positionals than declared, and a missing command when
the app declares commands but no `#f` handler. Parsing continues past each
problem, so one run reports everything wrong with the invocation.

`run-cli` prints each message to stderr prefixed with the app name, adds a
`--help` hint, and exits with status 2. Using the deploy tool above:

```
$ kaappi deploy.scm psuh
deploy: unknown command 'psuh'
Try 'deploy --help' for more information.

$ kaappi deploy.scm push --targe staging
deploy: unknown option '--targe'
deploy: unexpected argument 'staging'
Try 'deploy --help' for more information.

$ kaappi deploy.scm push --target
deploy: option '--target' requires a value
Try 'deploy --help' for more information.

$ echo $?
2
```

`--help` anywhere in argv still prints help and exits 0, even when the rest
of the invocation is wrong.

The errors are data on the parsed result, which is how tests see them:

```scheme
(define app
  (cli "deploy" "Deployment tool"
    (flag "-v" "--verbose" "Verbose output")
    (command "push" "Push to production"
      (option "-t" "--target" "Deploy target" "production"))))

(parsed-errors (run-cli-parse app '("push" "--targe" "staging")))
;=> ("unknown option '--targe'" "unexpected argument 'staging'")

(parsed-errors (run-cli-parse app '("-v" "push")))
;=> ()
```

To report errors your own way, add an entry keyed by the symbol `error` to
the handlers alist. It receives the parsed result, and `run-cli` returns
after calling it instead of exiting:

```scheme
(run-cli app
  `(("push" . ,push-handler)
    (error  . ,(lambda (r)
                 (for-each (lambda (m) (display m) (newline)) (parsed-errors r))
                 (exit 64)))))
```

!!! note
    Before kaappi-cli 0.2.0 the parser ignored unknown options and surplus
    arguments, and `run-cli` exited 0 on every path. A shell script that
    relied on that should check for the new exit status.

## Argument parsing details

### Option syntax

All of these are equivalent:

```bash
kaappi app.scm --output file.txt    # long form, separate value
kaappi app.scm --output=file.txt    # long form, = syntax
kaappi app.scm -o file.txt          # short form, separate value
kaappi app.scm -ofile.txt           # short form, attached value
kaappi app.scm -o=file.txt          # short form, = syntax
```

A value that starts with `-` is taken as a value only when it is a number
(`-n -5`) or the lone `-` (the stdin convention). Anything else that looks
like an option is parsed as one: the option is reported as missing its
value, and the stray token is reported on its own merits, as an unknown
option if it is one.

### Short option clusters

Short options combine into one token, as in getopt. Flags run together, and
the first option that takes a value swallows the rest of the token:

```bash
kaappi app.scm -vq        # --verbose --quiet
kaappi app.scm -vn 3      # --verbose --count 3
kaappi app.scm -vn3       # --verbose --count=3
kaappi app.scm -nv        # --count=v   (not --count then --verbose)
```

### Positional arguments and `--`

Positionals may appear anywhere among the options. `--` ends option
parsing, so everything after it is data even if it starts with `-`, and a
dash-leading token that reads as a real number is always data:

```bash
kaappi app.scm --verbose input.txt output.txt
kaappi app.scm input.txt --verbose output.txt   # same
kaappi app.scm -- -weird-name.txt               # positional "-weird-name.txt"
kaappi app.scm -5                               # positional "-5"
```

### Options after a subcommand

Top-level options are accepted before or after the subcommand token. When
the subcommand declares an option of the same name, the subcommand's wins
after its token; put the top-level one before it:

```scheme
(define app
  (cli "deploy" "Deployment tool"
    (flag "-v" "--verbose" "Verbose output")
    (command "push" "Push to production"
      (option "-t" "--target" "Deploy target" "production"))))

(define r (run-cli-parse app '("push" "-v" "--target" "staging")))
(parsed-flag? r "verbose")
;=> #t
(parsed-ref (parsed-sub r) "target")
;=> "staging"
```

## Help generation

Help is generated automatically from the spec. Every page, including one
for a subcommand with no options of its own, lists the `-h, --help` row.
You can also generate help programmatically:

```scheme
(generate-help app)            ;; print main help
(generate-help app "push")     ;; print help for a subcommand
```

`generate-help` raises an error when the subcommand name is not declared,
rather than printing a page for a command that does not exist.

## Building a standalone CLI

Compile your CLI tool into a single binary:

```bash
zig build -Dbundle-src=deploy.scm
cp zig-out/bin/kaappi deploy
./deploy push --target staging
```

See [Standalone Binaries](../guide/deployment.md#standalone-binaries).

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
| `(run-cli app handlers)` | Parse `(command-line)` and dispatch; usage errors exit 2 unless `handlers` has an `error` entry |
| `(run-cli app handlers argv)` | Same, with an explicit argv list |
| `(run-cli-parse app argv)` | Parse explicit argv; never exits |

### Result access

| Procedure | Description |
|-----------|-------------|
| `(parsed-ref result name)` | Option value by long name |
| `(parsed-flag? result name)` | Check if flag is set |
| `(parsed-args result)` | Positional args as alist |
| `(parsed-command result)` | Subcommand name or `#f` |
| `(parsed-sub result)` | Parsed result for subcommand |
| `(parsed-errors result)` | Usage errors as a list of strings, `()` when clean |

### Help

| Procedure | Description |
|-----------|-------------|
| `(generate-help app [command])` | Print formatted help; raises if `command` is not declared |
