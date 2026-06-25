# Creating Zig Extension Libraries

Kaappi extensions can be written in Zig instead of C. Since Kaappi's FFI
uses `dlopen`/`dlsym` with the C calling convention, any language that
produces shared libraries with C-ABI exports works — and Zig excels at
this.

For C extensions, see [Creating C Extension Libraries](c-extensions.md).

## Why Zig?

- **Memory safety** — bounds checking, no buffer overflows, optional types
- **Cross-compilation** — build for Linux from macOS with a single command
- **No separate toolchain** — Zig bundles libc for all major platforms
- **Familiar** — Kaappi itself is written in Zig, so the tooling is already set up
- **Performance** — equivalent to C, same LLVM backend

## Directory layout

```
kaappi-mylib/
├── build.zig             # Zig build configuration
├── build.zig.zon         # Zig package manifest
├── kaappi.pkg            # Kaappi package manifest
├── src/
│   └── mylib.zig         # Zig implementation
├── lib/kaappi/
│   ├── mylib.sld         # high-level Scheme API
│   └── mylib/
│       └── ffi.sld       # low-level FFI bindings
└── tests/
    └── test-mylib.scm
```

## Step 1: Write the Zig code

Create `src/mylib.zig`. Functions called from Scheme must use `export`
and C-compatible types:

```zig
const std = @import("std");

export fn mylib_add(a: c_int, b: c_int) c_int {
    return a + b;
}

export fn mylib_distance(x: f64, y: f64) f64 {
    return std.math.sqrt(x * x + y * y);
}

export fn mylib_strlen(s: [*:0]const u8) c_long {
    return @intCast(std.mem.len(s));
}

export fn mylib_reverse(s: [*:0]const u8) [*:0]const u8 {
    const len = std.mem.len(s);
    if (len == 0) return s;
    var buf = std.heap.c_allocator.allocSentinel(u8, len, 0) catch return s;
    for (0..len) |i| {
        buf[i] = s[len - 1 - i];
    }
    return buf.ptr;
}
```

### Type mapping

Use these Zig types to match Kaappi's FFI:

| FFI symbol | Zig type | Notes |
|-----------|----------|-------|
| `'int` | `c_int` | |
| `'long` | `c_long` | |
| `'double` | `f64` | |
| `'float` | `f32` | |
| `'string` | `[*:0]const u8` | null-terminated, not Zig slices |
| `'pointer` | `?*anyopaque` | |
| `'void` | `void` | |
| `'bool` | `c_int` | 0 = false, 1 = true |
| `'int8` ... `'int64` | `i8` ... `i64` | |
| `'uint8` ... `'uint64` | `u8` ... `u64` | |
| `'size_t` | `usize` | |

Functions can take up to 5 parameters.

### String handling

Kaappi's FFI passes strings as null-terminated `[*:0]const u8`, not Zig
slices. To use Zig string operations, convert with `std.mem.span()`:

```zig
export fn mylib_count_spaces(s: [*:0]const u8) c_int {
    const slice = std.mem.span(s);
    var count: c_int = 0;
    for (slice) |c| {
        if (c == ' ') count += 1;
    }
    return count;
}
```

### Memory management

When returning heap-allocated data, use `std.heap.c_allocator` so the
memory can be freed with standard `free()`:

```zig
export fn mylib_alloc_result() [*:0]const u8 {
    var buf = std.heap.c_allocator.allocSentinel(u8, 64, 0) catch return "";
    // ... fill buf ...
    return buf.ptr;
}

export fn mylib_free_result(ptr: ?*anyopaque) void {
    if (ptr) |p| std.heap.c_allocator.free(@as([*]u8, @ptrCast(p))[0..1]);
}
```

For simple cases, a static buffer works (same pattern as C extensions):

