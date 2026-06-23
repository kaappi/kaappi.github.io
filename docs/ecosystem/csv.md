# kaappi-csv — CSV Parser

```bash
thottam install kaappi-csv
```

Pure Scheme — no dependencies. RFC 4180 compliant.

## Quick start

```scheme
(import (kaappi csv))

;; With headers — rows become alists
(csv-read-string "name,age\nAlice,30\nBob,25" 'headers #t)
;=> ((("name" . "Alice") ("age" . "30"))
;    (("name" . "Bob") ("age" . "25")))

;; Without headers — rows are lists
(csv-read-string "a,b,c\n1,2,3")
;=> (("a" "b" "c") ("1" "2" "3"))
```

## API

### Reading

```scheme
(csv-read port [options...])
(csv-read-string str [options...])
(csv-read-row port [delimiter])       ; single row, #f at EOF
```

Options: `'delimiter char`, `'headers #t`

### Writing

```scheme
(csv-write rows port [options...])
(csv-write-string rows [options...])
```

### Streaming

```scheme
(csv-fold port proc init [options...])
```

## Features

Quoted fields, embedded commas/newlines, escaped quotes, custom delimiters (tab, semicolon), header mode (rows as alists), streaming fold.
