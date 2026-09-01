# Explicit Renaming Macros

R7RS-small standardizes exactly one macro system: `syntax-rules`, the
declarative pattern language covered in the
[Language Reference](language.md#macros). Kaappi implements it in full —
and ships a second, *procedural* macro system alongside it:
`er-macro-transformer`, standardized by
[SRFI 211](https://srfi.schemers.org/srfi-211/srfi-211.html) and available
since v0.22.0 as a Kaappi extension beyond R7RS-small's scope
([KEP-0006](https://github.com/kaappi/keps/blob/main/keps/0006-explicit-renaming-macros.md)).

Stated plainly: this is **not** `syntax-case`. `syntax-case` is the macro
system R7RS-large standardizes on; Kaappi does not implement it
([KEP-0007](https://github.com/kaappi/keps/blob/main/keps/0007-full-syntax-case-support.md)
tracks what full support would take). What Kaappi offers for macros is
`syntax-rules` plus explicit renaming — and the two are guaranteed to have
the same hygiene strength for keyword checks (see
[`compare`](#compare-keyword-matching) below).

## The (form rename compare) convention

```scheme
(import (scheme base) (srfi 211 explicit-renaming))

(define-syntax name
  (er-macro-transformer
   (lambda (form rename compare)
     ...)))                             ; returns the expansion, as data
```

The transformer is an ordinary Scheme procedure invoked **at expansion
time**, once per use of the macro, with three arguments:

- **`form`** — the macro use itself, as plain data: `(`name arg ...`)`,
  with no syntax-object wrapping.
- **`rename`** — a procedure that yields hygienic identifiers for the
  names your expansion emits (see below).
- **`compare`** — a procedure that tests whether two identifiers denote
  the same binding — the rule a `syntax-rules` literal matches by.

The transformer's return value *is* the expansion: a Scheme expression,
constructed as data. The classic example is `swap!`, whose temporary must
not be capturable by a use-site variable of the same name:

```scheme
(define-syntax swap!
  (er-macro-transformer
   (lambda (form rename compare)
     (let ((a (cadr form))
           (b (caddr form))
           (tmp (rename 'tmp)))
       `(let ((,tmp ,a))
          (set! ,a ,b)
          (set! ,b ,tmp))))))

(define x 1)
(define y 2)
(swap! x y)
(list x y)                              ;=> (2 1)

;; hygiene: a user variable literally named tmp survives the swap
(define tmp 'mine)
(define other 'yours)
(swap! tmp other)
(list tmp other)                        ;=> (yours mine)
```

!!! note "The transformer runs at definition time"
    The transformer expression is evaluated when the `define-syntax` is
    evaluated, in the global environment — so it cannot close over
    enclosing runtime locals (they have no values at expansion time).
    An error raised while transforming is reported as a syntax error at
    the macro *use* site, naming the use — see
    [When to reach for er-macro-transformer](#when-to-reach-for-er-macro-transformer).

## rename: referential transparency

Every identifier your expansion emits that should *not* be under the use
site's control goes through `rename`:

- A renamed name with a binding at the macro's **definition site** keeps
  resolving there — a macro defined in a library can emit calls to that
  library's own helpers, even if the use site binds the same name to
  something else.
- A renamed name with no definition-site binding becomes a **fresh
  identifier** that cannot capture, or be captured by, any use-site name —
  `tmp` in `swap!` above.
- Renaming the same symbol twice within one expansion yields the *same*
  identifier, so the binding and reference sites of `tmp` agree.

`rename` accepts any datum, not just a symbol: it returns a copy with
every symbol at the leaves renamed — `(rename form)` renames an entire
subtree of the input in one call.

## compare: keyword matching

`compare` is `free-identifier=?`: it returns `#t` when its two arguments
denote **the same binding, or both are unbound** — exactly the rule a
`syntax-rules` literal matches by (R7RS 4.3.2). It answers `#f` for
non-symbols. Use it to recognize auxiliary keywords in the input form:

```scheme
(define-syntax my-cond
  (er-macro-transformer
   (lambda (form rename compare)
     (let loop ((clauses (cdr form)))
       (cond
         ((null? clauses) #f)
         ((compare (caar clauses) (rename 'else))
          (cadr (car clauses)))
         ((and (pair? (cdr (car clauses)))
               (compare (cadr (car clauses)) (rename '=>)))
          (let ((t (rename 't)))
            `(let ((,t ,(caar clauses)))
               (if ,t (,(caddr (car clauses)) ,t)
                   ,(loop (cdr clauses))))))
         (else
          `(if ,(caar clauses) ,(cadr (car clauses))
               ,(loop (cdr clauses)))))))))

(my-cond (#f 'a) (else 'matched))        ;=> matched
(my-cond ((assv 2 '((1 . a) (2 . b))) => cdr))  ;=> b
```

`compare` is **binding-aware**: a use-site local that rebinds the
keyword's spelling makes `compare` refuse the match, exactly as the
equivalent `syntax-rules` literal would. The `else` clause above is *not*
an else clause when the user has a local `else`:

```scheme
(let ((else #f))
  (my-cond (#f 'wrong) (else 'shadowed-keyword) (#t 'fell-through)))
                                        ;=> fell-through
```

That equivalence is a pinned guarantee, not an approximation: for keyword
checks — reserved forms and macro keywords, plus renamed spellings
generally — an explicit-renaming macro answers exactly what a
`syntax-rules` macro with the same literals answers. The fine print on
reserved spellings, and the two macro systems' shared limitations, are
recorded in the core repo's
[SRFI 211 implementation notes](https://github.com/kaappi/kaappi/blob/main/docs/dev/srfi-implementation-notes.md#srfi-211--scheme-macro-libraries).

## When to reach for er-macro-transformer

Reach for `syntax-rules` first: it is declarative, usually shorter,
portable to every R7RS Scheme, and the docs-sweep examples on this site
overwhelmingly use it. Reach for `er-macro-transformer` when the
expansion must be *computed*:

- **Validation with good errors.** The transformer sees the whole form,
  so it can check its shape and fail with a precise message at expansion
  time, before any of the code runs:

  ```scheme
  (define-syntax strict-when
    (er-macro-transformer
     (lambda (form rename compare)
       (if (= (length form) 3)
           `(,(rename 'if) ,(cadr form) ,(caddr form))
           (error "strict-when: exactly one body form required"
                  (length form))))))

  (strict-when (> 3 2) 'ok)             ;=> ok
  ```

  Feed it `(strict-when #t 1 2 3)` and the program stops at that use site
  with a message naming the macro and the actual shape it got — raised at
  expansion, so it is reported once at the bad use rather than misfiring
  at runtime:

  ```console
  $ kaappi strict.scm
  ok
  strict.scm:10:1: syntax-error[KP2002]: strict-when: exactly one body form required 5
  ```

- **Recursion patterns `syntax-rules` cannot express.** The `my-cond`
  above processes each clause with full `cond`-style dispatch; anything
  that needs to *decide per element* — mangling, filtering, arithmetic on
  the form — is a procedure call, not a template.

- **Generating from data.** The transformer can consult tables and
  globals, then emit code shaped by what it finds.

The cost is symmetrical: you write the output construction `syntax-rules`
would do for you, and you take over responsibility for renaming every
identifier the expansion emits. A macro that fits in a `syntax-rules`
template should stay there.

## Detecting the feature

The library itself is the feature test — guard portable code that needs
procedural macros:

```scheme
(cond-expand
  ((library (srfi 211 explicit-renaming))
   (define (procedural-macro-system) 'er-macro-transformer))
  (else
   (define (procedural-macro-system) 'none)))

(procedural-macro-system)                ;=> er-macro-transformer
```

SRFI 211 has no bare `(srfi 211)` import on Kaappi — only its
sub-libraries, of which `(srfi 211 explicit-renaming)` is the one that
provides `er-macro-transformer`. The sibling sub-libraries and the ones
that are not provided are listed on the
[SRFI Support](srfi-support.md#sub-library-only) page.

---

Next: [Libraries](libraries.md)
