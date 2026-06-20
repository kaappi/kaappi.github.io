# Kaappi Scheme Procedure Reference

This document lists all built-in procedures organized by domain. Each procedure
shows its arity (`N` = exactly N arguments, `N+` = N or more arguments) and a
short description. Click any category heading for detailed documentation with
examples.

---

## [Numbers and Arithmetic](numbers.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`+`](numbers.md#plus) | 0+ | Sum of all arguments (0 with no args) |
| [`-`](numbers.md#minus) | 1+ | Negation (1 arg) or subtraction (2+ args) |
| [`*`](numbers.md#star) | 0+ | Product of all arguments (1 with no args) |
| [`/`](numbers.md#slash) | 1+ | Reciprocal (1 arg) or division (2+ args) |
| [`quotient`](numbers.md#quotient) | 2 | Integer division truncated toward zero |
| [`remainder`](numbers.md#remainder) | 2 | Remainder after truncated division |
| [`modulo`](numbers.md#modulo) | 2 | Modulo (sign follows divisor) |
| [`=`](numbers.md#num-equal) | 2+ | Numeric equality |
| [`<`](numbers.md#num-lt) | 2+ | Monotonically increasing |
| [`>`](numbers.md#num-gt) | 2+ | Monotonically decreasing |
| [`<=`](numbers.md#num-le) | 2+ | Monotonically non-decreasing |
| [`>=`](numbers.md#num-ge) | 2+ | Monotonically non-increasing |
| [`zero?`](numbers.md#zero) | 1 | True if argument is zero |
| [`positive?`](numbers.md#positive) | 1 | True if argument is positive |
| [`negative?`](numbers.md#negative) | 1 | True if argument is negative |
| [`abs`](numbers.md#abs) | 1 | Absolute value |
| [`min`](numbers.md#min) | 1+ | Minimum of arguments |
| [`max`](numbers.md#max) | 1+ | Maximum of arguments |
| [`even?`](numbers.md#even) | 1 | True if integer is even |
| [`odd?`](numbers.md#odd) | 1 | True if integer is odd |
| [`gcd`](numbers.md#gcd) | 0+ | Greatest common divisor |
| [`lcm`](numbers.md#lcm) | 0+ | Least common multiple |
| [`floor`](numbers.md#floor) | 1 | Largest integer not greater than argument |
| [`ceiling`](numbers.md#ceiling) | 1 | Smallest integer not less than argument |
| [`truncate`](numbers.md#truncate) | 1 | Integer part, truncated toward zero |
| [`round`](numbers.md#round) | 1 | Round to nearest integer (banker's rounding) |
| [`exact?`](numbers.md#exact-pred) | 1 | True if number is exact |
| [`inexact?`](numbers.md#inexact-pred) | 1 | True if number is inexact |
| [`exact-integer?`](numbers.md#exact-integer) | 1 | True if number is an exact integer |
| [`exact`](numbers.md#exact) | 1 | Convert to exact representation |
| [`inexact`](numbers.md#inexact) | 1 | Convert to inexact representation |
| [`exact->inexact`](numbers.md#exact-to-inexact) | 1 | Alias for `inexact` |
| [`inexact->exact`](numbers.md#inexact-to-exact) | 1 | Alias for `exact` |
| [`expt`](numbers.md#expt) | 2 | Raise base to a power |
| [`square`](numbers.md#square) | 1 | Square of a number |
| [`sqrt`](numbers.md#sqrt) | 1 | Square root (complex result for negative reals) |
| [`exact-integer-sqrt`](numbers.md#exact-integer-sqrt) | 1 | Integer square root, returns root and remainder via values |
| [`sin`](numbers.md#sin) | 1 | Sine (radians) |
| [`cos`](numbers.md#cos) | 1 | Cosine (radians) |
| [`tan`](numbers.md#tan) | 1 | Tangent (radians) |
| [`asin`](numbers.md#asin) | 1 | Arcsine |
| [`acos`](numbers.md#acos) | 1 | Arccosine |
| [`atan`](numbers.md#atan) | 1+ | Arctangent (1 arg) or two-argument atan2 |
| [`exp`](numbers.md#exp) | 1 | Exponential (e^x) |
| [`log`](numbers.md#log) | 1+ | Natural log (1 arg) or log base b (2 args) |
| [`finite?`](numbers.md#finite) | 1 | True if number is finite |
| [`infinite?`](numbers.md#infinite) | 1 | True if number is infinite |
| [`nan?`](numbers.md#nan) | 1 | True if number is NaN |
| [`number->string`](numbers.md#number-to-string) | 1 | Convert number to string representation |
| [`string->number`](numbers.md#string-to-number) | 1+ | Parse string as number (optional radix) |
| [`floor-quotient`](numbers.md#floor-quotient) | 2 | Quotient from floor division |
| [`floor-remainder`](numbers.md#floor-remainder) | 2 | Remainder from floor division |
| [`floor/`](numbers.md#floor-div) | 2 | Floor division returning quotient and remainder |
| [`truncate-quotient`](numbers.md#truncate-quotient) | 2 | Quotient from truncated division |
| [`truncate-remainder`](numbers.md#truncate-remainder) | 2 | Remainder from truncated division |
| [`truncate/`](numbers.md#truncate-div) | 2 | Truncated division returning quotient and remainder |
| [`numerator`](numbers.md#numerator) | 1 | Numerator of a rational (identity for integers) |
| [`denominator`](numbers.md#denominator) | 1 | Denominator of a rational (1 for integers) |
| [`rationalize`](numbers.md#rationalize) | 2 | Simplest rational within tolerance |
| [`make-rectangular`](numbers.md#make-rectangular) | 2 | Construct complex from real and imaginary parts |
| [`make-polar`](numbers.md#make-polar) | 2 | Construct complex from magnitude and angle |
| [`real-part`](numbers.md#real-part) | 1 | Real part of a complex number |
| [`imag-part`](numbers.md#imag-part) | 1 | Imaginary part of a complex number |
| [`magnitude`](numbers.md#magnitude) | 1 | Magnitude (absolute value) of a complex number |
| [`angle`](numbers.md#angle) | 1 | Angle (argument) of a complex number |

## [Pairs and Lists](pairs-and-lists.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`cons`](pairs-and-lists.md#cons) | 2 | Construct a pair |
| [`car`](pairs-and-lists.md#car) | 1 | First element of a pair |
| [`cdr`](pairs-and-lists.md#cdr) | 1 | Second element of a pair |
| [`set-car!`](pairs-and-lists.md#set-car) | 2 | Mutate the car of a pair |
| [`set-cdr!`](pairs-and-lists.md#set-cdr) | 2 | Mutate the cdr of a pair |
| [`list`](pairs-and-lists.md#list) | 0+ | Construct a list from arguments |
| [`length`](pairs-and-lists.md#length) | 1 | Length of a proper list |
| [`append`](pairs-and-lists.md#append) | 0+ | Append lists together |
| [`reverse`](pairs-and-lists.md#reverse) | 1 | Reverse a list |
| [`caar`](pairs-and-lists.md#caar) | 1 | `(car (car x))` |
| [`cadr`](pairs-and-lists.md#cadr) | 1 | `(car (cdr x))` |
| [`cdar`](pairs-and-lists.md#cdar) | 1 | `(cdr (car x))` |
| [`cddr`](pairs-and-lists.md#cddr) | 1 | `(cdr (cdr x))` |
| [`list-ref`](pairs-and-lists.md#list-ref) | 2 | Element at index k |
| [`list-tail`](pairs-and-lists.md#list-tail) | 2 | Sublist starting at index k |
| [`list-set!`](pairs-and-lists.md#list-set) | 3 | Set element at index k |
| [`list-copy`](pairs-and-lists.md#list-copy) | 1 | Shallow copy of a list |
| [`make-list`](pairs-and-lists.md#make-list) | 1+ | Create list of k elements (optional fill value) |
| [`member`](pairs-and-lists.md#member) | 2+ | Search by `equal?` (optional comparator) |
| [`memq`](pairs-and-lists.md#memq) | 2 | Search by `eq?` |
| [`memv`](pairs-and-lists.md#memv) | 2 | Search by `eqv?` |
| [`assoc`](pairs-and-lists.md#assoc) | 2+ | Association list lookup by `equal?` (optional comparator) |
| [`assq`](pairs-and-lists.md#assq) | 2 | Association list lookup by `eq?` |
| [`assv`](pairs-and-lists.md#assv) | 2 | Association list lookup by `eqv?` |
| [`map`](pairs-and-lists.md#map) | 2+ | Apply procedure to corresponding elements of lists |
| [`for-each`](pairs-and-lists.md#for-each) | 2+ | Like `map` but for side effects only |
| [`apply`](pairs-and-lists.md#apply) | 2+ | Apply procedure to a list of arguments |

### CXR Compositions (3- and 4-level)

All 24 compositions of `car` and `cdr` up to four deep. Each takes exactly 1 argument.
See [Pairs and Lists](pairs-and-lists.md#cxr-compositions) for the full table.

## [SRFI-1 List Library](srfi-1.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`fold`](srfi-1.md#fold) | 3+ | Left fold over one or more lists |
| [`fold-right`](srfi-1.md#fold-right) | 3+ | Right fold over one or more lists |
| [`reduce`](srfi-1.md#reduce) | 3 | Like fold with identity element |
| [`reduce-right`](srfi-1.md#reduce-right) | 3 | Like fold-right with identity element |
| [`filter`](srfi-1.md#filter) | 2 | Keep elements satisfying predicate |
| [`remove`](srfi-1.md#remove) | 2 | Remove elements satisfying predicate |
| [`partition`](srfi-1.md#partition) | 2 | Split list by predicate into two lists |
| [`find`](srfi-1.md#find) | 2 | First element satisfying predicate, or `#f` |
| [`find-tail`](srfi-1.md#find-tail) | 2 | Tail starting at first element satisfying predicate |
| [`any`](srfi-1.md#any) | 2+ | True if predicate holds for any element |
| [`every`](srfi-1.md#every) | 2+ | True if predicate holds for every element |
| [`count`](srfi-1.md#count) | 2+ | Count elements satisfying predicate |
| [`iota`](srfi-1.md#iota) | 1+ | Generate list of integers (count, optional start and step) |
| [`zip`](srfi-1.md#zip) | 1+ | Transpose lists into list of lists |
| [`concatenate`](srfi-1.md#concatenate) | 1 | Append a list of lists |
| [`take`](srfi-1.md#take) | 2 | First k elements |
| [`drop`](srfi-1.md#drop) | 2 | All but first k elements |
| [`take-while`](srfi-1.md#take-while) | 2 | Leading elements satisfying predicate |
| [`drop-while`](srfi-1.md#drop-while) | 2 | Drop leading elements satisfying predicate |
| [`filter-map`](srfi-1.md#filter-map) | 2+ | Map then filter false values |
| [`append-map`](srfi-1.md#append-map) | 2+ | Map then append results |
| [`last`](srfi-1.md#last) | 1 | Last element of a non-empty list |
| [`last-pair`](srfi-1.md#last-pair) | 1 | Last pair of a non-empty list |
| [`proper-list?`](srfi-1.md#proper-list) | 1 | True if argument is a proper list |
| [`dotted-list?`](srfi-1.md#dotted-list) | 1 | True if argument is a dotted (improper) list |
| [`circular-list?`](srfi-1.md#circular-list-pred) | 1 | True if argument is a circular list |
| [`not-pair?`](srfi-1.md#not-pair) | 1 | True if argument is not a pair |
| [`null-list?`](srfi-1.md#null-list) | 1 | True if argument is the empty list (error on non-list) |
| [`list=`](srfi-1.md#list-equal) | 2+ | Compare lists element-wise with a given equality predicate |
| [`cons*`](srfi-1.md#cons-star) | 1+ | Like `list` but last arg is the tail |
| [`xcons`](srfi-1.md#xcons) | 2 | `(cons cdr car)` — reversed cons |
| [`list-tabulate`](srfi-1.md#list-tabulate) | 2 | Build list of k elements from init procedure |
| [`circular-list`](srfi-1.md#circular-list) | 1+ | Build a circular list from arguments |
| [`first`](srfi-1.md#first) | 1 | First element (same as `car`) |
| [`second`](srfi-1.md#second) | 1 | Second element |
| [`third`](srfi-1.md#third) | 1 | Third element |
| [`fourth`](srfi-1.md#fourth) | 1 | Fourth element |
| [`fifth`](srfi-1.md#fifth) | 1 | Fifth element |
| [`sixth`](srfi-1.md#sixth) | 1 | Sixth element |
| [`seventh`](srfi-1.md#seventh) | 1 | Seventh element |
| [`eighth`](srfi-1.md#eighth) | 1 | Eighth element |
| [`ninth`](srfi-1.md#ninth) | 1 | Ninth element |
| [`tenth`](srfi-1.md#tenth) | 1 | Tenth element |
| [`car+cdr`](srfi-1.md#carcdr) | 1 | Return car and cdr as multiple values |
| [`take-right`](srfi-1.md#take-right) | 2 | Last k elements |
| [`drop-right`](srfi-1.md#drop-right) | 2 | All but last k elements |
| [`split-at`](srfi-1.md#split-at) | 2 | Split list at index k into two values |
| [`span`](srfi-1.md#span) | 2 | Split list at first element not satisfying predicate |
| [`break`](srfi-1.md#break) | 2 | Split list at first element satisfying predicate |
| [`unfold`](srfi-1.md#unfold) | 4+ | Unfold a list from a seed value |
| [`unfold-right`](srfi-1.md#unfold-right) | 4+ | Unfold a list in reverse from a seed value |
| [`pair-fold`](srfi-1.md#pair-fold) | 3+ | Fold over pairs (not elements) |
| [`pair-fold-right`](srfi-1.md#pair-fold-right) | 3+ | Right fold over pairs |
| [`pair-for-each`](srfi-1.md#pair-for-each) | 2+ | For-each over pairs |
| [`map-in-order`](srfi-1.md#map-in-order) | 2+ | Map with guaranteed left-to-right evaluation |
| [`list-index`](srfi-1.md#list-index) | 2+ | Index of first element satisfying predicate |
| [`delete`](srfi-1.md#delete) | 2+ | Remove all occurrences equal to element |
| [`delete-duplicates`](srfi-1.md#delete-duplicates) | 1+ | Remove duplicate elements |
| [`alist-cons`](srfi-1.md#alist-cons) | 3 | `(cons (cons key value) alist)` |
| [`alist-copy`](srfi-1.md#alist-copy) | 1 | Shallow copy of an association list |
| [`alist-delete`](srfi-1.md#alist-delete) | 2+ | Remove entries with matching key |
| [`lset=`](srfi-1.md#lset-equal) | 2+ | Set equality |
| [`lset-adjoin`](srfi-1.md#lset-adjoin) | 2+ | Add elements to a set |
| [`lset-union`](srfi-1.md#lset-union) | 2+ | Set union |
| [`lset-intersection`](srfi-1.md#lset-intersection) | 2+ | Set intersection |
| [`lset-difference`](srfi-1.md#lset-difference) | 2+ | Set difference |
| [`lset-xor`](srfi-1.md#lset-xor) | 2+ | Set symmetric difference |
| [`append-reverse`](srfi-1.md#append-reverse) | 2 | `(append (reverse list1) list2)` |
| [`length+`](srfi-1.md#length-plus) | 1 | Length or `#f` for circular lists |
| [`unzip1`](srfi-1.md#unzip1) | 1 | Unzip list of lists (first elements) |
| [`unzip2`](srfi-1.md#unzip2) | 1 | Unzip list of lists (first two elements as values) |

## [Strings](strings.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`string`](strings.md#string) | 0+ | Construct string from characters |
| [`make-string`](strings.md#make-string) | 1+ | Create string of k characters (optional fill char) |
| [`string-length`](strings.md#string-length) | 1 | Number of codepoints in string |
| [`string-ref`](strings.md#string-ref) | 2 | Character at codepoint index k |
| [`string-set!`](strings.md#string-set) | 3 | Set character at codepoint index k |
| [`substring`](strings.md#substring) | 3 | Extract substring by codepoint indices |
| [`string-append`](strings.md#string-append) | 0+ | Concatenate strings |
| [`string-copy`](strings.md#string-copy) | 1+ | Copy string (optional start and end) |
| [`string-copy!`](strings.md#string-copy-bang) | 3+ | Copy into mutable string at offset |
| [`string-fill!`](strings.md#string-fill) | 2+ | Fill string with a character (optional start/end) |
| [`string->list`](strings.md#string-to-list) | 1+ | Convert string to list of characters |
| [`list->string`](strings.md#list-to-string) | 1 | Convert list of characters to string |
| [`string->symbol`](strings.md#string-to-symbol) | 1 | Intern string as a symbol |
| [`symbol->string`](strings.md#symbol-to-string) | 1 | Symbol name as a string |
| [`string->utf8`](strings.md#string-to-utf8) | 1 | Convert string to UTF-8 bytevector |
| [`utf8->string`](strings.md#utf8-to-string) | 1 | Convert UTF-8 bytevector to string |
| [`string->vector`](strings.md#string-to-vector) | 1+ | Convert string to vector of characters |
| [`string->number`](strings.md#string-to-number) | 1+ | Parse string as number (optional radix) |
| [`number->string`](strings.md#number-to-string) | 1 | Convert number to string |
| [`string-for-each`](strings.md#string-for-each) | 2+ | Apply procedure to each character |
| [`string-map`](strings.md#string-map) | 2+ | Map procedure over characters |
| [`string<?`](strings.md#string-lt) | 2+ | Lexicographic less-than |
| [`string<=?`](strings.md#string-le) | 2+ | Lexicographic less-than-or-equal |
| [`string=?`](strings.md#string-eq) | 2+ | String equality |
| [`string>=?`](strings.md#string-ge) | 2+ | Lexicographic greater-than-or-equal |
| [`string>?`](strings.md#string-gt) | 2+ | Lexicographic greater-than |

## [SRFI-13 String Library](srfi-13.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`string-contains`](srfi-13.md#string-contains) | 2+ | Index of substring in string, or `#f` (optional start/end) |
| [`string-prefix?`](srfi-13.md#string-prefix) | 2+ | True if first string is a prefix of second (optional start/end) |
| [`string-suffix?`](srfi-13.md#string-suffix) | 2+ | True if first string is a suffix of second (optional start/end) |
| [`string-index`](srfi-13.md#string-index) | 2+ | Index of first char satisfying predicate/char-set (optional start/end) |
| [`string-index-right`](srfi-13.md#string-index-right) | 2+ | Index of last char satisfying predicate/char-set (optional start/end) |
| [`string-skip`](srfi-13.md#string-skip) | 2+ | Index of first char NOT satisfying predicate/char-set (optional start/end) |
| [`string-skip-right`](srfi-13.md#string-skip-right) | 2+ | Index of last char NOT satisfying predicate/char-set (optional start/end) |
| [`string-count`](srfi-13.md#string-count) | 2+ | Count chars satisfying predicate/char-set (optional start/end) |
| [`string-trim`](srfi-13.md#string-trim) | 1+ | Remove leading chars matching predicate/char-set (optional start/end) |
| [`string-trim-right`](srfi-13.md#string-trim-right) | 1+ | Remove trailing chars matching predicate/char-set (optional start/end) |
| [`string-trim-both`](srfi-13.md#string-trim-both) | 1+ | Remove leading and trailing chars (optional start/end) |
| [`string-split`](srfi-13.md#string-split) | 2 | Split string by delimiter into list of strings |
| [`string-join`](srfi-13.md#string-join) | 1+ | Join list of strings with delimiter |
| [`string-concatenate`](srfi-13.md#string-concatenate) | 1 | Concatenate a list of strings |
| [`string-take`](srfi-13.md#string-take) | 2 | First k characters |
| [`string-drop`](srfi-13.md#string-drop) | 2 | All but first k characters |
| [`string-take-right`](srfi-13.md#string-take-right) | 2 | Last k characters |
| [`string-drop-right`](srfi-13.md#string-drop-right) | 2 | All but last k characters |
| [`string-pad`](srfi-13.md#string-pad) | 2+ | Pad string on the left to given length |
| [`string-pad-right`](srfi-13.md#string-pad-right) | 2+ | Pad string on the right to given length |
| [`string-reverse`](srfi-13.md#string-reverse) | 1+ | Reverse a string (optional start/end) |
| [`string-filter`](srfi-13.md#string-filter) | 2+ | Keep chars satisfying predicate/char-set (optional start/end) |
| [`string-delete`](srfi-13.md#string-delete) | 2+ | Remove chars satisfying predicate/char-set (optional start/end) |
| [`string-replace`](srfi-13.md#string-replace) | 4 | Replace substring by codepoint indices |
| [`string-titlecase`](srfi-13.md#string-titlecase) | 1+ | Titlecase a string (optional start/end) |
| [`string-every`](srfi-13.md#string-every) | 2+ | True if predicate/char-set matches every char (optional start/end) |
| [`string-any`](srfi-13.md#string-any) | 2+ | True if predicate/char-set matches any char (optional start/end) |
| [`string-tabulate`](srfi-13.md#string-tabulate) | 2 | Build string from index-to-char procedure |
| [`string-unfold`](srfi-13.md#string-unfold) | 4+ | Unfold a string from a seed |
| [`string-unfold-right`](srfi-13.md#string-unfold-right) | 4+ | Unfold a string in reverse from a seed |

## [Characters](characters.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`char->integer`](characters.md#char-to-integer) | 1 | Unicode codepoint as integer |
| [`integer->char`](characters.md#integer-to-char) | 1 | Character from Unicode codepoint |
| [`char<?`](characters.md#char-lt) | 2+ | Character less-than by codepoint |
| [`char<=?`](characters.md#char-le) | 2+ | Character less-than-or-equal |
| [`char=?`](characters.md#char-eq) | 2+ | Character equality |
| [`char>=?`](characters.md#char-ge) | 2+ | Character greater-than-or-equal |
| [`char>?`](characters.md#char-gt) | 2+ | Character greater-than |
| [`char-alphabetic?`](characters.md#char-alphabetic) | 1 | True if Unicode alphabetic |
| [`char-numeric?`](characters.md#char-numeric) | 1 | True if Unicode numeric |
| [`char-whitespace?`](characters.md#char-whitespace) | 1 | True if Unicode whitespace |
| [`char-upper-case?`](characters.md#char-upper-case) | 1 | True if Unicode uppercase |
| [`char-lower-case?`](characters.md#char-lower-case) | 1 | True if Unicode lowercase |
| [`char-upcase`](characters.md#char-upcase) | 1 | Convert to uppercase |
| [`char-downcase`](characters.md#char-downcase) | 1 | Convert to lowercase |
| [`char-foldcase`](characters.md#char-foldcase) | 1 | Convert to foldcase (for case-insensitive comparison) |
| [`digit-value`](characters.md#digit-value) | 1 | Numeric value of digit character, or `#f` |
| [`char-ci<?`](characters.md#char-ci-lt) | 2+ | Case-insensitive character less-than |
| [`char-ci<=?`](characters.md#char-ci-le) | 2+ | Case-insensitive character less-than-or-equal |
| [`char-ci=?`](characters.md#char-ci-eq) | 2+ | Case-insensitive character equality |
| [`char-ci>=?`](characters.md#char-ci-ge) | 2+ | Case-insensitive character greater-than-or-equal |
| [`char-ci>?`](characters.md#char-ci-gt) | 2+ | Case-insensitive character greater-than |
| [`string-ci<?`](characters.md#string-ci-lt) | 2+ | Case-insensitive string less-than |
| [`string-ci<=?`](characters.md#string-ci-le) | 2+ | Case-insensitive string less-than-or-equal |
| [`string-ci=?`](characters.md#string-ci-eq) | 2+ | Case-insensitive string equality |
| [`string-ci>=?`](characters.md#string-ci-ge) | 2+ | Case-insensitive string greater-than-or-equal |
| [`string-ci>?`](characters.md#string-ci-gt) | 2+ | Case-insensitive string greater-than |
| [`string-upcase`](characters.md#string-upcase) | 1 | Convert entire string to uppercase |
| [`string-downcase`](characters.md#string-downcase) | 1 | Convert entire string to lowercase |
| [`string-foldcase`](characters.md#string-foldcase) | 1 | Foldcase entire string |

## [Vectors](vectors.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`vector`](vectors.md#vector) | 0+ | Construct vector from arguments |
| [`make-vector`](vectors.md#make-vector) | 1+ | Create vector of k elements (optional fill value) |
| [`vector?`](vectors.md#vector-pred) | 1 | True if argument is a vector |
| [`vector-length`](vectors.md#vector-length) | 1 | Number of elements |
| [`vector-ref`](vectors.md#vector-ref) | 2 | Element at index k |
| [`vector-set!`](vectors.md#vector-set) | 3 | Set element at index k |
| [`vector->list`](vectors.md#vector-to-list) | 1+ | Convert to list (optional start and end) |
| [`list->vector`](vectors.md#list-to-vector) | 1 | Convert list to vector |
| [`vector->string`](vectors.md#vector-to-string) | 1 | Convert vector of characters to string |
| [`vector-fill!`](vectors.md#vector-fill) | 2 | Fill vector with a value |
| [`vector-copy`](vectors.md#vector-copy) | 1+ | Copy vector (optional start and end) |
| [`vector-copy!`](vectors.md#vector-copy-mut) | 3+ | Copy into vector at offset |
| [`vector-append`](vectors.md#vector-append) | 0+ | Concatenate vectors |
| [`vector-for-each`](vectors.md#vector-for-each) | 2+ | Apply procedure to each element |
| [`vector-map`](vectors.md#vector-map) | 2+ | Map procedure over elements |

## [SRFI-133 Vector Library](srfi-133.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`vector-unfold`](srfi-133.md#vector-unfold) | 2+ | Build vector from seed function |
| [`vector-unfold-right`](srfi-133.md#vector-unfold-right) | 2+ | Build vector in reverse from seed function |
| [`vector-concatenate`](srfi-133.md#vector-concatenate) | 1 | Concatenate a list of vectors |
| [`vector-any`](srfi-133.md#vector-any) | 2+ | True if predicate holds for any element |
| [`vector-every`](srfi-133.md#vector-every) | 2+ | True if predicate holds for every element |
| [`vector-index`](srfi-133.md#vector-index) | 2+ | Index of first element satisfying predicate |
| [`vector-index-right`](srfi-133.md#vector-index-right) | 2+ | Index of last element satisfying predicate |
| [`vector-skip`](srfi-133.md#vector-skip) | 2+ | Index of first element NOT satisfying predicate |
| [`vector-skip-right`](srfi-133.md#vector-skip-right) | 2+ | Index of last element NOT satisfying predicate |
| [`vector-binary-search`](srfi-133.md#vector-binary-search) | 3 | Binary search with comparator |
| [`vector-swap!`](srfi-133.md#vector-swap) | 3 | Swap two elements by index |
| [`vector-reverse!`](srfi-133.md#vector-reverse-mut) | 1+ | Reverse vector in place (optional start/end) |
| [`vector-reverse-copy`](srfi-133.md#vector-reverse-copy) | 1+ | Reversed copy (optional start/end) |
| [`vector-cumulate`](srfi-133.md#vector-cumulate) | 3 | Cumulative fold into new vector |
| [`vector-partition`](srfi-133.md#vector-partition) | 2 | Partition by predicate into two vectors |
| [`vector-count`](srfi-133.md#vector-count) | 2+ | Count elements satisfying predicate |
| [`vector-fold`](srfi-133.md#vector-fold) | 3+ | Left fold over vector |
| [`vector-fold-right`](srfi-133.md#vector-fold-right) | 3+ | Right fold over vector |
| [`vector-map!`](srfi-133.md#vector-map-mut) | 2+ | In-place map |
| [`vector-empty?`](srfi-133.md#vector-empty) | 1 | True if vector has zero length |
| [`vector=`](srfi-133.md#vector-equal) | 3 | Element-wise equality with comparator |

## [Bytevectors](bytevectors.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`bytevector?`](bytevectors.md#bytevector-pred) | 1 | True if argument is a bytevector |
| [`make-bytevector`](bytevectors.md#make-bytevector) | 1+ | Create bytevector of k bytes (optional fill) |
| [`bytevector`](bytevectors.md#bytevector) | 0+ | Construct bytevector from byte values |
| [`bytevector-length`](bytevectors.md#bytevector-length) | 1 | Number of bytes |
| [`bytevector-u8-ref`](bytevectors.md#bytevector-u8-ref) | 2 | Byte at index k |
| [`bytevector-u8-set!`](bytevectors.md#bytevector-u8-set) | 3 | Set byte at index k |
| [`bytevector-copy`](bytevectors.md#bytevector-copy) | 1+ | Copy bytevector (optional start and end) |
| [`bytevector-copy!`](bytevectors.md#bytevector-copy-mut) | 3+ | Copy into bytevector at offset |
| [`bytevector-append`](bytevectors.md#bytevector-append) | 0+ | Concatenate bytevectors |
| [`utf8->string`](bytevectors.md#utf8-to-string) | 1+ | Decode UTF-8 bytevector to string |
| [`string->utf8`](bytevectors.md#string-to-utf8) | 1+ | Encode string to UTF-8 bytevector |
| [`read-u8`](bytevectors.md#read-u8) | 0+ | Read one byte from port |
| [`peek-u8`](bytevectors.md#peek-u8) | 0+ | Peek at next byte without consuming |
| [`write-u8`](bytevectors.md#write-u8) | 1+ | Write one byte to port |
| [`u8-ready?`](bytevectors.md#u8-ready) | 0+ | True if a byte is available to read |
| [`read-bytevector`](bytevectors.md#read-bytevector) | 1+ | Read k bytes into a new bytevector |
| [`read-bytevector!`](bytevectors.md#read-bytevector-mut) | 1+ | Read bytes into an existing bytevector |
| [`write-bytevector`](bytevectors.md#write-bytevector) | 1+ | Write bytevector to port |
| [`open-input-bytevector`](bytevectors.md#open-input-bytevector) | 1 | Open bytevector as input port |
| [`open-output-bytevector`](bytevectors.md#open-output-bytevector) | 0 | Create output port backed by bytevector |
| [`get-output-bytevector`](bytevectors.md#get-output-bytevector) | 1 | Get accumulated bytevector from output port |

## [Ports and I/O](ports-and-io.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`current-input-port`](ports-and-io.md#current-input-port) | 0 | Current default input port (stdin) |
| [`current-output-port`](ports-and-io.md#current-output-port) | 0 | Current default output port (stdout) |
| [`current-error-port`](ports-and-io.md#current-error-port) | 0 | Current default error port (stderr) |
| [`port?`](ports-and-io.md#port-pred) | 1 | True if argument is a port |
| [`input-port?`](ports-and-io.md#input-port) | 1 | True if port supports input |
| [`output-port?`](ports-and-io.md#output-port) | 1 | True if port supports output |
| [`textual-port?`](ports-and-io.md#textual-port) | 1 | True if port is textual |
| [`binary-port?`](ports-and-io.md#binary-port) | 1 | True if port is binary |
| [`input-port-open?`](ports-and-io.md#input-port-open) | 1 | True if input port is open |
| [`output-port-open?`](ports-and-io.md#output-port-open) | 1 | True if output port is open |
| [`open-input-file`](ports-and-io.md#open-input-file) | 1 | Open file for textual input |
| [`open-output-file`](ports-and-io.md#open-output-file) | 1 | Open file for textual output |
| [`open-binary-input-file`](ports-and-io.md#open-binary-input-file) | 1 | Open file for binary input |
| [`open-binary-output-file`](ports-and-io.md#open-binary-output-file) | 1 | Open file for binary output |
| [`close-port`](ports-and-io.md#close-port) | 1 | Close a port |
| [`close-input-port`](ports-and-io.md#close-input-port) | 1 | Close an input port |
| [`close-output-port`](ports-and-io.md#close-output-port) | 1 | Close an output port |
| [`file-exists?`](ports-and-io.md#file-exists) | 1 | True if file exists at path |
| [`delete-file`](ports-and-io.md#delete-file) | 1 | Delete a file |
| [`call-with-input-file`](ports-and-io.md#call-with-input-file) | 2 | Open file, call proc, close file |
| [`call-with-output-file`](ports-and-io.md#call-with-output-file) | 2 | Open file, call proc, close file |
| [`call-with-port`](ports-and-io.md#call-with-port) | 2 | Call proc with port, close port when done |
| [`with-input-from-file`](ports-and-io.md#with-input-from-file) | 2 | Parameterize current-input-port for proc |
| [`with-output-to-file`](ports-and-io.md#with-output-to-file) | 2 | Parameterize current-output-port for proc |
| [`read`](ports-and-io.md#read) | 0+ | Read a Scheme datum from port |
| [`read-char`](ports-and-io.md#read-char) | 0+ | Read one character |
| [`peek-char`](ports-and-io.md#peek-char) | 0+ | Peek at next character without consuming |
| [`read-line`](ports-and-io.md#read-line) | 0+ | Read a line as a string |
| [`read-string`](ports-and-io.md#read-string) | 1+ | Read k characters as a string |
| [`char-ready?`](ports-and-io.md#char-ready) | 0+ | True if a character is available to read |
| [`display`](ports-and-io.md#display) | 1+ | Write value in human-readable form |
| [`write`](ports-and-io.md#write) | 1+ | Write value in machine-readable form (with quotes) |
| [`write-shared`](ports-and-io.md#write-shared) | 1+ | Write with datum labels for shared structure |
| [`write-simple`](ports-and-io.md#write-simple) | 1+ | Write without datum labels |
| [`write-char`](ports-and-io.md#write-char) | 1+ | Write a single character |
| [`write-string`](ports-and-io.md#write-string) | 1+ | Write a string (or substring) |
| [`newline`](ports-and-io.md#newline) | 0+ | Write a newline character |
| [`flush-output-port`](ports-and-io.md#flush-output-port) | 0+ | Flush output port buffer |
| [`open-input-string`](ports-and-io.md#open-input-string) | 1 | Open string as input port |
| [`open-output-string`](ports-and-io.md#open-output-string) | 0 | Create output port backed by string |
| [`get-output-string`](ports-and-io.md#get-output-string) | 1 | Get accumulated string from output port |
| [`eof-object?`](ports-and-io.md#eof-object-pred) | 1 | True if argument is the EOF object |
| [`eof-object`](ports-and-io.md#eof-object) | 0 | Return the EOF object |

## [Control Flow](control-flow.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`apply`](control-flow.md#apply) | 2+ | Apply procedure to arguments |
| [`call-with-current-continuation`](control-flow.md#call-with-current-continuation) | 1 | Capture the current continuation |
| [`call/cc`](control-flow.md#callcc) | 1 | Alias for `call-with-current-continuation` |
| [`call-with-escape-continuation`](control-flow.md#call-with-escape-continuation) | 1 | Capture a one-shot escape continuation |
| [`call/ec`](control-flow.md#callec) | 1 | Alias for `call-with-escape-continuation` |
| [`dynamic-wind`](control-flow.md#dynamic-wind) | 3 | Install before/after thunks around a body |
| [`values`](control-flow.md#values) | 0+ | Return multiple values |
| [`call-with-values`](control-flow.md#call-with-values) | 2 | Pass multiple values from producer to consumer |
| [`raise`](control-flow.md#raise) | 1 | Raise an exception |
| [`raise-continuable`](control-flow.md#raise-continuable) | 1 | Raise a continuable exception |
| [`with-exception-handler`](control-flow.md#with-exception-handler) | 2 | Install an exception handler |
| [`error`](control-flow.md#error) | 1+ | Create error object and raise it |
| [`error-object?`](control-flow.md#error-object-pred) | 1 | True if argument is an error object |
| [`error-object-message`](control-flow.md#error-object-message) | 1 | Error message string |
| [`error-object-irritants`](control-flow.md#error-object-irritants) | 1 | List of irritant values from error |
| [`file-error?`](control-flow.md#file-error) | 1 | True if error is a file error |
| [`read-error?`](control-flow.md#read-error) | 1 | True if error is a read error |

## [Type Checking and Equivalence](type-checking.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`not`](type-checking.md#not) | 1 | Boolean negation |
| [`boolean=?`](type-checking.md#boolean-equal) | 2+ | True if all arguments are the same boolean |
| [`eq?`](type-checking.md#eq) | 2 | Pointer identity |
| [`eqv?`](type-checking.md#eqv) | 2 | Value equivalence (numbers, chars, booleans) |
| [`equal?`](type-checking.md#equal) | 2 | Deep structural equality |
| [`symbol=?`](type-checking.md#symbol-equal) | 2+ | True if all arguments are the same symbol |
| [`pair?`](type-checking.md#pair) | 1 | True if argument is a pair |
| [`null?`](type-checking.md#null) | 1 | True if argument is the empty list |
| [`number?`](type-checking.md#number) | 1 | True if argument is a number |
| [`integer?`](type-checking.md#integer) | 1 | True if argument is an integer |
| [`real?`](type-checking.md#real) | 1 | True if argument is a real number |
| [`complex?`](type-checking.md#complex) | 1 | True if argument is a complex number |
| [`rational?`](type-checking.md#rational) | 1 | True if argument is rational |
| [`symbol?`](type-checking.md#symbol) | 1 | True if argument is a symbol |
| [`string?`](type-checking.md#string) | 1 | True if argument is a string |
| [`boolean?`](type-checking.md#boolean) | 1 | True if argument is a boolean |
| [`char?`](type-checking.md#char) | 1 | True if argument is a character |
| [`procedure?`](type-checking.md#procedure) | 1 | True if argument is a procedure |
| [`list?`](type-checking.md#list) | 1 | True if argument is a proper list |
| [`vector?`](type-checking.md#vector) | 1 | True if argument is a vector |
| [`bytevector?`](type-checking.md#bytevector) | 1 | True if argument is a bytevector |
| [`port?`](type-checking.md#port) | 1 | True if argument is a port |
| [`hash-table?`](type-checking.md#hash-table) | 1 | True if argument is a hash table |
| [`promise?`](type-checking.md#promise) | 1 | True if argument is a promise |
| [`error-object?`](type-checking.md#error-object) | 1 | True if argument is an error object |

## [Hash Tables (SRFI-69)](hash-tables.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`make-hash-table`](hash-tables.md#make-hash-table) | 0+ | Create a new hash table |
| [`hash-table?`](hash-tables.md#hash-table-pred) | 1 | True if argument is a hash table |
| [`hash-table-ref`](hash-tables.md#hash-table-ref) | 2+ | Look up key (optional default value) |
| [`hash-table-set!`](hash-tables.md#hash-table-set) | 3 | Associate key with value |
| [`hash-table-delete!`](hash-tables.md#hash-table-delete) | 2 | Remove key |
| [`hash-table-exists?`](hash-tables.md#hash-table-exists) | 2 | True if key is present |
| [`hash-table-size`](hash-tables.md#hash-table-size) | 1 | Number of key-value pairs |
| [`hash-table-keys`](hash-tables.md#hash-table-keys) | 1 | List of all keys |
| [`hash-table-values`](hash-tables.md#hash-table-values) | 1 | List of all values |
| [`hash-table-walk`](hash-tables.md#hash-table-walk) | 2 | Call procedure on each key-value pair |
| [`hash-table->alist`](hash-tables.md#hash-table-to-alist) | 1 | Convert to association list |
| [`alist->hash-table`](hash-tables.md#alist-to-hash-table) | 1 | Convert association list to hash table |
| [`hash-table-copy`](hash-tables.md#hash-table-copy) | 1 | Shallow copy of hash table |
| [`hash-table-update!/default`](hash-tables.md#hash-table-update-default) | 4 | Update value for key using procedure, with default |

## [System and Environment](system.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`exit`](system.md#exit) | 0+ | Exit the process (optional status code) |
| [`emergency-exit`](system.md#emergency-exit) | 0+ | Immediate exit without cleanup |
| [`command-line`](system.md#command-line) | 0 | List of command-line arguments |
| [`get-environment-variable`](system.md#get-environment-variable) | 1 | Value of environment variable, or `#f` |
| [`get-environment-variables`](system.md#get-environment-variables) | 0 | Association list of all environment variables |
| [`current-second`](system.md#current-second) | 0 | Current TAI time as inexact real |
| [`current-jiffy`](system.md#current-jiffy) | 0 | Current time in jiffies (high resolution) |
| [`jiffies-per-second`](system.md#jiffies-per-second) | 0 | Number of jiffies per second |
| [`features`](system.md#features) | 0 | List of implementation feature identifiers |
| [`eval`](system.md#eval) | 1+ | Evaluate expression in an environment |
| [`environment`](system.md#environment) | 0+ | Create environment from library imports |
| [`interaction-environment`](system.md#interaction-environment) | 0 | REPL environment with all bindings |
| [`load`](system.md#load) | 1 | Load and evaluate a Scheme source file |
| [`make-parameter`](system.md#make-parameter) | 1+ | Create a parameter object (optional converter) |

## [Syntax Forms](syntax-forms.md)

| Form | Description |
|------|-------------|
| [`define`](syntax-forms.md#define) | Variable and function definition |
| [`lambda`](syntax-forms.md#lambda) | Anonymous function |
| [`if`](syntax-forms.md#if) | Conditional |
| [`quote`](syntax-forms.md#quote) | Literal datum |
| [`set!`](syntax-forms.md#set) | Variable mutation |
| [`begin`](syntax-forms.md#begin) | Sequence of expressions |
| [`cond`](syntax-forms.md#cond) | Multi-branch conditional |
| [`case`](syntax-forms.md#case) | Dispatch on datum equality |
| [`and`](syntax-forms.md#and) | Short-circuit logical and |
| [`or`](syntax-forms.md#or) | Short-circuit logical or |
| [`when`](syntax-forms.md#when) | One-armed conditional with implicit begin |
| [`unless`](syntax-forms.md#unless) | Negated one-armed conditional |
| [`let`](syntax-forms.md#let) | Local bindings |
| [`let*`](syntax-forms.md#let-star) | Sequential local bindings |
| [`letrec`](syntax-forms.md#letrec) | Mutually recursive bindings |
| [`letrec*`](syntax-forms.md#letrec-star) | Sequential mutually recursive bindings |
| [`let-values`](syntax-forms.md#let-values) | Destructure multiple values |
| [`let*-values`](syntax-forms.md#let-star-values) | Sequential destructure multiple values |
| [`do`](syntax-forms.md#do) | Iteration with step expressions |
| [`case-lambda`](syntax-forms.md#case-lambda) | Arity-dispatched lambda |
| [`define-syntax`](syntax-forms.md#define-syntax) | Define a macro |
| [`syntax-rules`](syntax-forms.md#syntax-rules) | Pattern-based macro transformer |
| [`let-syntax`](syntax-forms.md#let-syntax) | Local macro bindings |
| [`letrec-syntax`](syntax-forms.md#letrec-syntax) | Mutually recursive local macro bindings |
| [`quasiquote`](syntax-forms.md#quasiquote) | Template with unquote and unquote-splicing |
| [`define-record-type`](syntax-forms.md#define-record-type) | Define a record type |
| [`define-library`](syntax-forms.md#define-library) | Define a library |
| [`import`](syntax-forms.md#import) | Import library bindings |
| [`guard`](syntax-forms.md#guard) | Exception handling with cond clauses |
| [`delay`](syntax-forms.md#delay) | Create a promise (lazy thunk) |
| [`delay-force`](syntax-forms.md#delay-force) | Create an iterative promise |
| [`parameterize`](syntax-forms.md#parameterize) | Dynamically bind parameters |
| [`cond-expand`](syntax-forms.md#cond-expand) | Feature-based conditional expansion |

## [SRFI-18 Threads](threads.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`current-thread`](threads.md#current-thread) | 0 | Current thread object |
| [`thread?`](threads.md#thread-pred) | 1 | True if argument is a thread |
| [`make-thread`](threads.md#make-thread) | 1+ | Create a new thread (thunk, optional name) |
| [`thread-name`](threads.md#thread-name) | 1 | Thread's name |
| [`thread-specific`](threads.md#thread-specific) | 1 | Thread's specific value |
| [`thread-specific-set!`](threads.md#thread-specific-set) | 2 | Set thread's specific value |
| [`thread-start!`](threads.md#thread-start) | 1 | Start a thread |
| [`thread-yield!`](threads.md#thread-yield) | 0 | Yield to the scheduler |
| [`thread-sleep!`](threads.md#thread-sleep) | 1 | Sleep for a duration |
| [`thread-terminate!`](threads.md#thread-terminate) | 1 | Terminate a thread |
| [`thread-join!`](threads.md#thread-join) | 1+ | Wait for thread completion (optional timeout) |
| [`mutex?`](threads.md#mutex-pred) | 1 | True if argument is a mutex |
| [`make-mutex`](threads.md#make-mutex) | 0+ | Create a mutex (optional name) |
| [`mutex-name`](threads.md#mutex-name) | 1 | Mutex name |
| [`mutex-specific`](threads.md#mutex-specific) | 1 | Mutex specific value |
| [`mutex-specific-set!`](threads.md#mutex-specific-set) | 2 | Set mutex specific value |
| [`mutex-state`](threads.md#mutex-state) | 1 | Mutex state (locked/unlocked/owner) |
| [`mutex-lock!`](threads.md#mutex-lock) | 1+ | Lock a mutex (optional timeout/thread) |
| [`mutex-unlock!`](threads.md#mutex-unlock) | 1+ | Unlock a mutex (optional condition variable/timeout) |
| [`condition-variable?`](threads.md#condition-variable-pred) | 1 | True if argument is a condition variable |
| [`make-condition-variable`](threads.md#make-condition-variable) | 0+ | Create a condition variable (optional name) |
| [`condition-variable-name`](threads.md#condition-variable-name) | 1 | Condition variable name |
| [`condition-variable-specific`](threads.md#condition-variable-specific) | 1 | Condition variable specific value |
| [`condition-variable-specific-set!`](threads.md#condition-variable-specific-set) | 2 | Set condition variable specific value |
| [`condition-variable-signal!`](threads.md#condition-variable-signal) | 1 | Wake one waiting thread |
| [`condition-variable-broadcast!`](threads.md#condition-variable-broadcast) | 1 | Wake all waiting threads |
| [`current-time`](threads.md#current-time) | 0 | Current time as time object |
| [`time?`](threads.md#time-pred) | 1 | True if argument is a time object |
| [`time->seconds`](threads.md#time-to-seconds) | 1 | Convert time to seconds |
| [`seconds->time`](threads.md#seconds-to-time) | 1 | Convert seconds to time |
| [`join-timeout-exception?`](threads.md#join-timeout-exception) | 1 | True if exception is a join timeout |
| [`abandoned-mutex-exception?`](threads.md#abandoned-mutex-exception) | 1 | True if exception is an abandoned mutex |
| [`terminated-thread-exception?`](threads.md#terminated-thread-exception) | 1 | True if exception is a terminated thread |
| [`uncaught-exception?`](threads.md#uncaught-exception) | 1 | True if exception is an uncaught exception |
| [`uncaught-exception-reason`](threads.md#uncaught-exception-reason) | 1 | Get the reason from an uncaught exception |

## [Kaappi Extensions](extensions.md)

### FFI (Foreign Function Interface)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`ffi-open`](extensions.md#ffi-open) | 1 | Open a shared library by path |
| [`ffi-fn`](extensions.md#ffi-fn) | 4 | Bind a C function: `(ffi-fn lib "name" '(param-types) 'return-type)` |
| [`ffi-close`](extensions.md#ffi-close) | 1 | Close a shared library handle |

### Green Threads (Fibers)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`spawn`](extensions.md#spawn) | 1 | Create and start a fiber running a thunk |
| [`yield`](extensions.md#yield) | 0 | Yield to the fiber scheduler |
| [`fiber?`](extensions.md#fiber-pred) | 1 | True if argument is a fiber |
| [`fiber-join`](extensions.md#fiber-join) | 1 | Wait for fiber completion, return its result |
| [`make-channel`](extensions.md#make-channel) | 0 | Create a new channel |
| [`channel-send`](extensions.md#channel-send) | 2 | Send a value on a channel |
| [`channel-receive`](extensions.md#channel-receive) | 1 | Receive a value from a channel |
| [`channel?`](extensions.md#channel-pred) | 1 | True if argument is a channel |

## [Other Primitives](other.md)

### Lazy Evaluation

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`promise?`](other.md#promise-pred) | 1 | True if argument is a promise |
| [`make-promise`](other.md#make-promise) | 1 | Wrap a value as an already-forced promise |
| [`force`](other.md#force) | 1 | Force a promise, memoizing the result |

### Records (Internal Primitives)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`%make-record-type`](other.md#make-record-type) | 2 | Create a record type descriptor |
| [`%make-record`](other.md#make-record) | 1+ | Construct a record instance |
| [`%record?`](other.md#record-pred) | 2 | Check if value is instance of record type |
| [`%record-ref`](other.md#record-ref) | 2 | Access field by index |
| [`%record-set!`](other.md#record-set) | 3 | Mutate field by index |

### Random Numbers (SRFI-27)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`random-integer`](other.md#random-integer) | 1 | Random integer in [0, n) |
| [`random-real`](other.md#random-real) | 0 | Random real in [0, 1) |

## [SRFI-170 Filesystem](srfi-170.md)

| Procedure | Arity | Description |
|-----------|-------|-------------|
| [`file-info`](srfi-170.md#file-info) | 1+ | Get file metadata (optional follow-symlinks?) |
| [`file-info?`](srfi-170.md#file-info-pred) | 1 | True if argument is a file-info object |
| [`file-info-type`](srfi-170.md#file-info-type) | 1 | File type as symbol (regular, directory, symlink, ...) |
| [`file-info:size`](srfi-170.md#file-info-size) | 1 | File size in bytes |
| [`file-info:mtime`](srfi-170.md#file-info-mtime) | 1 | Modification time |
| [`file-info:atime`](srfi-170.md#file-info-atime) | 1 | Access time |
| [`file-info:ctime`](srfi-170.md#file-info-ctime) | 1 | Status change time |
| [`file-info:mode`](srfi-170.md#file-info-mode) | 1 | File permission mode |
| [`file-info:nlinks`](srfi-170.md#file-info-nlinks) | 1 | Number of hard links |
| [`file-info:uid`](srfi-170.md#file-info-uid) | 1 | Owner user ID |
| [`file-info:gid`](srfi-170.md#file-info-gid) | 1 | Owner group ID |
| [`file-info:inode`](srfi-170.md#file-info-inode) | 1 | Inode number |
| [`file-info:device`](srfi-170.md#file-info-device-id) | 1 | Device ID |
| [`file-info:rdev`](srfi-170.md#file-info-rdev) | 1 | Device ID (for device files) |
| [`file-info:blksize`](srfi-170.md#file-info-blksize) | 1 | Block size |
| [`file-info:blocks`](srfi-170.md#file-info-blocks) | 1 | Number of blocks |
| [`file-info-directory?`](srfi-170.md#file-info-directory) | 1 | True if file is a directory |
| [`file-info-regular?`](srfi-170.md#file-info-regular) | 1 | True if file is a regular file |
| [`file-info-symlink?`](srfi-170.md#file-info-symlink) | 1 | True if file is a symlink |
| [`file-info-fifo?`](srfi-170.md#file-info-fifo) | 1 | True if file is a FIFO |
| [`file-info-socket?`](srfi-170.md#file-info-socket) | 1 | True if file is a socket |
| [`file-info-device?`](srfi-170.md#file-info-device) | 1 | True if file is a device |
| [`create-directory`](srfi-170.md#create-directory) | 1+ | Create a directory (optional mode) |
| [`delete-directory`](srfi-170.md#delete-directory) | 1 | Delete a directory |
| [`rename-file`](srfi-170.md#rename-file) | 2 | Rename a file |
| [`create-symlink`](srfi-170.md#create-symlink) | 2 | Create a symbolic link |
| [`read-symlink`](srfi-170.md#read-symlink) | 1 | Read the target of a symbolic link |
| [`create-hard-link`](srfi-170.md#create-hard-link) | 2 | Create a hard link |
| [`real-path`](srfi-170.md#real-path) | 1 | Resolve to canonical absolute path |
| [`set-file-mode`](srfi-170.md#set-file-mode) | 2 | Set file permissions |
| [`truncate-file`](srfi-170.md#truncate-file) | 2 | Truncate file to given length |
| [`create-fifo`](srfi-170.md#create-fifo) | 1+ | Create a named pipe (optional mode) |
| [`set-file-owner`](srfi-170.md#set-file-owner) | 3 | Set file owner (uid, gid) |
| [`set-file-times`](srfi-170.md#set-file-times) | 1+ | Set access and modification times |
| [`directory-files`](srfi-170.md#directory-files) | 1+ | List files in a directory |
| [`open-directory`](srfi-170.md#open-directory) | 1+ | Open a directory stream |
| [`read-directory`](srfi-170.md#read-directory) | 1 | Read next entry from directory stream |
| [`close-directory`](srfi-170.md#close-directory) | 1 | Close a directory stream |
| [`pid`](srfi-170.md#pid) | 0 | Current process ID |
| [`umask`](srfi-170.md#umask) | 0 | Current umask |
| [`set-umask!`](srfi-170.md#set-umask) | 1 | Set umask |
| [`current-directory`](srfi-170.md#current-directory) | 0 | Current working directory |
| [`set-current-directory!`](srfi-170.md#set-current-directory) | 1 | Change working directory |
| [`user-uid`](srfi-170.md#user-uid) | 0 | Current user ID |
| [`user-gid`](srfi-170.md#user-gid) | 0 | Current group ID |
| [`user-effective-uid`](srfi-170.md#user-effective-uid) | 0 | Effective user ID |
| [`user-effective-gid`](srfi-170.md#user-effective-gid) | 0 | Effective group ID |
| [`user-supplementary-gids`](srfi-170.md#user-supplementary-gids) | 0 | Supplementary group IDs |
| [`nice`](srfi-170.md#nice) | 0+ | Adjust process priority |
| [`user-info`](srfi-170.md#user-info) | 1 | Get user info by UID or username |
| [`user-info?`](srfi-170.md#user-info-pred) | 1 | True if argument is a user-info object |
| [`user-info:name`](srfi-170.md#user-info-name) | 1 | User login name |
| [`user-info:uid`](srfi-170.md#user-info-uid) | 1 | User ID |
| [`user-info:gid`](srfi-170.md#user-info-gid) | 1 | User group ID |
| [`user-info:home-dir`](srfi-170.md#user-info-home-dir) | 1 | Home directory path |
| [`user-info:shell`](srfi-170.md#user-info-shell) | 1 | Login shell path |
| [`user-info:full-name`](srfi-170.md#user-info-full-name) | 1 | Full name (GECOS field) |
| [`group-info`](srfi-170.md#group-info) | 1 | Get group info by GID or group name |
| [`group-info?`](srfi-170.md#group-info-pred) | 1 | True if argument is a group-info object |
| [`group-info:name`](srfi-170.md#group-info-name) | 1 | Group name |
| [`group-info:gid`](srfi-170.md#group-info-gid) | 1 | Group ID |
| [`set-environment-variable!`](srfi-170.md#set-environment-variable) | 2 | Set an environment variable |
| [`delete-environment-variable!`](srfi-170.md#delete-environment-variable) | 1 | Delete an environment variable |
| [`terminal?`](srfi-170.md#terminal) | 1 | True if port is connected to a terminal |
| [`posix-time`](srfi-170.md#posix-time) | 0 | Current time as seconds since epoch |
| [`monotonic-time`](srfi-170.md#monotonic-time) | 0 | Monotonic clock time |
| [`temp-file-prefix`](srfi-170.md#temp-file-prefix) | 0 | Default temporary file prefix |
| [`create-temp-file`](srfi-170.md#create-temp-file) | 0+ | Create a temporary file (optional prefix) |

---
