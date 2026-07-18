#!/bin/bash
# Kaappi Scheme installer
# Usage: curl -fsSL https://kaappi-lang.org/install.sh | bash
#
# Installs the latest release binary to ~/.local/bin/kaappi (or INSTALL_DIR).
#
# Environment overrides:
#   INSTALL_DIR       install prefix for binaries (default: ~/.local/bin)
#   KAAPPI_VERSION    install a specific tag (e.g. v0.12.0) instead of latest
#   KAAPPI_NO_VERIFY  set to 1 to install without checksum verification

set -euo pipefail

REPO="kaappi/kaappi"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"
# Common curl flags: fail on HTTP error, follow redirects, HTTPS only.
CURL=(curl -fsSL --proto '=https' --tlsv1.2)

detect_platform() {
    local os arch
    os=$(uname -s)
    arch=$(uname -m)

    case "$os" in
        Darwin)  os="macos" ;;
        Linux)   os="linux" ;;
        FreeBSD) os="freebsd" ;;
        OpenBSD) os="openbsd" ;;
        *)
            echo "error: unsupported OS: $os" >&2
            echo "This install script supports macOS, Linux, FreeBSD, and OpenBSD." >&2
            echo "Windows users: download from https://kaappi-lang.org/download/" >&2
            exit 1
            ;;
    esac

    case "$arch" in
        arm64|aarch64) arch="aarch64" ;;
        # FreeBSD and OpenBSD report x86_64 as amd64 (uname -m).
        x86_64|amd64)  arch="x86_64" ;;
        riscv64)       arch="riscv64" ;;
        *)
            echo "error: unsupported architecture: $arch" >&2
            exit 1
            ;;
    esac

    echo "${arch}-${os}"
}

get_latest_tag() {
    # Follow the releases/latest redirect rather than hitting the JSON API,
    # which is rate-limited to 60 requests/hour/IP (unauthenticated). The
    # effective URL ends in /releases/tag/<tag>.
    local url
    url=$("${CURL[@]}" -I -o /dev/null -w '%{url_effective}' \
        "https://github.com/$REPO/releases/latest")
    printf '%s\n' "${url##*/tag/}"
}

main() {
    echo "Kaappi Scheme installer"
    echo

    local platform
    platform=$(detect_platform)
    echo "Platform: $platform"

    local tag
    if [ -n "${KAAPPI_VERSION:-}" ]; then
        tag="$KAAPPI_VERSION"
    else
        echo "Fetching latest release..."
        tag=$(get_latest_tag)
    fi
    if [ -z "$tag" ]; then
        echo "error: could not determine release to install" >&2
        echo "Check https://github.com/$REPO/releases" >&2
        exit 1
    fi
    echo "Version: $tag"

    local kaappi_artifact="kaappi-${platform}"
    local thottam_artifact="thottam-${platform}"
    local base_url="https://github.com/$REPO/releases/download/${tag}"

    echo "Downloading binaries..."
    local tmpdir
    tmpdir=$(mktemp -d)
    # Expand $tmpdir now (not at signal time): it is function-local and would
    # be out of scope — and unbound under `set -u` — when the EXIT trap fires.
    # shellcheck disable=SC2064
    trap "rm -rf '$tmpdir'" EXIT

    "${CURL[@]}" -o "$tmpdir/kaappi" "$base_url/$kaappi_artifact"
    "${CURL[@]}" -o "$tmpdir/thottam" "$base_url/$thottam_artifact"
    "${CURL[@]}" -o "$tmpdir/kaappi-lib.tar.gz" "$base_url/kaappi-lib.tar.gz"
    "${CURL[@]}" -o "$tmpdir/SHA256SUMS" "$base_url/SHA256SUMS"

    echo "Verifying checksums..."
    cd "$tmpdir"
    # SHA256SUMS references artifact names; remap to local filenames for verification
    grep "$kaappi_artifact" SHA256SUMS | sed "s|$kaappi_artifact|kaappi|" > check.txt
    grep "$thottam_artifact" SHA256SUMS | sed "s|$thottam_artifact|thottam|" >> check.txt
    grep "kaappi-lib.tar.gz" SHA256SUMS >> check.txt
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum -c --quiet check.txt
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 -c --quiet check.txt
    elif [ "${KAAPPI_NO_VERIFY:-0}" = "1" ]; then
        echo "warning: skipping checksum verification (KAAPPI_NO_VERIFY=1)" >&2
    else
        echo "error: no sha256sum or shasum found; cannot verify download" >&2
        echo "  install one, or set KAAPPI_NO_VERIFY=1 to bypass verification" >&2
        exit 1
    fi

    echo "Installing to $INSTALL_DIR/..."
    mkdir -p "$INSTALL_DIR"
    mv "$tmpdir/kaappi" "$INSTALL_DIR/kaappi"
    mv "$tmpdir/thottam" "$INSTALL_DIR/thottam"
    chmod +x "$INSTALL_DIR/kaappi" "$INSTALL_DIR/thottam"

    echo "Installing standard libraries to ~/.kaappi/lib/..."
    mkdir -p "$HOME/.kaappi/lib" "$tmpdir/libextract"
    # Extract first; only wipe the existing lib once extraction has succeeded,
    # so a failed download/extract never leaves the user without a stdlib.
    tar xzf "$tmpdir/kaappi-lib.tar.gz" -C "$tmpdir/libextract"
    rm -rf "$HOME/.kaappi/lib/"*
    cp -r "$tmpdir/libextract/lib/"* "$HOME/.kaappi/lib/"
    cp "$tmpdir/libextract/LICENSE" "$HOME/.kaappi/lib/"

    echo
    echo "Installed kaappi $tag to $INSTALL_DIR/"
    echo "Standard libraries installed to ~/.kaappi/lib/"

    if ! echo "$PATH" | tr ':' '\n' | grep -qx "$INSTALL_DIR"; then
        echo
        echo "Add $INSTALL_DIR to your PATH:"
        echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
    fi
}

main