```zig
var result_buf: [256:0]u8 = undefined;

export fn mylib_greet(name: [*:0]const u8) [*:0]const u8 {
    const slice = std.fmt.bufPrintZ(&result_buf, "Hello, {s}!", .{std.mem.span(name)}) catch return "Hello!";
    return slice.ptr;
}
```

## Step 2: Build the shared library

### Option A: Makefile (recommended)

The `zig build-lib` command is stable across Zig versions, while the
`build.zig` API changes between releases. A Makefile is more portable
and matches the pattern used by existing ecosystem libraries.

```makefile
UNAME := $(shell uname)

ifeq ($(UNAME), Darwin)
  DYLIB_EXT := dylib
else
  DYLIB_EXT := so
endif

TARGET := libkaappi_mylib.$(DYLIB_EXT)

all: $(TARGET)

$(TARGET): src/mylib.zig
	zig build-lib src/mylib.zig -dynamic -lc --name kaappi_mylib

clean:
	rm -f libkaappi_mylib.dylib libkaappi_mylib.so

.PHONY: all clean
```

```bash
make                                         # native build
zig build-lib src/mylib.zig -dynamic -lc --name kaappi_mylib -target x86_64-linux  # cross-compile
```

This is what [kaappi-math](https://github.com/kaappi/kaappi-math) uses.

### Option B: build.zig

If you prefer the Zig build system (note: the API may change between
Zig versions):

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const lib = b.addSharedLibrary(.{
        .name = "kaappi_mylib",
        .root_source_file = b.path("src/mylib.zig"),
        .target = target,
        .optimize = optimize,
    });
    lib.linkLibC();
    b.installArtifact(lib);
}
```

```bash
zig build
```

Output: `zig-out/lib/libkaappi_mylib.dylib` (macOS) or `.so` (Linux).

## Step 3: Write the FFI wrapper

Create `lib/kaappi/mylib/ffi.sld`:

```scheme
(define-library (kaappi mylib ffi)
  (import (scheme base) (kaappi ffi))
  (export %add %distance %strlen %reverse)
  (begin
    (define %lib (ffi-open "libkaappi_mylib"))

    (define %add      (ffi-fn %lib "mylib_add"      '(int int) 'int))
    (define %distance (ffi-fn %lib "mylib_distance"  '(double double) 'double))
    (define %strlen   (ffi-fn %lib "mylib_strlen"    '(string) 'long))
    (define %reverse  (ffi-fn %lib "mylib_reverse"   '(string) 'string))))
```

## Step 4: Write the high-level API

Create `lib/kaappi/mylib.sld`:

```scheme
(define-library (kaappi mylib)
  (import (scheme base) (kaappi mylib ffi))
  (export add distance byte-length reverse-string)
  (begin
    (define (add a b) (%add a b))
    (define (distance x y) (%distance (exact->inexact x) (exact->inexact y)))
    (define (byte-length s) (%strlen s))
    (define (reverse-string s) (%reverse s))))
```

## Step 5: Package manifest

Create `kaappi.pkg`:

```
name: kaappi-mylib
build: make
```

## Step 6: Test

```bash
make
kaappi --lib-path ./lib tests/test-mylib.scm
```

## Cross-compilation

One of Zig's strongest advantages — build for any platform from any
platform:

```bash
zig build -Dtarget=x86_64-linux       # Linux x86_64
zig build -Dtarget=aarch64-linux      # Linux ARM
```

No cross-compilation toolchain, sysroot, or Docker needed.

## Comparison with C extensions

| Aspect | C | Zig |
|--------|---|-----|
| Build system | Makefile | build.zig |
| Memory safety | Manual | Bounds-checked, optional types |
| Cross-compilation | Requires toolchain | Built-in |
| Error handling | errno / return codes | Error unions |
| String handling | `char *` | `[*:0]const u8` (explicit) |
| Standard library | libc | Zig std + libc |
| Binary size | Small | ~1-2 MB larger (Zig stdlib) |
| Debugging | gdb/lldb | gdb/lldb + Zig stack traces |
