# Tips

## REPL Workflow

- **Use `,time` to measure performance.** Wrap any expression to see how
  long it takes:

  ```
  kaappi> ,time (fib 30)
  fib(30): 0.173s
  ```

- **Use `,profile` for detailed analysis.** Shows per-function timing, call
  counts, and allocation bytes:

  ```
  kaappi> ,profile (fib 20)
  ```

- **Use `,expand` to debug macros.** Shows the expanded form of a macro
  call before evaluation:

  ```
  kaappi> ,expand (when (> x 0) (display x))
  ;; shows the if/begin expansion
  ```

- **Use `,env` to explore bindings.** Lists all global names, or filter by
  prefix:

  ```
  kaappi> ,env string-
  string-append string-copy string-length ...
  ```

- **Use `,gc` to check memory pressure.** Shows heap size, live objects,
  and collection count -- useful for diagnosing allocation-heavy code.

## Performance

- **Prefer vectors over lists for random access.** `vector-ref` is O(1);
  `list-ref` is O(n) because it walks the chain of pairs. Use lists for
  sequential processing, vectors when you need indexing:

  ```scheme
  ;; Fast: O(1) lookup
  (define v (vector 10 20 30 40 50))
  (vector-ref v 3)         ;=> 40

  ;; Slow: O(n) traversal
  (define ls (list 10 20 30 40 50))
  (list-ref ls 3)          ;=> 40
  ```

- **JIT compiles hot functions after 100 calls.** Kaappi's JIT compiler
  targets ARM64 and inlines fixnum arithmetic, comparisons, `car`/`cdr`,
  and `cons`. Functions called fewer than 100 times stay interpreted.
  Warm up critical paths before benchmarking:

  ```scheme
  ;; Warm up the JIT before measuring
  (fib 10)                     ;; triggers JIT compilation of fib
  (let ((start (current-jiffy)))
    (fib 35)
    (/ (- (current-jiffy) start)
       (jiffies-per-second)))  ;=> ~1.9
  ```

- **Use `for-each` instead of `map` when you don't need results.** `map`
  allocates a new list for its return value; `for-each` just applies the
  procedure for side effects:

  ```scheme
  ;; Allocates a list you throw away -- wasteful
  (map display '(1 2 3))

  ;; No allocation
  (for-each display '(1 2 3))
  ```

- **Hash tables are O(1) for lookup.** Kaappi uses open-addressing with
  linear probing. For key-value associations that grow beyond a handful of
  entries, `hash-table-ref` is much faster than `assoc` on an alist:

  ```scheme
  (import (srfi 69))
  (define ht (alist->hash-table '((a . 1) (b . 2) (c . 3))))
  (hash-table-ref ht 'b)  ;=> 2
  ```

## Language Essentials

- **Tail calls are optimized.** Write loops as recursive calls without
  worrying about stack overflow:

  ```scheme
  (define (loop n) (loop (+ n 1)))  ;; runs forever, no stack growth
  ```

- **Bignum arithmetic is automatic.** When a fixnum operation would
  overflow 63 bits, the result is promoted to a bignum:

  ```scheme
  (expt 2 100)  ;=> 1267650600228229401496703205376
  ```

- **Unicode works everywhere.** String indexing, character predicates, and
  case conversion all operate on Unicode codepoints:

  ```scheme
  (char-alphabetic? #\λ)         ;=> #t
  (string-upcase "straße")       ;=> "STRASSE"
  ```

- **Exact division produces rationals, not floats.** `(/ 1 3)` gives
  `1/3`, not `0.333...`. Use `inexact` to convert when you need a float:

  ```scheme
  (/ 1 3)           ;=> 1/3
  (inexact (/ 1 3)) ;=> 0.3333333333333333
  ```

## Common Pitfalls

- **`eq?` doesn't compare numbers reliably.** Use `=` for numeric
  equality, `eqv?` for numbers and characters, `equal?` for deep
  structural comparison. `eq?` tests pointer identity -- two equal numbers
  may not be `eq?`:

  ```scheme
  (eq? 42 42)           ;=> #t (fixnums are immediate)
  (eq? 3.14 3.14)       ;=> #f (flonums are heap-allocated)
  (= 3.14 3.14)         ;=> #t (use = for numbers)
  ```

- **`set!` changes the binding, not the value.** If you pass a variable to
  a function and `set!` it inside, the caller's variable is unaffected:

  ```scheme
  (define x 10)
  (define (change! v) (set! v 99))
  (change! x)
  x  ;=> 10  (unchanged -- set! modified the local binding v)
  ```

- **`string-set!` requires mutable strings.** String literals are
  immutable. Use `string-copy` to get a mutable copy first:

  ```scheme
  (define s (string-copy "hello"))
  (string-set! s 0 #\H)
  s  ;=> "Hello"
  ```

- **`map` and `for-each` stop at the shortest list.** When given multiple
  lists of different lengths, extra elements are silently ignored:

  ```scheme
  (map + '(1 2 3) '(10 20))  ;=> (11 22)
  ```

- **`begin` in a definition context defines, not sequences.** At the top
  level or in a library body, `begin` splices definitions rather than
  sequencing expressions:

  ```scheme
  (begin
    (define a 1)
    (define b 2))
  ;; a and b are now top-level definitions
  ```

## Error Handling and Safety

- **Use `guard` for structured error handling.** It combines exception
  catching with pattern matching:

  ```scheme
  (guard (e (#t (display "error caught\n")))
    (/ 1 0))
  ```

- **Use `call/ec` instead of `call/cc` for non-local exits.** `call/ec`
  captures a one-shot escape continuation with no stack snapshot -- much
  cheaper than `call/cc`, which copies all registers and frames:

  ```scheme
  (call/ec (lambda (exit)
    (for-each (lambda (x)
                (when (negative? x) (exit x)))
              '(1 2 -3 4))))
  ;=> -3
  ```

- **Use `write-shared` for circular structures.** `write` will hang on
  circular lists or vectors. `write-shared` prints them with datum labels:

  ```scheme
  (define x (list 1 2 3))
  (set-cdr! (cddr x) x)
  (write-shared x)  ;; prints: #0=(1 2 3 . #0#)
  ```

- **Sandbox mode blocks dangerous operations.** The `--sandbox` flag
  disables FFI, file I/O, `eval`, `load`, and environment variable
  access -- useful for running untrusted code safely.

---
