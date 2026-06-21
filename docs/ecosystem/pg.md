# PostgreSQL

`(kaappi pg)` — PostgreSQL client inspired by Python's DB-API 2.0 (PEP 249).

```bash
thottam install kaappi-pg
```

Requires PostgreSQL client libraries (`libpq`) and `pg_config` on PATH.

## Quick start

```scheme
(import (kaappi pg))

(define conn (pg-connect "host=localhost dbname=myapp"))

;; Query with cursor
(let ((cur (pg-cursor conn)))
  (pg-execute cur "SELECT name, age FROM users WHERE age > $1" 25)
  (pg-fetchall cur))
;=> (#("Alice" 30) #("Bob" 35))

(pg-close conn)
```

## Connection

```scheme
(pg-connect conninfo)                           ; libpq connection string
(pg-close conn)                                 ; close connection
(pg-connected? conn)                            ; check if open
(pg-error-message conn)                         ; last error message
```

Connection strings use [libpq format](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING):

```scheme
(pg-connect "host=localhost port=5432 dbname=myapp user=me password=secret")
```

## Cursors

Cursors hold query results and provide row-by-row access:

```scheme
(define cur (pg-cursor conn))

(pg-execute cur "SELECT * FROM users")

(pg-fetchone cur)      ;=> #("Alice" 30) or #f at end
(pg-fetchall cur)      ;=> list of row vectors
(pg-fetchmany cur 10)  ;=> up to 10 rows
(pg-description cur)   ;=> (("name" 25) ("age" 23))  — (name oid) pairs
(pg-rowcount cur)      ;=> number of rows

(pg-cursor-close cur)  ;=> free result resources
```

## Parameterized queries

Use `$1`, `$2`, etc. for parameters (PostgreSQL native format):

```scheme
(pg-execute cur "SELECT * FROM users WHERE name = $1 AND age > $2" "Alice" 25)
(pg-execute cur "INSERT INTO users (name, age) VALUES ($1, $2)" "Bob" 30)
```

Parameters are automatically converted:

| Scheme value | PostgreSQL |
|-------------|-----------|
| string | text |
| number | text representation |
| `#t` | boolean true |
| `#f` | NULL |

## Convenience shortcuts

```scheme
;; Execute + fetchall in one call
(pg-query conn "SELECT * FROM users WHERE age > $1" 25)
;=> (#("Alice" 30) #("Bob" 35))

;; Execute non-SELECT, returns row count
(pg-exec conn "DELETE FROM sessions WHERE expired < now()")
;=> 42
```

## Transactions

```scheme
;; Manual
(pg-exec conn "BEGIN")
(pg-exec conn "INSERT INTO ...")
(pg-commit conn)      ; or (pg-rollback conn)

;; Automatic — commits on success, rolls back on error
(call-with-pg-transaction conn
  (lambda ()
    (pg-exec conn "UPDATE accounts SET balance = balance - 100 WHERE id = $1" 1)
    (pg-exec conn "UPDATE accounts SET balance = balance + 100 WHERE id = $1" 2)))
```

## Auto-close connection

```scheme
(call-with-pg-connection "dbname=myapp"
  (lambda (conn)
    (pg-query conn "SELECT count(*) FROM users")))
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

## Full API reference

### Connection

| Procedure | Description |
|-----------|-------------|
| `(pg-connect conninfo)` | Connect to PostgreSQL |
| `(pg-close conn)` | Close connection |
| `(pg-connected? conn)` | Check if connected |
| `(pg-commit conn)` | Commit transaction |
| `(pg-rollback conn)` | Rollback transaction |
| `(call-with-pg-connection conninfo proc)` | Auto-closing connection |
| `(call-with-pg-transaction conn proc)` | Auto-commit/rollback |

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

### Convenience

| Procedure | Description |
|-----------|-------------|
| `(pg-query conn sql arg ...)` | Execute + fetchall |
| `(pg-exec conn sql arg ...)` | Execute non-SELECT, returns rowcount |
