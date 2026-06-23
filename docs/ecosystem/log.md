# kaappi-log — Structured Logging

```bash
thottam install kaappi-log
```

Pure Scheme — no dependencies.

## Quick start

```scheme
(import (kaappi log))

(log-info "server started" '("port" . 8080))
;=> 1719100000 [INFO] server started port=8080

(log-error "failed" '("code" . 500) '("path" . "/api"))
;=> 1719100000 [ERROR] failed code=500 path=/api
```

## API

### Logging

```scheme
(log-debug msg field ...)
(log-info msg field ...)
(log-warn msg field ...)
(log-error msg field ...)
(log-fatal msg field ...)
```

Fields are pairs: `'("key" . value)`

### Configuration

```scheme
(log-set-level! LOG-WARN)                ; filter below WARN
(log-set-port! (current-output-port))    ; output destination
(log-set-format! 'json)                  ; JSON output
(log-set-format! 'text)                  ; text output (default)
```

### Context fields

```scheme
(log-with-fields '(("req_id" . "abc"))
  (lambda ()
    (log-info "handling request")))       ; includes req_id=abc
```

## Output formats

**Text** (default):
```
1719100000 [INFO] request method=GET path=/api status=200
```

**JSON**:
```json
{"time":"1719100000","level":"INFO","msg":"request","method":"GET","status":200}
```

## Levels

`LOG-DEBUG` (0) < `LOG-INFO` (1) < `LOG-WARN` (2) < `LOG-ERROR` (3) < `LOG-FATAL` (4)
