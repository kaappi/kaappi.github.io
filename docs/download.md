---
render_macros: true
---

# Download Kaappi v{{ kaappi_version }}

## Recommended: install script

The install script auto-detects your platform, downloads the latest release,
verifies SHA256 checksums, and installs everything to the right place:

```bash
curl -fsSL https://kaappi-lang.org/install.sh | bash
```

This installs `kaappi` and `thottam` (the package manager) to `~/.local/bin/`
and standard libraries to `~/.kaappi/lib/`. Set `INSTALL_DIR` to change the
binary location:

```bash
curl -fsSL https://kaappi-lang.org/install.sh | INSTALL_DIR=/usr/local/bin bash
```

---

## Manual downloads

Download individual files from the latest GitHub release. You need at minimum
the `kaappi` binary for your platform and the library archive.

### Binaries

| Platform | Architecture | kaappi | thottam |
|----------|-------------|--------|---------|
| macOS | ARM64 (Apple Silicon) | [kaappi-aarch64-macos](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-aarch64-macos) | [thottam-aarch64-macos](https://github.com/kaappi/kaappi/releases/latest/download/thottam-aarch64-macos) |
| Linux | x86_64 | [kaappi-x86_64-linux](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-x86_64-linux) | [thottam-x86_64-linux](https://github.com/kaappi/kaappi/releases/latest/download/thottam-x86_64-linux) |
| Linux | ARM64 | [kaappi-aarch64-linux](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-aarch64-linux) | [thottam-aarch64-linux](https://github.com/kaappi/kaappi/releases/latest/download/thottam-aarch64-linux) |
| Linux | RISC-V 64 | [kaappi-riscv64-linux](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-riscv64-linux) | [thottam-riscv64-linux](https://github.com/kaappi/kaappi/releases/latest/download/thottam-riscv64-linux) |
| Linux | s390x (IBM Z) | [kaappi-s390x-linux](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-s390x-linux) | [thottam-s390x-linux](https://github.com/kaappi/kaappi/releases/latest/download/thottam-s390x-linux) |
| Linux | ppc64le (POWER) | [kaappi-powerpc64le-linux](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-powerpc64le-linux) | [thottam-powerpc64le-linux](https://github.com/kaappi/kaappi/releases/latest/download/thottam-powerpc64le-linux) |
| Windows | x86_64 (x64) | [kaappi-x86_64-windows.exe](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-x86_64-windows.exe) | [thottam-x86_64-windows.exe](https://github.com/kaappi/kaappi/releases/latest/download/thottam-x86_64-windows.exe) |
| Windows | ARM64 | [kaappi-aarch64-windows.exe](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-aarch64-windows.exe) | [thottam-aarch64-windows.exe](https://github.com/kaappi/kaappi/releases/latest/download/thottam-aarch64-windows.exe) |
| FreeBSD | x86_64 | [kaappi-x86_64-freebsd](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-x86_64-freebsd) | [thottam-x86_64-freebsd](https://github.com/kaappi/kaappi/releases/latest/download/thottam-x86_64-freebsd) |
| FreeBSD | ARM64 | [kaappi-aarch64-freebsd](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-aarch64-freebsd) | [thottam-aarch64-freebsd](https://github.com/kaappi/kaappi/releases/latest/download/thottam-aarch64-freebsd) |
| OpenBSD | x86_64 | [kaappi-x86_64-openbsd](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-x86_64-openbsd) | [thottam-x86_64-openbsd](https://github.com/kaappi/kaappi/releases/latest/download/thottam-x86_64-openbsd) |
| OpenBSD | ARM64 | [kaappi-aarch64-openbsd](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-aarch64-openbsd) | [thottam-aarch64-openbsd](https://github.com/kaappi/kaappi/releases/latest/download/thottam-aarch64-openbsd) |
| NetBSD | x86_64 | [kaappi-x86_64-netbsd](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-x86_64-netbsd) | [thottam-x86_64-netbsd](https://github.com/kaappi/kaappi/releases/latest/download/thottam-x86_64-netbsd) |
| NetBSD | ARM64 | [kaappi-aarch64-netbsd](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-aarch64-netbsd) | [thottam-aarch64-netbsd](https://github.com/kaappi/kaappi/releases/latest/download/thottam-aarch64-netbsd) |

macOS binaries are Developer ID signed and Apple notarized. Windows
binaries are not code-signed — SmartScreen may show a "Windows protected
your PC" warning on first run. Click **More info** → **Run anyway** to
proceed. See [Troubleshooting](guide/troubleshooting.md#windows-smartscreen-warning).

The RISC-V, s390x, and ppc64le builds run the bytecode interpreter;
`kaappi compile` (the LLVM native backend) is available on aarch64 and
x86_64 only, and on other architectures exits with a clear error rather
than attempt it.

### Other assets

| File | Description |
|------|-------------|
| [kaappi-lib.tar.gz](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-lib.tar.gz) | Standard libraries (SRFI, Scheme). Extract to `~/.kaappi/lib/` |
| [kaappi.wasm](https://github.com/kaappi/kaappi/releases/latest/download/kaappi.wasm) | WebAssembly binary (wasm32-wasi) |
| `libkaappi_rt-<platform>.a` | Runtime library for native compilation (`kaappi compile`) on macOS, Linux, and the BSDs — one per aarch64/x86_64 target. The install script fetches it for you; manual installs need it too (see below) |
| [libkaappi_rt-x86_64-windows.lib](https://github.com/kaappi/kaappi/releases/latest/download/libkaappi_rt-x86_64-windows.lib) | Same, for Windows x64. Install it as `kaappi_rt.lib` (see below) |
| [libkaappi_rt-aarch64-windows.lib](https://github.com/kaappi/kaappi/releases/latest/download/libkaappi_rt-aarch64-windows.lib) | Same, for Windows ARM64 |

### Manual install

After downloading, place the binaries in your `PATH`.

The runtime library goes in the `lib` directory *beside* the one holding the
binaries — `~/.local/bin/kaappi` pairs with `~/.local/lib/`. That is where
`kaappi compile` looks (it searches `KAAPPI_LIB_DIR`, then `<exe>/../lib`,
then `zig-out/lib`, then `/usr/local/lib`), so it is **not** `~/.kaappi/lib/`,
which holds Scheme libraries only. Put the binaries somewhere else and either
keep the same `bin`/`lib` pairing or point `KAAPPI_LIB_DIR` at the directory
you chose.

**macOS / Linux:**

```bash
chmod +x kaappi-* thottam-*
mv kaappi-*-$(uname -s | tr A-Z a-z) ~/.local/bin/kaappi
mv thottam-*-$(uname -s | tr A-Z a-z) ~/.local/bin/thottam

# Extract standard libraries
mkdir -p ~/.kaappi/lib
tar xzf kaappi-lib.tar.gz -C ~/.kaappi/lib

# Runtime library for native compilation (kaappi compile).
# aarch64-macos shown; substitute your platform.
mkdir -p ~/.local/lib
mv libkaappi_rt-aarch64-macos.a ~/.local/lib/libkaappi_rt.a
```

**Windows (PowerShell):**

```powershell
# x64 shown; on ARM64 substitute aarch64 for x86_64 throughout.
Move-Item kaappi-x86_64-windows.exe C:\Users\$env:USERNAME\.local\bin\kaappi.exe
Move-Item thottam-x86_64-windows.exe C:\Users\$env:USERNAME\.local\bin\thottam.exe

# Extract standard libraries
mkdir "$env:USERPROFILE\.kaappi\lib" -Force
tar xzf kaappi-lib.tar.gz -C "$env:USERPROFILE\.kaappi\lib"

# Runtime library for native compilation (kaappi compile). It belongs in the
# lib directory beside the binaries' bin directory — not in .kaappi\lib, which
# kaappi compile does not search. kaappi looks for it named kaappi_rt.lib, so
# rename it on the way in.
mkdir "C:\Users\$env:USERNAME\.local\lib" -Force
Move-Item libkaappi_rt-x86_64-windows.lib "C:\Users\$env:USERNAME\.local\lib\kaappi_rt.lib"
```

!!! note
    The install script (`install.sh`) supports macOS, Linux, FreeBSD, OpenBSD,
    and NetBSD. Windows users should download and install manually as shown
    above.

---

## Windows notes

Kaappi runs on **Windows 11**, on x86_64 and ARM64, with prebuilt binaries
for both. There is no installer — download the `kaappi` and `thottam`
executables for your architecture, place them on your `PATH` (see
[Manual install](#manual-install) above), and run them from a terminal
(Windows Terminal recommended). `install.sh` does not apply. Both
architectures run the same code, so everything below applies to both. A
few behaviors differ from the macOS, Linux, and BSD builds:

- **REPL.** A plain prompt and line reader — debug commands, multi-line input,
  and themes all work, but without history, completion, or line editing.
- **Package manager.** thottam's `install`, `remove`, `update`, `list`, and
  `verify` work for pure-Scheme packages (most of the ecosystem). Packages with
  a native `build:` step (C FFI libraries) are refused, and git operations need
  [Git for Windows](https://gitforwindows.org/) on your `PATH`.
- **SRFI-170.** The POSIX-only filesystem procedures — uid/gid,
  `user-info`/`group-info`, symlinks, hard links, FIFOs, `set-file-mode`,
  `umask`, `truncate-file`, `set-file-times` — raise a catchable file error;
  the names stay bound so portable code can probe them with `guard`.
  `file-info` works. See [SRFI-170](procedures/srfi-170.md).
- **Feature detection.** Windows builds expose the `windows` feature identifier
  and omit `posix`, so portable code can branch with
  `(cond-expand (windows ...) (else ...))`. See
  [Standards Conformance](conformance.md).

---

## Verifying releases

Every release includes SHA256 checksums and a GPG signature:

| File | Description |
|------|-------------|
| [SHA256SUMS](https://github.com/kaappi/kaappi/releases/latest/download/SHA256SUMS) | SHA256 checksums for all artifacts |
| [SHA256SUMS.asc](https://github.com/kaappi/kaappi/releases/latest/download/SHA256SUMS.asc) | GPG detached signature |

The install script verifies checksums automatically, but you can also verify
manually:

### SHA256 checksums

```bash
cd ~/Downloads  # or wherever you downloaded the binary
curl -LO https://github.com/kaappi/kaappi/releases/latest/download/SHA256SUMS
sha256sum --check --ignore-missing SHA256SUMS
```

### GPG signature

The release checksums are signed with the maintainer's GPG key. The public key
is available at [keybase.io/baijum](https://keybase.io/baijum).

```bash
# Import the public key from Keybase
curl https://keybase.io/baijum/pgp_keys.asc | gpg --import

# Download the signature and verify
curl -LO https://github.com/kaappi/kaappi/releases/latest/download/SHA256SUMS.asc
gpg --verify SHA256SUMS.asc SHA256SUMS
```

A successful verification shows "Good signature from ..." in the output.

### macOS binaries

macOS binaries are additionally Developer ID signed and Apple notarized — no
Gatekeeper warnings when downloading from GitHub releases.

---

## Build from source

See the [Installation guide](guide/installation.md) for building from source
with Zig 0.16+.

## Previous releases

All past releases are available on the
[GitHub Releases](https://github.com/kaappi/kaappi/releases) page.
