# Read Configuration Files

This recipe covers application configuration: loading a
[TOML](../ecosystem/toml.md) or [YAML](../ecosystem/yaml.md) file,
applying defaults, letting environment variables override the file, and
failing fast on invalid settings.

## Setup

```bash
thottam install kaappi-toml    # or kaappi-yaml
```

Both are pure Scheme — no system dependencies.

## Load a TOML config

Given `app.toml`:

```toml
[server]
host = "127.0.0.1"
port = 8080

[database]
url = "sqlite:///app.db"

[logging]
level = "info"
```

Parse it and read nested keys with `toml-ref*`:

```scheme
(import (scheme base) (scheme file) (kaappi toml))

(define config (call-with-input-file "app.toml" toml-read))

(toml-ref* config "server" "port")     ;=> 8080
(toml-ref* config "database" "url")    ;=> "sqlite:///app.db"
(toml-ref* config "missing" "key")     ;=> #f
```

## Apply defaults

`toml-ref*` returns `#f` for missing keys, so `or` gives you defaults in
one line:

```scheme
(define port  (or (toml-ref* config "server" "port") 8080))
(define host  (or (toml-ref* config "server" "host") "0.0.0.0"))
(define level (or (toml-ref* config "logging" "level") "info"))
```

To tolerate a missing config file entirely:

```scheme
(define (load-config path)
  (if (file-exists? path)
      (call-with-input-file path toml-read)
      '()))
```

## Override with environment variables

The common production pattern: the file holds defaults, the environment
wins. This keeps secrets out of files and matches how Docker and systemd
inject settings (see
[Deployment](../guide/deployment.md#environment-configuration)):

```scheme
(import (scheme process-context))

(define (config-value env-name config-keys default)
  (or (get-environment-variable env-name)
      (apply toml-ref* config config-keys)
      default))

(define port
  (let ((v (config-value "PORT" '("server" "port") 8080)))
    (if (string? v) (string->number v) v)))

(define db-url (config-value "DATABASE_URL" '("database" "url") "sqlite:///app.db"))
```

Environment variables are always strings — convert numbers with
`string->number` as above.

## Validate at startup

Fail fast with a clear message instead of crashing mid-request:

```scheme
(define (require-config! value name)
  (unless value
    (error "missing required config" name))
  value)

(define api-key
  (require-config! (get-environment-variable "API_KEY") "API_KEY"))

(unless (and (exact-integer? port) (< 0 port 65536))
  (error "server.port must be an integer between 1 and 65535" port))
```

## YAML instead of TOML

The [kaappi-yaml](../ecosystem/yaml.md) API mirrors the TOML one —
`yaml-read`, `yaml-ref`, `yaml-ref*`:

```scheme
(import (kaappi yaml))

;; app.yml:
;;   server:
;;     host: 127.0.0.1
;;     port: 8080

(define config (call-with-input-file "app.yml" yaml-read))
(yaml-ref* config "server" "port")   ;=> 8080
```

TOML and YAML both map files to alists, so the defaults, override, and
validation patterns above work unchanged with either format.

## Write a config file

Useful for `init` subcommands that scaffold a default config:

```scheme
(call-with-output-file "app.toml"
  (lambda (port)
    (toml-write
      '(("server" . (("host" . "0.0.0.0")
                     ("port" . 8080)))
        ("logging" . (("level" . "info"))))
      port)))
```

## Going further

- Full APIs: [kaappi-toml](../ecosystem/toml.md), [kaappi-yaml](../ecosystem/yaml.md)
- JSON config instead: [Process JSON Data](json-processing.md)
- Wiring config into a service: [Deployment](../guide/deployment.md)
