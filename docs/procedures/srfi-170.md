# SRFI-170 Filesystem

POSIX filesystem operations. Import with `(import (srfi 170))`.

---

## File Information

### `file-info` { #file-info }
<!-- index: 1+ | Get file metadata (optional follow-symlinks?) -->

**Syntax:** `(file-info path)` | `(file-info path follow?)`

Returns a file-info object for *path*. When *follow?* is `#t` (the
default), symbolic links are followed (stat). When *follow?* is `#f`,
the link itself is examined (lstat). Raises a file error if the path
does not exist or cannot be accessed.

```scheme
kaappi> (file-info ".")
;=> #<file-info>
kaappi> (define fi (file-info "/tmp"))
kaappi> (file-info-directory? fi)
;=> #t
kaappi> (file-info "/tmp/mylink" #f)   ; inspect the symlink itself
;=> #<file-info>
```

**See also:** [`file-info?`](#file-info-pred),
[`file-info-type`](#file-info-type)

---

### `file-info?` { #file-info-pred }
<!-- index: 1 | True if argument is a file-info object -->

**Syntax:** `(file-info? obj)`

Returns `#t` if *obj* is a file-info object, `#f` otherwise.

```scheme
kaappi> (file-info? (file-info "."))
;=> #t
kaappi> (file-info? "not a file-info")
;=> #f
```

---

### `file-info-type` { #file-info-type }
<!-- index: 1 | File type as symbol (regular, directory, symlink, ...) -->

**Syntax:** `(file-info-type file-info)`

Returns a symbol describing the type of the filesystem entry:
`regular`, `directory`, `symlink`, `fifo`, `socket`, `block-special`,
or `unknown`.

```scheme
kaappi> (file-info-type (file-info "."))
;=> directory
kaappi> (file-info-type (file-info "/etc/hosts"))
;=> regular
```

**See also:** [`file-info-directory?`](#file-info-directory),
[`file-info-regular?`](#file-info-regular)

---

### `file-info-directory?` { #file-info-directory }
<!-- index: 1 | True if file is a directory -->

**Syntax:** `(file-info-directory? file-info)`

Returns `#t` if the file-info describes a directory.

```scheme
kaappi> (file-info-directory? (file-info "."))
;=> #t
kaappi> (file-info-directory? (file-info "/etc/hosts"))
;=> #f
```

---

### `file-info-regular?` { #file-info-regular }
<!-- index: 1 | True if file is a regular file -->

**Syntax:** `(file-info-regular? file-info)`

Returns `#t` if the file-info describes a regular file.

```scheme
kaappi> (file-info-regular? (file-info "/etc/hosts"))
;=> #t
kaappi> (file-info-regular? (file-info "."))
;=> #f
```

---

### `file-info-symlink?` { #file-info-symlink }
<!-- index: 1 | True if file is a symlink -->

**Syntax:** `(file-info-symlink? file-info)`

Returns `#t` if the file-info describes a symbolic link. Only meaningful
when `file-info` was called with *follow?* set to `#f`.

```scheme
kaappi> (create-symlink "/etc/hosts" "/tmp/test-link")
kaappi> (file-info-symlink? (file-info "/tmp/test-link" #f))
;=> #t
kaappi> (file-info-symlink? (file-info "/tmp/test-link"))
;=> #f   ; followed the link, so it appears as regular
```

---

### `file-info-fifo?` { #file-info-fifo }
<!-- index: 1 | True if file is a FIFO -->

**Syntax:** `(file-info-fifo? file-info)`

Returns `#t` if the file-info describes a FIFO (named pipe).

```scheme
kaappi> (create-fifo "/tmp/test-fifo")
kaappi> (file-info-fifo? (file-info "/tmp/test-fifo"))
;=> #t
```

---

### `file-info-socket?` { #file-info-socket }
<!-- index: 1 | True if file is a socket -->

**Syntax:** `(file-info-socket? file-info)`

Returns `#t` if the file-info describes a socket.

---

### `file-info-device?` { #file-info-device }
<!-- index: 1 | True if file is a device -->

**Syntax:** `(file-info-device? file-info)`

Returns `#t` if the file-info describes a device (block or character
special file).

---

## File-Info Accessors

All accessors take a single file-info object and return an integer.

| Accessor | Returns |
|---|---|
| `file-info:size` { #file-info-size } | File size in bytes |  <!-- index: 1 | File size in bytes -->
| `file-info:mtime` { #file-info-mtime } | Last modification time (seconds since epoch) |  <!-- index: 1 | Modification time -->
| `file-info:atime` { #file-info-atime } | Last access time (seconds since epoch) |  <!-- index: 1 | Access time -->
| `file-info:ctime` { #file-info-ctime } | Last status-change time (seconds since epoch) |  <!-- index: 1 | Status change time -->
| `file-info:mode` { #file-info-mode } | POSIX permission mode (e.g. `#o755`) |  <!-- index: 1 | File permission mode -->
| `file-info:device` { #file-info-device-id } | Device ID of the filesystem |  <!-- index: 1 | Device ID -->
| `file-info:inode` { #file-info-inode } | Inode number |  <!-- index: 1 | Inode number -->
| `file-info:nlinks` { #file-info-nlinks } | Number of hard links |  <!-- index: 1 | Number of hard links -->
| `file-info:uid` { #file-info-uid } | Owner user ID |  <!-- index: 1 | Owner user ID -->
| `file-info:gid` { #file-info-gid } | Owner group ID |  <!-- index: 1 | Owner group ID -->
| `file-info:rdev` { #file-info-rdev } | Device ID (for special files) |  <!-- index: 1 | Device ID (for device files) -->
| `file-info:blksize` { #file-info-blksize } | Preferred I/O block size |  <!-- index: 1 | Block size -->
| `file-info:blocks` { #file-info-blocks } | Number of 512-byte blocks allocated |  <!-- index: 1 | Number of blocks -->

```scheme
kaappi> (define fi (file-info "/etc/hosts"))
kaappi> (file-info:size fi)
;=> 583
kaappi> (file-info:mtime fi)
;=> 1718900000
kaappi> (file-info:nlinks fi)
;=> 1
kaappi> (file-info:uid fi)
;=> 0
kaappi> (file-info:mode fi)
;=> 420   ; decimal for #o644
kaappi> (> (file-info:blksize fi) 0)
;=> #t
kaappi> (> (file-info:blocks fi) 0)
;=> #t
```

---

## Directory Operations

### `directory-files` { #directory-files }
<!-- index: 1+ | List files in a directory -->

**Syntax:** `(directory-files path)` | `(directory-files path dotfiles?)`

Returns a list of filenames (strings) in the directory at *path*. The
entries `.` and `..` are always excluded. When *dotfiles?* is `#t`,
hidden files (names beginning with `.`) are included; the default is
`#f`.

```scheme
kaappi> (directory-files "/tmp")
;=> ("kaappi-abcdef" "test.txt" ...)
kaappi> (directory-files "/tmp" #t)
;=> (".hidden" "kaappi-abcdef" "test.txt" ...)
```

**See also:** [`open-directory`](#open-directory)

---

### `create-directory` { #create-directory }
<!-- index: 1+ | Create a directory (optional mode) -->

**Syntax:** `(create-directory path)` | `(create-directory path mode)`

Creates a new directory at *path*. The optional *mode* specifies the
POSIX permission bits; the default is `#o755`. Raises a file error if
the directory cannot be created.

```scheme
kaappi> (create-directory "/tmp/mydir")
kaappi> (create-directory "/tmp/secure-dir" #o700)
kaappi> (file-info-directory? (file-info "/tmp/mydir"))
;=> #t
```

**See also:** [`delete-directory`](#delete-directory)

---

### `delete-directory` { #delete-directory }
<!-- index: 1 | Delete a directory -->

**Syntax:** `(delete-directory path)`

Removes the directory at *path*. The directory must be empty. Raises a
file error if the directory cannot be removed.

```scheme
kaappi> (delete-directory "/tmp/mydir")
```

**See also:** [`create-directory`](#create-directory)

---

### `open-directory` { #open-directory }
<!-- index: 1+ | Open a directory stream -->

**Syntax:** `(open-directory path)` | `(open-directory path dotfiles?)`

Opens the directory at *path* for sequential reading and returns a
directory object. When *dotfiles?* is `#t`, hidden files are included
during traversal; the default is `#f`. The entries `.` and `..` are
always skipped.

```scheme
kaappi> (define d (open-directory "."))
kaappi> (read-directory d)
;=> "README.md"
kaappi> (close-directory d)
```

**See also:** [`read-directory`](#read-directory),
[`close-directory`](#close-directory),
[`directory-files`](#directory-files)

---

### `read-directory` { #read-directory }
<!-- index: 1 | Read next entry from directory stream -->

**Syntax:** `(read-directory dir-object)`

Returns the next filename (a string) from the directory object, or
an eof-object when no entries remain. Once the eof-object is returned,
the directory is automatically closed.

```scheme
kaappi> (define d (open-directory "."))
kaappi> (let loop ((entry (read-directory d)))
         (if (eof-object? entry)
             'done
             (begin (display entry) (newline)
                    (loop (read-directory d)))))
```

**See also:** [`open-directory`](#open-directory)

---

### `close-directory` { #close-directory }
<!-- index: 1 | Close a directory stream -->

**Syntax:** `(close-directory dir-object)`

Closes the directory object, releasing the underlying file descriptor.
Safe to call multiple times; subsequent calls are a no-op.

```scheme
kaappi> (define d (open-directory "/tmp"))
kaappi> (close-directory d)
```

**See also:** [`open-directory`](#open-directory)

---

## File Manipulation

### `rename-file` { #rename-file }
<!-- index: 2 | Rename a file -->

**Syntax:** `(rename-file old-path new-path)`

Renames the file from *old-path* to *new-path*. This is an atomic
operation on the same filesystem. Raises a file error on failure.

```scheme
kaappi> (rename-file "/tmp/old-name.txt" "/tmp/new-name.txt")
```

---

### `create-symlink` { #create-symlink }
<!-- index: 2 | Create a symbolic link -->

**Syntax:** `(create-symlink old-path new-path)`

Creates a symbolic link at *new-path* pointing to *old-path*. Raises
a file error if the link cannot be created.

```scheme
kaappi> (create-symlink "/etc/hosts" "/tmp/hosts-link")
kaappi> (read-symlink "/tmp/hosts-link")
;=> "/etc/hosts"
```

**See also:** [`read-symlink`](#read-symlink),
[`create-hard-link`](#create-hard-link)

---

### `read-symlink` { #read-symlink }
<!-- index: 1 | Read the target of a symbolic link -->

**Syntax:** `(read-symlink path)`

Returns the target of the symbolic link at *path* as a string. Raises
a file error if *path* is not a symbolic link.

```scheme
kaappi> (create-symlink "/etc/hosts" "/tmp/test-link")
kaappi> (read-symlink "/tmp/test-link")
;=> "/etc/hosts"
```

**See also:** [`create-symlink`](#create-symlink)

---

### `create-hard-link` { #create-hard-link }
<!-- index: 2 | Create a hard link -->

**Syntax:** `(create-hard-link old-path new-path)`

Creates a hard link at *new-path* referring to the same inode as
*old-path*. Both paths must reside on the same filesystem. Raises a
file error on failure.

```scheme
kaappi> (create-hard-link "/tmp/original.txt" "/tmp/linked.txt")
kaappi> (= (file-info:inode (file-info "/tmp/original.txt"))
           (file-info:inode (file-info "/tmp/linked.txt")))
;=> #t
```

**See also:** [`create-symlink`](#create-symlink)

---

### `real-path` { #real-path }
<!-- index: 1 | Resolve to canonical absolute path -->

**Syntax:** `(real-path path)`

Returns the canonicalized absolute pathname for *path*, resolving all
symbolic links, `.`, and `..` components. Raises a file error if the
path cannot be resolved.

```scheme
kaappi> (real-path ".")
;=> "/home/user/project"
kaappi> (char=? #\/ (string-ref (real-path ".") 0))
;=> #t
```

---

### `set-file-mode` { #set-file-mode }
<!-- index: 2 | Set file permissions -->

**Syntax:** `(set-file-mode path mode)`

Sets the POSIX permission bits of the file at *path* to *mode*.

```scheme
kaappi> (set-file-mode "/tmp/test.txt" #o644)
kaappi> (set-file-mode "/tmp/script.sh" #o755)
```

---

### `set-file-owner` { #set-file-owner }
<!-- index: 3 | Set file owner (uid, gid) -->

**Syntax:** `(set-file-owner path uid gid)`

Changes the owner and group of the file at *path*. Pass `-1` for
*uid* or *gid* to leave that value unchanged. Typically requires
superuser privileges.

```scheme
kaappi> (set-file-owner "/tmp/test.txt" 1000 1000)
kaappi> (set-file-owner "/tmp/test.txt" -1 100)  ; change group only
```

---

### `truncate-file` { #truncate-file }
<!-- index: 2 | Truncate file to given length -->

**Syntax:** `(truncate-file path length)`

Truncates the file at *path* to exactly *length* bytes. If the file is
shorter, it is extended with zero bytes. Raises a file error on failure.

```scheme
kaappi> (truncate-file "/tmp/test.txt" 5)
kaappi> (file-info:size (file-info "/tmp/test.txt"))
;=> 5
```

---

### `set-file-times` { #set-file-times }
<!-- index: 1+ | Set access and modification times -->

**Syntax:** `(set-file-times path)` | `(set-file-times path atime)` | `(set-file-times path atime mtime)`

Sets the access and modification times of the file at *path*. With no
time arguments, both timestamps are set to the current time. Special
sentinel values:

- **-1** -- set to the current time (equivalent to omitting the argument)
- **-2** -- leave unchanged

Any other integer is interpreted as seconds since the Unix epoch.

```scheme
kaappi> (set-file-times "/tmp/test.txt")         ; touch: set both to now
kaappi> (set-file-times "/tmp/test.txt" -1 -2)   ; update atime only
kaappi> (set-file-times "/tmp/test.txt" -2 -1)   ; update mtime only
```

---

### `create-fifo` { #create-fifo }
<!-- index: 1+ | Create a named pipe (optional mode) -->

**Syntax:** `(create-fifo path)` | `(create-fifo path mode)`

Creates a FIFO (named pipe) at *path*. The optional *mode* specifies
permission bits; the default is `#o664`. Raises a file error on failure.

```scheme
kaappi> (create-fifo "/tmp/my-pipe")
kaappi> (create-fifo "/tmp/my-pipe2" #o600)
kaappi> (file-info-fifo? (file-info "/tmp/my-pipe"))
;=> #t
```

---

## Process State

### `pid` { #pid }
<!-- index: 0 | Current process ID -->

**Syntax:** `(pid)`

Returns the process ID of the current Kaappi process as an integer.

```scheme
kaappi> (pid)
;=> 42359
kaappi> (> (pid) 0)
;=> #t
```

---

### `umask` { #umask }
<!-- index: 0 | Current umask -->

**Syntax:** `(umask)`

Returns the current file-creation mask as an integer.

```scheme
kaappi> (umask)
;=> 18   ; decimal for #o022
```

**See also:** [`set-umask!`](#set-umask)

---

### `set-umask!` { #set-umask }
<!-- index: 1 | Set umask -->

**Syntax:** `(set-umask! mask)`

Sets the file-creation mask to *mask* (an integer in POSIX octal
notation).

```scheme
kaappi> (set-umask! #o077)
kaappi> (umask)
;=> 63   ; decimal for #o077
```

**See also:** [`umask`](#umask)

---

### `current-directory` { #current-directory }
<!-- index: 0 | Current working directory -->

**Syntax:** `(current-directory)`

Returns the absolute pathname of the current working directory as a
string.

```scheme
kaappi> (current-directory)
;=> "/home/user/project"
kaappi> (string? (current-directory))
;=> #t
```

**See also:** [`set-current-directory!`](#set-current-directory)

---

### `set-current-directory!` { #set-current-directory }
<!-- index: 1 | Change working directory -->

**Syntax:** `(set-current-directory! path)`

Changes the current working directory to *path*. Raises a file error
if the directory does not exist or is not accessible.

```scheme
kaappi> (set-current-directory! "/tmp")
kaappi> (current-directory)
;=> "/tmp"
```

**See also:** [`current-directory`](#current-directory)

---

### `user-uid` { #user-uid }
<!-- index: 0 | Current user ID -->

**Syntax:** `(user-uid)`

Returns the real user ID of the current process.

```scheme
kaappi> (user-uid)
;=> 1000
```

**See also:** [`user-effective-uid`](#user-effective-uid),
[`user-info`](#user-info)

---

### `user-gid` { #user-gid }
<!-- index: 0 | Current group ID -->

**Syntax:** `(user-gid)`

Returns the real group ID of the current process.

```scheme
kaappi> (user-gid)
;=> 1000
```

**See also:** [`user-effective-gid`](#user-effective-gid)

---

### `user-effective-uid` { #user-effective-uid }
<!-- index: 0 | Effective user ID -->

**Syntax:** `(user-effective-uid)`

Returns the effective user ID of the current process.

```scheme
kaappi> (user-effective-uid)
;=> 1000
```

**See also:** [`user-uid`](#user-uid)

---

### `user-effective-gid` { #user-effective-gid }
<!-- index: 0 | Effective group ID -->

**Syntax:** `(user-effective-gid)`

Returns the effective group ID of the current process.

```scheme
kaappi> (user-effective-gid)
;=> 1000
```

**See also:** [`user-gid`](#user-gid)

---

### `user-supplementary-gids` { #user-supplementary-gids }
<!-- index: 0 | Supplementary group IDs -->

**Syntax:** `(user-supplementary-gids)`

Returns a list of supplementary group IDs for the current process.

```scheme
kaappi> (user-supplementary-gids)
;=> (1000 4 24 27 30)
kaappi> (list? (user-supplementary-gids))
;=> #t
```

---

### `nice` { #nice }
<!-- index: 0+ | Adjust process priority -->

**Syntax:** `(nice)` | `(nice increment)`

Adjusts the scheduling priority of the current process. With no
argument, the priority is incremented by 1. With *increment*, the
priority is incremented by that amount. Returns the new nice value.
Higher values mean lower priority.

```scheme
kaappi> (nice)      ; increment by 1
;=> 1
kaappi> (nice 5)    ; increment by 5
;=> 6
```

---

## User Database

### `user-info` { #user-info }
<!-- index: 1 | Get user info by UID or username -->

**Syntax:** `(user-info uid-or-name)`

Returns a user-info object for the given user. Accepts either an integer
(UID) or a string (username). Returns `#f` if the user does not exist.

```scheme
kaappi> (define u (user-info (user-uid)))
kaappi> (user-info? u)
;=> #t
kaappi> (user-info:name u)
;=> "alice"
kaappi> (user-info "root")
;=> #<user-info>
```

**See also:** [`user-info?`](#user-info-pred)

---

### `user-info?` { #user-info-pred }
<!-- index: 1 | True if argument is a user-info object -->

**Syntax:** `(user-info? obj)`

Returns `#t` if *obj* is a user-info object, `#f` otherwise.

```scheme
kaappi> (user-info? (user-info 0))
;=> #t
kaappi> (user-info? "not a user-info")
;=> #f
```

---

### `user-info:name` { #user-info-name }
<!-- index: 1 | User login name -->

**Syntax:** `(user-info:name user-info)`

Returns the login name of the user as a string.

```scheme
kaappi> (user-info:name (user-info 0))
;=> "root"
```

---

### `user-info:uid` { #user-info-uid }
<!-- index: 1 | User ID -->

**Syntax:** `(user-info:uid user-info)`

Returns the numeric user ID.

```scheme
kaappi> (user-info:uid (user-info "root"))
;=> 0
```

---

### `user-info:gid` { #user-info-gid }
<!-- index: 1 | User group ID -->

**Syntax:** `(user-info:gid user-info)`

Returns the primary group ID of the user.

```scheme
kaappi> (user-info:gid (user-info "root"))
;=> 0
```

---

### `user-info:home-dir` { #user-info-home-dir }
<!-- index: 1 | Home directory path -->

**Syntax:** `(user-info:home-dir user-info)`

Returns the home directory of the user as a string.

```scheme
kaappi> (user-info:home-dir (user-info 0))
;=> "/root"
```

---

### `user-info:shell` { #user-info-shell }
<!-- index: 1 | Login shell path -->

**Syntax:** `(user-info:shell user-info)`

Returns the login shell of the user as a string.

```scheme
kaappi> (user-info:shell (user-info 0))
;=> "/bin/bash"
```

---

### `user-info:full-name` { #user-info-full-name }
<!-- index: 1 | Full name (GECOS field) -->

**Syntax:** `(user-info:full-name user-info)`

Returns the GECOS full-name field for the user as a string.

```scheme
kaappi> (user-info:full-name (user-info (user-uid)))
;=> "Alice Smith"
```

---

## Group Database

### `group-info` { #group-info }
<!-- index: 1 | Get group info by GID or group name -->

**Syntax:** `(group-info gid-or-name)`

Returns a group-info object for the given group. Accepts either an
integer (GID) or a string (group name). Returns `#f` if the group does
not exist.

```scheme
kaappi> (define g (group-info (user-gid)))
kaappi> (group-info? g)
;=> #t
kaappi> (group-info:name g)
;=> "staff"
```

**See also:** [`group-info?`](#group-info-pred)

---

### `group-info?` { #group-info-pred }
<!-- index: 1 | True if argument is a group-info object -->

**Syntax:** `(group-info? obj)`

Returns `#t` if *obj* is a group-info object, `#f` otherwise.

```scheme
kaappi> (group-info? (group-info 0))
;=> #t
kaappi> (group-info? 42)
;=> #f
```

---

### `group-info:name` { #group-info-name }
<!-- index: 1 | Group name -->

**Syntax:** `(group-info:name group-info)`

Returns the group name as a string.

```scheme
kaappi> (group-info:name (group-info 0))
;=> "wheel"
```

---

### `group-info:gid` { #group-info-gid }
<!-- index: 1 | Group ID -->

**Syntax:** `(group-info:gid group-info)`

Returns the numeric group ID.

```scheme
kaappi> (group-info:gid (group-info "wheel"))
;=> 0
```

---

## Environment Variables

### `set-environment-variable!` { #set-environment-variable }
<!-- index: 2 | Set an environment variable -->

**Syntax:** `(set-environment-variable! name value)`

Sets the environment variable *name* to *value*. Both arguments must be
strings. Overwrites any existing value. Raises a file error on failure.

```scheme
kaappi> (set-environment-variable! "MY_VAR" "hello")
kaappi> (get-environment-variable "MY_VAR")
;=> "hello"
```

**See also:** [`delete-environment-variable!`](#delete-environment-variable),
[`get-environment-variable`](./system.md#get-environment-variable)

---

### `delete-environment-variable!` { #delete-environment-variable }
<!-- index: 1 | Delete an environment variable -->

**Syntax:** `(delete-environment-variable! name)`

Removes the environment variable *name* from the process environment.

```scheme
kaappi> (set-environment-variable! "MY_VAR" "hello")
kaappi> (delete-environment-variable! "MY_VAR")
kaappi> (get-environment-variable "MY_VAR")
;=> #f
```

**See also:** [`set-environment-variable!`](#set-environment-variable),
[`get-environment-variable`](./system.md#get-environment-variable)

---

## Terminal

### `terminal?` { #terminal }
<!-- index: 1 | True if port is connected to a terminal -->

**Syntax:** `(terminal? port)`

Returns `#t` if *port* is associated with a terminal device, `#f`
otherwise. The argument must be a port object.

```scheme
kaappi> (terminal? (current-input-port))
;=> #t   ; when running interactively
kaappi> (terminal? (open-input-file "/tmp/test.txt"))
;=> #f
```

**See also:** [`current-input-port`](./ports-and-io.md#current-input-port)

---

## Time

### `posix-time` { #posix-time }
<!-- index: 0 | Current time as seconds since epoch -->

**Syntax:** `(posix-time)`

Returns the current time as seconds since the Unix epoch
(1970-01-01 00:00:00 UTC), using the realtime clock.

```scheme
kaappi> (posix-time)
;=> 1718900000
kaappi> (> (posix-time) 0)
;=> #t
```

**See also:** [`monotonic-time`](#monotonic-time)

---

### `monotonic-time` { #monotonic-time }
<!-- index: 0 | Monotonic clock time -->

**Syntax:** `(monotonic-time)`

Returns the current value of the monotonic clock in seconds. Unlike
`posix-time`, this clock is not affected by system time changes and
is suitable for measuring elapsed time.

```scheme
kaappi> (define start (monotonic-time))
kaappi> (>= (- (monotonic-time) start) 0)
;=> #t
```

**See also:** [`posix-time`](#posix-time)

---

## Temporary Files

### `create-temp-file` { #create-temp-file }
<!-- index: 0+ | Create a temporary file (optional prefix) -->

**Syntax:** `(create-temp-file)` | `(create-temp-file prefix)`

Creates a new temporary file using `mkstemp(3)` and returns its pathname
as a string. The file is created with mode `#o600` and is closed before
returning. The optional *prefix* is a path prefix for the temp file; the
default is the value of `(temp-file-prefix)`, which is `"/tmp/kaappi-"`.

```scheme
kaappi> (create-temp-file)
;=> "/tmp/kaappi-a1b2c3"
kaappi> (create-temp-file "/tmp/myapp-")
;=> "/tmp/myapp-x9y8z7"
```

**See also:** [`temp-file-prefix`](#temp-file-prefix)

---

### `temp-file-prefix` { #temp-file-prefix }
<!-- index: 0 | Default temporary file prefix -->

**Syntax:** `(temp-file-prefix)`

Returns the default prefix used by `create-temp-file`. In Kaappi this
is always `"/tmp/kaappi-"`.

```scheme
kaappi> (temp-file-prefix)
;=> "/tmp/kaappi-"
```

**See also:** [`create-temp-file`](#create-temp-file)

---
