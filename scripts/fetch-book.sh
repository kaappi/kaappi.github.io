#!/usr/bin/env bash
# Populate the (gitignored) embedded book PDF at docs/assets/kaappi-book.pdf
# from a kaappi-book release, verified against the release SHA256SUMS. Run
# once on a fresh clone before `mkdocs serve`; CI runs it before deploying.
#
# Usage: scripts/fetch-book.sh [vX.Y.Z]
#   Default tag: v<book_version> read from mkdocs.yml (the single source of
#   truth for which book edition the site embeds).
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -n "${1:-}" ]; then
    tag="$1"
else
    version=$(sed -n 's/^[[:space:]]*book_version:[[:space:]]*//p' mkdocs.yml | head -1)
    if [ -z "$version" ]; then
        echo "error: could not read book_version from mkdocs.yml" >&2
        exit 1
    fi
    tag="v$version"
fi

base_url="https://github.com/kaappi/kaappi-book/releases/download/${tag}"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

echo "Fetching kaappi-book.pdf for ${tag} ..."
curl -fsSL --proto '=https' --tlsv1.2 -o "$tmp/kaappi-book.pdf" "$base_url/kaappi-book.pdf"
curl -fsSL --proto '=https' --tlsv1.2 -o "$tmp/SHA256SUMS" "$base_url/SHA256SUMS"

echo "Verifying checksum ..."
(
    cd "$tmp"
    sums=$(grep -E ' [*]?kaappi-book\.pdf$' SHA256SUMS)
    if command -v sha256sum >/dev/null 2>&1; then
        printf '%s\n' "$sums" | sha256sum -c -
    elif command -v shasum >/dev/null 2>&1; then
        printf '%s\n' "$sums" | shasum -a 256 -c -
    else
        echo "error: no sha256sum or shasum available to verify" >&2
        exit 1
    fi
)

mkdir -p docs/assets
mv -f "$tmp/kaappi-book.pdf" docs/assets/kaappi-book.pdf
echo "Wrote docs/assets/kaappi-book.pdf (${tag})"
