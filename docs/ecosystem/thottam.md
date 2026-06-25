# thottam — Package Manager

**thottam** installs, updates, and removes Kaappi ecosystem libraries. It is a
compiled Zig binary that ships alongside `kaappi` in release artifacts for all
platforms (macOS, Linux x86_64, Linux aarch64, Linux riscv64).

## Getting thottam

thottam is installed automatically by the Kaappi installer:

```bash
curl -fsSL https://kaappi-lang.org/install.sh | bash
```

If you build from source, `zig build` produces both `kaappi` and `thottam` in
`zig-out/bin/`.

## Commands

```bash
thottam install <pkg>[@<ver>][::url]   # Install a package (optionally pinned/sourced)
thottam remove <package>               # Remove a package
thottam list                           # List installed packages
thottam update [package]               # Update one or all packages
thottam verify                         # Check installed packages match lockfile
```

## Install a package

```bash
thottam install kaappi-web
```

This will:

1. Clone `github.com/kaappi/kaappi-web` to `~/.kaappi/src/kaappi-web`
2. Read `kaappi.pkg` for dependencies (`kaappi-http`, `kaappi-json`)
3. Recursively install each dependency
4. Build if needed (`make`)
5. Copy `.sld` files and native libraries to `~/.kaappi/lib/`

## Auto-discovery

After installation, Kaappi automatically finds libraries in `~/.kaappi/lib/`. No `--lib-path` flags or environment variables needed:

```bash
# Before thottam:
DYLD_LIBRARY_PATH=../kaappi-net:../kaappi-http \
kaappi --lib-path ../kaappi-net/lib \
       --lib-path ../kaappi-http/lib \
       --lib-path ../kaappi-json/lib \
       app.scm

# After thottam:
kaappi app.scm
```

## List installed packages

```bash
$ thottam list
Installed packages:
  kaappi-net
  kaappi-http (depends: kaappi-net)
  kaappi-json
  kaappi-web (depends: kaappi-http kaappi-json)
```

## Update packages

```bash
thottam update              # update all installed packages
thottam update kaappi-web   # update a specific package
```

## Remove a package

```bash
thottam remove kaappi-web
```

## Version pinning

Pin a package to a specific tag or commit:

```bash
thottam install kaappi-web@v1.0.0
thottam install kaappi-http@abc1234
```

The resolved commit SHA is recorded in the lockfile (`~/.kaappi/thottam.lock`).

## Custom source URLs

Install a package from any Git URL using the `::` syntax:

```bash
thottam install kaappi-auth::https://github.com/bob/kaappi-auth
thottam install kaappi-http@v1.1::https://github.com/alice/kaappi-http
```

Without `::`, packages are fetched from `KAAPPI_ORG` (default:
`https://github.com/kaappi`). Custom URLs are recorded in the lockfile so
`thottam update` pulls from the correct source.

Dependencies can also specify source URLs in `kaappi.pkg`:

```
name: my-app
depends: kaappi-web kaappi-auth::https://github.com/bob/kaappi-auth
```

## Lockfile and reproducible installs

Every `thottam install` records the exact commit SHA in
`~/.kaappi/thottam.lock`. Use `--locked` to enforce the lockfile in CI or
production -- it refuses to install any package not already locked:

```bash
thottam --locked install kaappi-web   # fails if kaappi-web is not in lockfile
```

In `--locked` mode, the resolved SHA is also verified against the lockfile
entry. A mismatch aborts the install.

## Verify integrity

Check that all installed packages match their locked SHAs:

```bash
thottam verify
```

## Installation layout

```
~/.kaappi/
├── lib/                    # .sld files + native libraries
│   ├── kaappi/
│   │   ├── net.sld
│   │   ├── json.sld
│   │   ├── http.sld
│   │   ├── http/
│   │   │   ├── parse.sld
│   │   │   ├── client.sld
│   │   │   └── server.sld
│   │   └── web.sld
│   ├── libkaappi_net.dylib
│   └── libkaappi_pg.dylib
├── src/                    # Cloned source repos
│   ├── kaappi-net/
│   ├── kaappi-http/
│   └── ...
├── thottam.lock            # Pinned commit SHAs (and source URLs) for reproducibility
└── installed.txt           # Installed package list
```

## Package manifest

Each package has a `kaappi.pkg` file in its root:

```
name: kaappi-web
depends: kaappi-http kaappi-json
build: make
source: https://github.com/kaappi/kaappi-web
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | yes | Package name |
| `depends` | no | Space-separated dependency specs (`name[@ver][::url]`) |
| `build` | no | Build command (omit for pure Scheme) |
| `source` | no | Git URL where this package is hosted |

## Requirements

- Git (for cloning packages)
- C compiler (for packages with native code, e.g. kaappi-net)
- OpenSSL (`brew install openssl` / `apt install libssl-dev`) for kaappi-net
- PostgreSQL client libs (`brew install libpq` / `apt install libpq-dev`) for kaappi-pg

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KAAPPI_HOME` | `~/.kaappi` | Root directory for installed packages, source repos, and the lockfile |
| `KAAPPI_ORG` | `https://github.com/kaappi` | Base URL for fetching packages |

```bash
# Store packages in a project-local directory
KAAPPI_HOME=./vendor thottam install kaappi-json

# Fetch packages from a private GitHub org
KAAPPI_ORG=https://github.com/my-org thottam install my-lib
```
