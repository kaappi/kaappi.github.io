# SQLite

`(kaappi sqlite)` — SQLite database client with cursors and transactions.

```bash
thottam install kaappi-sqlite
```

Requires: `libsqlite3` (macOS: included, Linux: `apt install libsqlite3-dev`)

## Quick start

```scheme
(import (kaappi sqlite))

(call-with-sqlite ":memory:"
  (lambda (db)
    (sqlite-exec db "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    (sqlite-exec db "INSERT INTO users (name) VALUES (?)" "Alice")
    (sqlite-query db "SELECT * FROM users")))
;=> (#(1 "Alice"))
```

## Connection

```scheme
(sqlite-open path)             ;; ":memory:" for in-memory database
(sqlite-close conn)
(sqlite-open? conn)
(sqlite-error-message conn)    ;; last error message string
```

### Auto-closing connection

```scheme
(call-with-sqlite "app.db"
  (lambda (db)
    (sqlite-query db "SELECT count(*) FROM users")))
;; connection is closed automatically when the lambda returns
```

`call-with-sqlite` also accepts an existing open connection — it passes it
through without closing.

## Queries

### Convenience functions

For most use cases, `sqlite-query` and `sqlite-exec` are all you need:

```scheme
;; SELECT — returns list of row vectors
(sqlite-query db "SELECT * FROM users WHERE age > ?" 25)
;=> (#(1 "Alice" 30) #(2 "Bob" 28))

;; INSERT/UPDATE/DELETE — returns number of affected rows
(sqlite-exec db "INSERT INTO users (name, age) VALUES (?, ?)" "Carol" 22)
;=> 1

(sqlite-exec db "DELETE FROM users WHERE age < ?" 25)
;=> 3

;; Last inserted row ID
(sqlite-last-insert-id db)
;=> 4
```

### Parameterized queries

Use `?` placeholders. Types are preserved:

```scheme
(sqlite-exec db "INSERT INTO t VALUES (?, ?, ?, ?)" 42 3.14 "text" #f)
```

| Scheme value | SQLite type |
|-------------|-------------|
| exact integer | INTEGER |
| inexact number | REAL |
| string | TEXT |
| `#f` | NULL |

### Reading results

Rows are returned as vectors. Column values are converted automatically:

| SQLite type | Scheme value |
|-------------|-------------|
| INTEGER | exact integer |
| REAL | inexact number |
| TEXT | string |
| NULL | `#f` |
| BLOB | string |

```scheme
(define rows (sqlite-query db "SELECT id, name, score FROM scores"))
;; rows = (#(1 "Alice" 95.5) #(2 "Bob" 87.0))

(vector-ref (car rows) 0)   ;=> 1 (integer)
(vector-ref (car rows) 1)   ;=> "Alice" (string)
(vector-ref (car rows) 2)   ;=> 95.5 (inexact)
```

## Cursors

For streaming results or fine-grained control:

```scheme
(define cur (sqlite-cursor db))

(sqlite-execute cur "SELECT * FROM large_table")

;; One row at a time
(sqlite-fetchone cur)    ;=> #(1 "Alice") or #f at end

;; All remaining rows
(sqlite-fetchall cur)    ;=> list of vectors

;; Column names
(sqlite-description cur) ;=> (("id") ("name") ("age"))

;; Rows affected by last execute
(sqlite-rowcount cur)    ;=> number

;; Free resources
(sqlite-cursor-close cur)
```

### Streaming large results

Process rows one at a time without loading everything into memory:

```scheme
(define cur (sqlite-cursor db))
(sqlite-execute cur "SELECT * FROM events ORDER BY timestamp")

(let loop ((row (sqlite-fetchone cur)))
  (when row
    (process-event row)
    (loop (sqlite-fetchone cur))))

(sqlite-cursor-close cur)
```

## Transactions

### Automatic transactions

`call-with-sqlite-transaction` commits on success, rolls back on error:

```scheme
(call-with-sqlite-transaction db
  (lambda ()
    (sqlite-exec db "UPDATE accounts SET balance = balance - 100 WHERE id = ?" 1)
    (sqlite-exec db "UPDATE accounts SET balance = balance + 100 WHERE id = ?" 2)))
;; Both updates succeed or both are rolled back
```

If the lambda raises an error, the transaction is rolled back and the error
is re-raised.

### Manual transactions

```scheme
(sqlite-exec db "BEGIN")
(sqlite-exec db "INSERT INTO log (msg) VALUES (?)" "step 1")
(sqlite-exec db "INSERT INTO log (msg) VALUES (?)" "step 2")
(sqlite-exec db "COMMIT")
;; or (sqlite-exec db "ROLLBACK") to cancel
```

## Common patterns

### Create table if not exists

```scheme
(sqlite-exec db "CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  created_at TEXT DEFAULT (datetime('now'))
)")
```

### Upsert

```scheme
(sqlite-exec db "INSERT INTO config (key, value) VALUES (?, ?)
  ON CONFLICT(key) DO UPDATE SET value = excluded.value"
  "theme" "dark")
```

### Count rows

```scheme
(vector-ref (car (sqlite-query db "SELECT count(*) FROM users")) 0)
;=> 42
```

### Check if a row exists

```scheme
(not (null? (sqlite-query db "SELECT 1 FROM users WHERE email = ?" email)))
```

### Batch inserts in a transaction

```scheme
(call-with-sqlite-transaction db
  (lambda ()
    (for-each
      (lambda (user)
        (sqlite-exec db "INSERT INTO users (name) VALUES (?)" user))
      '("Alice" "Bob" "Carol" "Dave"))))
```

Wrapping batch inserts in a transaction is much faster than individual
commits — SQLite commits once instead of once per row.

## API reference

### Connection

| Procedure | Description |
|-----------|-------------|
| `(sqlite-open path)` | Open database |
| `(sqlite-close conn)` | Close connection |
| `(sqlite-open? conn)` | Check if open |
| `(sqlite-error-message conn)` | Last error message |
| `(call-with-sqlite path proc)` | Auto-closing connection |

### Convenience

| Procedure | Description |
|-----------|-------------|
| `(sqlite-exec conn sql param ...)` | Execute, return affected row count |
| `(sqlite-query conn sql param ...)` | Execute, return all rows as vectors |
| `(sqlite-last-insert-id conn)` | Last inserted ROWID |

### Cursor

| Procedure | Description |
|-----------|-------------|
| `(sqlite-cursor conn)` | Create cursor |
| `(sqlite-execute cur sql param ...)` | Execute with parameters |
| `(sqlite-fetchone cur)` | Next row as vector, `#f` at end |
| `(sqlite-fetchall cur)` | All remaining rows |
| `(sqlite-description cur)` | Column names |
| `(sqlite-rowcount cur)` | Rows affected |
| `(sqlite-cursor-close cur)` | Free resources |

### Transactions

| Procedure | Description |
|-----------|-------------|
| `(call-with-sqlite-transaction conn proc)` | Auto-commit/rollback |
