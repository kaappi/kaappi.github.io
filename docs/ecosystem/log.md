# Logging

`(kaappi log)` — structured logging with levels, fields, and JSON output.

```bash
thottam install kaappi-log
```

Pure Scheme — no dependencies.

## Quick start

```scheme
(import (kaappi log))

(log-info "server started" '("port" . 8080))
;=> 1719100000 [INFO] server started port=8080

(log-error "request failed" '("code" . 500) '("path" . "/api"))
;=> 1719100000 [ERROR] request failed code=500 path=/api
```

## Log levels

Five levels, from most to least verbose:

| Level | Constant | Value | Use for |
|-------|----------|:-----:|---------|
| Debug | `LOG-DEBUG` | 0 | Development diagnostics |
| Info | `LOG-INFO` | 1 | Normal operations |
| Warn | `LOG-WARN` | 2 | Unexpected but recoverable |
| Error | `LOG-ERROR` | 3 | Failures requiring attention |
| Fatal | `LOG-FATAL` | 4 | Unrecoverable failures |

```scheme
(log-debug "loading config" '("path" . "config.json"))
(log-info "server started" '("port" . 8080))
(log-warn "slow query" '("ms" . 1500) '("table" . "users"))
(log-error "connection lost" '("host" . "db.example.com"))
(log-fatal "out of memory" '("heap" . 1073741824))
```

## Structured fields

Attach key-value pairs as `'("key" . value)` arguments:

```scheme
(log-info "request"
  '("method" . "GET")
  '("path" . "/api/users")
  '("status" . 200)
  '("ms" . 12))
```

Text output:

```
1719100000 [INFO] request method=GET path=/api/users status=200 ms=12
```

Field values are converted automatically:

| Scheme type | Output |
|-------------|--------|
| string | as-is |
| number | decimal representation |
| boolean | `true` / `false` |
| other | `display` representation |

## Configuration

### Set minimum level

Messages below the minimum level are silently dropped:

```scheme
(log-set-level! LOG-WARN)

(log-info "this is hidden")    ;; dropped
(log-warn "this is visible")   ;; printed
(log-error "this too")         ;; printed
```

Default minimum level is `LOG-INFO`.

### Set output destination

```scheme
;; Log to a file
(log-set-port! (open-output-file "app.log"))

;; Log to stderr (default)
(log-set-port! (current-error-port))

;; Log to stdout
(log-set-port! (current-output-port))
```

### Switch to JSON format

```scheme
(log-set-format! 'json)

(log-info "request" '("method" . "GET") '("status" . 200))
```

Output:

```json
{"time":"1719100000","level":"INFO","msg":"request","method":"GET","status":200}
```

Switch back to text:

```scheme
(log-set-format! 'text)
```

## Context fields

Add fields that appear on every log line within a scope:

```scheme
(log-with-fields '(("req_id" . "abc-123") ("user" . "alice"))
  (lambda ()
    (log-info "loading data")
    ;=> 1719100000 [INFO] loading data req_id=abc-123 user=alice

    (log-info "query complete" '("rows" . 42))
    ;=> 1719100000 [INFO] query complete req_id=abc-123 user=alice rows=42
    ))
```

Context fields are prepended to per-call fields.

## Common patterns

### Application startup logging

```scheme
(import (kaappi log))

(log-set-format! 'json)
(log-set-level! LOG-INFO)

(log-info "starting"
  '("version" . "1.0.0")
  '("env" . "production")
  '("port" . 8080))
```

### Request logging in a web app

```scheme
(define (wrap-request-logging handler)
  (lambda (request)
    (let* ((start (current-second))
           (response (handler request))
           (elapsed (- (current-second) start)))
      (log-info "request"
        `("method" . ,(request-method request))
        `("path" . ,(request-path request))
        `("status" . ,(response-status response))
        `("seconds" . ,elapsed))
      response)))
```

### Error logging with context

```scheme
(guard (e (#t
           (log-error "unhandled exception"
             `("error" . ,(condition/report e))
             '("component" . "worker"))))
  (process-job job))
```

## API reference

### Logging

| Procedure | Description |
|-----------|-------------|
| `(log-debug msg field ...)` | Debug level log |
| `(log-info msg field ...)` | Info level log |
| `(log-warn msg field ...)` | Warning level log |
| `(log-error msg field ...)` | Error level log |
| `(log-fatal msg field ...)` | Fatal level log |

### Configuration

| Procedure | Description |
|-----------|-------------|
| `(log-set-level! level)` | Set minimum log level |
| `(log-set-port! port)` | Set output destination |
| `(log-set-format! fmt)` | Set format: `'text` or `'json` |
| `(log-with-fields fields thunk)` | Add context fields for scope |

### Constants

| Constant | Value | Description |
|----------|:-----:|-------------|
| `LOG-DEBUG` | 0 | Most verbose |
| `LOG-INFO` | 1 | Default minimum |
| `LOG-WARN` | 2 | Warnings |
| `LOG-ERROR` | 3 | Errors |
| `LOG-FATAL` | 4 | Unrecoverable |
