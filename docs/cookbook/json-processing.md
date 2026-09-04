# Process JSON Data

This recipe covers reading, transforming, and writing JSON — from files, from
strings, and from HTTP APIs.

## Setup

```bash
thottam install kaappi-json
thottam install kaappi-http    # only needed for the API examples
```

## Read JSON from a file

```scheme
(import (scheme base) (scheme write) (scheme file) (kaappi json))

(define (read-json-file path)
  (call-with-input-file path json-read))

(define config (read-json-file "config.json"))
(display config)
(newline)
```

## Access nested values

Non-empty JSON objects are alists, arrays are lists. Use `assoc` to look up
keys and `cdr` to get the value:

```scheme
;; Given: {"server": {"host": "localhost", "port": 8080}, "debug": true}
(define config
  (json-read-string "{\"server\":{\"host\":\"localhost\",\"port\":8080},\"debug\":true}"))

(cdr (assoc "debug" config))
;=> #t

(cdr (assoc "host" (cdr (assoc "server" config))))
;=> "localhost"
```

For deeply nested access, a helper avoids chaining `assoc`/`cdr`. It also
normalizes the empty object `{}` — which reads as the distinct
`json-empty-object` value, not as a list — so it never raises on an
empty object along the path:

```scheme
(import (kaappi json))

(define (object->alist o)
  (if (json-empty-object? o) '() o))

(define (json-ref obj . keys)
  (let loop ((o obj) (ks keys))
    (if (null? ks)
        o
        (let ((pair (assoc (car ks) (object->alist o))))
          (if pair
              (loop (cdr pair) (cdr ks))
              #f)))))

(json-ref config "server" "port")   ;=> 8080
(json-ref config "missing" "key")   ;=> #f
```

## Transform a list of objects

Filter and reshape a JSON array:

```scheme
(define data (json-read-string
  "[{\"name\":\"Alice\",\"age\":30,\"active\":true},
    {\"name\":\"Bob\",\"age\":25,\"active\":false},
    {\"name\":\"Carol\",\"age\":35,\"active\":true}]"))

;; Keep only active users, extract names.
;; json-ref (defined above) is safe here even if an element is {},
;; which decodes to the non-list json-empty-object value.
(define active-names
  (map (lambda (user) (json-ref user "name"))
       (filter (lambda (user) (json-ref user "active"))
               data)))

active-names  ;=> ("Alice" "Carol")
```

## Build JSON from Scheme data

Quasiquote with unquote makes building JSON structures natural:

```scheme
(define users '("Alice" "Bob" "Carol"))

(define result
  `(("count" . ,(length users))
    ("users" . ,(map (lambda (name)
                       `(("name" . ,name)
                         ("name_length" . ,(string-length name))))
                     users))))

(display (json-write-string result))
;=> {"count":3,"users":[{"name":"Alice","name_length":5},...]}
```

## Write JSON to a file

```scheme
(call-with-output-file "output.json"
  (lambda (port)
    (json-write result port)))
```

## Fetch JSON from an API

Combine `kaappi-http` with `kaappi-json` to call REST APIs:

```scheme
(import (kaappi http) (kaappi json))

(define (api-get url)
  (let ((resp (http-get url '(("Accept" . "application/json")))))
    (if (= (response-status resp) 200)
        (json-read-string (response-body resp))
        (error "API error" (response-status resp)))))

(define data (api-get "https://httpbin.org/get"))
(display (cdr (assoc "origin" data)))
(newline)
```

## POST JSON to an API

```scheme
(define (api-post url body)
  (let ((resp (http-post url
                '(("Content-Type" . "application/json"))
                (json-write-string body))))
    (json-read-string (response-body resp))))

(define result
  (api-post "https://httpbin.org/post"
    '(("name" . "Alice") ("score" . 95))))
```

## Round-trip: read, transform, write

A common pattern — read a JSON file, modify it, write it back:

```scheme
(import (scheme base) (scheme file) (kaappi json))

(define (update-json-file path transform)
  (let ((data (call-with-input-file path json-read)))
    (let ((updated (transform data)))
      (call-with-output-file path
        (lambda (port)
          (json-write updated port))))))

;; Add a "processed" field to every item in the array
(update-json-file "items.json"
  (lambda (items)
    (map (lambda (item)
           (cons '("processed" . #t) item))
         items)))
```

## Handle null values

JSON `null` is represented as the symbol `'null`:

```scheme
(json-read-string "{\"name\":\"Alice\",\"email\":null}")
;=> (("name" . "Alice") ("email" . null))

(json-null? 'null)   ;=> #t
(json-null? "hello") ;=> #f

;; Emit null in output — json-null is the constant 'null
(json-write-string `(("value" . ,json-null)))
;=> "{\"value\":null}"
```

## Handle empty objects

The empty object `{}` reads as the distinct value `json-empty-object`
(a record, *not* a list), so it round-trips as `{}` instead of `[]`:

```scheme
(json-empty-object? (json-read-string "{}")) ;=> #t
(json-empty-object? '())                     ;=> #f

;; a nested {} reads as the sentinel too
(json-empty-object?
  (cdr (assoc "server" (json-read-string "{\"server\":{}}"))))
;=> #t
```

`assoc`, `length` and `map` raise on it, and `null?` answers `#f` —
check `json-empty-object?` before treating a parsed object as an alist:

```scheme
(define (object->alist o)
  (if (json-empty-object? o) '() o))

(json-write-string (object->alist (json-read-string "{}")))
;=> "[]"
```

The flip side: `'()` writes as `[]`, so when a transform empties an
alist, substitute the sentinel before writing:

```scheme
(define obj '(("a" . 1) ("b" . 2)))
(define rest (filter (lambda (kv) (not (string=? (car kv) "a"))) obj))
(json-write-string (if (null? rest) json-empty-object rest))
;=> "{\"b\":2}"
```

See the [JSON library reference](../ecosystem/json.md#empty-objects) for
details.

## Checking decoded types

Parsed JSON decodes to ordinary Scheme values; test each with a predicate:

| Scheme value | Predicate |
|--------------|-----------|
| `"hello"` (string) | `string?` |
| `42` (integer) | `integer?` |
| `3.14` (float) | `inexact?` |
| `#t` / `#f` | `boolean?` |
| `'null` | `json-null?` |
| `(1 2 3)` (array) | `list?` |
| `(("a" . 1))` (object) | `pair?` with a `string?` car |
| `json-empty-object` (`{}`) | `json-empty-object?` |

!!! note
    The `pair?`/`string?` test is false for `{}`, which decodes to
    `json-empty-object` — a record, not a list. A `cond` written from
    this table checks `json-empty-object?` first, or every branch
    falls through on an empty object.

For the full JSON-to-Scheme representation table, see the
[JSON library reference](../ecosystem/json.md#type-mapping).
