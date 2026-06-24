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

Kaappi includes all 14 R7RS standard libraries, 9 built-in SRFIs, and 42
portable SRFIs. See the [Library Reference](library-authoring.md) for the
complete list.

## Writing Your Own Library

Create a file `mylib/math.sld`:

```scheme
(define-library (mylib math)
  (export square cube factorial)
  (import (scheme base))
  (begin
    (define (square x) (* x x))
    (define (cube x) (* x x x))
    (define (factorial n)
      (let loop ((i n) (acc 1))
        (if (= i 0) acc
            (loop (- i 1) (* i acc)))))))
```

Use it from another file:

```scheme
(import (mylib math))
(display (factorial 10))  ;=> 3628800
(newline)
```

## Library Search Paths

Kaappi searches for `.sld` files in this order:

1. The current directory (`./`)
2. The `./lib/` subdirectory
3. Directories specified with `--lib-path`

The library name `(mylib math)` maps to the file path `mylib/math.sld`.

```bash
kaappi --lib-path /path/to/libs program.scm
```

See the [Library Reference](library-authoring.md) for export specs, import
modifiers, bytecode caching, `cond-expand`, and the complete library list.

---

Next: [Advanced Features](advanced.md)

