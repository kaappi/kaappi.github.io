# YAML

`(kaappi yaml)` — YAML parser and writer.

```bash
thottam install kaappi-yaml
```

Pure Scheme — no dependencies.

## Quick start

```scheme
(import (kaappi yaml))

(define config (yaml-read-string "
server:
  host: localhost
  port: 8080
routes:
  - /
  - /api
"))

(yaml-ref* config "server" "port")   ;=> 8080
(yaml-ref config "routes")           ;=> ("/" "/api")
```

## Reading YAML

### From a string

```scheme
(yaml-read-string "key: value")
;=> (("key" . "value"))
```

### From a file

```scheme
(call-with-input-file "config.yml" yaml-read)
```

### Nested access

```scheme
(define config (yaml-read-string "
app:
  name: My Service
  version: 1.2.0
  features:
    - auth
    - logging
"))

(yaml-ref config "app")
;=> (("name" . "My Service") ("version" . "1.2.0") ("features" . ("auth" "logging")))

(yaml-ref* config "app" "name")      ;=> "My Service"
(yaml-ref* config "app" "features")  ;=> ("auth" "logging")
```

## Writing YAML

```scheme
(yaml-write-string
  '(("name" . "My App")
    ("version" . "1.0.0")
    ("features" . ("auth" "logging"))))

(call-with-output-file "output.yml"
  (lambda (port)
    (yaml-write '(("key" . "value")) port)))
```

## Type mapping

| YAML | Scheme | Example |
|------|--------|---------|
| Mapping | alist | `(("key" . "value"))` |
| Sequence | list | `(1 2 3)` |
| String | string | `"hello"` |
| Integer | exact integer | `42` |
| Float | inexact number | `3.14` |
| Boolean | `#t` / `#f` | `true`, `false`, `yes`, `no` |
| Null | `'null` | `~`, `null`, empty value |

### Null handling

```scheme
(yaml-read-string "value: ~")
;=> (("value" . null))

(yaml-read-string "value: null")
;=> (("value" . null))

(yaml-null? 'null)   ;=> #t
(yaml-null? "hello") ;=> #f
```

## Supported YAML features

- Block style mappings and sequences
- Flow style (inline) mappings `{a: 1, b: 2}` and sequences `[1, 2, 3]`
- Nested structures (any depth)
- Quoted strings (single and double)
- Automatic scalar type detection (numbers, booleans, null)
- Special float values (`.inf`, `-.inf`, `.nan`)
- Comments (`#`)

## Common patterns

### Load configuration

```scheme
(define (load-config path)
  (call-with-input-file path yaml-read))

(define config (load-config "app.yml"))
(define port (or (yaml-ref* config "server" "port") 8080))
```

### Process a list of items

```scheme
(define data (yaml-read-string "
users:
  - name: Alice
    role: admin
  - name: Bob
    role: user
"))

(for-each
  (lambda (user)
    (display (cdr (assoc "name" user)))
    (display " is ")
    (display (cdr (assoc "role" user)))
    (newline))
  (yaml-ref data "users"))
```

## API reference

| Procedure | Description |
|-----------|-------------|
| `(yaml-read [port])` | Parse from port |
| `(yaml-read-string str)` | Parse from string |
| `(yaml-write value [port])` | Serialize to port |
| `(yaml-write-string value)` | Serialize to string |
| `(yaml-ref table key)` | Lookup single key |
| `(yaml-ref* table key ...)` | Nested key lookup |
| `(yaml-null? value)` | Check for null |
