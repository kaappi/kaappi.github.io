# Your First Program

## Running a file

Create a file called `hello.scm`:

```scheme
(import (scheme base) (scheme write))

(display "Hello, world!")
(newline)
```

Run it:

```bash
kaappi hello.scm
```

Output:

```
Hello, world!
```

## The REPL

Launch the REPL with no arguments:

```bash
kaappi
```

```
Kaappi Scheme v0.1.0
Type (exit) to quit.

kaappi>
```

The REPL provides:

- **Line editing** -- arrow keys, Ctrl-A (start of line), Ctrl-E (end of line),
  backspace, delete
- **Command history** -- up/down arrows, persisted across sessions in
  `.kaappi_history`
- **Tab completion** -- completes all built-in and user-defined symbols
- **Multi-line input** -- open parentheses are tracked; the prompt changes to
  `  ... ` until all parens are balanced

```
kaappi> (define (square x)
  ...     (* x x))
kaappi> (square 7)
49
kaappi> (map square '(1 2 3 4 5))
(1 4 9 16 25)
```

Type `(exit)` or press Ctrl-D to quit.

!!! note "No install yet?"

    You can try all these examples in the [browser playground](../playground.md)
    — same interpreter, no installation required.

## A Multi-File Project

Real programs split code into libraries. Here's a small project that
computes statistics on a list of numbers.

Create the project structure:

```
stats-demo/
  mylib/
    stats.sld
  main.scm
```

Write the library in `mylib/stats.sld`:

```scheme
(define-library (mylib stats)
  (export mean median)
  (import (scheme base)
          (srfi 1)    ;; for fold
          (srfi 132)) ;; for list-sort
  (begin
    (define (mean lst)
      (/ (fold + 0 lst) (length lst)))

    (define (median lst)
      (let* ((sorted (list-sort < lst))
             (n (length sorted))
             (mid (quotient n 2)))
        (if (odd? n)
            (list-ref sorted mid)
            (/ (+ (list-ref sorted (- mid 1))
                  (list-ref sorted mid))
               2))))))
```

Write the main program in `main.scm`:

```scheme
(import (scheme base)
        (scheme write)
        (mylib stats))

(define data '(7 2 9 4 1 8 3 6 5))

(display "Data:   ") (display data)   (newline)
(display "Mean:   ") (display (inexact (mean data))) (newline)
(display "Median: ") (display (median data)) (newline)
```

Run it from inside `stats-demo/`:

```bash
cd stats-demo
kaappi main.scm
```

Output:

```
Data:   (7 2 9 4 1 8 3 6 5)
Mean:   5.0
Median: 5
```

The key points:

- Library name `(mylib stats)` maps to file path `mylib/stats.sld`
- `export` controls what the library exposes
- `import` in both the library and main program pulls in dependencies
- Kaappi finds `mylib/stats.sld` automatically from the current directory

For more on libraries, import modifiers, and search paths, see
[Working with Libraries](libraries.md).

---

Next: [Scheme Tutorial](tutorial.md)

