# kaappi-email — SMTP Client

```bash
thottam install kaappi-email
```

Depends on `kaappi-net` (auto-installed).

## Quick start

```scheme
(import (kaappi email))

(send-email "smtp.gmail.com" 465
  "you@gmail.com"
  '("recipient@example.com")
  "Hello from Kaappi!"
  "This email was sent from Kaappi Scheme."
  'tls #t
  'user "you@gmail.com"
  'password "your-app-password"
  'domain "gmail.com")
```

## API

### High-level

```scheme
(send-email host port from to subject body [options...])
```

Options: `'tls #t`, `'user "..."`, `'password "..."`, `'domain "..."`, `'cc '("...")`

### Message construction

```scheme
(make-message from to subject body [options...])
(message->string msg)    ; render to MIME string
```

Works standalone via `(import (kaappi email mime))` — no network needed.

### Low-level SMTP

```scheme
(smtp-connect host port)
(smtp-connect-tls host port)
(smtp-ehlo smtp domain)
(smtp-auth-plain smtp user pass)
(smtp-send-message smtp msg)
(smtp-close smtp)
```

### Utilities

```scheme
(base64-encode string)
```

## Sub-libraries

- `(kaappi email)` — high-level sending
- `(kaappi email mime)` — message construction (no network)
- `(kaappi email smtp)` — low-level SMTP protocol
