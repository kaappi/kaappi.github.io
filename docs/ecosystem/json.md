# JSON

`(kaappi json)` — JSON parser and serializer. Pure Scheme, no build step.

```bash
thottam install kaappi-json
```

## Quick start

```scheme
(import (kaappi json))

;; Parse JSON
(json-read-string "{\"name\": \"Alice\", \"age\": 30}")
;; => (("name" . "Alice") ("age" . 30))

;; Serialize to JSON
(json-write-string '(("name" . "Alice") ("age" . 30)))
;; => "{\"name\":\"Alice\",\"age\":30}"
```

## Type mapping

| JSON | Scheme | Example |
|------|--------|---------|
| object | alist | `(("key" . "value"))` |
| array | list | `(1 2 3)` |
| string | string | `"hello"` |
| number (integer) | exact integer | `42` |
| number (float) | inexact number | `3.14` |
| `true` | `#t` | |
| `false` | `#f` | |
| `null` | `'null` symbol | |

Vectors are written as JSON arrays: `#(1 2 3)` becomes `[1,2,3]`.

## API

### Reading

```scheme
(json-read [port])          ; parse JSON from port (default: current-input-port)
(json-read-string str)      ; parse JSON from a string
```

### Writing

```scheme
(json-write val [port])     ; write JSON to port (default: current-output-port)
(json-write-string val)     ; write JSON to a string
```

### Null

```scheme
(json-null)                 ; the null value ('null symbol)
(json-null? val)            ; test for null
```

## Examples

### Nested objects

```scheme
(json-read-string "{\"user\": {\"id\": 1, \"tags\": [\"admin\", \"active\"]}}")
;; => (("user" . (("id" . 1) ("tags" . ("admin" "active")))))
```

### Building JSON from data

```scheme
(json-write-string
  `(("users" . ,(map (lambda (name)
                       `(("name" . ,name)))
                     '("Alice" "Bob" "Charlie")))))
;; => "{\"users\":[{\"name\":\"Alice\"},{\"name\":\"Bob\"},{\"name\":\"Charlie\"}]}"
```

### Reading from a file

```scheme
(let ((port (open-input-file "config.json")))
  (let ((config (json-read port)))
    (close-input-port port)
    config))
```

## Features

- Full JSON spec compliance (RFC 8259)
- Unicode escape sequences (`\uXXXX`) including surrogate pairs
- All escape sequences (`\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`)
- Scientific notation (`1.5e-3`)
- Round-trip safe (parse then serialize preserves structure)
