# Deployment

This guide covers deploying Kaappi applications to production: standalone
binaries, WebAssembly, Docker, systemd services, reverse proxies, and
health checks.

## Standalone binaries

Two approaches for compiling Scheme programs into standalone executables:

### Bytecode bundling (interpreter)

Compiles your program to bytecode and embeds it in the interpreter binary:

```bash
zig build -Dbundle-src=app.scm
```

### Native compilation (LLVM backend)

Compiles your program to native code via LLVM IR. The simplest way:

```bash
kaappi compile app.scm -o app
```

Or via the build system:

```bash
zig build native -Dnative-src=app.scm
```

Both produce a single executable with the Kaappi runtime included.
The native backend supports tail call optimization (self-recursive
functions run in constant stack space), variadic parameters, and
let/let* bindings compiled natively.

Copy the executable to the server and run it:

```bash
scp zig-out/bin/program server:/opt/myapp/myapp
ssh server '/opt/myapp/myapp'
```

### Cross-compilation

Build for a different platform from any host:

```bash
# Linux x86_64 (most cloud servers)
zig build -Dbundle-src=app.scm -Dtarget=x86_64-linux

# Linux ARM64 (AWS Graviton, Oracle Ampere)
zig build -Dbundle-src=app.scm -Dtarget=aarch64-linux

# Linux RISC-V
zig build -Dbundle-src=app.scm -Dtarget=riscv64-linux
```

No cross-compiler installation needed — Zig handles cross-compilation
natively.

## WebAssembly

Kaappi can be compiled to WebAssembly for use in browsers or WASI
runtimes:

```bash
zig build wasm    # produces zig-out/bin/kaappi.wasm
```

The WASM build runs the same bytecode interpreter but with several
limitations:

- **No REPL** — WASM mode takes a source file, not interactive input
- **Interpreter only** — no LLVM native compilation
- **No FFI** — `ffi-open`, `ffi-fn` are unavailable
- **No file I/O** — limited to WASI-compatible stdin/stdout
- **No profiling or coverage** — `--profile`, `--coverage` flags are not available
- **No library paths** — `--lib-path` is not supported; only built-in libraries
- **No OS threads** — SRFI-18 is disabled (green fibers still work)

The [playground](../playground.md) and [interactive tour](../tour.md) use
the WASM build to run Scheme directly in the browser.

## Docker

### Minimal Dockerfile

```dockerfile
FROM ubuntu:24.04 AS builder
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://kaappi-lang.org/install.sh | bash

FROM ubuntu:24.04
COPY --from=builder /usr/local/bin/kaappi /usr/local/bin/kaappi
COPY --from=builder /usr/local/bin/thottam /usr/local/bin/thottam

WORKDIR /app
COPY . .
RUN thottam install kaappi-web

EXPOSE 8080
CMD ["kaappi", "app.scm"]
```

### Standalone binary Dockerfile

Even smaller — use the standalone binary approach:

```dockerfile
FROM ubuntu:24.04
COPY myapp /usr/local/bin/myapp
EXPOSE 8080
CMD ["myapp"]
```

Build the binary first with `zig build -Dbundle-src=app.scm -Dtarget=x86_64-linux`,
then `COPY` the result.

### With native libraries

If your app uses kaappi-pg, kaappi-net, or other C FFI libraries, install
their system dependencies:

```dockerfile
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
    libpq5 \
    libssl3 \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/kaappi /usr/local/bin/kaappi
COPY --from=builder /root/.kaappi /root/.kaappi

WORKDIR /app
COPY . .
EXPOSE 8080
CMD ["kaappi", "app.scm"]
```

## systemd service

Create `/etc/systemd/system/myapp.service`:

```ini
[Unit]
Description=My Kaappi App
After=network.target postgresql.service

[Service]
Type=simple
User=myapp
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/myapp
Restart=on-failure
RestartSec=5

Environment=DB_HOST=localhost
Environment=DB_NAME=myapp
Environment=DB_USER=myapp
EnvironmentFile=-/opt/myapp/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
sudo journalctl -u myapp -f    # view logs
```

### Using the interpreter instead of a standalone binary

If you prefer not to compile a standalone binary:

```ini
ExecStart=/usr/local/bin/kaappi /opt/myapp/app.scm
```

## Reverse proxy

### Nginx

```nginx
upstream myapp {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name myapp.example.com;

    location / {
        proxy_pass http://myapp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Caddy

```
myapp.example.com {
    reverse_proxy localhost:8080
}
```

Caddy handles TLS certificates automatically via Let's Encrypt.

## Health checks

Add a health check endpoint for load balancers and monitoring:

```scheme
(GET "/health"
  (lambda (req params)
    (json-response '(("status" . "ok")))))
```

For deeper health checks that verify database connectivity:

```scheme
(GET "/health"
  (lambda (req params)
    (guard (e (#t
               (json-response
                 `(("status" . "error")
                   ("detail" . ,(condition/report e)))
                 503)))
      (pg-query db "SELECT 1")
      (json-response '(("status" . "ok"))))))
```

### Docker health check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
```

## Multi-process serving

For production concurrency, use `serve-prefork`:

```scheme
(serve-prefork
  (wrap app wrap-json-body wrap-logging wrap-errors)
  8080
  4)    ;; 4 worker processes
```

Each worker is a separate OS process with its own memory space. Workers
share the listen socket via `fork()`. This avoids GIL-style contention
and works well behind a reverse proxy.

A good starting point is one worker per CPU core:

```bash
# Check available cores
nproc    # Linux
sysctl -n hw.ncpu    # macOS
```

## Logging in production

Use JSON-format structured logging for machine-parseable output:

```scheme
(import (kaappi log))

(log-set-format! 'json)
(log-set-level! LOG-INFO)
```

Output goes to stderr by default, which systemd captures in the journal.
For file logging:

```scheme
(log-set-port! (open-output-file "/var/log/myapp/app.log"))
```

## Environment configuration

Use environment variables for configuration that changes between
environments:

```scheme
(define port
  (or (let ((p (get-environment-variable "PORT")))
        (and p (string->number p)))
      8080))

(define db-url
  (or (get-environment-variable "DATABASE_URL")
      "dbname=myapp"))

(serve app port)
```

## Pre-deployment checklist

- [ ] Application builds and runs without errors
- [ ] Tests pass (`kaappi tests/test-all.scm`)
- [ ] Health check endpoint responds
- [ ] Database migrations applied
- [ ] Environment variables set (database, secrets, ports)
- [ ] `wrap-errors` middleware catches unhandled exceptions
- [ ] Structured logging configured (`log-set-format! 'json`)
- [ ] Reverse proxy configured with TLS
- [ ] Process manager (systemd/Docker) restarts on crash
- [ ] Resource limits set (`--timeout`, `--max-memory` if applicable)
