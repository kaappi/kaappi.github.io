# HTTP

`(kaappi http)` — HTTP/HTTPS client and HTTP server.

```bash
thottam install kaappi-http
```

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
(http-request method url headers body)  ; generic
```

HTTPS is automatic — just use `https://` URLs. TLS with SNI and certificate verification via OpenSSL.

### Response accessors

```scheme
(response-status resp)               ;=> 200
(response-reason resp)               ;=> "OK"
(response-headers resp)              ;=> (("content-type" . "application/json") ...)
(response-header resp "content-type") ;=> "application/json" or #f
(response-body resp)                 ;=> body string
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

### Server modes

```scheme
;; Sequential (one request at a time)
(http-listen handler port)

;; Threaded (OS thread per connection)
(http-listen-threaded handler port)

;; Pre-fork (N worker processes)
(http-listen-prefork handler port 4)
```

## URL utilities

```scheme
(parse-url "https://example.com:8443/path?q=1")
;=> (values "https" "example.com" 8443 "/path")

(parse-query-string "name=alice&age=30")
;=> (("name" . "alice") ("age" . "30"))
```

!!! tip "Use kaappi-web for routing"
    `(kaappi http)` provides the low-level HTTP primitives. For routing,
    middleware, and JSON helpers, use the [`(kaappi web)`](web.md) framework.
