# kaappi-yaml — YAML Parser

```bash
thottam install kaappi-yaml
```

Pure Scheme — no dependencies.

## Quick start

```scheme
(import (kaappi yaml))

(define config (yaml-read-string "
server:
  host: localhost
  port: 8080
routes:
  - /
  - /api
"))

(yaml-ref* config "server" "port")   ;=> 8080
(yaml-ref config "routes")           ;=> ("/" "/api")
```

## API

```scheme
(yaml-read [port])             ; parse from port
(yaml-read-string str)         ; parse from string
(yaml-write value [port])      ; serialize to port
(yaml-write-string value)      ; serialize to string
(yaml-ref table key)           ; lookup key
(yaml-ref* table key ...)      ; nested lookup
(yaml-null? value)             ; check for null
```

## Type mapping

| YAML | Scheme |
|------|--------|
| Mapping | alist |
| Sequence | list |
| String | string |
| Integer | exact integer |
| Float | inexact number |
| Boolean | `#t` / `#f` |
| Null | `'null` |

## Supported features

Block and flow styles, nested structures, quoted strings (double/single), comments, scalar type detection, special values (`.inf`, `.nan`, `~`, `null`).
