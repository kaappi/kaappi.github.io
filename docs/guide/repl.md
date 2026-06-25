# REPL Guide

Launch the interactive REPL with no arguments:

```bash
kaappi
```

```
Kaappi Scheme v0.5.0
Type ,help for commands, ,quit to exit.

kaappi> (+ 1 2)
3
kaappi> _
3
```

## Line Editing

The REPL uses [linenoise](https://github.com/antirez/linenoise) for line editing with full terminal support.

| Key | Action |
|-----|--------|
| **Left / Right** | Move cursor |
| **Up / Down** | Navigate history |
| **Ctrl+A** | Move to start of line |
| **Ctrl+E** | Move to end of line |
| **Ctrl+K** | Delete from cursor to end |
| **Ctrl+U** | Delete entire line |
| **Ctrl+W** | Delete previous word |
| **Ctrl+L** | Clear screen |
| **Ctrl+D** | Delete char at cursor (or exit if line empty) |
| **Ctrl+T** | Transpose characters |
| **Tab** | Auto-complete symbol names |
| **Ctrl+R** | Reverse history search |
| **Ctrl+C** | Cancel current line |

## Tab Completion

Press **Tab** to complete symbol names from the global environment:

```
kaappi> string-<TAB>
string-append  string-copy  string-length  string-ref  ...
```

Completion matches all bound symbols — built-in procedures, your own
definitions, and imported library exports.

Comma commands are also completed:

```
kaappi> ,ti<TAB>
,time
```

## History

History is saved automatically to `~/.kaappi/history`. Up to 1000
entries are preserved across sessions.

- **Up / Down arrows** — navigate through previous entries
- **Ctrl+P / Ctrl+N** — same as Up / Down

### Reverse History Search (Ctrl+R)

Press **Ctrl+R** to incrementally search through history, just like bash:

```
kaappi> <Ctrl+R>
(reverse-i-search)'': 
```

Type a search query — matching history entries appear as you type:

```
(reverse-i-search)'def': (define (fib n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2)))))
```

| Key | Action |
|-----|--------|
| *Type characters* | Refine search |
| **Ctrl+R** | Jump to next (older) match |
| **Enter** | Accept the match for editing |
| **Escape** | Cancel and restore original line |
| **Backspace** | Remove last search character |

## Multi-line Input

Expressions with unmatched parentheses automatically continue on the next line:

```
kaappi> (define (square x)
  ...    (* x x))
kaappi> (square 7)
49
```

The prompt changes to `  ... ` while input is incomplete. Press **Ctrl+C** to cancel a multi-line entry.

## The `_` Variable

The special variable `_` always holds the result of the last evaluation:

```
kaappi> (* 6 7)
42
kaappi> (+ _ 8)
50
kaappi> (string-append "answer: " (number->string _))
"answer: 50"
```

This is useful for exploratory programming — evaluate something, then use the result without re-typing or binding it.

## REPL Commands

All commands start with a comma (`,`). They are not Scheme expressions.

### Evaluation

#### `,time <expr>` — Measure execution time

```
kaappi> ,time (fib 30)
832040
; 0.173 seconds
```

#### `,type <expr>` — Show result type

```
kaappi> ,type (+ 1 2)
; integer
kaappi> ,type "hello"
; string
kaappi> ,type (list 1 2 3)
; pair
kaappi> ,type car
; procedure
kaappi> ,type #t
; boolean
```

#### `,expand <expr>` — Show macro expansion

```
kaappi> ,expand (when #t (display "yes"))
(if #t (begin (display "yes")))
```

#### `,profile <expr>` — Detailed profiling

Shows per-function timing, call counts, and memory allocations:

```
kaappi> ,profile (fib 25)
75025
; Profile Report
; ...
```

#### `,dis <expr>` — Disassemble a procedure

Shows the register-based bytecode for a procedure:

```
kaappi> ,dis factorial
; Function: factorial
; Arity: 1, Locals: 7, Upvalues: 0
; Constants: <=, 1, *, factorial, -
;
  0000  move            r2, r0
  0003  load_const      r3, 1
  ...
```

This is a shortcut for `(disassemble <expr>)`. See [Debugging](debugging.md#bytecode-inspection) for details.

### Inspection

#### `,describe <symbol>` — Show binding details

Shows the type, arity, and source location of a procedure:

```
kaappi> ,describe car
  car
    type: procedure
    arity: 1
kaappi> ,describe map
  map
    type: procedure
    arity: 2+
kaappi> ,describe +
  +
    type: procedure
    arity: 0+
```

For user-defined procedures, it also shows the source file and line:

```
kaappi> (define (greet name) (string-append "Hello, " name))
kaappi> ,describe greet
  greet
    type: procedure
    arity: 1, locals: 0
    source: <repl>:1
```

#### `,apropos <string>` — Search bindings

Searches all global bindings for names containing the given substring:

```
kaappi> ,apropos vector
  vector-append
  vector-copy
  vector-fill!
  vector-for-each
  vector-length
  vector-map
  vector-ref
  vector-set!
  vector?
  list->vector
  vector->list
  make-vector
  ...
; 18 matches
```

#### `,env [prefix]` — List bindings

Lists all global bindings, optionally filtered by prefix:

```
kaappi> ,env string-
  string-append
  string-copy
  string-length
  ...
; 24 bindings
```

### Debugging

#### `,break <name>` — Set breakpoint

```
kaappi> ,break fib
Breakpoint set on fib
```

#### `,breakpoints` — List breakpoints

```
kaappi> ,breakpoints
  [0] fib
```

#### `,step <expr>` — Single-step evaluation

```
kaappi> ,step (+ 1 2)
```

#### `,delete all` — Clear all breakpoints

```
kaappi> ,delete all
All breakpoints deleted
```

### System

#### `,gc` — Show GC statistics

```
kaappi> ,gc
GC Statistics:
  Collections:       42
  Live objects:      1523 (peak: 3201)
  Heap size:         48736 bytes (peak: 102400)
  ...
```

#### `,version` — Show Kaappi version

```
kaappi> ,version
Kaappi Scheme v0.5.0
```

#### `,load <file>` — Load and run a Scheme file

```
kaappi> ,load helpers.scm
```

Equivalent to `(load "helpers.scm")`. Definitions in the file become
available in the current REPL session.

#### `,import <lib>` — Import a library

```
kaappi> ,import (srfi 1)
kaappi> (iota 5)
(0 1 2 3 4)
```

Import one or more libraries interactively, just like `(import ...)` at
the top of a program. Supports all import modifiers (`only`, `except`,
`rename`, `prefix`):

```
kaappi> ,import (only (srfi 1) iota fold)
```

#### `,help` — Show all commands

```
kaappi> ,help
Commands:
  ,help             Show this message
  ,quit             Exit the REPL

 -- Evaluation:
  ,time <expr>      Measure execution time
  ,type <expr>      Show result type
  ,expand <expr>    Show macro expansion
  ,profile <expr>   Profile timing, calls, and allocations
  ,dis <expr>       Disassemble a procedure

 -- Inspection:
  ,describe <sym>   Show procedure arity and type
  ,apropos <str>    Search bindings by substring
  ,env [prefix]     List bindings (optionally filtered by prefix)

 -- Debugging:
  ,break <name>     Set breakpoint on function
  ,breakpoints      List active breakpoints
  ,delete all       Clear all breakpoints
  ,step <expr>      Evaluate with single-stepping

 -- System:
  ,gc               Show GC statistics
  ,version          Show Kaappi version
  ,load <file>      Load and run a Scheme file
  ,import <lib>     Import a library (e.g. ,import (srfi 1))

The variable _ holds the last result.
```

## Exiting

```
kaappi> ,quit
```

You can also type `(exit)` or press **Ctrl+D** on an empty line.

---

Next: [Tips](tips.md)
