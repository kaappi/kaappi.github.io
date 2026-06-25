# Strings

Strings in Kaappi are sequences of Unicode characters, internally encoded as
UTF-8. Indexing operations use codepoint positions, not byte offsets. These
procedures are available from `(scheme base)`. For extended string operations,
see [SRFI-13 String Library](./srfi-13.md).

## Performance characteristics

| Operation | Complexity | Notes |
|-----------|:----------:|-------|
| `string-length` | O(n) | Counts Unicode codepoints (not bytes) |
| `string-ref` | O(n) | Walks from the start to the k-th codepoint |
| `string-set!` | O(n) | May need to shift bytes if codepoint size changes |
| `string-append` | O(n+m) | Allocates a new string |
| `string-copy` | O(n) | Full copy |
| `substring` | O(k) | Copies k codepoints |
| `string=?` | O(n) | Byte-level comparison |
| `string->list` | O(n) | Allocates n pairs |

**Key points:**

- String indexing is by codepoint position, not byte offset. This means
  `string-ref` is O(n), not O(1). For performance-sensitive indexed access
  over many positions, convert to a vector of characters first
- String literals are immutable. Use `string-copy` to get a mutable copy
  before calling `string-set!`
- For extensive string manipulation (searching, splitting, trimming), use
  the [SRFI-13](./srfi-13.md) library

---

## Construction

### `string` { #string }

**Syntax:** `(string char ...)`

Returns a newly allocated string composed of the given characters. When called
with no arguments, returns the empty string.

```scheme
kaappi> (string #\a #\b #\c)
;=> "abc"
kaappi> (string)
;=> ""
```

