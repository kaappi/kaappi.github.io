# Numbers and Arithmetic

Kaappi supports a full numeric tower: fixnums (63-bit integers), bignums
(arbitrary precision), exact rationals, flonums (IEEE 754 f64), and complex
numbers. These procedures are available from `(scheme base)` and
`(scheme inexact)`.

---

## Basic Arithmetic

### `+` { #plus }

**Syntax:** `(+ z1 ...)`

Returns the sum of its arguments. With no arguments, returns `0` (the
additive identity). Accepts any combination of number types: when all
arguments are exact integers the result is exact, when any argument is
inexact the result is inexact, and when any argument is complex the
result is complex. Arithmetic on fixnums that overflows is transparently
promoted to bignums.

```scheme
kaappi> (+)
;=> 0
kaappi> (+ 1 2 3)
;=> 6
kaappi> (+ 1 2.0)
;=> 3.0
kaappi> (+ 1/3 2/3)
;=> 1
```

**See also:** [`-`](./numbers.md#minus), [`*`](./numbers.md#star)

---

### `-` { #minus }

**Syntax:** `(- z)` or `(- z1 z2 ...)`

With one argument, returns the additive inverse (negation). With two or
more arguments, returns the result of subtracting all subsequent arguments
from the first. Like `+`, the result type follows the usual exactness
and type-promotion rules.

```scheme
kaappi> (- 5)
;=> -5
kaappi> (- 10 3)
;=> 7
kaappi> (- 10.0 3)
;=> 7.0
kaappi> (- 5.0)
;=> -5.0
```

**See also:** [`+`](./numbers.md#plus)

---

### `*` { #star }

**Syntax:** `(* z1 ...)`

Returns the product of its arguments. With no arguments, returns `1`
(the multiplicative identity). Handles exact integers, rationals,
flonums, and complex numbers. Fixnum overflow is transparently promoted
to bignums.

```scheme
kaappi> (*)
;=> 1
kaappi> (* 2 3)
;=> 6
kaappi> (* 2 3.5)
;=> 7.0
kaappi> (* 1/2 1/3)
;=> 1/6
```

**See also:** [`/`](./numbers.md#slash), [`square`](./numbers.md#square)

---

### `/` { #slash }

**Syntax:** `(/ z)` or `(/ z1 z2 ...)`

With one argument, returns the multiplicative inverse (reciprocal). With
two or more arguments, divides the first argument by all subsequent ones.
Division of exact integers produces exact rationals rather than inexact
flonums: `(/ 1 3)` returns `1/3`, not `0.333...`. Division by zero
raises an error that can be caught with `guard`.

```scheme
kaappi> (/ 10 2)
;=> 5
kaappi> (/ 1 3)
;=> 1/3
kaappi> (/ 4)
;=> 1/4
kaappi> (/ 10 3)
;=> 10/3
kaappi> (/ 6.0 2.0)
;=> 3.0
```

!!! note
    Exact integer division always produces an exact result. Use
    `(inexact (/ 1 3))` if you need a flonum.

**See also:** [`quotient`](./numbers.md#quotient), [`remainder`](./numbers.md#remainder), [`floor/`](./numbers.md#floor-div)

---

### `quotient` { #quotient }

**Syntax:** `(quotient n1 n2)`

Returns the integer quotient of `n1` divided by `n2`, truncated toward
zero. This is the same operation as `truncate-quotient`. Works with
fixnums, bignums, and flonums. Division by zero raises an error.

```scheme
kaappi> (quotient 10 3)
;=> 3
kaappi> (quotient -10 3)
;=> -3
kaappi> (quotient 10 -3)
;=> -3
```

**See also:** [`remainder`](./numbers.md#remainder), [`modulo`](./numbers.md#modulo), [`truncate-quotient`](./numbers.md#truncate-quotient)

---

### `remainder` { #remainder }

**Syntax:** `(remainder n1 n2)`

Returns the remainder after dividing `n1` by `n2` with truncation toward
zero. The sign of the result always matches the sign of `n1`. This is
the same operation as `truncate-remainder`.

```scheme
kaappi> (remainder 10 3)
;=> 1
kaappi> (remainder -10 3)
;=> -1
kaappi> (remainder 10 -3)
;=> 1
```

**See also:** [`quotient`](./numbers.md#quotient), [`modulo`](./numbers.md#modulo), [`truncate-remainder`](./numbers.md#truncate-remainder)

---

### `modulo` { #modulo }

**Syntax:** `(modulo n1 n2)`

Returns the modulo of `n1` divided by `n2`. Unlike `remainder`, the sign
of the result always matches the sign of `n2`. This makes `modulo` useful
for cyclic arithmetic (e.g., clock calculations). Works with fixnums,
bignums, and flonums.

```scheme
kaappi> (modulo 10 3)
;=> 1
kaappi> (modulo -10 3)
;=> 2
kaappi> (modulo 10 -3)
;=> -2
```

**See also:** [`remainder`](./numbers.md#remainder), [`floor-remainder`](./numbers.md#floor-remainder)

---

## Comparisons

### `=` { #num-equal }

**Syntax:** `(= z1 z2 z3 ...)`

Returns `#t` if all arguments are numerically equal. Compares across
number types: `(= 1 1.0)` is `#t`. Comparisons involving `NaN` always
return `#f`. Complex numbers are compared component-wise.

```scheme
kaappi> (= 1 1)
;=> #t
kaappi> (= 1 1.0)
;=> #t
kaappi> (= 1 2)
;=> #f
kaappi> (= +nan.0 +nan.0)
;=> #f
```

**See also:** [`<`](./numbers.md#num-lt), [`>`](./numbers.md#num-gt)

---

### `<` { #num-lt }

**Syntax:** `(< x1 x2 x3 ...)`

Returns `#t` if the arguments are monotonically increasing (each
argument is strictly less than the next). Works with all real number
types. Comparisons involving `NaN` return `#f`.

```scheme
kaappi> (< 1 2 3)
;=> #t
kaappi> (< 1 2.5)
;=> #t
kaappi> (< 1 1)
;=> #f
```

**See also:** [`<=`](./numbers.md#num-le), [`>`](./numbers.md#num-gt)

---

### `>` { #num-gt }

**Syntax:** `(> x1 x2 x3 ...)`

Returns `#t` if the arguments are monotonically decreasing (each
argument is strictly greater than the next). Works with all real number
types. Comparisons involving `NaN` return `#f`.

```scheme
kaappi> (> 3 2 1)
;=> #t
kaappi> (> 3.5 2)
;=> #t
kaappi> (> 1 1)
;=> #f
```

**See also:** [`>=`](./numbers.md#num-ge), [`<`](./numbers.md#num-lt)

---

### `<=` { #num-le }

**Syntax:** `(<= x1 x2 x3 ...)`

Returns `#t` if the arguments are monotonically non-decreasing (each
argument is less than or equal to the next). Works with all real number
types. Comparisons involving `NaN` return `#f`.

```scheme
kaappi> (<= 1 1 2)
;=> #t
kaappi> (<= 1 1.0)
;=> #t
kaappi> (<= 2 1)
;=> #f
```

**See also:** [`<`](./numbers.md#num-lt), [`>=`](./numbers.md#num-ge)

---

### `>=` { #num-ge }

**Syntax:** `(>= x1 x2 x3 ...)`

Returns `#t` if the arguments are monotonically non-increasing (each
argument is greater than or equal to the next). Works with all real
number types. Comparisons involving `NaN` return `#f`.

```scheme
kaappi> (>= 2 1 1)
;=> #t
kaappi> (>= 2.0 2)
;=> #t
kaappi> (>= 1 2)
;=> #f
```

**See also:** [`>`](./numbers.md#num-gt), [`<=`](./numbers.md#num-le)

---

## Predicates

### `zero?` { #zero }

**Syntax:** `(zero? z)`

Returns `#t` if `z` is zero. Works with fixnums, flonums, bignums, and
complex numbers (both real and imaginary parts must be zero).

```scheme
kaappi> (zero? 0)
;=> #t
kaappi> (zero? 0.0)
;=> #t
kaappi> (zero? 1)
;=> #f
```

---

### `positive?` { #positive }

**Syntax:** `(positive? x)`

Returns `#t` if `x` is strictly greater than zero. Works with fixnums,
flonums, bignums, and rationals. For rationals, the sign is determined by
the numerator (the denominator is always positive).

```scheme
kaappi> (positive? 1)
;=> #t
kaappi> (positive? 1.5)
;=> #t
kaappi> (positive? 0)
;=> #f
kaappi> (positive? -1)
;=> #f
```

**See also:** [`negative?`](./numbers.md#negative), [`zero?`](./numbers.md#zero)

---

### `negative?` { #negative }

**Syntax:** `(negative? x)`

Returns `#t` if `x` is strictly less than zero. Works with fixnums,
flonums, bignums, and rationals.

```scheme
kaappi> (negative? -1)
;=> #t
kaappi> (negative? -2.3)
;=> #t
kaappi> (negative? 0)
;=> #f
kaappi> (negative? 1)
;=> #f
```

**See also:** [`positive?`](./numbers.md#positive), [`zero?`](./numbers.md#zero)

---

### `even?` { #even }

**Syntax:** `(even? n)`

Returns `#t` if the integer `n` is even. Works with fixnums, bignums,
and integer-valued flonums.

```scheme
kaappi> (even? 4)
;=> #t
kaappi> (even? 5)
;=> #f
kaappi> (even? 0)
;=> #t
```

**See also:** [`odd?`](./numbers.md#odd)

---

### `odd?` { #odd }

**Syntax:** `(odd? n)`

Returns `#t` if the integer `n` is odd. Works with fixnums, bignums,
and integer-valued flonums.

```scheme
kaappi> (odd? 3)
;=> #t
kaappi> (odd? 4)
;=> #f
```

**See also:** [`even?`](./numbers.md#even)

---

### `exact?` { #exact-pred }

**Syntax:** `(exact? z)`

Returns `#t` if `z` is an exact number: fixnums, bignums, and exact
rationals are exact. Flonums are inexact. Complex numbers are exact only
when both parts carry the exact flag.

```scheme
kaappi> (exact? 42)
;=> #t
kaappi> (exact? 3.14)
;=> #f
kaappi> (exact? 1/3)
;=> #t
```

**See also:** [`inexact?`](./numbers.md#inexact-pred), [`exact`](./numbers.md#exact)

---

### `inexact?` { #inexact-pred }

**Syntax:** `(inexact? z)`

Returns `#t` if `z` is an inexact number. Flonums are inexact. Complex
numbers are inexact if either part is inexact.

```scheme
kaappi> (inexact? 3.14)
;=> #t
kaappi> (inexact? 42)
;=> #f
```

**See also:** [`exact?`](./numbers.md#exact-pred), [`inexact`](./numbers.md#inexact)

---

### `exact-integer?` { #exact-integer }

**Syntax:** `(exact-integer? z)`

Returns `#t` if `z` is both exact and an integer. Fixnums and bignums
return `#t`; flonums (even integer-valued ones like `3.0`) return `#f`.

```scheme
kaappi> (exact-integer? 42)
;=> #t
kaappi> (exact-integer? 3.0)
;=> #f
kaappi> (exact-integer? 1/3)
;=> #f
```

---

### `finite?` { #finite }

**Syntax:** `(finite? z)`

Returns `#t` if `z` is finite. All exact numbers (fixnums, bignums,
rationals) are always finite. Flonums are finite unless they are
`+inf.0`, `-inf.0`, or `+nan.0`. For complex numbers, both parts must
be finite.

```scheme
kaappi> (finite? 1)
;=> #t
kaappi> (finite? +inf.0)
;=> #f
kaappi> (finite? +nan.0)
;=> #f
```

**See also:** [`infinite?`](./numbers.md#infinite), [`nan?`](./numbers.md#nan)

---

### `infinite?` { #infinite }

**Syntax:** `(infinite? z)`

Returns `#t` if `z` is positive or negative infinity. Exact numbers are
never infinite. For complex numbers, returns `#t` if either part is
infinite.

```scheme
kaappi> (infinite? +inf.0)
;=> #t
kaappi> (infinite? -inf.0)
;=> #t
kaappi> (infinite? 42)
;=> #f
```

**See also:** [`finite?`](./numbers.md#finite), [`nan?`](./numbers.md#nan)

---

### `nan?` { #nan }

**Syntax:** `(nan? z)`

Returns `#t` if `z` is NaN (Not a Number). Exact numbers are never NaN.
For complex numbers, returns `#t` if either part is NaN.

```scheme
kaappi> (nan? +nan.0)
;=> #t
kaappi> (nan? 42)
;=> #f
kaappi> (nan? 3.14)
;=> #f
```

**See also:** [`finite?`](./numbers.md#finite), [`infinite?`](./numbers.md#infinite)

---

## Min / Max / Abs

### `abs` { #abs }

**Syntax:** `(abs x)`

Returns the absolute value of `x`. Works with fixnums, bignums, flonums,
and rationals. For rationals, only the numerator's sign changes (the
denominator is always positive).

```scheme
kaappi> (abs -7)
;=> 7
kaappi> (abs 7)
;=> 7
kaappi> (abs -3.5)
;=> 3.5
```

**See also:** [`magnitude`](./numbers.md#magnitude)

---

### `min` { #min }

**Syntax:** `(min x1 x2 ...)`

Returns the smallest of its arguments. If any argument is inexact, the
result is inexact. Works with fixnums, bignums, flonums, and rationals.

```scheme
kaappi> (min 3 1 2)
;=> 1
kaappi> (min 1 2.5 0.5)
;=> 0.5
```

**See also:** [`max`](./numbers.md#max)

---

### `max` { #max }

**Syntax:** `(max x1 x2 ...)`

Returns the largest of its arguments. If any argument is inexact, the
result is inexact. Works with fixnums, bignums, flonums, and rationals.

```scheme
kaappi> (max 3 1 2)
;=> 3
kaappi> (max 1 2.5 0.5)
;=> 2.5
```

**See also:** [`min`](./numbers.md#min)

---

## GCD / LCM

### `gcd` { #gcd }

**Syntax:** `(gcd n1 ...)`

Returns the greatest common divisor of its arguments. With no arguments,
returns `0`. The result is always non-negative. Works with fixnums,
bignums, and flonums (which return an inexact result).

```scheme
kaappi> (gcd 32 -36)
;=> 4
kaappi> (gcd 12 18 24)
;=> 6
kaappi> (gcd)
;=> 0
```

**See also:** [`lcm`](./numbers.md#lcm)

---

### `lcm` { #lcm }

**Syntax:** `(lcm n1 ...)`

Returns the least common multiple of its arguments. With no arguments,
returns `1`. The result is always non-negative. Works with fixnums,
bignums, and flonums. Computed as `|a * b| / gcd(a, b)`.

```scheme
kaappi> (lcm 4 6)
;=> 12
kaappi> (lcm 3 5 7)
;=> 105
kaappi> (lcm)
;=> 1
```

**See also:** [`gcd`](./numbers.md#gcd)

---

## Rounding

### `floor` { #floor }

**Syntax:** `(floor x)`

Returns the largest integer not greater than `x`. For exact integers
(fixnums and bignums), returns the argument unchanged. For rationals,
returns an exact integer. For flonums, returns an inexact integer.

```scheme
kaappi> (floor 3.7)
;=> 3.0
kaappi> (floor -3.7)
;=> -4.0
kaappi> (floor 42)
;=> 42
```

**See also:** [`ceiling`](./numbers.md#ceiling), [`truncate`](./numbers.md#truncate), [`round`](./numbers.md#round)

---

### `ceiling` { #ceiling }

**Syntax:** `(ceiling x)`

Returns the smallest integer not less than `x`. For exact integers,
returns the argument unchanged. For rationals, returns an exact integer.
For flonums, returns an inexact integer.

```scheme
kaappi> (ceiling 3.2)
;=> 4.0
kaappi> (ceiling -3.2)
;=> -3.0
kaappi> (ceiling 42)
;=> 42
```

**See also:** [`floor`](./numbers.md#floor), [`truncate`](./numbers.md#truncate), [`round`](./numbers.md#round)

---

### `truncate` { #truncate }

**Syntax:** `(truncate x)`

Returns the integer closest to `x` whose absolute value is not greater
than `|x|` -- that is, it rounds toward zero. For exact integers,
returns the argument unchanged. For rationals, returns an exact integer.
For flonums, returns an inexact integer.

```scheme
kaappi> (truncate 3.7)
;=> 3.0
kaappi> (truncate -3.7)
;=> -3.0
kaappi> (truncate 42)
;=> 42
```

**See also:** [`floor`](./numbers.md#floor), [`ceiling`](./numbers.md#ceiling), [`round`](./numbers.md#round)

---

### `round` { #round }

**Syntax:** `(round x)`

Rounds `x` to the nearest integer. When `x` is exactly halfway between
two integers, Kaappi uses banker's rounding (round to even): `(round 0.5)`
returns `0.0` while `(round 1.5)` returns `2.0`. For exact integers,
returns the argument unchanged. For rationals, returns an exact integer.

```scheme
kaappi> (round 3.5)
;=> 4.0
kaappi> (round 4.5)
;=> 4.0
kaappi> (round 3.2)
;=> 3.0
kaappi> (round -3.7)
;=> -4.0
```

!!! note
    Kaappi implements banker's rounding (round half to even) as required
    by R7RS. This avoids the statistical bias of always rounding 0.5 upward.

**See also:** [`floor`](./numbers.md#floor), [`ceiling`](./numbers.md#ceiling), [`truncate`](./numbers.md#truncate)

---

## Exactness

### `exact` { #exact }

**Syntax:** `(exact z)`

Converts `z` to its exact representation. Fixnums, bignums, and
rationals are returned as-is. Integer-valued flonums become fixnums;
other flonums are converted to exact rationals using 2^52 scaling.
Raises an error for `+inf.0`, `-inf.0`, and `+nan.0` since these have
no exact representation.

```scheme
kaappi> (exact 3.0)
;=> 3
kaappi> (exact 0.5)
;=> 1/2
kaappi> (exact 42)
;=> 42
```

**See also:** [`inexact`](./numbers.md#inexact), [`inexact->exact`](./numbers.md#inexact-to-exact)

---

### `inexact` { #inexact }

**Syntax:** `(inexact z)`

Converts `z` to its inexact (flonum) representation. Flonums are
returned as-is. Fixnums and bignums are converted to the nearest f64.
Rationals are divided to produce a flonum.

```scheme
kaappi> (inexact 42)
;=> 42.0
kaappi> (inexact 1/3)
;=> 0.3333333333333333
kaappi> (inexact 3.14)
;=> 3.14
```

**See also:** [`exact`](./numbers.md#exact), [`exact->inexact`](./numbers.md#exact-to-inexact)

---

### `exact->inexact` { #exact-to-inexact }

**Syntax:** `(exact->inexact z)`

Alias for `inexact`. Converts an exact number to its inexact
representation. Provided for R5RS compatibility.

```scheme
kaappi> (exact->inexact 1/3)
;=> 0.3333333333333333
```

**See also:** [`inexact`](./numbers.md#inexact), [`inexact->exact`](./numbers.md#inexact-to-exact)

---

### `inexact->exact` { #inexact-to-exact }

**Syntax:** `(inexact->exact z)`

Alias for `exact`. Converts an inexact number to its exact
representation. Provided for R5RS compatibility.

```scheme
kaappi> (inexact->exact 0.5)
;=> 1/2
```

**See also:** [`exact`](./numbers.md#exact), [`exact->inexact`](./numbers.md#exact-to-inexact)

---

## Powers and Roots

### `expt` { #expt }

**Syntax:** `(expt z1 z2)`

Returns `z1` raised to the power `z2`. When both arguments are exact
integers and the exponent is non-negative, the result is exact (using
bignum arithmetic for large results). A negative exact exponent produces
an exact rational. Complex exponentiation uses the formula
`z^w = e^(w * ln(z))`.

```scheme
kaappi> (expt 2 10)
;=> 1024
kaappi> (expt 2 -1)
;=> 1/2
kaappi> (expt 2.0 0.5)
;=> 1.4142135623730951
```

**See also:** [`square`](./numbers.md#square), [`sqrt`](./numbers.md#sqrt)

---

### `square` { #square }

**Syntax:** `(square z)`

Returns `z * z`. This is more readable than `(* z z)` and the
implementation handles fixnum overflow by promoting to bignums. Also
works with flonums and exact rationals.

```scheme
kaappi> (square 5)
;=> 25
kaappi> (square 2.5)
;=> 6.25
kaappi> (square 1/3)
;=> 1/9
```

**See also:** [`expt`](./numbers.md#expt), [`sqrt`](./numbers.md#sqrt)

---

### `sqrt` { #sqrt }

**Syntax:** `(sqrt z)`

Returns the principal square root of `z`. For negative real numbers,
the result is a complex number: `(sqrt -1)` returns `0+1i`. For exact
integers that are perfect squares, the result is an exact integer.
Otherwise the result is a flonum. Also handles complex arguments.

```scheme
kaappi> (sqrt 4)
;=> 2
kaappi> (sqrt 2.0)
;=> 1.4142135623730951
kaappi> (sqrt -1)
;=> 0+1i
kaappi> (sqrt 9)
;=> 3
```

**See also:** [`exact-integer-sqrt`](./numbers.md#exact-integer-sqrt), [`expt`](./numbers.md#expt)

---

### `exact-integer-sqrt` { #exact-integer-sqrt }

**Syntax:** `(exact-integer-sqrt k)`

Returns two values: the largest integer `s` such that `s^2 <= k`, and
the remainder `k - s^2`. The argument `k` must be a non-negative exact
integer. Works with both fixnums and bignums (using Newton's method for
large values).

```scheme
kaappi> (exact-integer-sqrt 14)
;=> 3
;=> 5
kaappi> (exact-integer-sqrt 4)
;=> 2
;=> 0
kaappi> (exact-integer-sqrt 0)
;=> 0
;=> 0
```

!!! note
    `exact-integer-sqrt` returns two values. Use `call-with-values` or
    `let-values` to capture both the root and the remainder.

**See also:** [`sqrt`](./numbers.md#sqrt)

---

## Trigonometry

### `sin` { #sin }

**Syntax:** `(sin z)`

Returns the sine of `z` in radians. The result is always an inexact
flonum.

```scheme
kaappi> (sin 0)
;=> 0.0
kaappi> (sin 1.5707963267948966)
;=> 1.0
```

**See also:** [`cos`](./numbers.md#cos), [`tan`](./numbers.md#tan), [`asin`](./numbers.md#asin)

---

### `cos` { #cos }

**Syntax:** `(cos z)`

Returns the cosine of `z` in radians. The result is always an inexact
flonum.

```scheme
kaappi> (cos 0)
;=> 1.0
kaappi> (cos 3.141592653589793)
;=> -1.0
```

**See also:** [`sin`](./numbers.md#sin), [`tan`](./numbers.md#tan), [`acos`](./numbers.md#acos)

---

### `tan` { #tan }

**Syntax:** `(tan z)`

Returns the tangent of `z` in radians. The result is always an inexact
flonum.

```scheme
kaappi> (tan 0)
;=> 0.0
kaappi> (tan 0.7853981633974483)
;=> 1.0
```

**See also:** [`sin`](./numbers.md#sin), [`cos`](./numbers.md#cos), [`atan`](./numbers.md#atan)

---

### `asin` { #asin }

**Syntax:** `(asin z)`

Returns the arcsine of `z` in radians. The argument should be in the
range [-1, 1]. The result is always an inexact flonum.

```scheme
kaappi> (asin 0)
;=> 0.0
kaappi> (asin 1)
;=> 1.5707963267948966
```

**See also:** [`sin`](./numbers.md#sin), [`acos`](./numbers.md#acos), [`atan`](./numbers.md#atan)

---

### `acos` { #acos }

**Syntax:** `(acos z)`

Returns the arccosine of `z` in radians. The argument should be in the
range [-1, 1]. The result is always an inexact flonum.

```scheme
kaappi> (acos 1)
;=> 0.0
kaappi> (acos 0)
;=> 1.5707963267948966
```

**See also:** [`cos`](./numbers.md#cos), [`asin`](./numbers.md#asin), [`atan`](./numbers.md#atan)

---

### `atan` { #atan }

**Syntax:** `(atan z)` or `(atan y x)`

With one argument, returns the arctangent of `z` in radians. With two
arguments, returns the angle in radians between the positive x-axis and
the point `(x, y)`, equivalent to C's `atan2(y, x)`. The two-argument
form correctly handles all quadrants and the case where `x` is zero.

```scheme
kaappi> (atan 1.0)
;=> 0.7853981633974483
kaappi> (atan 0 1)
;=> 0.0
kaappi> (atan 1 0)
;=> 1.5707963267948966
kaappi> (atan -1 -1)
;=> -2.356194490192345
```

**See also:** [`tan`](./numbers.md#tan), [`asin`](./numbers.md#asin), [`acos`](./numbers.md#acos)

---

## Exponentials

### `exp` { #exp }

**Syntax:** `(exp z)`

Returns e raised to the power `z`. The result is always an inexact
flonum.

```scheme
kaappi> (exp 0)
;=> 1.0
kaappi> (exp 1)
;=> 2.718281828459045
```

**See also:** [`log`](./numbers.md#log)

---

### `log` { #log }

**Syntax:** `(log z)` or `(log z base)`

With one argument, returns the natural logarithm (base e) of `z`. With
two arguments, returns the logarithm of `z` in the given base, computed
as `(/ (log z) (log base))`. The result is always an inexact flonum.

```scheme
kaappi> (log 1)
;=> 0.0
kaappi> (log 2.718281828459045)
;=> 1.0
kaappi> (log 8 2)
;=> 3.0
kaappi> (log 100 10)
;=> 2.0
```

**See also:** [`exp`](./numbers.md#exp)

---

## Conversion

### `number->string` { #number-to-string }

**Syntax:** `(number->string z)` or `(number->string z radix)`

Converts the number `z` to its string representation. The optional
`radix` argument (default 10) specifies the base for integer output;
valid values range from 2 to 36. Works with fixnums, bignums, rationals,
flonums, and complex numbers.

```scheme
kaappi> (number->string 42)
;=> "42"
kaappi> (number->string 3.14)
;=> "3.14"
kaappi> (number->string 255 16)
;=> "ff"
kaappi> (number->string 42 2)
;=> "101010"
kaappi> (number->string +inf.0)
;=> "+inf.0"
```

**See also:** [`string->number`](./numbers.md#string-to-number)

---

### `string->number` { #string-to-number }

**Syntax:** `(string->number string)` or `(string->number string radix)`

Parses `string` as a number and returns the result. Returns `#f` if the
string cannot be parsed. The optional `radix` argument (default 10)
specifies the base for integer parsing; valid values are 2, 8, 10, and
16. Recognizes special float syntax (`+inf.0`, `-inf.0`, `+nan.0`),
rational syntax (`1/3`), and complex number syntax (`3+4i`).

```scheme
kaappi> (string->number "42")
;=> 42
kaappi> (string->number "3.14")
;=> 3.14
kaappi> (string->number "ff" 16)
;=> 255
kaappi> (string->number "101010" 2)
;=> 42
kaappi> (string->number "hello")
;=> #f
kaappi> (string->number "+inf.0")
;=> +inf.0
```

**See also:** [`number->string`](./numbers.md#number-to-string)

---

## Integer Division

### `floor-quotient` { #floor-quotient }

**Syntax:** `(floor-quotient n1 n2)`

Returns the integer quotient of `n1` divided by `n2`, rounded toward
negative infinity. This differs from `quotient`/`truncate-quotient` when
the arguments have different signs. Works with fixnums, bignums, and
flonums.

```scheme
kaappi> (floor-quotient 7 2)
;=> 3
kaappi> (floor-quotient -7 2)
;=> -4
kaappi> (floor-quotient 7 -2)
;=> -4
```

**See also:** [`floor-remainder`](./numbers.md#floor-remainder), [`floor/`](./numbers.md#floor-div), [`truncate-quotient`](./numbers.md#truncate-quotient)

---

### `floor-remainder` { #floor-remainder }

**Syntax:** `(floor-remainder n1 n2)`

Returns the remainder from floor division. The sign of the result always
matches the sign of `n2`. This is equivalent to `modulo` for integers.
Works with fixnums, bignums, and flonums.

```scheme
kaappi> (floor-remainder 7 2)
;=> 1
kaappi> (floor-remainder -7 2)
;=> 1
kaappi> (floor-remainder 7 -2)
;=> -1
```

**See also:** [`floor-quotient`](./numbers.md#floor-quotient), [`floor/`](./numbers.md#floor-div), [`truncate-remainder`](./numbers.md#truncate-remainder)

---

### `floor/` { #floor-div }

**Syntax:** `(floor/ n1 n2)`

Returns two values: the floor quotient and the floor remainder of `n1`
divided by `n2`. Equivalent to calling `floor-quotient` and
`floor-remainder` together but may be more efficient.

```scheme
kaappi> (floor/ 7 2)
;=> 3
;=> 1
kaappi> (floor/ -7 2)
;=> -4
;=> 1
```

**See also:** [`floor-quotient`](./numbers.md#floor-quotient), [`floor-remainder`](./numbers.md#floor-remainder), [`truncate/`](./numbers.md#truncate-div)

---

### `truncate-quotient` { #truncate-quotient }

**Syntax:** `(truncate-quotient n1 n2)`

Returns the integer quotient of `n1` divided by `n2`, truncated toward
zero. This is the same operation as `quotient`. Works with fixnums,
bignums, and flonums.

```scheme
kaappi> (truncate-quotient 7 2)
;=> 3
kaappi> (truncate-quotient -7 2)
;=> -3
kaappi> (truncate-quotient 7 -2)
;=> -3
```

**See also:** [`truncate-remainder`](./numbers.md#truncate-remainder), [`truncate/`](./numbers.md#truncate-div), [`floor-quotient`](./numbers.md#floor-quotient)

---

### `truncate-remainder` { #truncate-remainder }

**Syntax:** `(truncate-remainder n1 n2)`

Returns the remainder from truncated division. The sign of the result
always matches the sign of `n1`. This is the same operation as
`remainder`. Works with fixnums, bignums, and flonums.

```scheme
kaappi> (truncate-remainder 7 2)
;=> 1
kaappi> (truncate-remainder -7 2)
;=> -1
kaappi> (truncate-remainder 7 -2)
;=> 1
```

**See also:** [`truncate-quotient`](./numbers.md#truncate-quotient), [`truncate/`](./numbers.md#truncate-div), [`floor-remainder`](./numbers.md#floor-remainder)

---

### `truncate/` { #truncate-div }

**Syntax:** `(truncate/ n1 n2)`

Returns two values: the truncated quotient and the truncated remainder
of `n1` divided by `n2`. Equivalent to calling `truncate-quotient` and
`truncate-remainder` together.

```scheme
kaappi> (truncate/ 7 2)
;=> 3
;=> 1
kaappi> (truncate/ -7 2)
;=> -3
;=> -1
```

**See also:** [`truncate-quotient`](./numbers.md#truncate-quotient), [`truncate-remainder`](./numbers.md#truncate-remainder), [`floor/`](./numbers.md#floor-div)

---

## Rationals

### `numerator` { #numerator }

**Syntax:** `(numerator q)`

Returns the numerator of the rational number `q`. For integers, the
numerator is the integer itself. For flonums, converts to the best
rational approximation first and returns an inexact numerator.

```scheme
kaappi> (numerator 1/3)
;=> 1
kaappi> (numerator 5)
;=> 5
kaappi> (numerator -2/3)
;=> -2
kaappi> (numerator 0.5)
;=> 1.0
```

**See also:** [`denominator`](./numbers.md#denominator), [`rationalize`](./numbers.md#rationalize)

---

### `denominator` { #denominator }

**Syntax:** `(denominator q)`

Returns the denominator of the rational number `q`. For integers, the
denominator is always `1`. For flonums, converts to the best rational
approximation first and returns an inexact denominator.

```scheme
kaappi> (denominator 1/3)
;=> 3
kaappi> (denominator 5)
;=> 1
kaappi> (denominator 0.5)
;=> 2.0
```

**See also:** [`numerator`](./numbers.md#numerator), [`rationalize`](./numbers.md#rationalize)

---

### `rationalize` { #rationalize }

**Syntax:** `(rationalize x y)`

Returns the simplest rational number that differs from `x` by no more
than `y`. "Simplest" means the rational with the smallest denominator
within the tolerance interval `[x - |y|, x + |y|]`. If an integer falls
within the interval, that integer is returned (since integers have
denominator 1). When `x` is exact, the result is exact; when `x` is
inexact, the result is inexact.

```scheme
kaappi> (rationalize 3/10 1/10)
;=> 1/3
kaappi> (rationalize 0.3 1/10)
;=> 0.3333333333333333
```

**See also:** [`numerator`](./numbers.md#numerator), [`denominator`](./numbers.md#denominator)

---

## Complex Numbers

### `make-rectangular` { #make-rectangular }

**Syntax:** `(make-rectangular x1 x2)`

Constructs a complex number from real part `x1` and imaginary part `x2`.
If `x2` is zero, returns a real number instead. The exactness of each
part is preserved from the input arguments.

```scheme
kaappi> (make-rectangular 3 4)
;=> 3+4i
kaappi> (make-rectangular 1 0)
;=> 1
kaappi> (make-rectangular 0 1)
;=> 0+1i
```

**See also:** [`make-polar`](./numbers.md#make-polar), [`real-part`](./numbers.md#real-part), [`imag-part`](./numbers.md#imag-part)

---

### `make-polar` { #make-polar }

**Syntax:** `(make-polar mag ang)`

Constructs a complex number from magnitude `mag` and angle `ang` (in
radians). Computes `real = mag * cos(ang)` and `imag = mag * sin(ang)`.
If the imaginary part is zero, returns a real number.

```scheme
kaappi> (make-polar 1 0)
;=> 1.0
kaappi> (make-polar 1 1.5707963267948966)
;=> 0+1i
```

**See also:** [`make-rectangular`](./numbers.md#make-rectangular), [`magnitude`](./numbers.md#magnitude), [`angle`](./numbers.md#angle)

---

### `real-part` { #real-part }

**Syntax:** `(real-part z)`

Returns the real part of the complex number `z`. For real numbers
(fixnums and flonums), returns the argument itself. For exact complex
numbers whose real part is integer-valued, returns an exact integer.

```scheme
kaappi> (real-part 3+4i)
;=> 3
kaappi> (real-part 5)
;=> 5
kaappi> (real-part 3.14)
;=> 3.14
```

**See also:** [`imag-part`](./numbers.md#imag-part), [`make-rectangular`](./numbers.md#make-rectangular)

---

### `imag-part` { #imag-part }

**Syntax:** `(imag-part z)`

Returns the imaginary part of the complex number `z`. For real numbers,
returns `0` (exact) for fixnums or `0.0` (inexact) for flonums. For
exact complex numbers whose imaginary part is integer-valued, returns an
exact integer.

```scheme
kaappi> (imag-part 3+4i)
;=> 4
kaappi> (imag-part 5)
;=> 0
kaappi> (imag-part 3.14)
;=> 0.0
```

**See also:** [`real-part`](./numbers.md#real-part), [`make-rectangular`](./numbers.md#make-rectangular)

---

### `magnitude` { #magnitude }

**Syntax:** `(magnitude z)`

Returns the magnitude (absolute value) of `z`. For complex numbers,
this is `sqrt(real^2 + imag^2)`. For real numbers, this is the absolute
value. Fixnum inputs return exact fixnum results; all other inputs return
flonums.

```scheme
kaappi> (magnitude 3+4i)
;=> 5.0
kaappi> (magnitude -5)
;=> 5
kaappi> (magnitude 3.0)
;=> 3.0
```

**See also:** [`angle`](./numbers.md#angle), [`abs`](./numbers.md#abs)

---

### `angle` { #angle }

**Syntax:** `(angle z)`

Returns the angle (argument) of the complex number `z` in radians. For
complex numbers, this is `atan2(imag, real)`. For non-negative reals,
returns `0.0`. For negative reals, returns pi.

```scheme
kaappi> (angle 0+1i)
;=> 1.5707963267948966
kaappi> (angle 1)
;=> 0.0
kaappi> (angle -1)
;=> 3.141592653589793
```

**See also:** [`magnitude`](./numbers.md#magnitude), [`make-polar`](./numbers.md#make-polar)

---
