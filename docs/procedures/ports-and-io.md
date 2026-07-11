# Ports and I/O

Ports are Scheme's abstraction for I/O streams. Kaappi supports textual
and binary ports backed by files, strings, or bytevectors. Available from
`(scheme base)`, `(scheme read)`, and `(scheme write)`.

---

## Port Operations

### `current-input-port` { #current-input-port }
<!-- index: 0 | Current default input port (stdin) -->

**Syntax:** `(current-input-port)`

Returns the current default input port (an R7RS parameter object). This is
initially the standard input stream. The value can be temporarily changed
with `with-input-from-file` or `parameterize`.

```scheme
kaappi> (port? (current-input-port))
;=> #t
kaappi> (input-port? (current-input-port))
;=> #t
```

**See also:** [`current-output-port`](#current-output-port),
[`with-input-from-file`](#with-input-from-file)

---

### `current-output-port` { #current-output-port }
<!-- index: 0 | Current default output port (stdout) -->

**Syntax:** `(current-output-port)`

Returns the current default output port (an R7RS parameter object). This is
initially the standard output stream. The value can be temporarily changed
with `with-output-to-file` or `parameterize`.

```scheme
kaappi> (port? (current-output-port))
;=> #t
kaappi> (output-port? (current-output-port))
;=> #t
```

**See also:** [`current-input-port`](#current-input-port),
[`current-error-port`](#current-error-port),
[`with-output-to-file`](#with-output-to-file)

---

### `current-error-port` { #current-error-port }
<!-- index: 0 | Current default error port (stderr) -->

**Syntax:** `(current-error-port)`

Returns the current default error port (an R7RS parameter object). This is
initially the standard error stream. The value can be temporarily changed
with `parameterize`. Unlike `current-output-port`, error output is
typically unbuffered so diagnostic messages appear immediately.

```scheme
kaappi> (port? (current-error-port))
;=> #t
kaappi> (output-port? (current-error-port))
;=> #t
```

**See also:** [`current-output-port`](#current-output-port)

---

### `port?` { #port-pred }
<!-- index: 1 | True if argument is a port -->

**Syntax:** `(port? obj)`

Returns `#t` if *obj* is a port (input port, output port, or
input/output port), and `#f` otherwise.

```scheme
kaappi> (port? (current-input-port))
;=> #t
kaappi> (port? (open-input-string "hello"))
;=> #t
kaappi> (port? "not-a-port")
;=> #f
```

**See also:** [`input-port?`](#input-port), [`output-port?`](#output-port)

---

### `input-port?` { #input-port }
<!-- index: 1 | True if port supports input -->

**Syntax:** `(input-port? obj)`

Returns `#t` if *obj* is an input port, and `#f` otherwise.

```scheme
kaappi> (input-port? (current-input-port))
;=> #t
kaappi> (input-port? (open-input-string "hello"))
;=> #t
kaappi> (input-port? (current-output-port))
;=> #f
```

**See also:** [`output-port?`](#output-port), [`port?`](#port-pred)

---

### `output-port?` { #output-port }
<!-- index: 1 | True if port supports output -->

**Syntax:** `(output-port? obj)`

Returns `#t` if *obj* is an output port, and `#f` otherwise.

```scheme
kaappi> (output-port? (current-output-port))
;=> #t
kaappi> (output-port? (open-output-string))
;=> #t
kaappi> (output-port? (current-input-port))
;=> #f
```

**See also:** [`input-port?`](#input-port), [`port?`](#port-pred)

---

### `textual-port?` { #textual-port }
<!-- index: 1 | True if port is textual -->

**Syntax:** `(textual-port? obj)`

Returns `#t` if *obj* is a textual port (one that reads or writes
characters and strings), and `#f` otherwise. Ports opened with
`open-input-file`, `open-output-file`, `open-input-string`, and
`open-output-string` are textual.

```scheme
kaappi> (textual-port? (current-input-port))
;=> #t
kaappi> (textual-port? (open-input-string "hello"))
;=> #t
```

**See also:** [`binary-port?`](#binary-port)

---

### `binary-port?` { #binary-port }
<!-- index: 1 | True if port is binary -->

**Syntax:** `(binary-port? obj)`

Returns `#t` if *obj* is a binary port (one that reads or writes bytes
and bytevectors), and `#f` otherwise. Ports opened with
`open-binary-input-file` and `open-binary-output-file` are binary.

```scheme
kaappi> (binary-port? (current-input-port))
;=> #f
kaappi> (binary-port? (open-binary-input-file "/dev/null"))
;=> #t
```

**See also:** [`textual-port?`](#textual-port)

---

### `input-port-open?` { #input-port-open }
<!-- index: 1 | True if input port is open -->

**Syntax:** `(input-port-open? port)`

Returns `#t` if *port* is an input port that has not been closed, and
`#f` otherwise. After calling `close-port` or `close-input-port`, this
returns `#f`.

```scheme
kaappi> (let ((p (open-input-string "hello")))
         (let ((before (input-port-open? p)))
           (close-port p)
           (list before (input-port-open? p))))
;=> (#t #f)
```

**See also:** [`output-port-open?`](#output-port-open),
[`close-port`](#close-port)

---

### `output-port-open?` { #output-port-open }
<!-- index: 1 | True if output port is open -->

**Syntax:** `(output-port-open? port)`

Returns `#t` if *port* is an output port that has not been closed, and
`#f` otherwise. After calling `close-port` or `close-output-port`, this
returns `#f`.

```scheme
kaappi> (let ((p (open-output-string)))
         (let ((before (output-port-open? p)))
           (close-port p)
           (list before (output-port-open? p))))
;=> (#t #f)
```

**See also:** [`input-port-open?`](#input-port-open),
[`close-port`](#close-port)

---

## File I/O

### `open-input-file` { #open-input-file }
<!-- index: 1 | Open file for textual input -->

**Syntax:** `(open-input-file filename)`

Opens the file named by the string *filename* for reading and returns
a textual input port. It is an error if the file does not exist or
cannot be opened for reading.

```scheme
kaappi> (let ((p (open-input-file "data.txt")))
         (let ((line (read-line p)))
           (close-port p)
           line))
;=> "first line of file"
```

**See also:** [`open-output-file`](#open-output-file),
[`call-with-input-file`](#call-with-input-file),
[`close-port`](#close-port)

---

### `open-output-file` { #open-output-file }
<!-- index: 1 | Open file for textual output -->

**Syntax:** `(open-output-file filename)`

Opens the file named by the string *filename* for writing and returns
a textual output port. If the file already exists, its contents are
truncated. If it does not exist, a new file is created.

```scheme
kaappi> (let ((p (open-output-file "out.txt")))
         (write-string "hello" p)
         (close-port p))
```

**See also:** [`open-input-file`](#open-input-file),
[`call-with-output-file`](#call-with-output-file),
[`close-port`](#close-port)

---

### `open-binary-input-file` { #open-binary-input-file }
<!-- index: 1 | Open file for binary input -->

**Syntax:** `(open-binary-input-file filename)`

Opens the file named by the string *filename* for reading in binary
mode and returns a binary input port. It is an error if the file does
not exist or cannot be opened for reading.

```scheme
kaappi> (let ((p (open-binary-input-file "image.bin")))
         (let ((byte (read-u8 p)))
           (close-port p)
           byte))
;=> 137
```

**See also:** [`open-binary-output-file`](#open-binary-output-file),
[`open-input-file`](#open-input-file)

---

### `open-binary-output-file` { #open-binary-output-file }
<!-- index: 1 | Open file for binary output -->

**Syntax:** `(open-binary-output-file filename)`

Opens the file named by the string *filename* for writing in binary
mode and returns a binary output port. If the file already exists, its
contents are truncated. If it does not exist, a new file is created.

```scheme
kaappi> (let ((p (open-binary-output-file "out.bin")))
         (write-u8 255 p)
         (close-port p))
```

**See also:** [`open-binary-input-file`](#open-binary-input-file),
[`open-output-file`](#open-output-file)

---

### `close-port` { #close-port }
<!-- index: 1 | Close a port -->

**Syntax:** `(close-port port)`

Closes *port*, releasing any associated resources. After closing, I/O
operations on the port will raise an error. If *port* is already closed,
`close-port` has no effect. The return value is unspecified.

```scheme
kaappi> (let ((p (open-input-string "hello")))
         (close-port p)
         (input-port-open? p))
;=> #f
```

**See also:** [`close-input-port`](#close-input-port),
[`close-output-port`](#close-output-port),
[`call-with-port`](#call-with-port)

---

### `close-input-port` { #close-input-port }
<!-- index: 1 | Close an input port -->

**Syntax:** `(close-input-port port)`

Closes the input side of *port*. Equivalent to `close-port` for pure
input ports. For input/output ports, only the input direction is closed.
The return value is unspecified.

```scheme
kaappi> (let ((p (open-input-string "hello")))
         (close-input-port p)
         (input-port-open? p))
;=> #f
```

**See also:** [`close-port`](#close-port),
[`close-output-port`](#close-output-port)

---

### `close-output-port` { #close-output-port }
<!-- index: 1 | Close an output port -->

**Syntax:** `(close-output-port port)`

Closes the output side of *port*. Equivalent to `close-port` for pure
output ports. For input/output ports, only the output direction is
closed. Any buffered output is flushed before closing. The return value
is unspecified.

```scheme
kaappi> (let ((p (open-output-string)))
         (write-string "hello" p)
         (close-output-port p)
         (output-port-open? p))
;=> #f
```

**See also:** [`close-port`](#close-port),
[`close-input-port`](#close-input-port),
[`flush-output-port`](#flush-output-port)

---

### `file-exists?` { #file-exists }
<!-- index: 1 | True if file exists at path -->

**Syntax:** `(file-exists? filename)`

Returns `#t` if the file named by the string *filename* exists, and `#f`
otherwise. Available from `(scheme file)`.

```scheme
kaappi> (file-exists? "/tmp")
;=> #t
kaappi> (file-exists? "/nonexistent")
;=> #f
```

**See also:** [`delete-file`](#delete-file),
[`open-input-file`](#open-input-file)

---

### `delete-file` { #delete-file }
<!-- index: 1 | Delete a file -->

**Syntax:** `(delete-file filename)`

Deletes the file named by the string *filename*. It is an error if the
file does not exist or cannot be deleted. The return value is
unspecified. Available from `(scheme file)`.

```scheme
kaappi> (call-with-output-file "/tmp/test.txt"
         (lambda (p) (write-string "temp" p)))
kaappi> (file-exists? "/tmp/test.txt")
;=> #t
kaappi> (delete-file "/tmp/test.txt")
kaappi> (file-exists? "/tmp/test.txt")
;=> #f
```

**See also:** [`file-exists?`](#file-exists)

---

### `call-with-input-file` { #call-with-input-file }
<!-- index: 2 | Open file, call proc, close file -->

**Syntax:** `(call-with-input-file filename proc)`

Opens the file named by *filename* for reading, passes the resulting
textual input port to *proc*, and returns the value returned by *proc*.
The port is not automatically closed when *proc* returns -- use
`call-with-port` if automatic closing is needed. Available from
`(scheme file)`.

```scheme
kaappi> (call-with-input-file "data.txt"
         (lambda (p) (read-line p)))
;=> "first line of file"
```

**See also:** [`call-with-output-file`](#call-with-output-file),
[`call-with-port`](#call-with-port),
[`with-input-from-file`](#with-input-from-file)

---

### `call-with-output-file` { #call-with-output-file }
<!-- index: 2 | Open file, call proc, close file -->

**Syntax:** `(call-with-output-file filename proc)`

Opens the file named by *filename* for writing, passes the resulting
textual output port to *proc*, and returns the value returned by *proc*.
The port is not automatically closed when *proc* returns. Available from
`(scheme file)`.

```scheme
kaappi> (call-with-output-file "out.txt"
         (lambda (p) (write-string "hello, world" p)))
```

**See also:** [`call-with-input-file`](#call-with-input-file),
[`call-with-port`](#call-with-port),
[`with-output-to-file`](#with-output-to-file)

---

### `call-with-port` { #call-with-port }
<!-- index: 2 | Call proc with port, close port when done -->

**Syntax:** `(call-with-port port proc)`

Calls *proc* with *port* as its argument. When *proc* returns, the port
is closed automatically. The value returned by *proc* is returned. This
ensures the port is always closed, even if *proc* raises an exception.

```scheme
kaappi> (call-with-port (open-input-string "hello")
         (lambda (p) (read-line p)))
;=> "hello"
kaappi> (let ((p (open-input-string "test")))
         (call-with-port p read-line)
         (input-port-open? p))
;=> #f
```

**See also:** [`call-with-input-file`](#call-with-input-file),
[`close-port`](#close-port)

---

### `with-input-from-file` { #with-input-from-file }
<!-- index: 2 | Parameterize current-input-port for proc -->

**Syntax:** `(with-input-from-file filename thunk)`

Opens the file named by *filename* for reading and parameterizes
`current-input-port` to the resulting port for the dynamic extent of the
call to *thunk*. The port is closed when *thunk* returns. Procedures
like `read` and `read-line` that default to `current-input-port` will
read from this file. Available from `(scheme file)`.

```scheme
kaappi> (with-input-from-file "data.txt"
         (lambda () (read-line)))
;=> "first line of file"
```

**See also:** [`with-output-to-file`](#with-output-to-file),
[`current-input-port`](#current-input-port),
[`call-with-input-file`](#call-with-input-file)

---

### `with-output-to-file` { #with-output-to-file }
<!-- index: 2 | Parameterize current-output-port for proc -->

**Syntax:** `(with-output-to-file filename thunk)`

Opens the file named by *filename* for writing and parameterizes
`current-output-port` to the resulting port for the dynamic extent of
the call to *thunk*. The port is closed when *thunk* returns. Procedures
like `display` and `write` that default to `current-output-port` will
write to this file. Available from `(scheme file)`.

```scheme
kaappi> (with-output-to-file "out.txt"
         (lambda () (display "hello, world")))
```

**See also:** [`with-input-from-file`](#with-input-from-file),
[`current-output-port`](#current-output-port),
[`call-with-output-file`](#call-with-output-file)

---

## Textual Input

### `read` { #read }
<!-- index: 0+ | Read a Scheme datum from port -->

**Syntax:** `(read)` | `(read port)`

Reads and returns the next Scheme datum from *port*, which defaults to
`current-input-port`. At end of input, returns the eof object. The datum
is parsed according to Scheme's read syntax -- strings, numbers, lists,
vectors, and so on are all recognized. Available from `(scheme read)`.

```scheme
kaappi> (read (open-input-string "(+ 1 2)"))
;=> (+ 1 2)
kaappi> (read (open-input-string "42"))
;=> 42
kaappi> (read (open-input-string ""))
;=> #<eof>
```

**See also:** [`read-line`](#read-line), [`read-char`](#read-char),
[`eof-object?`](#eof-object-pred)

---

### `read-char` { #read-char }
<!-- index: 0+ | Read one character -->

**Syntax:** `(read-char)` | `(read-char port)`

Reads and returns the next character from *port*, which defaults to
`current-input-port`. At end of input, returns the eof object. The
character is consumed from the port.

```scheme
kaappi> (read-char (open-input-string "hello"))
;=> #\h
kaappi> (read-char (open-input-string ""))
;=> #<eof>
```

**See also:** [`peek-char`](#peek-char), [`read-line`](#read-line),
[`read-string`](#read-string)

---

### `peek-char` { #peek-char }
<!-- index: 0+ | Peek at next character without consuming -->

**Syntax:** `(peek-char)` | `(peek-char port)`

Returns the next character from *port* without consuming it. Successive
calls to `peek-char` without an intervening read return the same
character. At end of input, returns the eof object. The port defaults to
`current-input-port`.

```scheme
kaappi> (let ((p (open-input-string "abc")))
         (let ((c1 (peek-char p))
               (c2 (peek-char p))
               (c3 (read-char p)))
           (list c1 c2 c3)))
;=> (#\a #\a #\a)
```

**See also:** [`read-char`](#read-char), [`char-ready?`](#char-ready)

---

### `read-line` { #read-line }
<!-- index: 0+ | Read a line as a string -->

**Syntax:** `(read-line)` | `(read-line port)`

Reads and returns the next line of text from *port* as a string. The
line terminator (newline or carriage return + newline) is consumed but
not included in the result. At end of input, returns the eof object. The
port defaults to `current-input-port`.

```scheme
kaappi> (read-line (open-input-string "hello\nworld"))
;=> "hello"
kaappi> (let ((p (open-input-string "line1\nline2\n")))
         (list (read-line p) (read-line p) (read-line p)))
;=> ("line1" "line2" #<eof>)
```

**See also:** [`read-char`](#read-char), [`read-string`](#read-string),
[`read`](#read)

---

### `read-string` { #read-string }
<!-- index: 1+ | Read k characters as a string -->

**Syntax:** `(read-string k)` | `(read-string k port)`

Reads and returns a string of at most *k* characters from *port*. If
fewer than *k* characters remain before end of input, the returned
string contains only those characters. At end of input with no
characters read, returns the eof object. The port defaults to
`current-input-port`.

```scheme
kaappi> (read-string 3 (open-input-string "hello"))
;=> "hel"
kaappi> (read-string 10 (open-input-string "hi"))
;=> "hi"
kaappi> (read-string 3 (open-input-string ""))
;=> #<eof>
```

**See also:** [`read-line`](#read-line), [`read-char`](#read-char)

---

### `char-ready?` { #char-ready }
<!-- index: 0+ | True if a character is available to read -->

**Syntax:** `(char-ready?)` | `(char-ready? port)`

Returns `#t` if a character is ready to be read from *port* without
blocking, or if the port is at end of input. Returns `#f` if reading
would block. The port defaults to `current-input-port`. For string
ports, this always returns `#t`.

```scheme
kaappi> (char-ready? (open-input-string "hello"))
;=> #t
kaappi> (char-ready? (open-input-string ""))
;=> #t
```

**See also:** [`peek-char`](#peek-char), [`read-char`](#read-char)

---

## Textual Output

### `display` { #display }
<!-- index: 1+ | Write value in human-readable form -->

**Syntax:** `(display obj)` | `(display obj port)`

Writes *obj* to *port* in human-readable form. Strings are written
without enclosing double quotes and without escaping special characters.
Characters are written as if by `write-char`. Other types are written as
by `write`. The port defaults to `current-output-port`. The return value
is unspecified.

```scheme
kaappi> (display "hello")
hello
kaappi> (display 42)
42
kaappi> (display '(1 2 3))
(1 2 3)
kaappi> (display #\a)
a
```

!!! note "display vs write"
    `display` is for output intended for people -- strings appear without
    quotes. `write` is for output that can be read back by `read` --
    strings appear with quotes. Compare: `(display "hi")` prints `hi`,
    while `(write "hi")` prints `"hi"`.

**See also:** [`write`](#write), [`write-string`](#write-string),
[`newline`](#newline)

---

### `write` { #write }
<!-- index: 1+ | Write value in machine-readable form (with quotes) -->

**Syntax:** `(write obj)` | `(write obj port)`

Writes *obj* to *port* in machine-readable form. The output uses the
same syntax accepted by `read`, so `(read)` applied to the output
reproduces the original value (for types that have a read syntax).
Strings are enclosed in double quotes with special characters escaped.
The port defaults to `current-output-port`. The return value is
unspecified. Available from `(scheme write)`.

```scheme
kaappi> (write "hello")
"hello"
kaappi> (write '(1 "two" #\3))
(1 "two" #\3)
kaappi> (write 42)
42
```

**See also:** [`display`](#display), [`write-shared`](#write-shared),
[`write-simple`](#write-simple), [`read`](#read)

---

### `write-shared` { #write-shared }
<!-- index: 1+ | Write with datum labels for shared structure -->

**Syntax:** `(write-shared obj)` | `(write-shared obj port)`

Like `write`, but detects shared structure and circular references in
*obj*, outputting them with datum labels (`#N=` to define and `#N#` to
reference). This guarantees that the output is finite even for circular
structures and that shared substructure is preserved when read back.
Available from `(scheme write)`.

```scheme
kaappi> (let ((x (list 1 2)))
         (write-shared (list x x)))
(#0=(1 2) #0#)
kaappi> (let ((x (list 1 2 3)))
         (set-cdr! (cddr x) x)
         (write-shared x))
#0=(1 2 3 . #0#)
```

**See also:** [`write`](#write), [`write-simple`](#write-simple)

---

### `write-simple` { #write-simple }
<!-- index: 1+ | Write without datum labels -->

**Syntax:** `(write-simple obj)` | `(write-simple obj port)`

Like `write`, but does not detect or mark shared structure. If *obj*
contains cycles, `write-simple` may loop forever. This is faster than
`write-shared` when you know the data has no cycles. Available from
`(scheme write)`.

```scheme
kaappi> (write-simple '(1 2 3))
(1 2 3)
kaappi> (write-simple "hello")
"hello"
```

**See also:** [`write`](#write), [`write-shared`](#write-shared)

---

### `write-char` { #write-char }
<!-- index: 1+ | Write a single character -->

**Syntax:** `(write-char char)` | `(write-char char port)`

Writes the character *char* to *port*. The port defaults to
`current-output-port`. The return value is unspecified.

```scheme
kaappi> (write-char #\A)
A
kaappi> (write-char #\newline)

```

**See also:** [`write-string`](#write-string), [`display`](#display),
[`read-char`](#read-char)

---

### `write-string` { #write-string }
<!-- index: 1+ | Write a string (or substring) -->

**Syntax:** `(write-string string)` | `(write-string string port)` | `(write-string string port start)` | `(write-string string port start end)`

Writes the characters of *string* from index *start* (inclusive) to
*end* (exclusive) to *port*. The port defaults to `current-output-port`,
*start* defaults to 0, and *end* defaults to the length of the string.
The return value is unspecified.

```scheme
kaappi> (write-string "hello")
hello
kaappi> (write-string "hello world" (current-output-port) 6)
world
kaappi> (write-string "hello world" (current-output-port) 0 5)
hello
```

**See also:** [`write-char`](#write-char), [`display`](#display)

---

### `newline` { #newline }
<!-- index: 0+ | Write a newline character -->

**Syntax:** `(newline)` | `(newline port)`

Writes a newline character to *port*. The port defaults to
`current-output-port`. Equivalent to `(write-char #\newline port)`. The
return value is unspecified.

```scheme
kaappi> (begin (display "hello") (newline) (display "world") (newline))
hello
world
```

**See also:** [`display`](#display), [`write-char`](#write-char)

---

### `flush-output-port` { #flush-output-port }
<!-- index: 0+ | Flush output port buffer -->

**Syntax:** `(flush-output-port)` | `(flush-output-port port)`

Flushes any buffered output for *port* to the underlying file or device.
The port defaults to `current-output-port`. This is useful when you need
output to appear immediately, for example when writing a prompt before
reading input. The return value is unspecified.

```scheme
kaappi> (display "Enter name: ")
kaappi> (flush-output-port)
```

**See also:** [`close-output-port`](#close-output-port),
[`current-output-port`](#current-output-port)

---

## String Ports

### `open-input-string` { #open-input-string }
<!-- index: 1 | Open string as input port -->

**Syntax:** `(open-input-string string)`

Returns a textual input port that reads from *string*. This is useful
for parsing Scheme data from strings or for testing I/O procedures
without creating temporary files.

```scheme
kaappi> (read (open-input-string "(+ 1 2)"))
;=> (+ 1 2)
kaappi> (read-line (open-input-string "hello\nworld"))
;=> "hello"
kaappi> (let ((p (open-input-string "abc")))
         (list (read-char p) (read-char p) (read-char p)))
;=> (#\a #\b #\c)
```

**See also:** [`open-output-string`](#open-output-string),
[`open-input-file`](#open-input-file)

---

### `open-output-string` { #open-output-string }
<!-- index: 0 | Create output port backed by string -->

**Syntax:** `(open-output-string)`

Returns a textual output port that accumulates its output in an internal
buffer. The accumulated string can be retrieved with
`get-output-string`. This is the standard pattern for building strings
incrementally.

```scheme
kaappi> (let ((p (open-output-string)))
         (write-string "hello" p)
         (write-char #\space p)
         (write-string "world" p)
         (get-output-string p))
;=> "hello world"
```

**See also:** [`get-output-string`](#get-output-string),
[`open-input-string`](#open-input-string),
[`open-output-file`](#open-output-file)

---

### `get-output-string` { #get-output-string }
<!-- index: 1 | Get accumulated string from output port -->

**Syntax:** `(get-output-string port)`

Returns a string containing all characters written to *port*, which must
be a string output port created by `open-output-string`. The port
remains open and can continue to accumulate output. Each call returns
the full accumulated string from the beginning.

```scheme
kaappi> (let ((p (open-output-string)))
         (display "hello" p)
         (let ((s1 (get-output-string p)))
           (display " world" p)
           (let ((s2 (get-output-string p)))
             (list s1 s2))))
;=> ("hello" "hello world")
```

**See also:** [`open-output-string`](#open-output-string)

---

### `eof-object?` { #eof-object-pred }
<!-- index: 1 | True if argument is the EOF object -->

**Syntax:** `(eof-object? obj)`

Returns `#t` if *obj* is the end-of-file object, and `#f` otherwise.
The eof object is returned by read procedures when the end of input is
reached. There is exactly one eof object.

```scheme
kaappi> (eof-object? (read (open-input-string "")))
;=> #t
kaappi> (eof-object? (read-char (open-input-string "")))
;=> #t
kaappi> (eof-object? "")
;=> #f
kaappi> (eof-object? #f)
;=> #f
```

**See also:** [`eof-object`](#eof-object), [`read`](#read),
[`read-char`](#read-char)

---

### `eof-object` { #eof-object }
<!-- index: 0 | Return the EOF object -->

**Syntax:** `(eof-object)`

Returns the end-of-file object. This is the same object returned by read
procedures at the end of input. There is exactly one eof object, so it
can be compared with `eq?`.

```scheme
kaappi> (eof-object)
;=> #<eof>
kaappi> (eq? (eof-object) (read (open-input-string "")))
;=> #t
kaappi> (eof-object? (eof-object))
;=> #t
```

**See also:** [`eof-object?`](#eof-object-pred), [`read`](#read)
