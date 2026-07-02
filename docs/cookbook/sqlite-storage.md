# Store Data in SQLite

This recipe covers local, file-based persistence with
[kaappi-sqlite](../ecosystem/sqlite.md): creating a schema, CRUD
operations, streaming large results, and fast batch inserts.

## Setup

```bash
thottam install kaappi-sqlite
```

Requires `libsqlite3` (included on macOS; `apt install libsqlite3-dev` on
Linux).

## Create a database and schema

`sqlite-open` creates the file if it doesn't exist. `CREATE TABLE IF NOT
EXISTS` makes startup idempotent:

```scheme
(import (scheme base) (kaappi sqlite))

(define db (sqlite-open "notes.db"))

(sqlite-exec db "CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  body TEXT,
  created_at TEXT DEFAULT (datetime('now'))
)")
```

For throwaway work and tests, use `":memory:"` instead of a path.

## Insert and query

Always use `?` placeholders — never build SQL by concatenating input
(see [Security](../guide/security.md#sql-injection-prevention)):

```scheme
(sqlite-exec db "INSERT INTO notes (title, body) VALUES (?, ?)"
  "Shopping" "coffee, filters")
(sqlite-last-insert-id db)   ;=> 1

(sqlite-query db "SELECT id, title FROM notes WHERE title LIKE ?" "S%")
;=> (#(1 "Shopping"))
```

Rows come back as vectors; `NULL` becomes `#f`:

```scheme
(define row (car (sqlite-query db "SELECT id, title, body FROM notes")))
(vector-ref row 0)   ;=> 1
(vector-ref row 1)   ;=> "Shopping"
```

## Wrap it in CRUD helpers

A thin layer of procedures keeps SQL in one place:

```scheme
(define (add-note! db title body)
  (sqlite-exec db "INSERT INTO notes (title, body) VALUES (?, ?)" title body)
  (sqlite-last-insert-id db))

(define (get-note db id)
  (let ((rows (sqlite-query db "SELECT id, title, body FROM notes WHERE id = ?" id)))
    (if (null? rows) #f (car rows))))

(define (update-note! db id title body)
  (sqlite-exec db "UPDATE notes SET title = ?, body = ? WHERE id = ?" title body id))

(define (delete-note! db id)
  (sqlite-exec db "DELETE FROM notes WHERE id = ?" id))

(define id (add-note! db "Ideas" "cookbook recipe"))
(get-note db id)        ;=> #(2 "Ideas" "cookbook recipe")
(delete-note! db id)    ;=> 1
```

## Auto-close the connection

`call-with-sqlite` closes the connection when the procedure returns,
even on error:

```scheme
(call-with-sqlite "notes.db"
  (lambda (db)
    (sqlite-query db "SELECT count(*) FROM notes")))
```

## Batch inserts in a transaction

Wrapping a batch in a transaction is dramatically faster than one commit
per row, and `call-with-sqlite-transaction` rolls everything back if any
insert fails:

```scheme
(call-with-sqlite-transaction db
  (lambda ()
    (for-each
      (lambda (title)
        (sqlite-exec db "INSERT INTO notes (title) VALUES (?)" title))
      '("one" "two" "three" "four"))))
```

## Stream a large table

`sqlite-query` loads all rows into memory. For large results, use a
cursor and fetch one row at a time:

```scheme
(define cur (sqlite-cursor db))
(sqlite-execute cur "SELECT id, title FROM notes ORDER BY created_at")

(let loop ((row (sqlite-fetchone cur)))
  (when row
    (display (vector-ref row 1))
    (newline)
    (loop (sqlite-fetchone cur))))

(sqlite-cursor-close cur)
```

## Use an in-memory database in tests

Tests run against `":memory:"` so they are fast and leave no files
behind:

```scheme
(import (kaappi test) (kaappi sqlite))

(test-group "notes"
  (call-with-sqlite ":memory:"
    (lambda (db)
      (sqlite-exec db "CREATE TABLE notes (id INTEGER PRIMARY KEY, title TEXT)")
      (test-equal "insert returns id" 1
        (begin
          (sqlite-exec db "INSERT INTO notes (title) VALUES (?)" "hello")
          (sqlite-last-insert-id db))))))
```

## Going further

- Full API: [kaappi-sqlite reference](../ecosystem/sqlite.md)
- Client/server database instead: [kaappi-pg](../ecosystem/pg.md)
- Serving stored data over HTTP: [Build a REST API](rest-api.md)
