# Creating C Extension Libraries

This guide walks through building a Kaappi library that wraps C code
via the FFI. The same pattern is used by `kaappi-net`, `kaappi-crypto`,
`kaappi-pg`, `kaappi-sqlite`, and `kaappi-redis`.

## Directory layout

```
kaappi-mylib/
├── Makefile              # builds the shared library
├── kaappi.pkg            # package manifest for thottam
├── csrc/
│   └── kaappi_mylib.c    # C implementation
├── lib/kaappi/
│   ├── mylib.sld         # high-level Scheme API
│   └── mylib/
│       └── ffi.sld       # low-level FFI bindings
└── tests/
    └── test-mylib.scm    # tests
```

## Step 1: Write the C code

Create `csrc/kaappi_mylib.c`. Functions that will be called from Scheme
must use C-compatible types and follow the naming convention
`k<libname>_<function>`:

```c
#include <string.h>
#include <math.h>

/* (double, double) -> double */
double kmylib_distance(double x, double y) {
    return sqrt(x * x + y * y);
}

/* (string) -> int */
int kmylib_length(const char *s) {
    return (int)strlen(s);
}

/* (int, int) -> int */
int kmylib_add(int a, int b) {
    return a + b;
}
```

### Supported C types

| C type | FFI symbol | Scheme type |
|--------|-----------|-------------|
| `int` | `'int` | fixnum |
| `long` | `'long` | fixnum |
| `double` | `'double` | flonum |
| `float` | `'float` | flonum |
| `const char *` | `'string` | string |
| `void *` | `'pointer` | fixnum (address) |
| `void` | `'void` | void |
| `bool` | `'bool` | boolean |
| `int8_t` ... `int64_t` | `'int8` ... `'int64` | fixnum |
| `uint8_t` ... `uint64_t` | `'uint8` ... `'uint64` | fixnum |
| `size_t` | `'size_t` | fixnum |
| `char` | `'char` | fixnum |

Functions can take up to 4 parameters.

## Step 2: Write the Makefile

```makefile
UNAME := $(shell uname)

ifeq ($(UNAME), Darwin)
  DYLIB_EXT  := dylib
  DYLIB_FLAG := -dynamiclib
else
  DYLIB_EXT  := so
  DYLIB_FLAG := -shared -fPIC
endif

TARGET := libkaappi_mylib.$(DYLIB_EXT)

all: $(TARGET)

$(TARGET): csrc/kaappi_mylib.c
	$(CC) $(DYLIB_FLAG) -o $@ $< -O2 -Wall -lm

clean:
	rm -f $(TARGET)

.PHONY: all clean
```

If your C code depends on an external library (e.g., OpenSSL, libpq),
add it via `pkg-config`:

```makefile
SSL_CFLAGS := $(shell pkg-config --cflags openssl 2>/dev/null)
SSL_LIBS   := $(shell pkg-config --libs openssl 2>/dev/null || echo "-lssl -lcrypto")

$(TARGET): csrc/kaappi_mylib.c
	$(CC) $(DYLIB_FLAG) -o $@ $< $(SSL_CFLAGS) $(SSL_LIBS) -O2 -Wall
```

## Step 3: Write the FFI wrapper

Create `lib/kaappi/mylib/ffi.sld` — the low-level bindings that map
each C function to a Scheme procedure:

```scheme
(define-library (kaappi mylib ffi)
  (import (scheme base) (kaappi ffi))
  (export %distance %length %add)
  (begin
    (define %lib (ffi-open "libkaappi_mylib"))

    (define %distance (ffi-fn %lib "kmylib_distance" '(double double) 'double))
    (define %length   (ffi-fn %lib "kmylib_length"   '(string) 'int))
    (define %add      (ffi-fn %lib "kmylib_add"      '(int int) 'int))))
```

`ffi-open` searches for the shared library in this order:
1. The given path as-is
2. With `.dylib` (macOS) or `.so` (Linux) appended
3. `~/.kaappi/lib/` (where thottam installs packages)

## Step 4: Write the high-level API

Create `lib/kaappi/mylib.sld` — the public API that users import.
This layer adds error handling, validation, and Scheme-idiomatic names:

```scheme
(define-library (kaappi mylib)
  (import (scheme base)
          (kaappi mylib ffi))
  (export distance string-byte-length add)
  (begin
    (define (distance x y) (%distance (exact->inexact x) (exact->inexact y)))
    (define (string-byte-length s) (%length s))
    (define (add a b) (%add a b))))
```

Users import only the high-level library:

```scheme
(import (kaappi mylib))
(distance 3 4)          ;=> 5.0
(string-byte-length "hello")  ;=> 5
```

## Step 5: Create the package manifest

Create `kaappi.pkg` at the repo root:

```
name: kaappi-mylib
build: make
```

If your library depends on other Kaappi packages:

```
name: kaappi-mylib
build: make
depends: kaappi-net
```

## Step 6: Test

```bash
make                                         # build the shared library
kaappi --lib-path ./lib tests/test-mylib.scm # run tests
```

A simple test file:

```scheme
(import (scheme base) (scheme write) (kaappi mylib))

(display (distance 3 4))          (newline)  ; 5.0
(display (string-byte-length "hi")) (newline)  ; 2
(display (add 40 2))              (newline)  ; 42
```

## Step 7: Publish

Push to GitHub as `kaappi/<package-name>`, then users install with:

```bash
thottam install kaappi-mylib
```

Thottam clones the repo, runs `make`, and copies the `.dylib`/`.so` and
`.sld` files to `~/.kaappi/lib/`. After installation, `--lib-path` is
not needed.

## FFI callbacks

Pass Scheme procedures to C functions that expect function pointers:

```scheme
(define cb (ffi-callback
             (lambda (a b) (- a b))
             '(pointer pointer)
             'int))
;; Pass cb to a C sorting function, etc.
(ffi-callback-release cb)  ;; free when done
```

## Error handling pattern

C functions typically return negative values on error. Wrap them in
Scheme with error checks:

```c
/* C side */
static int last_err = 0;
int kmylib_connect(const char *host, int port) {
    int fd = do_connect(host, port);
    if (fd < 0) last_err = errno;
    return fd;
}
int kmylib_last_error(void) { return last_err; }
```

```scheme
;; Scheme side
(define %connect    (ffi-fn lib "kmylib_connect"    '(string int) 'int))
(define %last-error (ffi-fn lib "kmylib_last_error" '() 'int))

(define (connect host port)
  (let ((fd (%connect host port)))
    (if (< fd 0)
        (error "connect failed" host port (%last-error))
        fd)))
```
