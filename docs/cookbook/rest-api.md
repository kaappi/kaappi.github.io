# Build a REST API

This recipe builds a JSON REST API with PostgreSQL storage, Redis caching,
input validation, structured logging, and proper error handling. By the end
you will have a working API you can deploy.

## Setup

Install the libraries:

```bash
thottam install kaappi-web    # also installs kaappi-http, kaappi-json, kaappi-net
thottam install kaappi-pg
thottam install kaappi-redis
thottam install kaappi-log
```

Create the database:

```bash
createdb bookshelf
```

## Project structure

```
bookshelf/
  lib/
    bookshelf/
      db.sld
      cache.sld
      handlers.sld
      validate.sld
  app.scm
```

## Step 1: Database layer

Start with a library that owns all database access. Parameterized queries
with `$1` placeholders prevent SQL injection.

`lib/bookshelf/db.sld`:

```scheme
(define-library (bookshelf db)
  (export db-init db-list-books db-get-book db-create-book
          db-update-book db-delete-book)
  (import (scheme base) (kaappi pg))
  (begin

    (define (db-init conn)
      (pg-exec conn "CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER,
        created_at TIMESTAMP DEFAULT now()
      )"))

    (define (db-list-books conn)
      (pg-query conn "SELECT id, title, author, year FROM books ORDER BY id"))

    (define (db-get-book conn id)
      (let ((rows (pg-query conn "SELECT id, title, author, year FROM books WHERE id = $1" id)))
        (if (null? rows) #f (car rows))))

    (define (db-create-book conn title author year)
      (pg-exec conn "INSERT INTO books (title, author, year) VALUES ($1, $2, $3)"
        title author year)
      (car (pg-query conn "SELECT id, title, author, year FROM books ORDER BY id DESC LIMIT 1")))

    (define (db-update-book conn id title author year)
      (let ((count (pg-exec conn
                    "UPDATE books SET title = $1, author = $2, year = $3 WHERE id = $4"
                    title author year id)))
        (if (> count 0)
            (db-get-book conn id)
            #f)))

    (define (db-delete-book conn id)
      (> (pg-exec conn "DELETE FROM books WHERE id = $1" id) 0))))
```

## Step 2: Redis cache

Cache individual book lookups so repeated reads skip the database.

`lib/bookshelf/cache.sld`:

```scheme
(define-library (bookshelf cache)
  (export cache-get cache-set cache-invalidate)
  (import (scheme base) (kaappi redis) (kaappi json))
  (begin

    (define (cache-key id)
      (string-append "book:" (number->string id)))

    (define (cache-get redis id)
      (let ((val (redis-get redis (cache-key id))))
        (if val (json-read-string val) #f)))

    (define (cache-set redis id book-vec)
      (let ((data `(("id"     . ,(vector-ref book-vec 0))
                    ("title"  . ,(vector-ref book-vec 1))
                    ("author" . ,(vector-ref book-vec 2))
                    ("year"   . ,(vector-ref book-vec 3)))))
        (redis-setex redis (cache-key id) 300 (json-write-string data))))

    (define (cache-invalidate redis id)
      (redis-del redis (cache-key id)))))
