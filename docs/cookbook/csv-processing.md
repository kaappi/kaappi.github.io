# Parse and Generate CSV

This recipe covers reading, processing, and writing CSV files — including
header mode, custom delimiters, and streaming large files.

## Setup

```bash
thottam install kaappi-csv
```

## Read a CSV file

```scheme
(import (scheme base) (scheme file) (kaappi csv))

;; Simple read — rows as lists of strings
(define rows
  (call-with-input-file "data.csv"
    (lambda (port)
      (csv-read port))))

rows
;=> (("name" "age" "city") ("Alice" "30" "Berlin") ("Bob" "25" "Tokyo"))
```

## Read with headers

When the first row is a header, use `'headers #t` to get rows as alists:

```scheme
(define records
  (call-with-input-file "data.csv"
    (lambda (port)
      (csv-read port 'headers #t))))

records
;=> ((("name" . "Alice") ("age" . "30") ("city" . "Berlin"))
;    (("name" . "Bob") ("age" . "25") ("city" . "Tokyo")))

;; Access fields by name
(cdr (assoc "name" (car records)))  ;=> "Alice"
```

## Parse a CSV string

```scheme
(csv-read-string "a,b,c\n1,2,3\n4,5,6")
;=> (("a" "b" "c") ("1" "2" "3") ("4" "5" "6"))

(csv-read-string "name,score\nAlice,95\nBob,87" 'headers #t)
;=> ((("name" . "Alice") ("score" . "95"))
;    (("name" . "Bob") ("score" . "87")))
```

## Filter and transform rows

CSV values are always strings. Convert types as needed:

```scheme
(import (scheme base) (scheme file) (kaappi csv))

(define data
  (call-with-input-file "scores.csv"
    (lambda (port) (csv-read port 'headers #t))))

;; Keep only scores above 90
(define high-scores
  (filter (lambda (row)
            (> (string->number (cdr (assoc "score" row))) 90))
          data))

;; Extract just the names
(map (lambda (row) (cdr (assoc "name" row)))
     high-scores)
```

## Write CSV to a file

```scheme
(define rows
  '(("name" "age" "city")
    ("Alice" "30" "Berlin")
    ("Bob" "25" "Tokyo")))

(call-with-output-file "output.csv"
  (lambda (port)
    (csv-write rows port)))
```

## Write CSV to a string

```scheme
(csv-write-string
  '(("name" "score")
    ("Alice" "95")
    ("Bob" "87")))
;=> "name,score\r\nAlice,95\r\nBob,87\r\n"
```

## Tab-separated values (TSV)

Use `'delimiter #\tab`:

```scheme
(csv-read-string "name\tscore\nAlice\t95" 'delimiter #\tab)
;=> (("name" "score") ("Alice" "95"))

(csv-write-string '(("a" "b") ("1" "2")) 'delimiter #\tab)
;=> "a\tb\r\n1\t2\r\n"
```

## Stream large files with fold

Process rows one at a time without loading the entire file into memory:

```scheme
(import (scheme base) (scheme file) (kaappi csv))

;; Sum the "amount" column without loading all rows
(define total
  (call-with-input-file "transactions.csv"
    (lambda (port)
      (csv-read-row port)  ;; skip header row
      (csv-fold port
        (lambda (row acc)
          (+ acc (string->number (list-ref row 2))))
        0))))

(display total)
(newline)
```

## Handle quoted fields

The parser handles RFC 4180 quoting automatically — fields with commas,
newlines, or quotes are enclosed in double quotes:

```scheme
(csv-read-string "name,bio\nAlice,\"Likes commas, really\"\nBob,\"Line 1\nLine 2\"")
;=> (("name" "bio")
;    ("Alice" "Likes commas, really")
;    ("Bob" "Line 1\nLine 2"))
```

Escaped quotes (`""`) inside quoted fields are also handled:

```scheme
(csv-read-string "val\n\"She said \"\"hello\"\"\"")
;=> (("val") ("She said \"hello\""))
```

## Convert CSV to JSON

Combine kaappi-csv and kaappi-json to convert between formats:

```scheme
(import (scheme base) (scheme file)
        (kaappi csv) (kaappi json))

(define records
  (call-with-input-file "data.csv"
    (lambda (port) (csv-read port 'headers #t))))

(call-with-output-file "data.json"
  (lambda (port)
    (json-write records port)))
```

Since header-mode rows are already alists, they serialize directly to JSON
objects.

## Read one row at a time

For custom parsing logic where fold is too rigid:

```scheme
(call-with-input-file "data.csv"
  (lambda (port)
    (let loop ((row (csv-read-row port)))
      (when row
        (display row) (newline)
        (loop (csv-read-row port))))))
```

`csv-read-row` returns `#f` at end of file.
