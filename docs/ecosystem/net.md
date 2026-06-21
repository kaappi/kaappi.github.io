# Networking (TCP/TLS)

`(kaappi net)` — shared TCP client/server and TLS client. Used internally by kaappi-redis, kaappi-http, and kaappi-web.

```bash
thottam install kaappi-net
```

You typically don't use this library directly — the higher-level libraries handle it. But it's available for custom protocols.

## TCP Client

```scheme
(import (kaappi net))

(let ((fd (tcp-connect "example.com" 80)))
  (let ((req (string->utf8 "GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")))
    (tcp-send fd req (bytevector-length req)))
  (let ((buf (make-bytevector 4096 0)))
    (let ((n (tcp-recv fd buf 4096)))
      (display (utf8->string (bytevector-copy buf 0 n)))))
  (tcp-close fd))
```

## TCP Server

```scheme
(let ((listen-fd (tcp-listen "0.0.0.0" 8080)))
  (let loop ()
    (let ((client-fd (tcp-accept listen-fd)))
      ;; handle client...
      (tcp-close client-fd)
      (loop))))
```

## TLS Client

```scheme
(let ((ssl (tls-connect "api.github.com" 443)))
  (tls-send ssl request-bv (bytevector-length request-bv))
  (tls-recv ssl buf len)
  (tls-close ssl))
```

TLS includes SNI (Server Name Indication) and certificate verification via OpenSSL.

## API

### TCP

| Procedure | Description |
|-----------|-------------|
| `(tcp-connect host port [timeout])` | Connect to host:port, returns fd |
| `(tcp-listen host port [backlog])` | Bind + listen, returns listen fd |
| `(tcp-accept listen-fd)` | Accept connection, returns client fd |
| `(tcp-send fd buf len)` | Send bytes |
| `(tcp-recv fd buf len)` | Receive bytes (0 = EOF) |
| `(tcp-close fd)` | Close socket |
| `(tcp-last-error)` | Last errno |

### TLS

| Procedure | Description |
|-----------|-------------|
| `(tls-connect host port [timeout])` | TLS handshake, returns handle |
| `(tls-send ssl buf len)` | Send over TLS |
| `(tls-recv ssl buf len)` | Receive over TLS |
| `(tls-close ssl)` | Shutdown TLS + close socket |

### Non-blocking

| Procedure | Description |
|-----------|-------------|
| `(set-nonblocking fd)` | Set O_NONBLOCK on socket |
| `(poll-read fd timeout-ms)` | 1 = ready, 0 = timeout, -1 = error |
| `(nb-accept listen-fd)` | Non-blocking accept (-2 = EAGAIN) |
