# Library Authoring Guide

This document covers how to create, organize, and use Scheme libraries with
Kaappi's R7RS library system.

---

## define-library Syntax

A library definition contains a name and one or more declarations:

```scheme
(define-library (library-name ...)
  (export export-spec ...)
  (import import-set ...)
  (begin body ...)
  (include filename ...)
  (include-ci filename ...)
  (cond-expand clause ...))
```

### Declarations

| Declaration | Purpose |
|-------------|---------|
| `export` | Names to make visible to importers |
| `import` | Libraries this library depends on |
| `begin` | Scheme code defining the library's bindings |
| `include` | Include source from another file (as if pasted into begin) |
| `include-ci` | Like include, but case-folded identifiers |
| `cond-expand` | Conditional declarations based on feature flags |

---

## Complete Example

A math utility library in `mylib/math.sld`:

```scheme
(define-library (mylib math)
  (export square cube factorial fibonacci)
  (import (scheme base))
  (begin
    (define (square x) (* x x))

    (define (cube x) (* x x x))

    (define (factorial n)
      (let loop ((i n) (acc 1))
        (if (= i 0) acc
            (loop (- i 1) (* i acc)))))

    (define (fibonacci n)
      (let loop ((i 0) (a 0) (b 1))
        (if (= i n) a
            (loop (+ i 1) b (+ a b)))))))
```

Using it from a program:

```scheme
(import (mylib math))

(display (square 5))      ;=> 25
(newline)
(display (factorial 10))  ;=> 3628800
(newline)
(display (fibonacci 20))  ;=> 6765
(newline)
```

---

## Export Specifications

The `export` declaration lists what the library makes available:

```scheme
;; Export names as-is
(export square cube factorial)

;; Export with renaming
(export (rename internal-name external-name))
```

Example with renaming:

```scheme
(define-library (mylib strings)
  (export (rename str-join join)
          (rename str-split split))
  (import (scheme base))
  (begin
    (define (str-join lst sep) ...)
    (define (str-split s sep) ...)))
```

---

## Import Sets and Modifiers

The `import` declaration accepts the same import sets as program-level
`import`: plain library names plus the `only`, `except`, `rename`, and
`prefix` modifiers, which can be nested. See
[Import Modifiers](libraries.md#import-modifiers) in the Libraries guide.

```scheme
(import (scheme base)
        (prefix (only (scheme char) char-upcase) c:))
```

---

## File Naming and Search Paths

### Naming Convention

Library names map to file paths by joining components with `/` and appending
`.sld`:

| Library Name | File Path |
|-------------|-----------|
| `(mylib math)` | `mylib/math.sld` |
| `(mylib util strings)` | `mylib/util/strings.sld` |
| `(srfi 1)` | `srfi/1.sld` |

### Search Order

Kaappi searches for `.sld` files in this order:

1. Current directory (`./`)
2. `./lib/` subdirectory
3. Directories specified with `--lib-path`

Example:

```bash
kaappi --lib-path /opt/scheme-libs --lib-path ./vendor program.scm
```

With this invocation, `(import (mylib math))` searches:

1. `./mylib/math.sld`
2. `./lib/mylib/math.sld`
3. `/opt/scheme-libs/mylib/math.sld`
4. `./vendor/mylib/math.sld`

---

## Bytecode Caching

Libraries are **not** bytecode-cached: a `.sld` file is compiled from source
each time it is loaded. (An earlier scheme that read `.sbc` files placed next
to libraries was removed as unsound -- if you have stray `.sbc` files sitting
beside your `.sld` sources from following older docs, they are ignored and
can be deleted.)

Program files *are* cached automatically: running `kaappi program.scm` stores
the compiled bytecode in a central cache at `$KAAPPI_HOME/cache` (default
`~/.kaappi/cache`), keyed by the source content and the exact binary that
compiled it -- so an upgraded or rebuilt `kaappi` never serves stale
bytecode. Subsequent runs of an unchanged program skip the
read/expand/compile pipeline entirely. Inspect or wipe the cache from the
CLI:

```bash
kaappi cache status   # cache location, entries, sizes, staleness
kaappi cache clear    # remove all entries
```

`kaappi --compile file.scm` still writes an explicit `.sbc` artifact -- an
output you asked for by name (for example to embed with `zig build
-Dbundle=file.sbc`), separate from the automatic cache.

---

## Available Libraries

For everything you can import — the 14 standard R7RS libraries, all 72
SRFIs, and the Kaappi extension libraries — see
[Available Libraries](libraries.md#available-libraries) and
[SRFI Support](srfi-support.md).

---

## cond-expand for Portable Code

Use `cond-expand` to write code that adapts to different Scheme implementations:

```scheme
(define-library (mylib compat)
  (export platform-name)
  (import (scheme base))
  (cond-expand
    (kaappi
     (begin
       (define platform-name "kaappi")))
    (chicken
     (begin
       (define platform-name "chicken")))
    (else
     (begin
       (define platform-name "unknown")))))
```

The `features` procedure returns the list of feature identifiers that Kaappi
supports:

```scheme
(features)  ;=> (r7rs kaappi ...)
```

---

## Library Organization Tips

- Put each library in its own `.sld` file.
- Use a consistent directory structure that mirrors library names.
- Keep a `lib/` directory for project-local libraries.
- Use `include` to split large libraries across multiple files:

  ```scheme
  (define-library (mylib big)
    (export ...)
    (import (scheme base))
    (include "big-part1.scm")
    (include "big-part2.scm"))
  ```

- Pre-compile libraries that don't change often:

  ```bash
  kaappi --compile lib/mylib/utils.sld
  ```

---

Next: [SRFI Support](srfi-support.md)
