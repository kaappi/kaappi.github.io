# Ecosystem

Kaappi has a growing ecosystem of libraries. All are installed with **thottam**, the Kaappi package manager.

## Web & Networking

| Package | Description |
|---------|-------------|
| [kaappi-net](net.md) | TCP client/server and TLS client |
| [kaappi-http](http.md) | HTTP/HTTPS client and HTTP server |
| [kaappi-web](web.md) | Web framework (routing, middleware, JSON helpers) |
| [kaappi-template](template.md) | Text and HTML template engine (auto-escaping) |
| [kaappi-email](email.md) | SMTP email client (plain and TLS) |

## Data Formats

| Package | Description |
|---------|-------------|
| [kaappi-json](json.md) | JSON parser and serializer |
| [kaappi-toml](toml.md) | TOML parser and serializer |
| [kaappi-yaml](yaml.md) | YAML parser and writer |
| [kaappi-csv](csv.md) | CSV parser and writer (RFC 4180) |

## Databases

| Package | Description |
|---------|-------------|
| [kaappi-pg](pg.md) | PostgreSQL client with DB-API 2.0 style cursors |
| [kaappi-sqlite](sqlite.md) | SQLite client with cursors |
| [kaappi-redis](redis.md) | Redis client (strings, lists, hashes, pub/sub) |

## Developer Tools

| Package | Description |
|---------|-------------|
| [kaappi-test](test.md) | Test framework (assertions, groups, reporting) |
| [kaappi-log](log.md) | Structured logging (text and JSON formats) |
| [kaappi-crypto](crypto.md) | Hashing (SHA-256/512, MD5) and HMAC |
| [kaappi-cli](cli.md) | CLI argument parsing, subcommands, help generation |

## Getting started

```bash
# thottam is included when you install Kaappi:
# curl -fsSL https://kaappi-lang.org/install.sh | bash

# Install a library:
thottam install kaappi-web

# That's it. Now use it:
kaappi my-app.scm
```

No `--lib-path` flags, no `DYLD_LIBRARY_PATH` — thottam handles everything.

## Dependency graph

```
kaappi-web ──→ kaappi-http ──→ kaappi-net (TCP/TLS)
           └─→ kaappi-json

kaappi-email ──→ kaappi-net
kaappi-redis ──→ kaappi-net

kaappi-pg (standalone, links libpq)
kaappi-sqlite (standalone, links libsqlite3)
kaappi-crypto (standalone, links OpenSSL)

kaappi-toml, kaappi-yaml, kaappi-csv, kaappi-template,
kaappi-test, kaappi-log, kaappi-cli (pure Scheme, no dependencies)
```

When you install a package, thottam automatically installs its dependencies.
