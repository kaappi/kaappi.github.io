# Ecosystem

Kaappi has a growing ecosystem of libraries for web development, databases, and networking. All libraries are installed with **thottam**, the Kaappi package manager.

## Libraries

| Package | Description |
|---------|-------------|
| [kaappi-net](net.md) | TCP client/server and TLS client (shared networking layer) |
| [kaappi-json](json.md) | JSON parser and serializer |
| [kaappi-redis](redis.md) | Redis client (strings, lists, hashes, sets, pub/sub, pipelining) |
| [kaappi-pg](pg.md) | PostgreSQL client with DB-API 2.0 style cursors |
| [kaappi-http](http.md) | HTTP/HTTPS client and HTTP server |
| [kaappi-web](web.md) | Web framework (routing, middleware, JSON helpers) |

## Getting started

```bash
# Install thottam (comes with Kaappi)
# Then install a library:
thottam install kaappi-web

# That's it. Now use it:
kaappi my-app.scm
```

No `--lib-path` flags, no `DYLD_LIBRARY_PATH` — thottam handles everything.

## Dependency graph

```
kaappi-web ──→ kaappi-http ──→ kaappi-net (TCP/TLS)
           └─→ kaappi-json

kaappi-redis ──→ kaappi-net

kaappi-pg (standalone, links libpq)
```

When you install a package, thottam automatically installs its dependencies.
