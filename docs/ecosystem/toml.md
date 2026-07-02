# TOML

`(kaappi toml)` — TOML parser and serializer.

```bash
thottam install kaappi-toml
```

Pure Scheme — no dependencies.

For a task-oriented walkthrough (defaults, environment overrides,
validation), see the cookbook recipe
[Read Configuration Files](../cookbook/config-files.md).

## Quick start

```scheme
(import (kaappi toml))

(define config (toml-read-string "
[server]
host = \"localhost\"
port = 8080

[database]
url = \"sqlite:///app.db\"
"))

(toml-ref* config "server" "port")   ;=> 8080
```

## Reading TOML

### From a string

```scheme
(toml-read-string "key = \"value\"")
;=> (("key" . "value"))
```

### From a file

```scheme
(call-with-input-file "config.toml" toml-read)
```

### Nested access

Use `toml-ref` for single keys and `toml-ref*` for nested paths:

```scheme
(define config (toml-read-string "
[server]
host = \"localhost\"
port = 8080
debug = true
"))

(toml-ref config "server")
;=> (("host" . "localhost") ("port" . 8080) ("debug" . #t))

(toml-ref* config "server" "host")   ;=> "localhost"
(toml-ref* config "server" "port")   ;=> 8080
(toml-ref* config "server" "debug")  ;=> #t
```

## Writing TOML

```scheme
(toml-write-string
  '(("title" . "My App")
    ("server" . (("host" . "0.0.0.0")
                 ("port" . 8080)))))

(call-with-output-file "config.toml"
  (lambda (port)
    (toml-write '(("key" . "value")) port)))
```

## Type mapping

| TOML | Scheme | Example |
|------|--------|---------|
| String | string | `"hello"` |
| Integer | exact integer | `42` |
| Float | inexact number | `3.14` |
| Boolean | `#t` / `#f` | |
| Array | list | `(1 2 3)` |
| Table | alist | `(("key" . "value"))` |
| Datetime | string | `"2026-06-25T10:00:00Z"` |

## Supported TOML features

- Basic and literal strings, multiline strings
- Integers in decimal, hex (`0x`), octal (`0o`), binary (`0b`), with
  underscores (`1_000_000`)
- Floats including `inf`, `-inf`, `nan`
- Booleans
- Arrays and nested arrays
- Tables and nested tables
- Inline tables
- Array of tables (`[[section]]`)
- Comments
- Datetime strings (offset, local date, local time)
- Unicode escape sequences

## Common patterns

### Application config

```scheme
(define (load-config path)
  (call-with-input-file path toml-read))

(define config (load-config "app.toml"))

(define db-url (toml-ref* config "database" "url"))
(define port (or (toml-ref* config "server" "port") 8080))
```

### Config with defaults

```scheme
(define (config-ref config . keys)
  (let loop ((c config) (ks keys))
    (if (null? ks)
        c
        (let ((pair (assoc (car ks) c)))
          (if pair
              (loop (cdr pair) (cdr ks))
              #f)))))

(or (config-ref config "server" "port") 8080)
(or (config-ref config "server" "host") "0.0.0.0")
```

## API reference

| Procedure | Description |
|-----------|-------------|
| `(toml-read [port])` | Parse from port |
| `(toml-read-string str)` | Parse from string |
| `(toml-write table [port])` | Serialize to port |
| `(toml-write-string table)` | Serialize to string |
| `(toml-ref table key)` | Lookup single key |
| `(toml-ref* table key ...)` | Nested key lookup |
