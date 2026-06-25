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

JSON objects are alists, arrays are lists. Use `assoc` to look up keys and
`cdr` to get the value:

```scheme
;; Given: {"server": {"host": "localhost", "port": 8080}, "debug": true}
(define config
  (json-read-string "{\"server\":{\"host\":\"localhost\",\"port\":8080},\"debug\":true}"))

(cdr (assoc "debug" config))
;=> #t

(cdr (assoc "host" (cdr (assoc "server" config))))
;=> "localhost"
```

For deeply nested access, a helper avoids chaining `assoc`/`cdr`:

```scheme
(define (json-ref obj . keys)
  (let loop ((o obj) (ks keys))
    (if (null? ks)
        o
        (let ((pair (assoc (car ks) o)))
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

;; Keep only active users, extract names
(define active-names
  (map (lambda (user) (cdr (assoc "name" user)))
       (filter (lambda (user) (cdr (assoc "active" user)))
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

;; Emit null in output
(json-write-string `(("value" . ,(json-null))))
;=> "{\"value\":null}"
```

## Type mapping reference

| JSON | Scheme | Check |
|------|--------|-------|
| `"hello"` | `"hello"` | `string?` |
| `42` | `42` | `integer?` |
| `3.14` | `3.14` | `inexact?` |
| `true` | `#t` | `boolean?` |
| `false` | `#f` | `boolean?` |
| `null` | `'null` | `json-null?` |
| `[1,2,3]` | `(1 2 3)` | `list?` |
| `{"a":1}` | `(("a" . 1))` | `pair?` with `string?` car |
