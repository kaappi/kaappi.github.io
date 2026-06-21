# Web Framework

`(kaappi web)` — routing, middleware, and response helpers for building web applications.

```bash
thottam install kaappi-web
```

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

The first matching route wins. If no route matches, a 404 JSON response is returned automatically.

### Path parameters

Use `:name` in path patterns to capture segments:

```scheme
(GET "/users/:id"
  (lambda (req params)
    ;; params = (("id" . "42"))
    (param params "id")            ;=> "42"
    (param/number params "id")     ;=> 42
    ...))

(GET "/users/:uid/posts/:pid"
  (lambda (req params)
    ;; params = (("uid" . "5") ("pid" . "99"))
    ...))
```

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
(param params "id")              ; get path parameter or #f
(param/number params "id")       ; get path param as number or #f
(request-json req)               ; parsed JSON body (set by wrap-json-body)
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

Middleware runs outside-in: `wrap-errors` catches exceptions from everything inside it.

### Built-in middleware

#### `wrap-json-body`

Parses `application/json` request bodies. Access the parsed data with `(request-json req)`:

```scheme
(POST "/api/data"
  (lambda (req params)
    (let ((body (request-json req)))
      ;; body is a Scheme alist from the JSON
      (json-response body))))
```

#### `wrap-logging`

Prints each request to stdout:

```
GET /users/42
POST /api/data
```

#### `(wrap-cors origin)`

Adds CORS headers and handles OPTIONS preflight:

```scheme
(wrap-cors "*")                ; allow all origins
(wrap-cors "https://myapp.com") ; specific origin
```

#### `wrap-errors`

Catches unhandled exceptions and returns a 500 JSON error:

```json
{"error": "Internal server error"}
```

### Custom middleware

```scheme
(define (wrap-auth handler)
  (lambda (request)
    (if (request-header request "authorization")
        (handler request)
        (json-response '(("error" . "Unauthorized")) 401))))
```

## Server modes

```scheme
(serve app 8080)                    ; sequential
(serve-prefork app 8080 4)          ; 4 pre-forked worker processes
```

## Example: REST API

```scheme
(import (kaappi web) (kaappi pg) (kaappi json))

(define db (pg-connect "dbname=myapp"))

(define app
  (routes
    (GET "/users"
      (lambda (req params)
        (json-response (pg-query db "SELECT * FROM users"))))

    (GET "/users/:id"
      (lambda (req params)
        (let ((rows (pg-query db "SELECT * FROM users WHERE id = $1"
                      (param/number params "id"))))
          (if (null? rows)
              (json-response '(("error" . "not found")) 404)
              (json-response (car rows))))))

    (POST "/users"
      (lambda (req params)
        (let ((body (request-json req)))
          (pg-exec db "INSERT INTO users (name) VALUES ($1)"
            (cdr (assoc "name" body)))
          (json-response '(("created" . #t)) 201))))

    (DELETE "/users/:id"
      (lambda (req params)
        (pg-exec db "DELETE FROM users WHERE id = $1"
          (param/number params "id"))
        (json-response '(("deleted" . #t)))))))

(serve
  (wrap app wrap-json-body wrap-logging (wrap-cors "*") wrap-errors)
  8080)
```
