# Working with Libraries

## Importing Standard Libraries

Every R7RS program starts by importing what it needs:

```scheme
(import (scheme base))
(import (scheme write))
(display (+ 1 2))
(newline)
```

Multiple imports can be combined:

```scheme
(import (scheme base)
        (scheme write)
        (scheme char))
```

## Import Modifiers

```scheme
;; Import only specific names
(import (only (scheme base) map filter))

;; Import everything except certain names
(import (except (scheme base) error))

;; Rename on import
(import (rename (scheme base) (map scheme-map)))

;; Add a prefix to all imported names
(import (prefix (scheme char) char:))
(char:char-alphabetic? #\A)  ;=> #t
```

## Available Libraries

Kaappi includes all 14 R7RS standard libraries, 72 SRFIs (8 built-in,
64 portable), and two Kaappi extension libraries.

### Standard R7RS Libraries (14)

| Library | Exports | Description |
|---------|---------|-------------|
| `(scheme base)` | 230+ | Core procedures and syntax |
| `(scheme case-lambda)` | 1 | `case-lambda` syntax |
| `(scheme char)` | 22 | Unicode character operations |
| `(scheme complex)` | 6 | Complex number procedures |
| `(scheme cxr)` | 28 | Car/cdr compositions (3 and 4 deep) |
| `(scheme eval)` | 3 | `eval`, `environment`, `interaction-environment` |
| `(scheme file)` | 10 | File I/O |
| `(scheme inexact)` | 12 | Transcendental math (sin, cos, exp, log, ...) |
| `(scheme lazy)` | 5 | `delay`, `force`, promises |
| `(scheme load)` | 1 | `load` |
| `(scheme process-context)` | 5 | `exit`, `command-line`, environment variables |
| `(scheme read)` | 1 | `read` |
| `(scheme time)` | 3 | `current-second`, jiffies |
| `(scheme write)` | 7 | `write`, `display`, `write-shared` |

### SRFI Libraries (72)

See the [SRFI Support](srfi-support.md) page for the complete list of
all 72 supported SRFIs, built-in and portable.

### Kaappi Extension Libraries

| Library | Description |
|---------|-------------|
| `(kaappi ffi)` | Foreign function interface (ffi-open, ffi-fn, ffi-callback, ffi-close) |
| `(kaappi fibers)` | Green threads (spawn, yield, fiber-join, channels) |

## Writing Your Own Library

Define libraries with `define-library` in `.sld` files. The
[Library Authoring](library-authoring.md) guide covers the full syntax:
export specifications, `include`, `cond-expand`, file naming, bytecode
caching, and organization tips.

## Library Search Paths

Kaappi searches for `.sld` files in this order:

1. The current directory (`./`)
2. The `./lib/` subdirectory
3. Directories specified with `--lib-path`

The library name `(mylib math)` maps to the file path `mylib/math.sld`.

```bash
kaappi --lib-path /path/to/libs program.scm
```

---

Next: [Library Authoring](library-authoring.md)

