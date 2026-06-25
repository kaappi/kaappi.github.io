# Web Framework

`(kaappi web)` — routing, middleware, cookies, sessions, and response helpers
for building web applications.

```bash
thottam install kaappi-web
```

Depends on [kaappi-http](http.md) and [kaappi-json](json.md) (auto-installed).

## Quick start

```scheme
(import (kaappi web))

(define app
  (routes
    (GET "/"
      (lambda (req params)
        (text-response "Hello, World!")))

    (GET "/users/:id"
      (lambda (req params)
        (json-response
          `(("id" . ,(param/number params "id"))))))

    (POST "/users"
      (lambda (req params)
        (let ((body (request-json req)))
          (json-response body 201))))))

(serve (wrap app wrap-json-body wrap-logging wrap-errors) 8080)
```

## Routing

Define routes with method + path pattern + handler:

```scheme
(routes
  (GET    "/path"       handler)
  (POST   "/path"       handler)
  (PUT    "/path"       handler)
  (DELETE "/path"       handler)
  (PATCH  "/path"       handler)
  (HEAD   "/path"       handler))
```

The first matching route wins. If no route matches, a 404 JSON response is
returned automatically.

### Path parameters

Use `:name` in path patterns to capture segments:

```scheme
(GET "/users/:id"
  (lambda (req params)
    (param params "id")            ;=> "42"
    (param/number params "id")     ;=> 42
    ...))

(GET "/users/:uid/posts/:pid"
  (lambda (req params)
    ;; params = (("uid" . "5") ("pid" . "99"))
    ...))
