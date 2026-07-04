---
render_macros: true
---

# Procedure Reference

This document lists all built-in procedures organized by domain. Each procedure
shows its arity (`N` = exactly N arguments, `N+` = N or more arguments) and a
short description. Click any category heading for detailed documentation with
examples.

---

## [Numbers and Arithmetic](numbers.md)

{{ procedures_table("numbers.md") }}

## [Pairs and Lists](pairs-and-lists.md)

{{ procedures_table("pairs-and-lists.md") }}

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

{{ procedures_table("strings.md") }}

## [SRFI-13 String Library](srfi-13.md)

{{ procedures_table("srfi-13.md") }}

## [Characters](characters.md)

{{ procedures_table("characters.md") }}

## [Vectors](vectors.md)

{{ procedures_table("vectors.md") }}

## [SRFI-133 Vector Library](srfi-133.md)

{{ procedures_table("srfi-133.md") }}

## [Bytevectors](bytevectors.md)

{{ procedures_table("bytevectors.md") }}

## [Ports and I/O](ports-and-io.md)

{{ procedures_table("ports-and-io.md") }}

## [Control Flow](control-flow.md)

{{ procedures_table("control-flow.md") }}

## [Type Checking and Equivalence](type-checking.md)

{{ procedures_table("type-checking.md") }}

## [Hash Tables (SRFI-69)](hash-tables.md)

{{ procedures_table("hash-tables.md") }}

## [System and Environment](system.md)

{{ procedures_table("system.md") }}

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

{{ procedures_table("threads.md") }}

## [Kaappi Extensions](extensions.md)

{{ procedures_table("extensions.md") }}
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

{{ procedures_table("other.md") }}
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