**See also:** [`make-string`](#make-string), [`list->string`](#list-to-string)

---

### `make-string` { #make-string }

**Syntax:** `(make-string k)` | `(make-string k char)`

Returns a newly allocated string of length *k*. If *char* is given, every
position is initialized to *char*; otherwise each position is initialized to
`#\space`. The fill character may be any Unicode codepoint.

```scheme
kaappi> (string-length (make-string 5))
;=> 5
kaappi> (make-string 3 #\x)
;=> "xxx"
```

**See also:** [`string`](#string), [`string-fill!`](#string-fill)

---

## Access and Mutation

### `string-length` { #string-length }

**Syntax:** `(string-length string)`

Returns the number of Unicode codepoints in *string*. O(n) — counts
codepoints, not bytes.

**Errors:** Raises `TypeError` if the argument is not a string.

```scheme
kaappi> (string-length "hello")
;=> 5
kaappi> (string-length "")
;=> 0
```

!!! note "Codepoint counting"
    `string-length` counts Unicode codepoints, not bytes. A string containing
    multi-byte characters will report its codepoint count, which may differ from
    the underlying byte length. For example, `(string-length "hello")` and
    `(string-length "h\x00E9;llo")` both return 5, even though the second string
    uses 6 bytes in UTF-8.

**See also:** [`string-ref`](#string-ref)

---

### `string-ref` { #string-ref }

**Syntax:** `(string-ref string k)`

Returns the character at codepoint index *k* in *string*, using zero-based
indexing. O(k) — walks from the start to position k.

**Errors:** Raises `IndexOutOfBounds` if *k* is out of range. Raises
`TypeError` if *string* is not a string or *k* is not a non-negative
integer.

```scheme
kaappi> (string-ref "hello" 0)
;=> #\h
kaappi> (string-ref "hello" 4)
;=> #\o
```

!!! note "Codepoint indexing"
    Indices refer to Unicode codepoint positions, not byte offsets. In a string
    like `"h\x00E9;llo"`, index 1 returns the e-acute character (U+00E9), and
    index 2 returns `#\l`. Since `string-ref` is O(k), use
    `string->vector` first if you need many indexed accesses.

**See also:** [`string-length`](#string-length), [`string-set!`](#string-set)

---

### `string-set!` { #string-set }

**Syntax:** `(string-set! string k char)`

Stores *char* into position *k* of *string*. The string must be mutable --
strings returned by `string-copy` are mutable, but string literals and strings
returned by `symbol->string` are immutable. Returns void.

When the new character has a different UTF-8 byte width than the character it
replaces, the string's internal buffer is reallocated.

```scheme
kaappi> (let ((s (string-copy "hello")))
         (string-set! s 0 #\H)
         s)
;=> "Hello"
```

**See also:** [`string-ref`](#string-ref), [`string-copy`](#string-copy), [`string-fill!`](#string-fill)

---

### `substring` { #substring }

**Syntax:** `(substring string start end)`

Returns a newly allocated string containing the characters of *string* from
codepoint index *start* (inclusive) to *end* (exclusive). Both *start* and *end*
must be valid codepoint indices with *start* <= *end*.

**Errors:** Raises `IndexOutOfBounds` if *start* or *end* are out of range
or if *start* > *end*.

```scheme
kaappi> (substring "hello world" 0 5)
;=> "hello"
kaappi> (substring "hello world" 6 11)
;=> "world"
kaappi> (substring "abc" 1 2)
;=> "b"
kaappi> (substring "abc" 0 0)
;=> ""
kaappi> (substring "abc" 0 3)
;=> "abc"
```

**See also:** [`string-copy`](#string-copy)

---

## Building

### `string-append` { #string-append }

**Syntax:** `(string-append string ...)`

Returns a newly allocated string whose characters are the concatenation of all
the given strings. When called with no arguments, returns the empty string.
O(n) where n is the total length of all arguments.

**Errors:** Raises `TypeError` if any argument is not a string.

```scheme
kaappi> (string-append "hello" " " "world")
;=> "hello world"
kaappi> (string-append)
;=> ""
kaappi> (string-append "a" "" "b")
;=> "ab"
```

**Common pattern** — building strings from parts:

```scheme
(string-append "Hello, " name "! You have "
               (number->string count) " messages.")
```

**See also:** [`string-copy`](#string-copy)

---

### `string-copy` { #string-copy }

**Syntax:** `(string-copy string)` | `(string-copy string start)` | `(string-copy string start end)`

Returns a newly allocated mutable copy of *string*. When *start* and/or *end*
are given, only the substring from codepoint index *start* (inclusive) to *end*
(exclusive) is copied. If *end* is omitted it defaults to the length of the
string; if *start* is also omitted it defaults to 0.

```scheme
kaappi> (string-copy "hello")
;=> "hello"
kaappi> (string-copy "hello" 1 3)
;=> "el"
```

**See also:** [`substring`](#substring), [`string-copy!`](#string-copy-bang)

---

### `string-copy!` { #string-copy-bang }

**Syntax:** `(string-copy! to at from)` | `(string-copy! to at from start)` | `(string-copy! to at from start end)`

Copies characters from string *from* into the mutable string *to*, starting at
codepoint position *at* in *to*. The optional *start* and *end* arguments
select a substring of *from*. The destination must have enough room for the
copied characters. Overlapping copies (where *to* and *from* are the same
string) are handled correctly. Returns void.

```scheme
kaappi> (let ((s (string-copy "abcde")))
         (string-copy! s 1 "xy")
         s)
;=> "axyде"
kaappi> (let ((s (string-copy "abcde")))
         (string-copy! s 0 "hello" 1 3)
         s)
;=> "elcde"
```

**See also:** [`string-copy`](#string-copy), [`string-fill!`](#string-fill)

---

### `string-fill!` { #string-fill }

**Syntax:** `(string-fill! string char)` | `(string-fill! string char start)` | `(string-fill! string char start end)`

Fills the mutable string *string* with *char* from codepoint index *start*
(inclusive, default 0) to *end* (exclusive, default `(string-length string)`).
Returns void.

```scheme
kaappi> (let ((s (make-string 3 #\a)))
         (string-fill! s #\z)
         s)
;=> "zzz"
```

**See also:** [`make-string`](#make-string), [`string-set!`](#string-set)

---

## Conversion

### `string->list` { #string-to-list }

**Syntax:** `(string->list string)` | `(string->list string start)` | `(string->list string start end)`

Returns a list of the characters in *string*. The optional *start* and *end*
arguments select a substring using codepoint indices.

```scheme
kaappi> (string->list "abc")
;=> (#\a #\b #\c)
kaappi> (string->list "")
;=> ()
```

**See also:** [`list->string`](#list-to-string), [`string->vector`](#string-to-vector)

---

### `list->string` { #list-to-string }

**Syntax:** `(list->string list)`

Returns a newly allocated string formed from the characters in *list*. It is an
error if any element of *list* is not a character.

```scheme
kaappi> (list->string '(#\a #\b #\c))
;=> "abc"
kaappi> (list->string '())
;=> ""
```

**See also:** [`string->list`](#string-to-list), [`string`](#string)

---

### `string->symbol` { #string-to-symbol }

**Syntax:** `(string->symbol string)`

Returns the symbol whose name is *string*. Symbols are interned, so two calls
with `string=?`-equal strings will return the same symbol (in the `eqv?` sense).

```scheme
kaappi> (string->symbol "hello")
;=> hello
kaappi> (symbol? (string->symbol "test"))
;=> #t
```

**See also:** [`symbol->string`](#symbol-to-string)

---

### `symbol->string` { #symbol-to-string }

**Syntax:** `(symbol->string symbol)`

Returns the name of *symbol* as an immutable string. Calling `string-set!` on
the returned string is an error.

```scheme
kaappi> (symbol->string 'hello)
;=> "hello"
```

**See also:** [`string->symbol`](#string-to-symbol)

---

### `string->utf8` { #string-to-utf8 }

**Syntax:** `(string->utf8 string)`

Returns a bytevector containing the UTF-8 encoding of *string*.

!!! note "Bytevector support"
    Bytevector support in Kaappi is currently limited. This procedure may raise
    an error until full bytevector support is available.

**See also:** [`utf8->string`](#utf8-to-string)

---

### `utf8->string` { #utf8-to-string }

**Syntax:** `(utf8->string bytevector)`

Decodes the UTF-8 encoded *bytevector* and returns the corresponding string.

!!! note "Bytevector support"
    Bytevector support in Kaappi is currently limited. This procedure may raise
    an error until full bytevector support is available.

**See also:** [`string->utf8`](#string-to-utf8)

---

### `string->vector` { #string-to-vector }

**Syntax:** `(string->vector string)` | `(string->vector string start)` | `(string->vector string start end)`

Returns a vector of the characters in *string*. The optional *start* and *end*
arguments select a substring using codepoint indices.

```scheme
kaappi> (string->vector "abc")
;=> #(#\a #\b #\c)
kaappi> (vector-length (string->vector "hello"))
;=> 5
```

**See also:** [`string->list`](#string-to-list)

---

### `string->number` { #string-to-number }

**Syntax:** `(string->number string)` | `(string->number string radix)`

Parses *string* as a number and returns the corresponding numeric value, or
`#f` if the string does not represent a valid number. The optional *radix*
argument (an integer between 2 and 36, default 10) specifies the numeric base.

Recognizes integers, floating-point numbers, rationals (e.g. `"3/4"`), and the
special values `"+inf.0"`, `"-inf.0"`, `"+nan.0"`, and `"-nan.0"`.

```scheme
kaappi> (string->number "42")
;=> 42
kaappi> (string->number "3.14")
;=> 3.14
kaappi> (string->number "ff" 16)
;=> 255
kaappi> (string->number "bad")
;=> #f
```

**See also:** [`number->string`](#number-to-string)

---

### `number->string` { #number-to-string }

**Syntax:** `(number->string z)` | `(number->string z radix)`

Returns a string representation of the number *z*. The optional *radix*
argument (an integer between 2 and 36, default 10) specifies the output base.
Supports fixnums, bignums, rationals, flonums, and complex numbers.

```scheme
kaappi> (number->string 42)
;=> "42"
kaappi> (number->string -7)
;=> "-7"
kaappi> (number->string 255 16)
;=> "ff"
kaappi> (number->string 3.14)
;=> "3.14"
```

**See also:** [`string->number`](#string-to-number)

---

## Iteration

### `string-for-each` { #string-for-each }

**Syntax:** `(string-for-each proc string1 string2 ...)`

Applies *proc* element-wise to the characters of the given strings, in order
from the first character to the last, for its side effects. When multiple
strings are provided, *proc* receives one character from each string per call.
Iteration stops at the length of the shortest string. Returns void.

```scheme
kaappi> (let ((count 0))
         (string-for-each (lambda (c) (set! count (+ count 1)))
                          "hello")
         count)
;=> 5
```

**See also:** [`string-map`](#string-map)

---

### `string-map` { #string-map }

**Syntax:** `(string-map proc string1 string2 ...)`

Applies *proc* element-wise to the characters of the given strings, collecting
the resulting characters into a new string. *proc* must return a character.
When multiple strings are provided, *proc* receives one character from each
string per call. The result has the length of the shortest input string.

```scheme
kaappi> (string-map char-upcase "hello")
;=> "HELLO"
kaappi> (string-map (lambda (c) (integer->char (+ 1 (char->integer c))))
                    "abc")
;=> "bcd"
```

**See also:** [`string-for-each`](#string-for-each)

---

## Comparison

String comparisons are lexicographic, comparing strings by their Unicode
codepoint values from left to right. All comparison procedures accept two or
more arguments and verify that the ordering holds for every consecutive pair.

### `string<?` { #string-lt }

**Syntax:** `(string<? string1 string2 string3 ...)`

Returns `#t` if the strings are monotonically increasing in lexicographic order.

```scheme
kaappi> (string<? "abc" "abd")
;=> #t
kaappi> (string<? "abd" "abc")
;=> #f
kaappi> (string<? "a" "b" "c")
;=> #t
```

**See also:** [`string<=?`](#string-le), [`string=?`](#string-eq)

---

### `string<=?` { #string-le }

**Syntax:** `(string<=? string1 string2 string3 ...)`

Returns `#t` if the strings are monotonically non-decreasing in lexicographic
order.

```scheme
kaappi> (string<=? "abc" "abc")
;=> #t
kaappi> (string<=? "abc" "abd")
;=> #t
kaappi> (string<=? "abd" "abc")
;=> #f
```

**See also:** [`string<?`](#string-lt), [`string=?`](#string-eq)

---

### `string=?` { #string-eq }

**Syntax:** `(string=? string1 string2 string3 ...)`

Returns `#t` if all strings are equal (contain the same sequence of
characters).

```scheme
kaappi> (string=? "abc" "abc")
;=> #t
kaappi> (string=? "abc" "abd")
;=> #f
```

**See also:** [`string<?`](#string-lt), [`string>?`](#string-gt)

---

### `string>=?` { #string-ge }

**Syntax:** `(string>=? string1 string2 string3 ...)`

Returns `#t` if the strings are monotonically non-increasing in lexicographic
order.

```scheme
kaappi> (string>=? "abc" "abc")
;=> #t
kaappi> (string>=? "abd" "abc")
;=> #t
kaappi> (string>=? "abc" "abd")
;=> #f
```

**See also:** [`string>?`](#string-gt), [`string=?`](#string-eq)

---

### `string>?` { #string-gt }

**Syntax:** `(string>? string1 string2 string3 ...)`

Returns `#t` if the strings are monotonically decreasing in lexicographic
order.

```scheme
kaappi> (string>? "abd" "abc")
;=> #t
kaappi> (string>? "abc" "abd")
;=> #f
kaappi> (string>? "c" "b" "a")
;=> #t
```

**See also:** [`string>=?`](#string-ge), [`string=?`](#string-eq)

---