```

Path matching is segment-based — `:id` matches exactly one path segment
between `/` delimiters.

### Handlers

Every handler takes `(request params)` and returns a response:

```scheme
(lambda (req params)
  (json-response '(("status" . "ok"))))
```

## Response helpers

| Procedure | Description |
|-----------|-------------|
| `(json-response data [status])` | JSON body with `application/json` content type |
| `(text-response text [status])` | Plain text response |
| `(html-response html [status])` | HTML response |
| `(redirect url [status])` | 302 redirect (or custom status) |
| `(no-content)` | 204 No Content |

Status defaults to 200 unless specified:

```scheme
(json-response '(("created" . #t)) 201)
(json-response '(("error" . "not found")) 404)
(redirect "/login" 301)
```

## Request utilities

```scheme
(request-method req)             ;=> "GET"
(request-path req)               ;=> "/api/users"
(request-body req)               ;=> raw body string
(request-header req "host")      ;=> "localhost:8080" or #f
(request-query-params req)       ;=> (("page" . "1") ("limit" . "10"))

(param params "id")              ;=> path parameter or #f
(param/number params "id")       ;=> path param as number or #f
(request-json req)               ;=> parsed JSON body (set by wrap-json-body)
```

## Middleware

Middleware are `(handler -> handler)` functions. Compose them with `wrap`:

```scheme
(serve
  (wrap app
    wrap-json-body
    wrap-logging
    (wrap-cors "*")
    wrap-errors)
  8080)
```

Middleware runs outside-in: `wrap-errors` catches exceptions from everything
inside it.

### Built-in middleware

#### `wrap-json-body`

Parses `application/json` request bodies. Access the parsed data with
`(request-json req)`:

```scheme
(POST "/api/data"
  (lambda (req params)
    (let ((body (request-json req)))
      (json-response body))))
```

#### `wrap-logging`

Prints each request to stdout:

```
GET /users/42
POST /api/data
```

Includes method, path, and query string.

#### `(wrap-cors origin)`

Adds CORS headers and handles OPTIONS preflight:

```scheme
(wrap-cors "*")                 ;; allow all origins
(wrap-cors "https://myapp.com") ;; specific origin
```

Allows GET, POST, PUT, DELETE, PATCH, and OPTIONS methods.

#### `wrap-errors`

Catches unhandled exceptions and returns a 500 JSON error:

```json
{"error": "Internal server error"}
```

Place `wrap-errors` as the outermost middleware so it catches errors from
all inner layers.

### Custom middleware

A middleware function takes a handler and returns a new handler:

```scheme
(define (wrap-auth handler)
  (lambda (request)
    (if (request-header request "authorization")
        (handler request)
        (json-response '(("error" . "Unauthorized")) 401))))
```

### Middleware composition example

```scheme
(define (wrap-request-id handler)
  (lambda (request)
    (let ((id (number->string (random-integer 1000000))))
      (handler request))))

(define (wrap-timing handler)
  (lambda (request)
    (let* ((start (current-jiffy))
           (response (handler request))
           (elapsed (/ (- (current-jiffy) start)
                       (jiffies-per-second))))
      (log-info "request" `("elapsed" . ,elapsed))
      response)))

(serve
  (wrap app
    wrap-json-body
    wrap-timing
    wrap-request-id
    wrap-logging
    wrap-errors)
  8080)
```

## Cookies

Read and write HTTP cookies:

```scheme
;; Read cookies from a request
(request-cookies req)           ;=> (("session" . "abc") ("theme" . "dark"))
(request-cookie req "session")  ;=> "abc" or #f

;; Set a cookie on a response
(with-cookie
  (json-response '(("ok" . #t)))
  "session" "abc123"
  '((path . "/")
    (max-age . 3600)
    (http-only . #t)
    (secure . #t)
    (same-site . "Strict")))
```

### Cookie options

| Option | Type | Description |
|--------|------|-------------|
| `path` | string | Cookie path (default: none) |
| `domain` | string | Cookie domain |
| `max-age` | integer | Seconds until expiry |
| `http-only` | boolean | Inaccessible to JavaScript |
| `secure` | boolean | HTTPS only |
| `same-site` | string | `"Strict"`, `"Lax"`, or `"None"` |

### Build a Set-Cookie header directly

```scheme
(set-cookie "theme" "dark" '((path . "/") (max-age . 86400)))
;=> ("Set-Cookie" . "theme=dark; Path=/; Max-Age=86400")
```

## Sessions

Server-side sessions backed by an in-memory store, with a session ID cookie:

```scheme
(import (kaappi web))

(define store (make-memory-session-store))

(define app
  (routes
    (POST "/login"
      (lambda (req params)
        (let ((body (request-json req)))
          (session-set! req "user" (cdr (assoc "username" body)))
          (json-response '(("logged_in" . #t))))))

    (GET "/profile"
      (lambda (req params)
        (let ((user (session-ref req "user")))
          (if user
              (json-response `(("user" . ,user)))
              (json-response '(("error" . "not logged in")) 401)))))

    (POST "/logout"
      (lambda (req params)
        (session-destroy! req)
        (json-response '(("logged_out" . #t)))))))

(serve
  (wrap app
    wrap-json-body
    (wrap-session store)
    wrap-errors)
  8080)
```

### Session API

```scheme
(session-ref req "key")            ;=> value or #f
(session-set! req "key" value)     ;=> sets value in session
(session-delete! req "key")        ;=> removes key from session
(session-destroy! req)             ;=> clears entire session
(session-id req)                   ;=> session ID string
```

`wrap-session` middleware must be in the middleware stack for sessions to work.

## Authentication

Built-in authentication middleware that checks for a `user` key in the session:

```scheme
;; Protect routes — redirects unauthenticated users to /login
(serve
  (wrap app
    wrap-json-body
    (wrap-session (make-memory-session-store))
    (wrap-auth "/login")
    wrap-errors)
  8080)
```

### Authentication helpers

```scheme
(authenticated? req)    ;=> #t if session has "user" key
(current-user req)      ;=> session "user" value or #f
```

`wrap-auth` accepts either a redirect URL string or a handler function for
custom unauthorized responses:

```scheme
;; Redirect to login page
(wrap-auth "/login")

;; Return JSON error
(wrap-auth (lambda (req)
  (json-response '(("error" . "authentication required")) 401)))
```

## Server modes

```scheme
(serve app 8080)                    ;; sequential
(serve app 8080 "0.0.0.0")         ;; explicit bind address
(serve-prefork app 8080 4)          ;; 4 pre-forked worker processes
```

`serve-prefork` forks worker processes that share the listen socket. Each
worker handles requests independently. Good for CPU-bound workloads.

## Full API reference

### Routing

| Procedure | Description |
|-----------|-------------|
| `(routes route ...)` | Combine routes into a handler |
| `(GET pattern handler)` | GET route |
| `(POST pattern handler)` | POST route |
| `(PUT pattern handler)` | PUT route |
| `(DELETE pattern handler)` | DELETE route |
| `(PATCH pattern handler)` | PATCH route |
| `(HEAD pattern handler)` | HEAD route |

### Response

| Procedure | Description |
|-----------|-------------|
| `(json-response data [status])` | JSON response |
| `(text-response text [status])` | Plain text response |
| `(html-response html [status])` | HTML response |
| `(redirect url [status])` | Redirect (default 302) |
| `(no-content)` | 204 No Content |

### Request

| Procedure | Description |
|-----------|-------------|
| `(param params name)` | Path parameter by name |
| `(param/number params name)` | Path parameter as number |
| `(request-json req)` | Parsed JSON body |
| `(request-cookies req)` | All cookies as alist |
| `(request-cookie req name)` | Single cookie value |

### Cookies

| Procedure | Description |
|-----------|-------------|
| `(set-cookie name value [opts])` | Build Set-Cookie header pair |
| `(with-cookie response name value [opts])` | Add cookie to response |

### Sessions

| Procedure | Description |
|-----------|-------------|
| `(make-memory-session-store)` | Create in-memory session store |
| `(wrap-session handler [store])` | Session middleware |
| `(session-ref req key)` | Get session value |
| `(session-set! req key value)` | Set session value |
| `(session-delete! req key)` | Remove session key |
| `(session-destroy! req)` | Clear entire session |
| `(session-id req)` | Get session ID |

### Authentication

| Procedure | Description |
|-----------|-------------|
| `(authenticated? req)` | Check if user is in session |
| `(current-user req)` | Get user from session |
| `(wrap-auth handler-or-url)` | Auth guard middleware |

### Middleware

| Procedure | Description |
|-----------|-------------|
| `(wrap handler mw ...)` | Compose middleware |
| `wrap-json-body` | Parse JSON request bodies |
| `wrap-logging` | Log requests to stdout |
| `(wrap-cors origin)` | Add CORS headers |
| `wrap-errors` | Catch exceptions, return 500 |

### Server

| Procedure | Description |
|-----------|-------------|
| `(serve handler port [host])` | Start server |
| `(serve-prefork handler port workers [host])` | Start prefork server |
