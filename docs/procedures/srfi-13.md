# SRFI-13 String Library

Extended string operations beyond R7RS base. Import with
`(import (srfi 13))`. For core string procedures, see
[Strings](./strings.md).

---

## Searching

### `string-contains` { #string-contains }
<!-- index: 2+ | Index of substring in string, or `#f` (optional start/end) -->

**Syntax:** `(string-contains string pattern)` | `(string-contains string pattern start)` | `(string-contains string pattern start end)`

Searches *string* for the first occurrence of *pattern* as a substring. Returns
the index of the beginning of the match, or `#f` if *pattern* is not found.
The optional *start* and *end* arguments restrict the search to a substring of
*string*.

```scheme
kaappi> (string-contains "hello world" "world")
;=> 6
kaappi> (string-contains "hello world" "xyz")
;=> #f
kaappi> (string-contains "abcabc" "bc" 3)
;=> 4
```

**See also:** [`string-index`](#string-index),
[`string-prefix?`](#string-prefix)

---

### `string-index` { #string-index }
<!-- index: 2+ | Index of first char satisfying predicate/char-set (optional start/end) -->

**Syntax:** `(string-index string pred/char/char-set)` | `(string-index string pred/char/char-set start)` | `(string-index string pred/char/char-set start end)`

Returns the index of the first character in *string* that satisfies
*pred/char/char-set*. The criterion can be a predicate procedure, a character,
or a char-set. Returns `#f` if no matching character is found. The optional
*start* and *end* arguments restrict the search to a substring.

```scheme
kaappi> (string-index "hello world" char-whitespace?)
;=> 5
kaappi> (string-index "hello" #\l)
;=> 2
kaappi> (string-index "abcde" char-numeric?)
;=> #f
```

**See also:** [`string-index-right`](#string-index-right),
[`string-skip`](#string-skip)

---

### `string-index-right` { #string-index-right }
<!-- index: 2+ | Index of last char satisfying predicate/char-set (optional start/end) -->

**Syntax:** `(string-index-right string pred/char/char-set)` | `(string-index-right string pred/char/char-set start)` | `(string-index-right string pred/char/char-set start end)`

Like [`string-index`](#string-index), but searches from right to left, returning
the index of the last character that satisfies the criterion. Returns `#f` if
no matching character is found.

```scheme
kaappi> (string-index-right "hello world" #\l)
;=> 9
kaappi> (string-index-right "hello" char-upper-case?)
;=> #f
```

**See also:** [`string-index`](#string-index),
[`string-skip-right`](#string-skip-right)

---

### `string-skip` { #string-skip }
<!-- index: 2+ | Index of first char NOT satisfying predicate/char-set (optional start/end) -->

**Syntax:** `(string-skip string pred/char/char-set)` | `(string-skip string pred/char/char-set start)` | `(string-skip string pred/char/char-set start end)`

Returns the index of the first character in *string* that does *not* satisfy
*pred/char/char-set*. This is the complement of [`string-index`](#string-index).
Returns `#f` if every character matches.

```scheme
kaappi> (string-skip "   hello" char-whitespace?)
;=> 3
kaappi> (string-skip "aaabcd" #\a)
;=> 3
```

**See also:** [`string-skip-right`](#string-skip-right),
[`string-index`](#string-index)

---

### `string-skip-right` { #string-skip-right }
<!-- index: 2+ | Index of last char NOT satisfying predicate/char-set (optional start/end) -->

**Syntax:** `(string-skip-right string pred/char/char-set)` | `(string-skip-right string pred/char/char-set start)` | `(string-skip-right string pred/char/char-set start end)`

Like [`string-skip`](#string-skip), but searches from right to left, returning
the index of the last character that does *not* satisfy the criterion.

```scheme
kaappi> (string-skip-right "hello   " char-whitespace?)
;=> 4
kaappi> (string-skip-right "aaa" #\a)
;=> #f
```

**See also:** [`string-skip`](#string-skip),
[`string-index-right`](#string-index-right)

---

### `string-count` { #string-count }
<!-- index: 2+ | Count chars satisfying predicate/char-set (optional start/end) -->

**Syntax:** `(string-count string pred/char/char-set)` | `(string-count string pred/char/char-set start)` | `(string-count string pred/char/char-set start end)`

Returns the number of characters in *string* that satisfy *pred/char/char-set*.
The optional *start* and *end* arguments restrict the count to a substring.

```scheme
kaappi> (string-count "hello world" char-alphabetic?)
;=> 10
kaappi> (string-count "abracadabra" #\a)
;=> 5
kaappi> (string-count "12345" char-numeric?)
;=> 5
```

**See also:** [`string-index`](#string-index),
[`string-every`](#string-every)

---

### `string-prefix?` { #string-prefix }
<!-- index: 2+ | True if first string is a prefix of second (optional start/end) -->

**Syntax:** `(string-prefix? prefix string)` | `(string-prefix? prefix string start)` | `(string-prefix? prefix string start end)`

Returns `#t` if *prefix* is a prefix of *string*. The optional *start* and
*end* arguments restrict the comparison to a substring of *string*.

```scheme
kaappi> (string-prefix? "hel" "hello")
;=> #t
kaappi> (string-prefix? "world" "hello")
;=> #f
kaappi> (string-prefix? "" "anything")
;=> #t
```

**See also:** [`string-suffix?`](#string-suffix),
[`string-contains`](#string-contains)

---

### `string-suffix?` { #string-suffix }
<!-- index: 2+ | True if first string is a suffix of second (optional start/end) -->

**Syntax:** `(string-suffix? suffix string)` | `(string-suffix? suffix string start)` | `(string-suffix? suffix string start end)`

Returns `#t` if *suffix* is a suffix of *string*. The optional *start* and
*end* arguments restrict the comparison to a substring of *string*.

```scheme
kaappi> (string-suffix? "llo" "hello")
;=> #t
kaappi> (string-suffix? "world" "hello")
;=> #f
kaappi> (string-suffix? "" "anything")
;=> #t
```

**See also:** [`string-prefix?`](#string-prefix),
[`string-contains`](#string-contains)

---

## Trimming

### `string-trim` { #string-trim }
<!-- index: 1+ | Remove leading chars matching predicate/char-set (optional start/end) -->

**Syntax:** `(string-trim string)` | `(string-trim string pred/char/char-set)` | `(string-trim string pred/char/char-set start)` | `(string-trim string pred/char/char-set start end)`

Returns *string* with leading characters that satisfy *pred/char/char-set*
removed. When called without a criterion, trims whitespace. The optional
*start* and *end* arguments restrict the operation to a substring.

```scheme
kaappi> (string-trim "  hello  ")
;=> "hello  "
kaappi> (string-trim "xxhello" #\x)
;=> "hello"
```

**See also:** [`string-trim-right`](#string-trim-right),
[`string-trim-both`](#string-trim-both)

---

### `string-trim-right` { #string-trim-right }
<!-- index: 1+ | Remove trailing chars matching predicate/char-set (optional start/end) -->

**Syntax:** `(string-trim-right string)` | `(string-trim-right string pred/char/char-set)` | `(string-trim-right string pred/char/char-set start)` | `(string-trim-right string pred/char/char-set start end)`

Returns *string* with trailing characters that satisfy *pred/char/char-set*
removed. When called without a criterion, trims whitespace.

```scheme
kaappi> (string-trim-right "  hello  ")
;=> "  hello"
kaappi> (string-trim-right "helloxx" #\x)
;=> "hello"
```

**See also:** [`string-trim`](#string-trim),
[`string-trim-both`](#string-trim-both)

---

### `string-trim-both` { #string-trim-both }
<!-- index: 1+ | Remove leading and trailing chars (optional start/end) -->

**Syntax:** `(string-trim-both string)` | `(string-trim-both string pred/char/char-set)` | `(string-trim-both string pred/char/char-set start)` | `(string-trim-both string pred/char/char-set start end)`

Returns *string* with both leading and trailing characters that satisfy
*pred/char/char-set* removed. When called without a criterion, trims
whitespace.

```scheme
kaappi> (string-trim-both "  hello  ")
;=> "hello"
kaappi> (string-trim-both "xxhelloxx" #\x)
;=> "hello"
```

**See also:** [`string-trim`](#string-trim),
[`string-trim-right`](#string-trim-right)

---

## Splitting and Joining

### `string-split` { #string-split }
<!-- index: 2 | Split string by delimiter into list of strings -->

**Syntax:** `(string-split string delimiter)`

Splits *string* at every occurrence of the *delimiter* string. Returns a list
of strings. If the delimiter does not appear, returns a list containing the
original string. Adjacent delimiters produce empty strings in the result.

```scheme
kaappi> (string-split "one,two,three" ",")
;=> ("one" "two" "three")
kaappi> (string-split "hello" ",")
;=> ("hello")
kaappi> (string-split "a::b::c" "::")
;=> ("a" "b" "c")
```

**See also:** [`string-join`](#string-join),
[`string-contains`](#string-contains)

---

### `string-join` { #string-join }
<!-- index: 1+ | Join list of strings with delimiter -->

**Syntax:** `(string-join list)` | `(string-join list delimiter)` | `(string-join list delimiter grammar)`

Joins a list of strings into a single string. The optional *delimiter*
defaults to a single space. The optional *grammar* controls delimiter
placement:

- `'infix` (default) -- delimiter between elements
- `'suffix` -- delimiter after each element
- `'prefix` -- delimiter before each element

```scheme
kaappi> (string-join '("one" "two" "three"))
;=> "one two three"
kaappi> (string-join '("one" "two" "three") ", ")
;=> "one, two, three"
kaappi> (string-join '("usr" "local" "bin") "/" 'prefix)
;=> "/usr/local/bin"
kaappi> (string-join '("a" "b" "c") ";" 'suffix)
;=> "a;b;c;"
```

**See also:** [`string-split`](#string-split),
[`string-concatenate`](#string-concatenate)

---

### `string-concatenate` { #string-concatenate }
<!-- index: 1 | Concatenate a list of strings -->

**Syntax:** `(string-concatenate list)`

Returns the concatenation of all strings in *list*. Equivalent to
`(apply string-append list)` but may be more efficient for large lists.

```scheme
kaappi> (string-concatenate '("hello" " " "world"))
;=> "hello world"
kaappi> (string-concatenate '())
;=> ""
```

**See also:** [`string-join`](#string-join),
[`string-append`](./strings.md#string-append)

---

## Selection

### `string-take` { #string-take }
<!-- index: 2 | First k characters -->

**Syntax:** `(string-take string nchars)`

Returns the first *nchars* characters of *string*. It is an error if *nchars*
is greater than the length of *string*.

```scheme
kaappi> (string-take "hello world" 5)
;=> "hello"
kaappi> (string-take "hello" 0)
;=> ""
```

**See also:** [`string-drop`](#string-drop),
[`string-take-right`](#string-take-right),
[`substring`](./strings.md#substring)

---

### `string-drop` { #string-drop }
<!-- index: 2 | All but first k characters -->

**Syntax:** `(string-drop string nchars)`

Returns *string* with the first *nchars* characters removed. It is an error if
*nchars* is greater than the length of *string*.

```scheme
kaappi> (string-drop "hello world" 6)
;=> "world"
kaappi> (string-drop "hello" 0)
;=> "hello"
```

**See also:** [`string-take`](#string-take),
[`string-drop-right`](#string-drop-right)

---

### `string-take-right` { #string-take-right }
<!-- index: 2 | Last k characters -->

**Syntax:** `(string-take-right string nchars)`

Returns the last *nchars* characters of *string*.

```scheme
kaappi> (string-take-right "hello world" 5)
;=> "world"
kaappi> (string-take-right "hello" 0)
;=> ""
```

**See also:** [`string-drop-right`](#string-drop-right),
[`string-take`](#string-take)

---

### `string-drop-right` { #string-drop-right }
<!-- index: 2 | All but last k characters -->

**Syntax:** `(string-drop-right string nchars)`

Returns *string* with the last *nchars* characters removed.

```scheme
kaappi> (string-drop-right "hello world" 6)
;=> "hello"
kaappi> (string-drop-right "hello" 0)
;=> "hello"
```

**See also:** [`string-take-right`](#string-take-right),
[`string-drop`](#string-drop)

---

## Padding

### `string-pad` { #string-pad }
<!-- index: 2+ | Pad string on the left to given length -->

**Syntax:** `(string-pad string len)` | `(string-pad string len char)` | `(string-pad string len char start)` | `(string-pad string len char start end)`

Returns a string of length *len* by padding *string* on the left with *char*
(default `#\space`). If *string* is longer than *len*, it is truncated on the
left to fit. The optional *start* and *end* arguments select a substring before
padding.

```scheme
kaappi> (string-pad "42" 5)
;=> "   42"
kaappi> (string-pad "42" 5 #\0)
;=> "00042"
kaappi> (string-pad "hello" 3)
;=> "llo"
```

**See also:** [`string-pad-right`](#string-pad-right)

---

### `string-pad-right` { #string-pad-right }
<!-- index: 2+ | Pad string on the right to given length -->

**Syntax:** `(string-pad-right string len)` | `(string-pad-right string len char)` | `(string-pad-right string len char start)` | `(string-pad-right string len char start end)`

Returns a string of length *len* by padding *string* on the right with *char*
(default `#\space`). If *string* is longer than *len*, it is truncated on the
right to fit.

```scheme
kaappi> (string-pad-right "hi" 5)
;=> "hi   "
kaappi> (string-pad-right "hi" 5 #\.)
;=> "hi..."
kaappi> (string-pad-right "hello" 3)
;=> "hel"
```

**See also:** [`string-pad`](#string-pad)

---

## Transformation

### `string-reverse` { #string-reverse }
<!-- index: 1+ | Reverse a string (optional start/end) -->

**Syntax:** `(string-reverse string)` | `(string-reverse string start)` | `(string-reverse string start end)`

Returns a newly allocated string whose characters are the reverse of *string*.
The optional *start* and *end* arguments restrict the reversal to a substring.

```scheme
kaappi> (string-reverse "hello")
;=> "olleh"
kaappi> (string-reverse "abcde" 1 4)
;=> "dcb"
```

**See also:** [`reverse`](./pairs-and-lists.md#reverse)

---

### `string-filter` { #string-filter }
<!-- index: 2+ | Keep chars satisfying predicate/char-set (optional start/end) -->

**Syntax:** `(string-filter pred/char/char-set string)` | `(string-filter pred/char/char-set string start)` | `(string-filter pred/char/char-set string start end)`

Returns a string containing only the characters of *string* that satisfy
*pred/char/char-set*. The optional *start* and *end* arguments restrict the
operation to a substring.

```scheme
kaappi> (string-filter char-alphabetic? "h3l1o w0rld")
;=> "hlorld"
kaappi> (string-filter #\a "abracadabra")
;=> "aaaaa"
```

**See also:** [`string-delete`](#string-delete),
[`string-count`](#string-count)

---

### `string-delete` { #string-delete }
<!-- index: 2+ | Remove chars satisfying predicate/char-set (optional start/end) -->

**Syntax:** `(string-delete pred/char/char-set string)` | `(string-delete pred/char/char-set string start)` | `(string-delete pred/char/char-set string start end)`

Returns a string with all characters of *string* that satisfy *pred/char/char-set*
removed. This is the complement of [`string-filter`](#string-filter).

```scheme
kaappi> (string-delete char-whitespace? "hello world")
;=> "helloworld"
kaappi> (string-delete #\l "hello")
;=> "heo"
```

**See also:** [`string-filter`](#string-filter)

---

### `string-replace` { #string-replace }
<!-- index: 4 | Replace substring by codepoint indices -->

**Syntax:** `(string-replace string1 string2 start end)`

Returns a new string in which the substring of *string1* from codepoint index
*start* (inclusive) to *end* (exclusive) has been replaced with *string2*. The
replacement string may be a different length than the replaced region.

```scheme
kaappi> (string-replace "hello world" "there" 6 11)
;=> "hello there"
kaappi> (string-replace "abcde" "XY" 1 4)
;=> "aXYe"
kaappi> (string-replace "abc" "123" 1 1)
;=> "a123bc"
```

**See also:** [`substring`](./strings.md#substring),
[`string-copy!`](./strings.md#string-copy-bang)

---

### `string-titlecase` { #string-titlecase }
<!-- index: 1+ | Titlecase a string (optional start/end) -->

**Syntax:** `(string-titlecase string)` | `(string-titlecase string start)` | `(string-titlecase string start end)`

Returns a string with the first letter of each word capitalized and the
remaining letters downcased. Word boundaries are determined by transitions
from non-letter to letter characters. The optional *start* and *end* arguments
restrict the operation to a substring.

```scheme
kaappi> (string-titlecase "hello world")
;=> "Hello World"
kaappi> (string-titlecase "one-two-three")
;=> "One-Two-Three"
```

**See also:** [`string-upcase`](./characters.md#string-upcase),
[`string-downcase`](./characters.md#string-downcase)

---

## Predicates

### `string-every` { #string-every }
<!-- index: 2+ | True if predicate/char-set matches every char (optional start/end) -->

**Syntax:** `(string-every pred/char/char-set string)` | `(string-every pred/char/char-set string start)` | `(string-every pred/char/char-set string start end)`

Returns `#t` if *pred/char/char-set* is satisfied by every character in
*string*. Returns `#t` for the empty string. When *pred* is a procedure,
returns the value of the last application, or `#t` if the string is empty.
The optional *start* and *end* arguments restrict the test to a substring.

```scheme
kaappi> (string-every char-alphabetic? "hello")
;=> #t
kaappi> (string-every char-alphabetic? "hello world")
;=> #f
kaappi> (string-every char-numeric? "12345")
;=> #t
kaappi> (string-every char-alphabetic? "")
;=> #t
```

**See also:** [`string-any`](#string-any),
[`string-count`](#string-count)

---

### `string-any` { #string-any }
<!-- index: 2+ | True if predicate/char-set matches any char (optional start/end) -->

**Syntax:** `(string-any pred/char/char-set string)` | `(string-any pred/char/char-set string start)` | `(string-any pred/char/char-set string start end)`

Returns `#t` if *pred/char/char-set* is satisfied by at least one character in
*string*. Returns `#f` for the empty string. When *pred* is a procedure,
returns the value of the first successful application. The optional *start* and
*end* arguments restrict the test to a substring.

```scheme
kaappi> (string-any char-numeric? "hello5")
;=> #t
kaappi> (string-any char-numeric? "hello")
;=> #f
kaappi> (string-any char-upper-case? "Hello")
;=> #t
```

**See also:** [`string-every`](#string-every),
[`string-index`](#string-index)

---

## Constructors

### `string-tabulate` { #string-tabulate }
<!-- index: 2 | Build string from index-to-char procedure -->

**Syntax:** `(string-tabulate proc len)`

Returns a string of length *len* where each character is produced by calling
*proc* with the corresponding index (0 to *len* - 1). *proc* must return a
character.

```scheme
kaappi> (string-tabulate (lambda (i) (integer->char (+ i 65))) 5)
;=> "ABCDE"
kaappi> (string-tabulate (lambda (i) #\x) 3)
;=> "xxx"
```

**See also:** [`make-string`](./strings.md#make-string),
[`list-tabulate`](./srfi-1.md#list-tabulate)

---

### `string-unfold` { #string-unfold }
<!-- index: 4+ | Unfold a string from a seed -->

**Syntax:** `(string-unfold pred mapper successor seed)` | `(string-unfold pred mapper successor seed base)` | `(string-unfold pred mapper successor seed base make-final)`

Builds a string by repeatedly applying *successor* to *seed* until *pred*
returns true. At each step, *mapper* is called on the current seed value and
must return a character that is appended to the result. The optional *base*
string is prepended to the result. The optional *make-final* procedure is
called on the terminal seed value and its result is appended.

```scheme
kaappi> (string-unfold (lambda (i) (= i 5))
                       (lambda (i) (integer->char (+ i 65)))
                       (lambda (i) (+ i 1))
                       0)
;=> "ABCDE"
kaappi> (string-unfold null? car cdr '(#\a #\b #\c))
;=> "abc"
```

**See also:** [`string-unfold-right`](#string-unfold-right),
[`string-tabulate`](#string-tabulate)

---

### `string-unfold-right` { #string-unfold-right }
<!-- index: 4+ | Unfold a string in reverse from a seed -->

**Syntax:** `(string-unfold-right pred mapper successor seed)` | `(string-unfold-right pred mapper successor seed base)` | `(string-unfold-right pred mapper successor seed base make-final)`

Like [`string-unfold`](#string-unfold), but builds the string from right to
left. Characters produced by *mapper* are prepended to the result rather than
appended.

```scheme
kaappi> (string-unfold-right (lambda (i) (= i 5))
                             (lambda (i) (integer->char (+ i 65)))
                             (lambda (i) (+ i 1))
                             0)
;=> "EDCBA"
kaappi> (string-unfold-right null? car cdr '(#\a #\b #\c))
;=> "cba"
```

**See also:** [`string-unfold`](#string-unfold),
[`string-reverse`](#string-reverse)

---
