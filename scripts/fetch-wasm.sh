#!/usr/bin/env bash
# Populate the (gitignored) playground WASM at docs/wasm/kaappi.wasm from a
# kaappi release, verified against the release SHA256SUMS. Run once on a fresh
# clone before `mkdocs serve`; CI runs it before deploying.
#
# Usage: scripts/fetch-wasm.sh [vX.Y.Z]
#   Default tag: v<kaappi_version> read from mkdocs.yml (the single source of
#   truth for which release the site serves).
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -n "${1:-}" ]; then
    tag="$1"
else
    version=$(sed -n 's/^[[:space:]]*kaappi_version:[[:space:]]*//p' mkdocs.yml | head -1)
    if [ -z "$version" ]; then
        echo "error: could not read kaappi_version from mkdocs.yml" >&2
        exit 1
    fi
    tag="v$version"
fi

base_url="https://github.com/kaappi/kaappi/releases/download/${tag}"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

echo "Fetching kaappi.wasm for ${tag} ..."
curl -fsSL --proto '=https' --tlsv1.2 -o "$tmp/kaappi.wasm" "$base_url/kaappi.wasm"
curl -fsSL --proto '=https' --tlsv1.2 -o "$tmp/SHA256SUMS" "$base_url/SHA256SUMS"

echo "Verifying checksum ..."
(
    cd "$tmp"
    sums=$(grep -E ' [*]?kaappi\.wasm$' SHA256SUMS)
    if command -v sha256sum >/dev/null 2>&1; then
        printf '%s\n' "$sums" | sha256sum -c -
    elif command -v shasum >/dev/null 2>&1; then
        printf '%s\n' "$sums" | shasum -a 256 -c -
    else
        echo "error: no sha256sum or shasum available to verify" >&2
        exit 1
    fi
)

mkdir -p docs/wasm
mv -f "$tmp/kaappi.wasm" docs/wasm/kaappi.wasm
echo "Wrote docs/wasm/kaappi.wasm (${tag})"