```

## Step 3: Input validation

Validate request bodies before they reach the database. Return a list of
error messages (empty means valid).

`lib/bookshelf/validate.sld`:

```scheme
(define-library (bookshelf validate)
  (export validate-book)
  (import (scheme base))
  (begin

    (define (validate-book body)
      (let ((errors '()))
        (when (not (assoc "title" body))
          (set! errors (cons "title is required" errors)))
        (when (and (assoc "title" body)
                   (string=? (cdr (assoc "title" body)) ""))
          (set! errors (cons "title must not be empty" errors)))
        (when (not (assoc "author" body))
          (set! errors (cons "author is required" errors)))
        (when (and (assoc "year" body)
                   (not (number? (cdr (assoc "year" body)))))
          (set! errors (cons "year must be a number" errors)))
        (reverse errors)))))
```

## Step 4: Route handlers

Wire everything together. Each handler gets a database connection, a Redis
connection, and the request.

`lib/bookshelf/handlers.sld`:

```scheme
(define-library (bookshelf handlers)
  (export make-app)
  (import (scheme base)
          (kaappi web)
          (kaappi json)
          (kaappi log)
          (bookshelf db)
          (bookshelf cache)
          (bookshelf validate))
  (begin

    (define (book-vec->alist v)
      `(("id"     . ,(vector-ref v 0))
        ("title"  . ,(vector-ref v 1))
        ("author" . ,(vector-ref v 2))
        ("year"   . ,(vector-ref v 3))))

    (define (make-app db redis)

      (routes

        ;; List all books
        (GET "/books"
          (lambda (req params)
            (log-info "list books")
            (json-response
              (map book-vec->alist (db-list-books db)))))

        ;; Get one book (with cache)
        (GET "/books/:id"
          (lambda (req params)
            (let* ((id (param/number params "id"))
                   (cached (cache-get redis id)))
              (if cached
                  (begin (log-info "cache hit" `("id" . ,id))
                         (json-response cached))
                  (let ((book (db-get-book db id)))
                    (if book
                        (begin (cache-set redis id book)
                               (log-info "cache miss" `("id" . ,id))
                               (json-response (book-vec->alist book)))
                        (json-response '(("error" . "book not found")) 404)))))))

        ;; Create a book
        (POST "/books"
          (lambda (req params)
            (let* ((body (request-json req))
                   (errors (validate-book body)))
              (if (not (null? errors))
                  (json-response `(("errors" . ,errors)) 400)
                  (let ((book (db-create-book db
                                (cdr (assoc "title" body))
                                (cdr (assoc "author" body))
                                (if (assoc "year" body)
                                    (cdr (assoc "year" body))
                                    #f))))
                    (log-info "created book" `("id" . ,(vector-ref book 0)))
                    (json-response (book-vec->alist book) 201))))))

        ;; Update a book
        (PUT "/books/:id"
          (lambda (req params)
            (let* ((id (param/number params "id"))
                   (body (request-json req))
                   (errors (validate-book body)))
              (if (not (null? errors))
                  (json-response `(("errors" . ,errors)) 400)
                  (let ((book (db-update-book db id
                                (cdr (assoc "title" body))
                                (cdr (assoc "author" body))
                                (if (assoc "year" body)
                                    (cdr (assoc "year" body))
                                    #f))))
                    (if book
                        (begin (cache-invalidate redis id)
                               (json-response (book-vec->alist book)))
                        (json-response '(("error" . "book not found")) 404)))))))

        ;; Delete a book
        (DELETE "/books/:id"
          (lambda (req params)
            (let ((id (param/number params "id")))
              (if (db-delete-book db id)
                  (begin (cache-invalidate redis id)
                         (no-content))
                  (json-response '(("error" . "book not found")) 404)))))

        ;; Health check
        (GET "/health"
          (lambda (req params)
            (json-response '(("status" . "ok")))))))))
```

## Step 5: Application entry point

`app.scm`:

```scheme
(import (scheme base)
        (kaappi web)
        (kaappi pg)
        (kaappi redis)
        (kaappi log)
        (bookshelf db)
        (bookshelf handlers))

(log-set-format! 'json)

(define db (pg-connect "dbname=bookshelf"))
(define redis (redis-connect "127.0.0.1" 6379))

(db-init db)

(log-info "starting server" '("port" . 8080))
(serve
  (wrap (make-app db redis)
    wrap-json-body
    wrap-logging
    (wrap-cors "*")
    wrap-errors)
  8080)
```

## Run it

```bash
cd bookshelf
redis-server --daemonize yes
kaappi app.scm
```

## Try it

```bash
# Create a book
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"title":"SICP","author":"Abelson & Sussman","year":1996}' \
     http://localhost:8080/books | kaappi -e '(import (kaappi json)) (display (json-read))'

# List all books
curl -s http://localhost:8080/books

# Get one book (second request hits cache)
curl -s http://localhost:8080/books/1
curl -s http://localhost:8080/books/1

# Update a book
curl -s -X PUT -H "Content-Type: application/json" \
     -d '{"title":"SICP","author":"Abelson & Sussman","year":1985}' \
     http://localhost:8080/books/1

# Delete a book
curl -s -X DELETE http://localhost:8080/books/1

# Validation error
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"year":"not a number"}' \
     http://localhost:8080/books
```

## What to try next

- Add pagination with `LIMIT`/`OFFSET` and query parameters
- Add authentication middleware (see [custom middleware](../ecosystem/web.md#custom-middleware))
- Switch to `serve-prefork` for multi-process serving
- Add structured logging fields for request tracing
- Write tests with [kaappi-test](../ecosystem/test.md)
