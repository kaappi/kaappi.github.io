# Email (SMTP)

`(kaappi email)` — send email via SMTP with TLS and authentication.

```bash
thottam install kaappi-email
```

Depends on [kaappi-net](net.md) (auto-installed).

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

## High-level API

### `send-email`

```scheme
(send-email host port from to subject body [options...])
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | string | SMTP server hostname |
| `port` | integer | SMTP port (465 for TLS, 587 for STARTTLS, 25 for plain) |
| `from` | string | Sender email address |
| `to` | list | List of recipient email addresses |
| `subject` | string | Email subject line |
| `body` | string | Email body text |

### Options

| Option | Type | Description |
|--------|------|-------------|
| `'tls` | boolean | Use TLS connection (port 465) |
| `'user` | string | SMTP username for authentication |
| `'password` | string | SMTP password |
| `'domain` | string | EHLO domain |
| `'cc` | list | CC recipients |

### Send to multiple recipients

```scheme
(send-email "smtp.example.com" 465
  "sender@example.com"
  '("alice@example.com" "bob@example.com")
  "Team Update"
  "Here is the weekly update."
  'tls #t
  'user "sender@example.com"
  'password "password"
  'cc '("manager@example.com"))
```

## Message construction

Build messages without sending them — useful for testing or custom
delivery:

```scheme
(import (kaappi email mime))

(define msg
  (make-message
    "sender@example.com"
    '("recipient@example.com")
    "Test Subject"
    "Hello, world!"))

(display (message->string msg))
```

The `(kaappi email mime)` sub-library handles message construction
independently from the network layer.

## Low-level SMTP

For full control over the SMTP session:

```scheme
(import (kaappi email smtp))

(define smtp (smtp-connect-tls "smtp.gmail.com" 465))
(smtp-ehlo smtp "example.com")
(smtp-auth-plain smtp "user@gmail.com" "app-password")

(define msg (make-message "from@example.com" '("to@example.com")
              "Subject" "Body"))
(smtp-send-message smtp msg)

(smtp-close smtp)
```

### SMTP procedures

| Procedure | Description |
|-----------|-------------|
| `(smtp-connect host port)` | Plain SMTP connection |
| `(smtp-connect-tls host port)` | TLS SMTP connection |
| `(smtp-ehlo smtp domain)` | Send EHLO greeting |
| `(smtp-auth-plain smtp user pass)` | PLAIN authentication |
| `(smtp-send-message smtp msg)` | Send a constructed message |
| `(smtp-close smtp)` | Close connection |

## Provider setup

### Gmail

Use an [App Password](https://support.google.com/accounts/answer/185833)
(not your regular password):

```scheme
(send-email "smtp.gmail.com" 465
  "you@gmail.com" '("to@example.com")
  "Subject" "Body"
  'tls #t
  'user "you@gmail.com"
  'password "your-16-char-app-password"
  'domain "gmail.com")
```

### Amazon SES

```scheme
(send-email "email-smtp.us-east-1.amazonaws.com" 465
  "verified@yourdomain.com" '("to@example.com")
  "Subject" "Body"
  'tls #t
  'user "AKIAIOSFODNN7EXAMPLE"
  'password "ses-smtp-password"
  'domain "yourdomain.com")
```

### Local / development

For testing without authentication:

```scheme
(send-email "localhost" 1025
  "test@localhost" '("dev@localhost")
  "Test" "Testing email locally")
```

Use [MailHog](https://github.com/mailhog/MailHog) or similar for local
SMTP testing.

## Sub-libraries

| Library | Purpose |
|---------|---------|
| `(kaappi email)` | High-level `send-email` |
| `(kaappi email mime)` | Message construction (no network) |
| `(kaappi email smtp)` | Low-level SMTP protocol |

## Utilities

```scheme
(base64-encode "hello")  ;=> "aGVsbG8="
```

## API reference

### High-level

| Procedure | Description |
|-----------|-------------|
| `(send-email host port from to subject body [opts])` | Send email |

### Message

| Procedure | Description |
|-----------|-------------|
| `(make-message from to subject body [opts])` | Create message |
| `(message->string msg)` | Render to MIME string |

### SMTP

| Procedure | Description |
|-----------|-------------|
| `(smtp-connect host port)` | Plain connection |
| `(smtp-connect-tls host port)` | TLS connection |
| `(smtp-ehlo smtp domain)` | EHLO greeting |
| `(smtp-auth-plain smtp user pass)` | Authenticate |
| `(smtp-send-message smtp msg)` | Send message |
| `(smtp-close smtp)` | Close connection |
