# PostgreSQL

`(kaappi pg)` — PostgreSQL client with parameterized queries, cursors,
transactions, and automatic type conversion.

```bash
thottam install kaappi-pg
```

Requires PostgreSQL client libraries (`libpq`) and `pg_config` on PATH.

## Quick start

```scheme
(import (kaappi pg))

(define conn (pg-connect "host=localhost dbname=myapp"))

(pg-query conn "SELECT name, age FROM users WHERE age > $1" 25)
;=> (#("Alice" 30) #("Bob" 35))

(pg-close conn)
```

## Connection

```scheme
(pg-connect conninfo)                           ;; libpq connection string
(pg-close conn)                                 ;; close connection
(pg-connected? conn)                            ;; check if open
(pg-error-message conn)                         ;; last error message
```

Connection strings use [libpq format](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING):

```scheme
(pg-connect "host=localhost port=5432 dbname=myapp user=me password=secret")
(pg-connect "dbname=myapp")
```

### Auto-closing connection

```scheme
(call-with-pg-connection "dbname=myapp"
  (lambda (conn)
    (pg-query conn "SELECT count(*) FROM users")))
;; connection is closed automatically
```

## Convenience functions

For most use cases, `pg-query` and `pg-exec` are all you need:

```scheme
;; SELECT — returns list of row vectors
(pg-query conn "SELECT * FROM users WHERE age > $1" 25)
;=> (#("Alice" 30) #("Bob" 35))

;; INSERT/UPDATE/DELETE — returns number of affected rows
(pg-exec conn "DELETE FROM sessions WHERE expired < now()")
;=> 42

(pg-exec conn "INSERT INTO users (name, age) VALUES ($1, $2)" "Carol" 28)
;=> 1
```

## Parameterized queries

Use `$1`, `$2`, etc. for parameters (PostgreSQL native format). This
prevents SQL injection:

```scheme
(pg-query conn "SELECT * FROM users WHERE name = $1 AND age > $2" "Alice" 25)
(pg-exec conn "INSERT INTO users (name, age) VALUES ($1, $2)" "Bob" 30)
```

Parameters are automatically converted:

| Scheme value | PostgreSQL |
|-------------|-----------|
| string | text |
| number | text representation |
| `#t` | boolean true |
| `#f` | NULL |

!!! note "Use $1 parameters, not string interpolation"
    Never build SQL by concatenating user input. Always use `$1`
    parameters — they prevent SQL injection and handle escaping correctly.

## Cursors

Cursors hold query results and provide row-by-row access. Useful for large
result sets:

```scheme
(define cur (pg-cursor conn))

(pg-execute cur "SELECT * FROM large_table")

(pg-fetchone cur)      ;=> #("Alice" 30) or #f at end
(pg-fetchall cur)      ;=> list of remaining row vectors
(pg-fetchmany cur 10)  ;=> up to 10 rows
(pg-description cur)   ;=> (("name" 25) ("age" 23)) — (name oid) pairs
(pg-rowcount cur)      ;=> number of rows

(pg-cursor-close cur)  ;=> free resources
```

### Streaming large results

```scheme
(define cur (pg-cursor conn))
(pg-execute cur "SELECT * FROM events ORDER BY created_at")

(let loop ((row (pg-fetchone cur)))
  (when row
    (process-event row)
    (loop (pg-fetchone cur))))

(pg-cursor-close cur)
```

## Transactions

### Automatic transactions

`call-with-pg-transaction` commits on success, rolls back on error:

```scheme
(call-with-pg-transaction conn
  (lambda ()
    (pg-exec conn "UPDATE accounts SET balance = balance - 100 WHERE id = $1" 1)
    (pg-exec conn "UPDATE accounts SET balance = balance + 100 WHERE id = $1" 2)))
;; Both updates succeed or both are rolled back
```

### Manual transactions

```scheme
(pg-exec conn "BEGIN")
(pg-exec conn "INSERT INTO log (msg) VALUES ($1)" "step 1")
(pg-exec conn "INSERT INTO log (msg) VALUES ($1)" "step 2")
(pg-commit conn)      ;; or (pg-rollback conn) to cancel
```

## Type conversion

Results are automatically converted from PostgreSQL text format:

| PostgreSQL type | Scheme value |
|----------------|-------------|
| boolean | `#t` / `#f` |
| smallint, integer, bigint | exact integer |
| real, double precision | inexact number |
| numeric | number |
| text, varchar | string |
| NULL | `#f` |
| everything else | string |

## Common patterns

### Check if a row exists

```scheme
(not (null? (pg-query conn "SELECT 1 FROM users WHERE email = $1" email)))
```

### Count rows

```scheme
(vector-ref (car (pg-query conn "SELECT count(*) FROM users")) 0)
;=> 42
```

### Insert and return the new row

```scheme
(car (pg-query conn
  "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id, name, email"
  "Alice" "alice@example.com"))
;=> #(1 "Alice" "alice@example.com")
```

### Batch inserts in a transaction

```scheme
(call-with-pg-transaction conn
  (lambda ()
    (for-each
      (lambda (user)
        (pg-exec conn "INSERT INTO users (name) VALUES ($1)" user))
      '("Alice" "Bob" "Carol" "Dave"))))
```

### Upsert

```scheme
(pg-exec conn
  "INSERT INTO config (key, value) VALUES ($1, $2)
   ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value"
  "theme" "dark")
```

### Connection pooling pattern

For long-running servers, keep one connection open:

```scheme
(define db (pg-connect "dbname=myapp"))

;; In request handlers:
(GET "/users"
  (lambda (req params)
    (json-response (pg-query db "SELECT * FROM users"))))
```

For higher concurrency with `serve-prefork`, each worker process gets its
own connection automatically (via `fork()`).

## Full API reference

### Connection

| Procedure | Description |
|-----------|-------------|
| `(pg-connect conninfo)` | Connect to PostgreSQL |
| `(pg-close conn)` | Close connection |
| `(pg-connected? conn)` | Check if connected |
| `(pg-error-message conn)` | Last error message |
| `(pg-commit conn)` | Commit transaction |
| `(pg-rollback conn)` | Rollback transaction |
| `(call-with-pg-connection conninfo proc)` | Auto-closing connection |
| `(call-with-pg-transaction conn proc)` | Auto-commit/rollback |

### Convenience

| Procedure | Description |
|-----------|-------------|
| `(pg-query conn sql arg ...)` | Execute + fetchall |
| `(pg-exec conn sql arg ...)` | Execute non-SELECT, returns rowcount |

### Cursor

| Procedure | Description |
|-----------|-------------|
| `(pg-cursor conn)` | Create cursor |
| `(pg-execute cur sql arg ...)` | Execute with `$1` params |
| `(pg-fetchone cur)` | Next row as vector, `#f` at end |
| `(pg-fetchall cur)` | All remaining rows |
| `(pg-fetchmany cur n)` | Up to N rows |
| `(pg-description cur)` | Column info: `((name oid) ...)` |
| `(pg-rowcount cur)` | Rows affected/returned |
| `(pg-cursor-close cur)` | Free resources |
