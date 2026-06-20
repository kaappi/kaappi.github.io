# Bytevectors

Bytevectors are fixed-length sequences of bytes (unsigned 8-bit integers).
They are used for binary data and UTF-8 encoding. Available from
`(scheme base)`.

---

## Construction and Access

### `bytevector?` { #bytevector-pred }

**Syntax:** `(bytevector? obj)`

Returns `#t` if *obj* is a bytevector, `#f` otherwise.

```scheme
kaappi> (bytevector? #u8(1 2 3))
;=> #t
kaappi> (bytevector? #(1 2 3))
;=> #f
kaappi> (bytevector? "hello")
;=> #f
```

**See also:** [`bytevector`](#bytevector), [`vector?`](./vectors.md#vector-pred)

---

### `make-bytevector` { #make-bytevector }

**Syntax:** `(make-bytevector k)` | `(make-bytevector k byte)`

Returns a newly allocated bytevector of length *k*. If *byte* is given, every
position is initialized to *byte*; otherwise each position is initialized to 0.
The *byte* argument must be an exact integer in the range 0-255.

```scheme
kaappi> (bytevector-length (make-bytevector 5))
;=> 5
kaappi> (make-bytevector 3 42)
;=> #u8(42 42 42)
kaappi> (make-bytevector 4)
;=> #u8(0 0 0 0)
```

**See also:** [`bytevector`](#bytevector), [`make-vector`](./vectors.md#make-vector)

---

### `bytevector` { #bytevector }

**Syntax:** `(bytevector byte ...)`

Returns a newly allocated bytevector composed of the given byte values. Each
argument must be an exact integer in the range 0-255. When called with no
arguments, returns the empty bytevector.

```scheme
kaappi> (bytevector 0 1 2 3)
;=> #u8(0 1 2 3)
kaappi> (bytevector 72 101 108 108 111)
;=> #u8(72 101 108 108 111)
kaappi> (bytevector)
;=> #u8()
```

**See also:** [`make-bytevector`](#make-bytevector),
[`string->utf8`](#string-to-utf8)

---

### `bytevector-length` { #bytevector-length }

**Syntax:** `(bytevector-length bytevector)`

Returns the number of bytes in *bytevector*.

```scheme
kaappi> (bytevector-length #u8(1 2 3))
;=> 3
kaappi> (bytevector-length #u8())
;=> 0
```

**See also:** [`bytevector-u8-ref`](#bytevector-u8-ref)

---

### `bytevector-u8-ref` { #bytevector-u8-ref }

**Syntax:** `(bytevector-u8-ref bytevector k)`

Returns the byte at index *k* in *bytevector*, using zero-based indexing. The
result is an exact integer in the range 0-255. It is an error if *k* is not a
valid index. This operation is O(1).

```scheme
kaappi> (bytevector-u8-ref #u8(10 20 30) 0)
;=> 10
kaappi> (bytevector-u8-ref #u8(10 20 30) 2)
;=> 30
```

**See also:** [`bytevector-u8-set!`](#bytevector-u8-set),
[`bytevector-length`](#bytevector-length)

---

### `bytevector-u8-set!` { #bytevector-u8-set }

**Syntax:** `(bytevector-u8-set! bytevector k byte)`

Stores *byte* into position *k* of *bytevector*. The *byte* argument must be an
exact integer in the range 0-255. It is an error if *k* is not a valid index.
This operation is O(1). Returns void.

```scheme
kaappi> (let ((bv (bytevector 1 2 3)))
         (bytevector-u8-set! bv 1 99)
         bv)
;=> #u8(1 99 3)
```

**See also:** [`bytevector-u8-ref`](#bytevector-u8-ref),
[`vector-set!`](./vectors.md#vector-set)

---

## Copying

### `bytevector-copy` { #bytevector-copy }

**Syntax:** `(bytevector-copy bytevector)` | `(bytevector-copy bytevector start)` | `(bytevector-copy bytevector start end)`

Returns a newly allocated bytevector containing the bytes of *bytevector* from
index *start* (inclusive, default 0) to *end* (exclusive, default
`(bytevector-length bytevector)`).

```scheme
kaappi> (bytevector-copy #u8(0 1 2 3 4))
;=> #u8(0 1 2 3 4)
kaappi> (bytevector-copy #u8(0 1 2 3 4) 1 4)
;=> #u8(1 2 3)
```

**See also:** [`bytevector-copy!`](#bytevector-copy-mut),
[`bytevector-append`](#bytevector-append)

---

### `bytevector-copy!` { #bytevector-copy-mut }

**Syntax:** `(bytevector-copy! to at from)` | `(bytevector-copy! to at from start)` | `(bytevector-copy! to at from start end)`

Copies bytes from bytevector *from* into bytevector *to*, starting at index *at*
in *to*. The optional *start* and *end* arguments select a subrange of *from*.
The destination must have enough room for the copied bytes. Overlapping ranges
(where *to* and *from* are the same bytevector) are handled correctly. Returns
void.

```scheme
kaappi> (let ((bv (bytevector 1 2 3 4 5)))
         (bytevector-copy! bv 1 #u8(10 20))
         bv)
;=> #u8(1 10 20 4 5)
kaappi> (let ((bv (bytevector 1 2 3 4 5)))
         (bytevector-copy! bv 0 #u8(10 20 30 40 50) 2 4)
         bv)
;=> #u8(30 40 3 4 5)
```

**See also:** [`bytevector-copy`](#bytevector-copy),
[`vector-copy!`](./vectors.md#vector-copy-mut)

---

### `bytevector-append` { #bytevector-append }

**Syntax:** `(bytevector-append bytevector ...)`

Returns a newly allocated bytevector whose bytes are the concatenation of the
given bytevectors. When called with no arguments, returns the empty bytevector.

```scheme
kaappi> (bytevector-append #u8(1 2) #u8(3 4))
;=> #u8(1 2 3 4)
kaappi> (bytevector-append #u8(1) #u8(2) #u8(3))
;=> #u8(1 2 3)
kaappi> (bytevector-append)
;=> #u8()
```

**See also:** [`bytevector-copy`](#bytevector-copy),
[`vector-append`](./vectors.md#vector-append)

---

## UTF-8 Conversion

### `utf8->string` { #utf8-to-string }

**Syntax:** `(utf8->string bytevector)` | `(utf8->string bytevector start)` | `(utf8->string bytevector start end)`

Decodes the UTF-8 encoded bytes in *bytevector* and returns the corresponding
string. The optional *start* and *end* arguments select a subrange of bytes. It
is an error if the selected bytes do not form valid UTF-8.

```scheme
kaappi> (utf8->string #u8(72 101 108 108 111))
;=> "Hello"
kaappi> (utf8->string #u8(72 101 108 108 111) 0 2)
;=> "He"
```

**See also:** [`string->utf8`](#string-to-utf8),
[`string->utf8`](./strings.md#string-to-utf8)

---

### `string->utf8` { #string-to-utf8 }

**Syntax:** `(string->utf8 string)` | `(string->utf8 string start)` | `(string->utf8 string start end)`

Returns a bytevector containing the UTF-8 encoding of *string*. The optional
*start* and *end* arguments select a substring by codepoint indices.

```scheme
kaappi> (string->utf8 "Hello")
;=> #u8(72 101 108 108 111)
kaappi> (string->utf8 "abc" 1 2)
;=> #u8(98)
```

**See also:** [`utf8->string`](#utf8-to-string),
[`utf8->string`](./strings.md#utf8-to-string)

---

## Binary I/O

These procedures operate on binary ports. When no port argument is given,
they default to `(current-input-port)` for input procedures and
`(current-output-port)` for output procedures.

### `read-u8` { #read-u8 }

**Syntax:** `(read-u8)` | `(read-u8 port)`

Reads and returns the next byte from *port* as an exact integer in the range
0-255. If no more bytes are available, returns an eof object.

```scheme
kaappi> (let ((p (open-input-bytevector #u8(65 66 67))))
         (list (read-u8 p) (read-u8 p) (read-u8 p)))
;=> (65 66 67)
kaappi> (let ((p (open-input-bytevector #u8())))
         (eof-object? (read-u8 p)))
;=> #t
```

**See also:** [`peek-u8`](#peek-u8), [`read-char`](./ports-and-io.md#read-char)

---

### `peek-u8` { #peek-u8 }

**Syntax:** `(peek-u8)` | `(peek-u8 port)`

Returns the next byte from *port* without consuming it. Subsequent calls to
`peek-u8` or `read-u8` will see the same byte. If no bytes are available,
returns an eof object.

```scheme
kaappi> (let ((p (open-input-bytevector #u8(65 66))))
         (let ((b (peek-u8 p)))
           (list b (read-u8 p) (read-u8 p))))
;=> (65 65 66)
```

**See also:** [`read-u8`](#read-u8), [`peek-char`](./ports-and-io.md#peek-char)

---

### `write-u8` { #write-u8 }

**Syntax:** `(write-u8 byte)` | `(write-u8 byte port)`

Writes *byte* to *port*. The *byte* argument must be an exact integer in the
range 0-255. Returns void.

```scheme
kaappi> (let ((p (open-output-bytevector)))
         (write-u8 72 p)
         (write-u8 105 p)
         (get-output-bytevector p))
;=> #u8(72 105)
```

**See also:** [`write-bytevector`](#write-bytevector),
[`write-char`](./ports-and-io.md#write-char)

---

### `u8-ready?` { #u8-ready }

**Syntax:** `(u8-ready?)` | `(u8-ready? port)`

Returns `#t` if a byte is available for reading from *port* without blocking, or
if the port is at end of file. Returns `#f` if reading would block.

```scheme
kaappi> (let ((p (open-input-bytevector #u8(1 2 3))))
         (u8-ready? p))
;=> #t
```

**See also:** [`read-u8`](#read-u8),
[`char-ready?`](./ports-and-io.md#char-ready)

---

### `read-bytevector` { #read-bytevector }

**Syntax:** `(read-bytevector k)` | `(read-bytevector k port)`

Reads up to *k* bytes from *port* and returns them as a newly allocated
bytevector. The result may contain fewer than *k* bytes if the end of file is
reached before *k* bytes are available. If no bytes are available before end of
file, returns an eof object.

```scheme
kaappi> (let ((p (open-input-bytevector #u8(10 20 30 40 50))))
         (read-bytevector 3 p))
;=> #u8(10 20 30)
kaappi> (let ((p (open-input-bytevector #u8(10 20))))
         (read-bytevector 5 p))
;=> #u8(10 20)
```

**See also:** [`read-bytevector!`](#read-bytevector-mut),
[`read-string`](./ports-and-io.md#read-string)

---

### `read-bytevector!` { #read-bytevector-mut }

**Syntax:** `(read-bytevector! bytevector)` | `(read-bytevector! bytevector port)` | `(read-bytevector! bytevector port start)` | `(read-bytevector! bytevector port start end)`

Reads bytes from *port* into *bytevector*, starting at index *start* (default 0)
and stopping at *end* (default `(bytevector-length bytevector)`) or end of file.
Returns the number of bytes actually read, or an eof object if no bytes were
available.

```scheme
kaappi> (let ((bv (make-bytevector 5 0))
              (p (open-input-bytevector #u8(10 20 30))))
         (let ((n (read-bytevector! bv p)))
           (list n bv)))
;=> (3 #u8(10 20 30 0 0))
```

**See also:** [`read-bytevector`](#read-bytevector),
[`bytevector-copy!`](#bytevector-copy-mut)

---

### `write-bytevector` { #write-bytevector }

**Syntax:** `(write-bytevector bytevector)` | `(write-bytevector bytevector port)` | `(write-bytevector bytevector port start)` | `(write-bytevector bytevector port start end)`

Writes the bytes of *bytevector* from index *start* (default 0) to *end*
(default `(bytevector-length bytevector)`) to *port*. Returns void.

```scheme
kaappi> (let ((p (open-output-bytevector)))
         (write-bytevector #u8(1 2 3 4 5) p)
         (get-output-bytevector p))
;=> #u8(1 2 3 4 5)
kaappi> (let ((p (open-output-bytevector)))
         (write-bytevector #u8(1 2 3 4 5) p 1 4)
         (get-output-bytevector p))
;=> #u8(2 3 4)
```

**See also:** [`write-u8`](#write-u8),
[`write-string`](./ports-and-io.md#write-string)

---

### `open-input-bytevector` { #open-input-bytevector }

**Syntax:** `(open-input-bytevector bytevector)`

Returns a binary input port that reads bytes from *bytevector*. The port
supports `read-u8`, `peek-u8`, `read-bytevector`, and related procedures.

```scheme
kaappi> (let ((p (open-input-bytevector #u8(10 20 30))))
         (list (read-u8 p) (read-u8 p) (read-u8 p)))
;=> (10 20 30)
```

**See also:** [`open-output-bytevector`](#open-output-bytevector),
[`open-input-string`](./ports-and-io.md#open-input-string)

---

### `open-output-bytevector` { #open-output-bytevector }

**Syntax:** `(open-output-bytevector)`

Returns a binary output port that accumulates bytes written to it. Use
`get-output-bytevector` to retrieve the accumulated data.

```scheme
kaappi> (let ((p (open-output-bytevector)))
         (write-u8 1 p)
         (write-u8 2 p)
         (write-u8 3 p)
         (get-output-bytevector p))
;=> #u8(1 2 3)
```

**See also:** [`get-output-bytevector`](#get-output-bytevector),
[`open-output-string`](./ports-and-io.md#open-output-string)

---

### `get-output-bytevector` { #get-output-bytevector }

**Syntax:** `(get-output-bytevector port)`

Returns a bytevector containing the bytes that have been written to the output
bytevector port *port*. The *port* must have been created by
`open-output-bytevector`.

```scheme
kaappi> (let ((p (open-output-bytevector)))
         (write-bytevector #u8(72 101 108 108 111) p)
         (get-output-bytevector p))
;=> #u8(72 101 108 108 111)
```

!!! note "Accumulator pattern"
    The `open-output-bytevector` / `get-output-bytevector` pair is the standard
    way to build up binary data incrementally. Write bytes with `write-u8` or
    `write-bytevector`, then extract the result.

**See also:** [`open-output-bytevector`](#open-output-bytevector),
[`get-output-string`](./ports-and-io.md#get-output-string)

---
