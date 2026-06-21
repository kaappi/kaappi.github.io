# thottam — Package Manager

**thottam** installs, updates, and removes Kaappi ecosystem libraries.

## Commands

```bash
thottam install <package>    # Install a package and its dependencies
thottam remove <package>     # Remove a package
thottam list                 # List installed packages
thottam update [package]     # Update one or all packages
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
└── installed.txt           # Installed package list
```

## Package manifest

Each package has a `kaappi.pkg` file in its root:

```
name: kaappi-web
depends: kaappi-http kaappi-json
build: make
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | yes | Package name |
| `depends` | no | Space-separated dependency names |
| `build` | no | Build command (omit for pure Scheme) |

## Requirements

- Git (for cloning packages)
- C compiler (for packages with native code)
- OpenSSL (`brew install openssl` / `apt install libssl-dev`) for kaappi-net
- PostgreSQL client libs for kaappi-pg
