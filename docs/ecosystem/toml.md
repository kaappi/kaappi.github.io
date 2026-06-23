# kaappi-toml — TOML Parser

```bash
thottam install kaappi-toml
```

Pure Scheme — no dependencies.

## Quick start

```scheme
(import (kaappi toml))

(define config (toml-read-string "
[server]
host = \"localhost\"
port = 8080

[database]
url = \"sqlite:///app.db\"
"))

(toml-ref* config "server" "port")   ;=> 8080
```

## API

```scheme
(toml-read [port])             ; parse from port
(toml-read-string str)         ; parse from string
(toml-write table [port])      ; serialize to port
(toml-write-string table)      ; serialize to string
(toml-ref table key)           ; lookup key
(toml-ref* table key ...)      ; nested lookup
```

## Type mapping

| TOML | Scheme |
|------|--------|
| String | string |
| Integer | exact integer |
| Float | inexact number |
| Boolean | `#t` / `#f` |
| Array | list |
| Table | alist |
| Datetime | string |

## Supported features

Strings (basic/literal/multiline), integers (dec/hex/oct/bin/underscores), floats (inf/nan), booleans, arrays, tables, array of tables, inline tables, comments, datetimes, unicode escapes.
