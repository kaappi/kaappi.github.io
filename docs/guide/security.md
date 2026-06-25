# Security

This guide covers secure coding practices for Kaappi applications: input
validation, SQL injection prevention, safe FFI, TLS, sandbox mode, and the
overall security model.

## SQL injection prevention

Always use parameterized queries. Never build SQL by concatenating user
input:

```scheme
;; WRONG — vulnerable to SQL injection
(pg-query conn
  (string-append "SELECT * FROM users WHERE name = '" name "'"))

;; CORRECT — parameterized query
(pg-query conn "SELECT * FROM users WHERE name = $1" name)
```

PostgreSQL uses `$1`, `$2` placeholders. SQLite uses `?`:

```scheme
(sqlite-query db "SELECT * FROM users WHERE email = ?" email)
```

Parameters are sent separately from the SQL text and are never interpreted
as SQL. This prevents injection regardless of what the user provides.

## Input validation

Validate user input at the boundary — before it reaches your application
logic:

```scheme
(define (validate-email s)
  (and (string? s)
       (> (string-length s) 0)
       (string-contains s "@")))

(define (validate-positive-integer s)
  (let ((n (string->number s)))
    (and n (exact-integer? n) (positive? n))))
```

In a web handler:

```scheme
(POST "/users"
  (lambda (req params)
    (let ((body (request-json req)))
      (cond
        ((not (assoc "name" body))
         (json-response '(("error" . "name is required")) 400))
        ((not (assoc "email" body))
         (json-response '(("error" . "email is required")) 400))
        ((not (validate-email (cdr (assoc "email" body))))
         (json-response '(("error" . "invalid email")) 400))
        (else
         (create-user db body)
         (json-response '(("created" . #t)) 201))))))
```

## XSS prevention

When serving HTML, use `template-render-html` (not `template-render`) to
auto-escape user data:

```scheme
(import (kaappi template))

;; SAFE — auto-escapes <, >, &, ", '
(template-render-html "<p>{{.name}}</p>"
  `(("name" . ,user-input)))

;; UNSAFE — user input rendered as raw HTML
(template-render "<p>{{.name}}</p>"
  `(("name" . ,user-input)))
```

`template-render-html` escapes these characters:

| Character | Escape |
|-----------|--------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |
| `"` | `&quot;` |
| `'` | `&#39;` |

You can also use `html-escape` directly:

```scheme
(html-escape "<script>alert('xss')</script>")
;=> "&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;"
```

## TLS and HTTPS

The HTTP client uses TLS with certificate verification by default for
`https://` URLs:

```scheme
(http-get "https://api.example.com/data"
  '(("Authorization" . "Bearer token123")))
```

TLS is provided by OpenSSL with SNI (Server Name Indication) and system
certificate verification. There is no way to disable certificate
verification — this is intentional.

For the low-level TLS API:

```scheme
(import (kaappi net))
(define ssl (tls-connect "api.example.com" 443))
;; SNI and certificate verification are automatic
```

## Safe FFI practices

FFI gives native code full access to the host process. Treat it as a trust
boundary:

### Only load trusted libraries

```scheme
;; Load a system library — OK
(define libm (ffi-open "libm.dylib"))

;; Load a user-provided path — DANGEROUS
;; Never pass user input to ffi-open
(define lib (ffi-open user-provided-path))  ;; DON'T DO THIS
```

### Validate FFI inputs

C functions don't check types. Pass wrong arguments and you get undefined
behavior:

```scheme
(define c-strlen (ffi-fn libc "strlen" '(string) 'size_t))

;; Always validate before calling
(define (safe-strlen s)
  (unless (string? s) (error "strlen: expected string" s))
  (c-strlen s))
```

### Release resources

```scheme
(define lib (ffi-open "libfoo.dylib"))
;; ... use lib ...
(ffi-close lib)

;; For callbacks:
(define cb (ffi-callback my-proc '(int) 'int))
;; ... pass cb to C ...
(ffi-callback-release cb)
```

## Sandbox mode

The `--sandbox` flag runs code with restricted capabilities — designed for
untrusted input:

```bash
kaappi --sandbox untrusted.scm
```

### What sandbox blocks

| Category | Blocked procedures |
|----------|-------------------|
| **File I/O** | `open-input-file`, `open-output-file`, `call-with-input-file`, `call-with-output-file`, `with-input-from-file`, `with-output-to-file`, `file-exists?`, `delete-file` |
| **FFI** | `ffi-open`, `ffi-fn`, `ffi-close`, `ffi-callback` |
| **Code loading** | `eval`, `load` |
| **Process context** | `get-environment-variable`, `get-environment-variables`, `command-line`, `exit` |
| **Filesystem** | All SRFI-170 operations |
| **OS threads** | SRFI-18 (`thread-start!`, mutexes, etc.) |

### What sandbox allows

Arithmetic, strings, lists, vectors, hash tables, standard output
(`display`, `write`), green fibers, and all pure-computation libraries.

### Resource limits

Combine sandbox with resource limits to prevent infinite loops and memory
exhaustion:

```bash
kaappi --sandbox --timeout 5000 --max-memory 10000000 untrusted.scm
```

| Flag | Description |
|------|-------------|
| `--timeout N` | Kill execution after N milliseconds |
| `--max-memory N` | Cap heap allocation at N bytes (GC runs first) |

Both flags work independently of `--sandbox`.

### Sandbox escape testing

The sandbox boundary is verified by a test suite of 31 escape tests that
confirm every gated capability is blocked. These tests run in CI on every
commit.

## Secrets management

Never hardcode secrets in source files:

```scheme
;; WRONG
(define api-key "sk-live-abc123...")

;; CORRECT — read from environment
(define api-key (get-environment-variable "API_KEY"))
```

For database credentials:

```scheme
;; Use environment variables
(define db
  (pg-connect
    (string-append "host=" (get-environment-variable "DB_HOST")
                   " dbname=" (get-environment-variable "DB_NAME")
                   " user=" (get-environment-variable "DB_USER")
                   " password=" (get-environment-variable "DB_PASS"))))
```

## Security model summary

| Component | Trust level | Notes |
|-----------|-------------|-------|
| R7RS Scheme code | Sandboxable | Use `--sandbox` for untrusted code |
| FFI (native code) | Full trust | Same privileges as host process |
| `.sbc` bytecode | Trusted input | Don't load from untrusted sources |
| `thottam` packages | Trusted | Native packages have full access |
| HTTPS | Certificate verified | SNI + system CA store |
| Parameterized queries | SQL-injection safe | Use `$1` / `?` parameters |

## Reporting vulnerabilities

See [SECURITY.md](https://github.com/kaappi/kaappi/blob/main/SECURITY.md).
Use GitHub's private security advisory feature — do not open a public issue.
