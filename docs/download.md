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
| Windows | ARM64 | [kaappi-aarch64-windows.exe](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-aarch64-windows.exe) | [thottam-aarch64-windows.exe](https://github.com/kaappi/kaappi/releases/latest/download/thottam-aarch64-windows.exe) |

macOS binaries are Developer ID signed and Apple notarized. Windows
binaries are not code-signed — SmartScreen may show a "Windows protected
your PC" warning on first run. Click **More info** → **Run anyway** to
proceed. See [Troubleshooting](guide/troubleshooting.md#windows-smartscreen-warning).

### Other assets

| File | Description |
|------|-------------|
| [kaappi-lib.tar.gz](https://github.com/kaappi/kaappi/releases/latest/download/kaappi-lib.tar.gz) | Standard libraries (SRFI, Scheme). Extract to `~/.kaappi/lib/` |
| [kaappi.wasm](https://github.com/kaappi/kaappi/releases/latest/download/kaappi.wasm) | WebAssembly binary (wasm32-wasi) |
| [kaappi_rt.lib](https://github.com/kaappi/kaappi/releases/latest/download/kaappi_rt.lib) | Runtime library for native compilation on Windows |

### Manual install

After downloading, place the binaries in your `PATH`.

**macOS / Linux:**

```bash
chmod +x kaappi-* thottam-*
mv kaappi-*-$(uname -s | tr A-Z a-z) ~/.local/bin/kaappi
mv thottam-*-$(uname -s | tr A-Z a-z) ~/.local/bin/thottam

# Extract standard libraries
mkdir -p ~/.kaappi/lib
tar xzf kaappi-lib.tar.gz -C ~/.kaappi/lib
```

**Windows (PowerShell):**

```powershell
Move-Item kaappi-aarch64-windows.exe C:\Users\$env:USERNAME\.local\bin\kaappi.exe
Move-Item thottam-aarch64-windows.exe C:\Users\$env:USERNAME\.local\bin\thottam.exe

# Extract standard libraries
mkdir "$env:USERPROFILE\.kaappi\lib" -Force
tar xzf kaappi-lib.tar.gz -C "$env:USERPROFILE\.kaappi\lib"

# Runtime library for native compilation (kaappi compile)
Move-Item kaappi_rt.lib "$env:USERPROFILE\.kaappi\lib\kaappi_rt.lib"
```

!!! note
    The install script (`install.sh`) supports macOS and Linux only. Windows
    users should download and install manually as shown above.

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
