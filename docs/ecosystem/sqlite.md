# kaappi-sqlite — SQLite Client

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

## API

### Connection

```scheme
(sqlite-open path)             ; ":memory:" for in-memory
(sqlite-close conn)
(sqlite-open? conn)
(sqlite-error-message conn)
```

### Convenience

```scheme
(sqlite-exec conn sql params...)     ; returns change count
(sqlite-query conn sql params...)    ; returns list of row vectors
(sqlite-last-insert-id conn)
```

### Cursor (streaming)

```scheme
(sqlite-cursor conn)
(sqlite-execute cur sql params...)
(sqlite-fetchone cur)                ; vector or #f
(sqlite-fetchall cur)
(sqlite-description cur)             ; column names
(sqlite-cursor-close cur)
```

### Resource management

```scheme
(call-with-sqlite path proc)
(call-with-sqlite-transaction conn proc)
```

### Parameters

Use `?` placeholders. Types are preserved:

```scheme
(sqlite-exec db "INSERT INTO t VALUES (?, ?, ?)" 42 3.14 "text")
(sqlite-exec db "INSERT INTO t VALUES (?)" #f)  ; #f = NULL
```

## Type mapping

| SQLite | Scheme |
|--------|--------|
| INTEGER | exact integer |
| REAL | inexact number |
| TEXT | string |
| NULL | `#f` |
| BLOB | string |
