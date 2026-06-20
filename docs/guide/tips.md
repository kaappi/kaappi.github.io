# Tips

- **Tail calls are optimized.** Write loops as recursive calls without worrying
  about stack overflow:

  ```scheme
  (define (loop n) (loop (+ n 1)))  ;; runs forever, no stack growth
  ```

- **Bignum arithmetic is automatic.** When a fixnum operation would overflow
  63 bits, the result is promoted to a bignum:

  ```scheme
  (expt 2 100)  ;=> 1267650600228229401496703205376
  ```

- **Unicode works everywhere.** String indexing, character predicates, and case
  conversion all operate on Unicode codepoints:

  ```scheme
  (char-alphabetic? #\λ)         ;=> #t
  (string-upcase "straße")       ;=> "STRASSE"
  ```

- **Use `guard` for structured error handling.** It combines exception catching
  with pattern matching:

  ```scheme
  (guard (e (#t (display "error caught\n")))
    (/ 1 0))
  ```

- **Use `call/ec` instead of `call/cc` for non-local exits.** `call/ec` captures
  a one-shot escape continuation with no stack snapshot -- much cheaper than
  `call/cc`, which copies all registers and frames:

  ```scheme
  (call/ec (lambda (exit)
    (for-each (lambda (x)
                (when (negative? x) (exit x)))
              '(1 2 -3 4))))
  ;=> -3
  ```

- **JIT compiles hot functions automatically.** After 100 calls, a function is
  compiled to native ARM64 code. No annotation needed. Use `--no-jit` to
  disable for debugging.

- **Use `write-shared` for circular structures.** `write` will hang on circular
  lists or vectors. `write-shared` prints them with datum labels:

  ```scheme
  (define x (list 1 2 3))
  (set-cdr! (cddr x) x)
  (write-shared x)  ;; prints: #0=(1 2 3 . #0#)
  ```

- **Exact division produces rationals, not floats.** `(/ 1 3)` gives `1/3`, not
  `0.333...`. Use `inexact` to convert when you need a float:

  ```scheme
  (/ 1 3)           ;=> 1/3
  (inexact (/ 1 3)) ;=> 0.3333333333333333
  ```

- **`string-set!` requires mutable strings.** String literals are immutable.
  Use `string-copy` to get a mutable copy first:

  ```scheme
  (define s (string-copy "hello"))
  (string-set! s 0 #\H)
  s  ;=> "Hello"
  ```

- **Sandbox mode blocks dangerous operations.** The `--sandbox` flag disables
  FFI, file I/O, `eval`, `load`, and environment variable access -- useful for
  running untrusted code safely.

---
