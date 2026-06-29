# HTTP

`(kaappi http)` — HTTP/HTTPS client and HTTP server.

```bash
thottam install kaappi-http
```

Depends on [kaappi-net](net.md) (auto-installed).

## Client

### GET request

```scheme
(import (kaappi http))

(let ((resp (http-get "https://api.github.com/"
              '(("User-Agent" . "my-app/1.0")))))
  (display (response-status resp))   ;=> 200
  (display (response-body resp)))    ;=> JSON string
```

### POST request

```scheme
(let ((resp (http-post "https://httpbin.org/post"
              '(("Content-Type" . "application/json"))
              "{\"name\": \"Alice\"}")))
  (response-status resp))  ;=> 200
```

### All methods

```scheme
(http-get url [headers])
(http-post url [headers] [body])
(http-put url [headers] [body])
(http-delete url [headers])
(http-head url [headers])
(http-request method url headers body)  ;; generic
```

HTTPS is automatic — just use `https://` URLs. TLS with SNI and certificate
verification via OpenSSL.

### Response accessors

```scheme
(response-status resp)               ;=> 200
(response-reason resp)               ;=> "OK"
(response-headers resp)              ;=> (("content-type" . "application/json") ...)
(response-header resp "content-type") ;=> "application/json" or #f
(response-body resp)                 ;=> body string
```

### Error handling

Network errors and HTTP errors are separate concerns. Network errors (DNS
failure, connection refused, TLS errors) raise Scheme errors. HTTP error
status codes (4xx, 5xx) return normally — check `response-status`:

```scheme
(let ((resp (http-get "https://httpbin.org/status/404")))
  (cond
    ((= (response-status resp) 200)
     (display "ok"))
    ((= (response-status resp) 404)
     (display "not found"))
    (else
     (display "error: ")
     (display (response-status resp)))))
```

For network errors, use `guard`:

```scheme
(import (scheme base))

(guard (e (#t (display "network error\n")))
  (http-get "https://unreachable.invalid/"))
```

### Sending JSON

Combine with [kaappi-json](json.md) for typed request/response:

```scheme
(import (kaappi http) (kaappi json))

(define (api-post url data)
  (let ((resp (http-post url
                '(("Content-Type" . "application/json")
                  ("Accept" . "application/json"))
                (json-write-string data))))
    (if (= (response-status resp) 200)
        (json-read-string (response-body resp))
        (error "API error" (response-status resp)
               (response-body resp)))))

(api-post "https://httpbin.org/post"
  '(("name" . "Alice") ("score" . 95)))
```

### Following redirects

The HTTP client does not automatically follow redirects. Check for 3xx
status and re-request:

```scheme
(define (http-get-follow url headers)
  (let ((resp (http-get url headers)))
    (if (and (>= (response-status resp) 300)
             (< (response-status resp) 400))
        (let ((location (response-header resp "location")))
          (if location
              (http-get-follow location headers)
              resp))
        resp)))
```

## Server

### Basic server

```scheme
(import (kaappi http))

(define (handler request)
  (make-response 200 "Hello, World!"
    '(("Content-Type" . "text/plain"))))

(http-listen handler 8080)
```

### Request accessors

```scheme
(request-method req)        ;=> "GET"
(request-path req)          ;=> "/api/users"
(request-query req)         ;=> "page=1&limit=10"
(request-query-params req)  ;=> (("page" . "1") ("limit" . "10"))
(request-headers req)       ;=> alist
(request-header req "host") ;=> "localhost:8080" or #f
(request-body req)          ;=> body string
```

### Response constructors

```scheme
(make-response status body)
(make-response status body headers)
```

Headers is an alist of string pairs:

```scheme
(make-response 200 "{\"ok\":true}"
  '(("Content-Type" . "application/json")
    ("Cache-Control" . "max-age=60")))
```

### Routing by hand

Without the web framework, route by matching method and path:

```scheme
(define (handler req)
  (let ((method (request-method req))
        (path (request-path req)))
    (cond
      ((and (string=? method "GET") (string=? path "/"))
       (make-response 200 "Home"))
      ((and (string=? method "GET") (string=? path "/health"))
       (make-response 200 "{\"status\":\"ok\"}"
         '(("Content-Type" . "application/json"))))
      (else
       (make-response 404 "Not Found")))))
```

### Server modes

```scheme
;; Sequential (one request at a time)
(http-listen handler port)
(http-listen handler port "0.0.0.0")

;; Threaded (OS thread per connection)
(http-listen-threaded handler port)

;; Pre-fork (N worker processes)
(http-listen-prefork handler port 4)
```

Threaded mode uses SRFI-18 OS threads, which are unavailable in
`--sandbox` mode and in the WebAssembly build. Pre-fork mode uses
`fork()` and is the recommended approach for production concurrency.

## URL utilities

```scheme
(parse-url "https://example.com:8443/path?q=1")
;=> (values "https" "example.com" 8443 "/path")
```

Use `let-values` to bind the result:

```scheme
(let-values (((scheme host port path)
              (parse-url "https://api.example.com/v1/users")))
  (display host))   ;=> "api.example.com"
```

### Query string parsing

```scheme
(parse-query-string "name=alice&age=30")
;=> (("name" . "alice") ("age" . "30"))

(parse-query-string "q=hello+world&tag=a%26b")
;=> (("q" . "hello world") ("tag" . "a&b"))
```

Handles `+` (space) and `%XX` URL encoding.

## API reference

### Client

| Procedure | Description |
|-----------|-------------|
| `(http-get url [headers])` | GET request |
| `(http-post url [headers] [body])` | POST request |
| `(http-put url [headers] [body])` | PUT request |
| `(http-delete url [headers])` | DELETE request |
| `(http-head url [headers])` | HEAD request |
| `(http-request method url headers body)` | Generic request |

### Response

| Procedure | Description |
|-----------|-------------|
| `(make-response status body [headers])` | Create response |
| `(response-status resp)` | Status code |
| `(response-reason resp)` | Reason phrase |
| `(response-headers resp)` | All headers as alist |
| `(response-header resp name)` | Single header value |
| `(response-body resp)` | Body string |

### Request

| Procedure | Description |
|-----------|-------------|
| `(request-method req)` | HTTP method |
| `(request-path req)` | Request path |
| `(request-query req)` | Raw query string |
| `(request-query-params req)` | Parsed query params as alist |
| `(request-headers req)` | All headers as alist |
| `(request-header req name)` | Single header value |
| `(request-body req)` | Body string |

### Server

| Procedure | Description |
|-----------|-------------|
| `(http-listen handler port [host])` | Sequential server |
| `(http-listen-threaded handler port [host])` | Threaded server |
| `(http-listen-prefork handler port workers [host])` | Pre-fork server |

### URL

| Procedure | Description |
|-----------|-------------|
| `(parse-url url)` | Returns `(values scheme host port path)` |
| `(parse-query-string qs)` | Parse query string to alist |

!!! tip "Use kaappi-web for routing"
    `(kaappi http)` provides the low-level HTTP primitives. For routing,
    middleware, and JSON helpers, use the [`(kaappi web)`](web.md) framework.
