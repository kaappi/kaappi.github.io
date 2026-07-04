# Characters

Characters represent individual Unicode codepoints. Character literals are
written as `#\a`, `#\space`, `#\newline`, or `#\x1F600` (hex codepoint).
These procedures are available from `(scheme base)` and `(scheme char)`.

---

## Conversion

### `char->integer` { #char-to-integer }
<!-- index: 1 | Unicode codepoint as integer -->

**Syntax:** `(char->integer char)`

Returns the Unicode codepoint of *char* as an exact integer. The result is
always a non-negative fixnum in the range 0 to `#x10FFFF`.

```scheme
kaappi> (char->integer #\a)
;=> 97
kaappi> (char->integer #\space)
;=> 32
kaappi> (char->integer #\x03BB)
;=> 955
```

**See also:** [`integer->char`](#integer-to-char)

---

### `integer->char` { #integer-to-char }
<!-- index: 1 | Character from Unicode codepoint -->

**Syntax:** `(integer->char n)`

Returns the character whose Unicode codepoint is the exact integer *n*. It is
an error if *n* is not an exact integer in the range 0 to `#x10FFFF`.

```scheme
kaappi> (integer->char 97)
;=> #\a
kaappi> (integer->char 955)
;=> #\x03BB
kaappi> (integer->char 32)
;=> #\space
```

**See also:** [`char->integer`](#char-to-integer)

---

## Comparison

All character comparison procedures accept two or more arguments and check
that the relation holds transitively across every consecutive pair. Comparison
is by Unicode codepoint value.

### `char<?` { #char-lt }
<!-- index: 2+ | Character less-than by codepoint -->

**Syntax:** `(char<? char1 char2 ...)`

Returns `#t` if the codepoints of the characters are monotonically increasing
(each strictly less than the next).

```scheme
kaappi> (char<? #\a #\b #\c)
;=> #t
kaappi> (char<? #\a #\a)
;=> #f
```

**See also:** [`char<=?`](#char-le), [`char-ci<?`](#char-ci-lt)

---

### `char<=?` { #char-le }
<!-- index: 2+ | Character less-than-or-equal -->

**Syntax:** `(char<=? char1 char2 ...)`

Returns `#t` if the codepoints of the characters are monotonically
non-decreasing.

```scheme
kaappi> (char<=? #\a #\a #\b)
;=> #t
kaappi> (char<=? #\b #\a)
;=> #f
```

**See also:** [`char<?`](#char-lt), [`char-ci<=?`](#char-ci-le)

---

### `char=?` { #char-eq }
<!-- index: 2+ | Character equality -->

**Syntax:** `(char=? char1 char2 ...)`

Returns `#t` if all characters have the same codepoint.

```scheme
kaappi> (char=? #\a #\a #\a)
;=> #t
kaappi> (char=? #\a #\A)
;=> #f
```

**See also:** [`char-ci=?`](#char-ci-eq)

---

### `char>=?` { #char-ge }
<!-- index: 2+ | Character greater-than-or-equal -->

**Syntax:** `(char>=? char1 char2 ...)`

Returns `#t` if the codepoints of the characters are monotonically
non-increasing.

```scheme
kaappi> (char>=? #\c #\b #\a)
;=> #t
kaappi> (char>=? #\a #\b)
;=> #f
```

**See also:** [`char>?`](#char-gt), [`char-ci>=?`](#char-ci-ge)

---

### `char>?` { #char-gt }
<!-- index: 2+ | Character greater-than -->

**Syntax:** `(char>? char1 char2 ...)`

Returns `#t` if the codepoints of the characters are monotonically decreasing
(each strictly greater than the next).

```scheme
kaappi> (char>? #\c #\b #\a)
;=> #t
kaappi> (char>? #\a #\a)
;=> #f
```

**See also:** [`char>=?`](#char-ge), [`char-ci>?`](#char-ci-gt)

---

## Classification

Classification predicates test Unicode properties, not just ASCII. For
example, `char-alphabetic?` recognizes letters from Latin, Greek, Cyrillic,
CJK, Hangul, Devanagari, Thai, Arabic, Hebrew, and many other scripts.

### `char-alphabetic?` { #char-alphabetic }
<!-- index: 1 | True if Unicode alphabetic -->

**Syntax:** `(char-alphabetic? char)`

Returns `#t` if *char* is a Unicode alphabetic character. This covers letters
across all supported scripts -- Latin, Greek, Cyrillic, Armenian, Georgian,
Cherokee, Hangul, Hiragana, Katakana, CJK ideographs, Devanagari, Thai,
Arabic, Hebrew, and more.

```scheme
kaappi> (char-alphabetic? #\a)
;=> #t
kaappi> (char-alphabetic? #\1)
;=> #f
kaappi> (char-alphabetic? #\x03BB)   ; Greek lambda
;=> #t
```

**See also:** [`char-numeric?`](#char-numeric), [`char-upper-case?`](#char-upper-case), [`char-lower-case?`](#char-lower-case)

---

### `char-numeric?` { #char-numeric }
<!-- index: 1 | True if Unicode numeric -->

**Syntax:** `(char-numeric? char)`

Returns `#t` if *char* is a Unicode numeric digit. This includes ASCII digits
0-9 as well as digits from other scripts (Arabic-Indic, Devanagari, Thai,
Tibetan, fullwidth digits, and many more -- 36 digit ranges are recognized).

```scheme
kaappi> (char-numeric? #\5)
;=> #t
kaappi> (char-numeric? #\a)
;=> #f
kaappi> (char-numeric? #\x0966)   ; Devanagari digit zero
;=> #t
```

**See also:** [`digit-value`](#digit-value), [`char-alphabetic?`](#char-alphabetic)

---

### `char-whitespace?` { #char-whitespace }
<!-- index: 1 | True if Unicode whitespace -->

**Syntax:** `(char-whitespace? char)`

Returns `#t` if *char* is a Unicode whitespace character. This includes ASCII
whitespace (tab, newline, vertical tab, form feed, carriage return, space) and
Unicode whitespace such as no-break space (U+00A0), ogham space mark (U+1680),
en/em spaces (U+2000--U+200A), line separator (U+2028), paragraph separator
(U+2029), narrow no-break space (U+202F), medium mathematical space (U+205F),
and ideographic space (U+3000).

```scheme
kaappi> (char-whitespace? #\space)
;=> #t
kaappi> (char-whitespace? #\newline)
;=> #t
kaappi> (char-whitespace? #\a)
;=> #f
```

**See also:** [`char-alphabetic?`](#char-alphabetic)

---

### `char-upper-case?` { #char-upper-case }
<!-- index: 1 | True if Unicode uppercase -->

**Syntax:** `(char-upper-case? char)`

Returns `#t` if *char* is a Unicode uppercase letter. A character is
considered uppercase if it has a lowercase mapping in the Unicode case tables
or belongs to an additional set of uppercase letters (mathematical symbols,
etc.).

```scheme
kaappi> (char-upper-case? #\A)
;=> #t
kaappi> (char-upper-case? #\a)
;=> #f
kaappi> (char-upper-case? #\x0391)   ; Greek capital Alpha
;=> #t
```

**See also:** [`char-lower-case?`](#char-lower-case), [`char-upcase`](#char-upcase)

---

### `char-lower-case?` { #char-lower-case }
<!-- index: 1 | True if Unicode lowercase -->

**Syntax:** `(char-lower-case? char)`

Returns `#t` if *char* is a Unicode lowercase letter. A character is
considered lowercase if it has an uppercase mapping in the Unicode case tables
or belongs to an additional set of lowercase letters (phonetic extensions,
etc.).

```scheme
kaappi> (char-lower-case? #\a)
;=> #t
kaappi> (char-lower-case? #\A)
;=> #f
kaappi> (char-lower-case? #\x03B1)   ; Greek small alpha
;=> #t
```

**See also:** [`char-upper-case?`](#char-upper-case), [`char-downcase`](#char-downcase)

---

## Case Conversion

### `char-upcase` { #char-upcase }
<!-- index: 1 | Convert to uppercase -->

**Syntax:** `(char-upcase char)`

Returns the uppercase equivalent of *char* using Unicode case mappings. If
*char* has no uppercase mapping, it is returned unchanged. For ASCII
characters, this uses the standard ASCII mapping; for non-ASCII characters, the
Unicode uppercase mapping table is consulted.

```scheme
kaappi> (char-upcase #\a)
;=> #\A
kaappi> (char-upcase #\A)
;=> #\A
kaappi> (char-upcase #\1)
;=> #\1
kaappi> (char-upcase #\x03B1)   ; Greek small alpha
;=> #\x0391                     ; Greek capital Alpha
```

**See also:** [`char-downcase`](#char-downcase), [`char-foldcase`](#char-foldcase), [`string-upcase`](#string-upcase)

---

### `char-downcase` { #char-downcase }
<!-- index: 1 | Convert to lowercase -->

**Syntax:** `(char-downcase char)`

Returns the lowercase equivalent of *char* using Unicode case mappings. If
*char* has no lowercase mapping, it is returned unchanged.

```scheme
kaappi> (char-downcase #\A)
;=> #\a
kaappi> (char-downcase #\a)
;=> #\a
kaappi> (char-downcase #\x0391)   ; Greek capital Alpha
;=> #\x03B1                       ; Greek small alpha
```

**See also:** [`char-upcase`](#char-upcase), [`char-foldcase`](#char-foldcase), [`string-downcase`](#string-downcase)

---

### `char-foldcase` { #char-foldcase }
<!-- index: 1 | Convert to foldcase (for case-insensitive comparison) -->

**Syntax:** `(char-foldcase char)`

Returns the case-folded form of *char*. Case folding is used internally by the
`char-ci` comparison procedures to normalize characters before comparison.
For most characters this is equivalent to `char-downcase`, but certain
characters have special fold mappings. For example, the long s (U+017F) folds
to the ordinary lowercase `s`.

```scheme
kaappi> (char-foldcase #\A)
;=> #\a
kaappi> (char-foldcase #\a)
;=> #\a
kaappi> (char-foldcase #\x017F)   ; Latin small long s
;=> #\s
```

!!! note "Fold vs. downcase"
    `char-foldcase` consults a dedicated Unicode case-folding table and falls
    back to `char-downcase` only when no explicit fold mapping exists. This
    distinction matters for correct case-insensitive comparison of certain
    scripts.

**See also:** [`char-upcase`](#char-upcase), [`char-downcase`](#char-downcase), [`string-foldcase`](#string-foldcase)

---

### `digit-value` { #digit-value }
<!-- index: 1 | Numeric value of digit character, or `#f` -->

**Syntax:** `(digit-value char)`

If *char* is a Unicode decimal digit, returns its numeric value as an exact
integer (0--9). Otherwise returns `#f`. This procedure recognizes digits from
36 different scripts, including ASCII, Arabic-Indic, Devanagari, Bengali,
Gujarati, Gurmukhi, Oriya, Tamil, Telugu, Kannada, Malayalam, Sinhala, Thai,
Lao, Tibetan, Myanmar, Khmer, Mongolian, Limbu, New Tai Lue, Tai Tham,
Balinese, Sundanese, Lepcha, Ol Chiki, Vai, Saurashtra, Kayah Li, Cham,
Meetei Mayek, and fullwidth digits.

```scheme
kaappi> (digit-value #\3)
;=> 3
kaappi> (digit-value #\a)
;=> #f
kaappi> (digit-value #\x0966)   ; Devanagari digit zero
;=> 0
kaappi> (digit-value #\x0E53)   ; Thai digit three
;=> 3
```

**See also:** [`char-numeric?`](#char-numeric)

---

## Case-Insensitive Character Comparisons

These procedures compare characters after applying Unicode case folding via
`char-foldcase`. Like the case-sensitive variants, they accept two or more
arguments and check the relation transitively across every consecutive pair.

### `char-ci<?` { #char-ci-lt }
<!-- index: 2+ | Case-insensitive character less-than -->

**Syntax:** `(char-ci<? char1 char2 ...)`

Returns `#t` if the case-folded codepoints are monotonically increasing.

```scheme
kaappi> (char-ci<? #\a #\B)
;=> #t
kaappi> (char-ci<? #\A #\a)
;=> #f
```

**See also:** [`char<?`](#char-lt), [`char-ci<=?`](#char-ci-le)

---

### `char-ci<=?` { #char-ci-le }
<!-- index: 2+ | Case-insensitive character less-than-or-equal -->

**Syntax:** `(char-ci<=? char1 char2 ...)`

Returns `#t` if the case-folded codepoints are monotonically non-decreasing.

```scheme
kaappi> (char-ci<=? #\A #\a)
;=> #t
kaappi> (char-ci<=? #\b #\A)
;=> #f
```

**See also:** [`char<=?`](#char-le), [`char-ci<?`](#char-ci-lt)

---

### `char-ci=?` { #char-ci-eq }
<!-- index: 2+ | Case-insensitive character equality -->

**Syntax:** `(char-ci=? char1 char2 ...)`

Returns `#t` if all characters are equal after case folding.

```scheme
kaappi> (char-ci=? #\A #\a)
;=> #t
kaappi> (char-ci=? #\a #\b)
;=> #f
kaappi> (char-ci=? #\x017F #\s)   ; long s equals s
;=> #t
```

**See also:** [`char=?`](#char-eq), [`string-ci=?`](#string-ci-eq)

---

### `char-ci>=?` { #char-ci-ge }
<!-- index: 2+ | Case-insensitive character greater-than-or-equal -->

**Syntax:** `(char-ci>=? char1 char2 ...)`

Returns `#t` if the case-folded codepoints are monotonically non-increasing.

```scheme
kaappi> (char-ci>=? #\B #\a)
;=> #t
kaappi> (char-ci>=? #\A #\a)
;=> #t
```

**See also:** [`char>=?`](#char-ge), [`char-ci>?`](#char-ci-gt)

---

### `char-ci>?` { #char-ci-gt }
<!-- index: 2+ | Case-insensitive character greater-than -->

**Syntax:** `(char-ci>? char1 char2 ...)`

Returns `#t` if the case-folded codepoints are monotonically decreasing.

```scheme
kaappi> (char-ci>? #\B #\a)
;=> #t
kaappi> (char-ci>? #\A #\a)
;=> #f
```

**See also:** [`char>?`](#char-gt), [`char-ci>=?`](#char-ci-ge)

---

## Case-Insensitive String Comparisons

These procedures compare strings by case-folding each codepoint with
`char-downcase` before comparing. Comparison proceeds codepoint-by-codepoint
over the UTF-8 encoding. They accept two or more string arguments and check
the relation transitively.

### `string-ci<?` { #string-ci-lt }
<!-- index: 2+ | Case-insensitive string less-than -->

**Syntax:** `(string-ci<? string1 string2 ...)`

Returns `#t` if the case-folded strings are monotonically increasing in
lexicographic order.

```scheme
kaappi> (string-ci<? "apple" "Banana")
;=> #t
kaappi> (string-ci<? "banana" "APPLE")
;=> #f
```

**See also:** [`string-ci<=?`](#string-ci-le), [`char-ci<?`](#char-ci-lt)

---

### `string-ci<=?` { #string-ci-le }
<!-- index: 2+ | Case-insensitive string less-than-or-equal -->

**Syntax:** `(string-ci<=? string1 string2 ...)`

Returns `#t` if the case-folded strings are monotonically non-decreasing in
lexicographic order.

```scheme
kaappi> (string-ci<=? "Hello" "hello")
;=> #t
kaappi> (string-ci<=? "hello" "HELLO" "world")
;=> #t
```

**See also:** [`string-ci<?`](#string-ci-lt), [`string-ci=?`](#string-ci-eq)

---

### `string-ci=?` { #string-ci-eq }
<!-- index: 2+ | Case-insensitive string equality -->

**Syntax:** `(string-ci=? string1 string2 ...)`

Returns `#t` if all strings are equal after case folding each codepoint.

```scheme
kaappi> (string-ci=? "Hello" "HELLO")
;=> #t
kaappi> (string-ci=? "hello" "world")
;=> #f
```

**See also:** [`char-ci=?`](#char-ci-eq), [`string=?`](./strings.md#string-eq)

---

### `string-ci>=?` { #string-ci-ge }
<!-- index: 2+ | Case-insensitive string greater-than-or-equal -->

**Syntax:** `(string-ci>=? string1 string2 ...)`

Returns `#t` if the case-folded strings are monotonically non-increasing in
lexicographic order.

```scheme
kaappi> (string-ci>=? "Banana" "apple")
;=> #t
kaappi> (string-ci>=? "HELLO" "hello")
;=> #t
```

**See also:** [`string-ci>?`](#string-ci-gt), [`string-ci=?`](#string-ci-eq)

---

### `string-ci>?` { #string-ci-gt }
<!-- index: 2+ | Case-insensitive string greater-than -->

**Syntax:** `(string-ci>? string1 string2 ...)`

Returns `#t` if the case-folded strings are monotonically decreasing in
lexicographic order.

```scheme
kaappi> (string-ci>? "banana" "APPLE")
;=> #t
kaappi> (string-ci>? "hello" "HELLO")
;=> #f
```

**See also:** [`string-ci>=?`](#string-ci-ge), [`char-ci>?`](#char-ci-gt)

---

## String Case Conversion

These procedures return newly allocated strings with case mappings applied
codepoint-by-codepoint. They handle Unicode special cases where a single
codepoint may expand into multiple codepoints (e.g., German sharp s).

### `string-upcase` { #string-upcase }
<!-- index: 1 | Convert entire string to uppercase -->

**Syntax:** `(string-upcase string)`

Returns a newly allocated string with every codepoint replaced by its Unicode
uppercase mapping. Handles special expansions: German sharp s (U+00DF) becomes
"SS", Latin ligatures (fb00--fb04) expand to their component letters, and
certain Greek characters expand to multiple codepoints.

```scheme
kaappi> (string-upcase "hello")
;=> "HELLO"
kaappi> (string-upcase "Stra\x00DF;e")   ; sharp s
;=> "STRASSE"
```

!!! note "Expanding case mappings"
    Some characters expand to multiple characters when uppercased. The German
    sharp s (U+00DF) becomes "SS", the Latin small ligature fi (U+FB01) becomes
    "FI", and similar expansions apply to other ligatures. The returned string
    may therefore be longer than the input.

**See also:** [`string-downcase`](#string-downcase), [`string-foldcase`](#string-foldcase), [`char-upcase`](#char-upcase)

---

### `string-downcase` { #string-downcase }
<!-- index: 1 | Convert entire string to lowercase -->

**Syntax:** `(string-downcase string)`

Returns a newly allocated string with every codepoint replaced by its Unicode
lowercase mapping. Implements context-sensitive downcasing for Greek capital
sigma (U+03A3): when sigma appears at the end of a word (preceded by a cased
character and not followed by one), it becomes final sigma (U+03C2) instead
of the regular small sigma (U+03C3). Also handles Turkish dotted capital I
(U+0130), which expands to lowercase i followed by a combining dot above.

```scheme
kaappi> (string-downcase "HELLO")
;=> "hello"
kaappi> (string-downcase "\x03A3;")   ; lone capital Sigma
;=> "\x03C3;"                          ; small sigma
```

!!! note "Greek final sigma"
    The Greek capital sigma is context-sensitive: at the end of a word it
    becomes final sigma, and in other positions it becomes the standard small
    sigma. This follows the Unicode case mapping specification.

**See also:** [`string-upcase`](#string-upcase), [`string-foldcase`](#string-foldcase), [`char-downcase`](#char-downcase)

---

### `string-foldcase` { #string-foldcase }
<!-- index: 1 | Foldcase entire string -->

**Syntax:** `(string-foldcase string)`

Returns a newly allocated string with Unicode case folding applied to every
codepoint. Case folding is similar to lowercasing but uses the full Unicode
`CaseFolding.txt` mappings, which differ from simple lowercasing for certain
characters. This is the operation used internally by the `string-ci`
comparison procedures.

Like `string-upcase` and `string-downcase`, this handles expanding mappings.
For example, German sharp s (U+00DF) folds to "ss", and Latin ligatures fold
to their lowercase component letters. The long s/t ligatures (U+FB05, U+FB06)
fold to "st".

```scheme
kaappi> (string-foldcase "HELLO")
;=> "hello"
kaappi> (string-foldcase "Stra\x00DF;e")
;=> "strasse"
```

!!! note "Foldcase vs. downcase"
    `string-foldcase` and `string-downcase` produce different results for
    certain inputs. Case folding is specifically designed for case-insensitive
    comparison and may map characters differently than simple lowercasing.
    The sharp s is a classic example: `string-downcase` preserves it, while
    `string-foldcase` expands it to "ss".

**See also:** [`string-upcase`](#string-upcase), [`string-downcase`](#string-downcase), [`char-foldcase`](#char-foldcase)
