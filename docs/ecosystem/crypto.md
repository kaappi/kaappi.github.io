# kaappi-crypto — Hashing & HMAC

```bash
thottam install kaappi-crypto
```

Requires OpenSSL (`brew install openssl` / `apt install libssl-dev`).

## Quick start

```scheme
(import (kaappi crypto))

(sha256 "hello")
;=> "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

(hmac-sha256 "secret-key" "message to sign")
;=> "..."
```

## API

### Hashing

```scheme
(sha256 string)    ; SHA-256, returns hex string
(sha512 string)    ; SHA-512
(sha1 string)      ; SHA-1
(md5 string)       ; MD5
```

### HMAC

```scheme
(hmac-sha256 key message)
(hmac-sha512 key message)
(hmac-sha1 key message)
(hmac-md5 key message)
```

All functions return lowercase hex-encoded strings.
