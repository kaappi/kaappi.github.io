# Call HTTP APIs

This recipe covers the client side of [kaappi-http](../ecosystem/http.md):
making requests, decoding JSON responses, handling failures, retries, and
downloading files. HTTPS works automatically with certificate
verification.

## Setup

```bash
thottam install kaappi-http
thottam install kaappi-json    # for the JSON examples
```

## Make a GET request

```scheme
(import (scheme base) (kaappi http))

(define resp
  (http-get "https://api.github.com/zen"
    '(("User-Agent" . "my-app/1.0"))))

(response-status resp)   ;=> 200
(response-body resp)     ;=> "Keep it logically awesome."
```

Headers are an alist of string pairs. Some APIs (like GitHub's) reject
requests without a `User-Agent`.

## Decode a JSON response

Most APIs speak JSON — combine with
[kaappi-json](../ecosystem/json.md):

```scheme
(import (kaappi http) (kaappi json))

(define (api-get url)
  (let ((resp (http-get url '(("Accept" . "application/json")))))
    (if (= (response-status resp) 200)
        (json-read-string (response-body resp))
        (error "API error" (response-status resp)))))

(define data (api-get "https://httpbin.org/get"))
(cdr (assoc "origin" data))   ;=> "203.0.113.7"
```

## Send data

`http-post`, `http-put`, and `http-delete` cover the writing methods:

```scheme
(define resp
  (http-post "https://httpbin.org/post"
    '(("Content-Type" . "application/json"))
    (json-write-string '(("name" . "Alice") ("score" . 95)))))

(http-put "https://httpbin.org/put"
  '(("Content-Type" . "text/plain"))
  "updated content")

(http-delete "https://httpbin.org/delete")
```

## Handle failures

Two distinct failure modes need two distinct handlers. HTTP error
statuses (4xx, 5xx) return normally — check `response-status`. Network
errors (DNS failure, connection refused, TLS problems) raise exceptions
— catch them with `guard`:

```scheme
(define (fetch url)
  (guard (e (#t (display "network error\n") #f))
    (let ((resp (http-get url)))
      (cond
        ((= (response-status resp) 200) (response-body resp))
        ((= (response-status resp) 404) #f)
        (else (error "unexpected status" (response-status resp)))))))
```

## Retry with backoff

Transient errors (timeouts, 500s, rate limits) deserve a few retries.
`thread-sleep!` from SRFI-18 pauses between attempts:

```scheme
(import (srfi 18))

(define (with-retries n thunk)
  (let loop ((attempt 1))
    (guard (e ((< attempt n)
               (thread-sleep! (* attempt 2))   ; 2s, 4s, 6s...
               (loop (+ attempt 1))))
      (thunk))))

(define body
  (with-retries 3
    (lambda ()
      (let ((resp (http-get "https://api.example.com/data")))
        (if (>= (response-status resp) 500)
            (error "server error" (response-status resp))
            (response-body resp))))))
```

## Follow redirects

The client does not follow redirects automatically. Loop on 3xx status
and the `location` header:

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

## Download to a file

```scheme
(import (scheme file))

(define (download url path)
  (let ((resp (http-get url)))
    (unless (= (response-status resp) 200)
      (error "download failed" url (response-status resp)))
    (call-with-output-file path
      (lambda (port)
        (write-string (response-body resp) port)))))

(download "https://kaappi-lang.org/install.sh" "install.sh")
```

## Build query strings

Encode parameters when constructing URLs by hand:

```scheme
(define (query-string params)
  (string-join
    (map (lambda (p) (string-append (car p) "=" (cdr p))) params)
    "&"))

(define url
  (string-append "https://httpbin.org/get?"
                 (query-string '(("page" . "1") ("limit" . "10")))))
```

(`string-join` comes from `(srfi 13)`. For values that may contain
spaces or `&`, percent-encode them first.)

## Going further

- Full API: [kaappi-http reference](../ecosystem/http.md)
- Serving HTTP instead: [Build a REST API](rest-api.md)
- Working with the responses: [Process JSON Data](json-processing.md)
