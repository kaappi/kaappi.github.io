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
;=> (("name" . "Alice") ("age" . 30))

;; Serialize to JSON
(json-write-string '(("name" . "Alice") ("age" . 30)))
;=> "{\"name\":\"Alice\",\"age\":30}"
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

## Reading JSON

### From a string

```scheme
(json-read-string "{\"x\": 1}")
;=> (("x" . 1))

(json-read-string "[1, 2, 3]")
;=> (1 2 3)

(json-read-string "\"hello\"")
;=> "hello"

(json-read-string "42")
;=> 42
```

### From a port

```scheme
(json-read [port])
```

Reads from `port`, or `current-input-port` if omitted:

```scheme
(call-with-input-file "config.json" json-read)
```

### From stdin

```bash
echo '{"key": "value"}' | kaappi -e '(import (kaappi json)) (display (json-read))'
```

## Writing JSON

### To a string

```scheme
(json-write-string '(("name" . "Alice") ("age" . 30)))
;=> "{\"name\":\"Alice\",\"age\":30}"

(json-write-string '(1 2 3))
;=> "[1,2,3]"

(json-write-string "hello")
;=> "\"hello\""
```

### To a port

```scheme
(json-write val [port])
```

Writes to `port`, or `current-output-port` if omitted:

```scheme
(call-with-output-file "output.json"
  (lambda (port)
    (json-write '(("result" . "ok")) port)))
```

## Working with nested data

### Access nested values

JSON objects are alists. Use `assoc` to look up keys:

```scheme
(define data
  (json-read-string "{\"user\": {\"id\": 1, \"tags\": [\"admin\", \"active\"]}}"))

;; Top-level key
(cdr (assoc "user" data))
;=> (("id" . 1) ("tags" . ("admin" "active")))

;; Nested key
(cdr (assoc "id" (cdr (assoc "user" data))))
;=> 1

;; Array element
(car (cdr (assoc "tags" (cdr (assoc "user" data)))))
;=> "admin"
```

### Build nested structures

Quasiquote makes building JSON natural:

```scheme
(json-write-string
  `(("users" . ,(map (lambda (name)
                       `(("name" . ,name)))
                     '("Alice" "Bob" "Charlie")))))
;=> "{\"users\":[{\"name\":\"Alice\"},{\"name\":\"Bob\"},{\"name\":\"Charlie\"}]}"
```

### Build from computed data

```scheme
(define (user->json name email)
  `(("name" . ,name)
    ("email" . ,email)
    ("created" . ,(number->string (current-second)))))

(json-write-string
  `(("users" . ,(list (user->json "Alice" "alice@example.com")
                      (user->json "Bob" "bob@example.com")))))
```

## Null handling

JSON `null` is the symbol `'null`:

```scheme
(json-read-string "null")
;=> null

(json-null)
;=> null

(json-null? 'null)   ;=> #t
(json-null? "hello") ;=> #f
(json-null? #f)      ;=> #f
```

Emit null in output:

```scheme
(json-write-string `(("value" . ,(json-null))))
;=> "{\"value\":null}"
```

!!! note "null vs #f"
    JSON `null` is `'null` (a symbol), not `#f`. JSON `false` is `#f`.
    This distinction matters when checking for missing vs. false values.

## Round-trip safety

Parsing and then serializing preserves structure:

```scheme
(define original "{\"a\":1,\"b\":[true,null,\"x\"]}")
(define roundtrip (json-write-string (json-read-string original)))
;; roundtrip preserves all values and types
```

## Unicode and escape sequences

Full JSON spec compliance (RFC 8259):

```scheme
;; Unicode escapes
(json-read-string "\"\\u0041\"")       ;=> "A"

;; Surrogate pairs (emoji)
(json-read-string "\"\\uD83D\\uDE00\"") ;=> a grinning face emoji

;; All standard escapes
(json-read-string "\"\\n\\t\\r\\\\\\\"\"")
;=> a string with newline, tab, return, backslash, quote

;; Scientific notation
(json-read-string "1.5e-3")            ;=> 0.0015
(json-read-string "2.5E+10")           ;=> 25000000000.0
```

## Common patterns

### Config file loading

```scheme
(define (load-config path)
  (call-with-input-file path json-read))

(define config (load-config "config.json"))
(define port (cdr (assoc "port" (cdr (assoc "server" config)))))
```

### Transform and filter

```scheme
(define data (json-read-string "[{\"name\":\"a\",\"active\":true},{\"name\":\"b\",\"active\":false}]"))

(define active
  (filter (lambda (item) (cdr (assoc "active" item))) data))

(json-write-string active)
;=> "[{\"name\":\"a\",\"active\":true}]"
```

### Merge objects

```scheme
(define (json-merge a b)
  (append b a))

(json-merge '(("x" . 1) ("y" . 2))
            '(("y" . 99) ("z" . 3)))
;=> (("y" . 99) ("z" . 3) ("x" . 1) ("y" . 2))
;; assoc finds ("y" . 99) first, so b's values take precedence
```

## API reference

| Procedure | Description |
|-----------|-------------|
| `(json-read [port])` | Parse JSON from port (default: stdin) |
| `(json-read-string str)` | Parse JSON from string |
| `(json-write val [port])` | Write JSON to port (default: stdout) |
| `(json-write-string val)` | Write JSON to string |
| `(json-null)` | The null value (`'null` symbol) |
| `(json-null? val)` | Test for null |
