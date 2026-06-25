# CSV

`(kaappi csv)` — CSV parser and writer. Pure Scheme, no build step.

```bash
thottam install kaappi-csv
```

RFC 4180 compliant — handles quoted fields, embedded commas, embedded
newlines, and escaped quotes.

## Quick start

```scheme
(import (kaappi csv))

;; With headers — rows become alists
(csv-read-string "name,age\nAlice,30\nBob,25" 'headers #t)
;=> ((("name" . "Alice") ("age" . "30"))
;    (("name" . "Bob") ("age" . "25")))

;; Without headers — rows are lists of strings
(csv-read-string "a,b,c\n1,2,3")
;=> (("a" "b" "c") ("1" "2" "3"))
```

## Reading CSV

### From a file

```scheme
(import (scheme base) (scheme file) (kaappi csv))

(define rows
  (call-with-input-file "data.csv"
    (lambda (port) (csv-read port))))
```

### From a string

```scheme
(csv-read-string "a,b,c\n1,2,3\n4,5,6")
;=> (("a" "b" "c") ("1" "2" "3") ("4" "5" "6"))
```

### With headers

When the first row contains column names, use `'headers #t` to get rows as
alists:

```scheme
(csv-read-string "name,age\nAlice,30\nBob,25" 'headers #t)
;=> ((("name" . "Alice") ("age" . "30"))
;    (("name" . "Bob") ("age" . "25")))

;; Access fields by name
(cdr (assoc "name" (car records)))  ;=> "Alice"
```

### Custom delimiters

Tab-separated, semicolon-separated, or any character:

```scheme
(csv-read-string "name\tscore\nAlice\t95" 'delimiter #\tab)
;=> (("name" "score") ("Alice" "95"))

(csv-read-string "a;b;c\n1;2;3" 'delimiter #\;)
;=> (("a" "b" "c") ("1" "2" "3"))
```

### One row at a time

```scheme
(call-with-input-file "data.csv"
  (lambda (port)
    (let loop ((row (csv-read-row port)))
      (when row
        (display row) (newline)
        (loop (csv-read-row port))))))
```

`csv-read-row` returns `#f` at end of file.

## Writing CSV

### To a file

```scheme
(call-with-output-file "output.csv"
  (lambda (port)
    (csv-write '(("name" "age") ("Alice" "30") ("Bob" "25")) port)))
```

### To a string

```scheme
(csv-write-string '(("name" "score") ("Alice" "95") ("Bob" "87")))
;=> "name,score\r\nAlice,95\r\nBob,87\r\n"
```

### Write a single row

```scheme
(csv-write-row '("Alice" "30" "Berlin") port)
```

### Custom delimiter in output

```scheme
(csv-write-string '(("a" "b") ("1" "2")) 'delimiter #\tab)
;=> "a\tb\r\n1\t2\r\n"
```

### Type coercion in output

Values are converted to strings automatically:

| Scheme type | Output |
|-------------|--------|
| string | as-is |
| number | decimal representation |
| boolean | `"true"` / `"false"` |
| `#f` | empty field |
| other | `display` representation |

## Streaming with fold

Process rows one at a time without loading the entire file into memory:

```scheme
;; Sum the third column
(define total
  (call-with-input-file "transactions.csv"
    (lambda (port)
      (csv-read-row port)  ;; skip header
      (csv-fold port
        (lambda (row acc)
          (+ acc (string->number (list-ref row 2))))
        0))))
```

`csv-fold` also supports options:

```scheme
(csv-fold port proc init 'delimiter #\tab 'headers #t)
```

With `'headers #t`, the first row is read as headers and each row passed to
`proc` is an alist.

## Quoted fields

The parser handles RFC 4180 quoting automatically:

```scheme
;; Fields with commas
(csv-read-string "name,bio\nAlice,\"Likes commas, really\"")
;=> (("name" "bio") ("Alice" "Likes commas, really"))

;; Fields with newlines
(csv-read-string "name,bio\nAlice,\"Line 1\nLine 2\"")
;=> (("name" "bio") ("Alice" "Line 1\nLine 2"))

;; Escaped quotes (doubled)
(csv-read-string "val\n\"She said \"\"hello\"\"\"")
;=> (("val") ("She said \"hello\""))
```

When writing, fields containing commas, quotes, or newlines are
automatically quoted.

## Common patterns

### Convert types

CSV values are always strings. Convert as needed:

```scheme
(define data
  (csv-read-string "name,score\nAlice,95\nBob,87" 'headers #t))

(define scores
  (map (lambda (row)
         (string->number (cdr (assoc "score" row))))
       data))

scores  ;=> (95 87)
```

### Filter rows

```scheme
(define high-scores
  (filter (lambda (row)
            (> (string->number (cdr (assoc "score" row))) 90))
          data))
```

### CSV to JSON

```scheme
(import (kaappi csv) (kaappi json))

(define records
  (call-with-input-file "data.csv"
    (lambda (port) (csv-read port 'headers #t))))

(call-with-output-file "data.json"
  (lambda (port) (json-write records port)))
```

Header-mode rows are alists, which serialize directly to JSON objects.

## API reference

### Reading

| Procedure | Description |
|-----------|-------------|
| `(csv-read port [opts ...])` | Read CSV from port |
| `(csv-read-string str [opts ...])` | Read CSV from string |
| `(csv-read-row port [delim])` | Single row, `#f` at EOF |

### Writing

| Procedure | Description |
|-----------|-------------|
| `(csv-write rows port [opts ...])` | Write rows to port |
| `(csv-write-string rows [opts ...])` | Write rows to string |
| `(csv-write-row row port [delim])` | Write single row |

### Streaming

| Procedure | Description |
|-----------|-------------|
| `(csv-fold port proc init [opts ...])` | Fold over rows |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `'delimiter char` | `#\,` | Field separator |
| `'headers #t` | `#f` | First row is headers |
