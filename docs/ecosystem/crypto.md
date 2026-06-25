# Crypto

`(kaappi crypto)` — cryptographic hashing and HMAC.

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
;=> "97d2a569059bbcd8ead4444ff99071f4c01d005bcefe0d3567e1be628e5fdcd9"
```

## Hash functions

All hash functions take a string and return a lowercase hex-encoded digest:

```scheme
(sha256 "hello")
;=> "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

(sha512 "hello")
;=> "9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca7..."

(sha1 "hello")
;=> "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"

(md5 "hello")
;=> "5d41402abc4b2a76b9719d911017c592"
```

### Digest lengths

| Function | Algorithm | Hex length |
|----------|-----------|:----------:|
| `sha256` | SHA-256 | 64 |
| `sha512` | SHA-512 | 128 |
| `sha1` | SHA-1 | 40 |
| `md5` | MD5 | 32 |

### Empty string hashes

```scheme
(sha256 "")
;=> "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
```

!!! note "SHA-1 and MD5"
    SHA-1 and MD5 are provided for compatibility with existing systems
    (checksums, legacy APIs). For new security-sensitive code, use SHA-256
    or SHA-512.

## HMAC

HMAC (Hash-based Message Authentication Code) verifies both integrity and
authenticity of a message using a secret key:

```scheme
(hmac-sha256 "secret-key" "message to sign")
;=> "97d2a569059bbcd8ead4444ff99071f4c01d005bcefe0d3567e1be628e5fdcd9"

(hmac-sha512 "key" "message")
;=> "..."

(hmac-sha1 "key" "message")
;=> "..."

(hmac-md5 "key" "message")
;=> "..."
```

All HMAC functions return lowercase hex strings.

## Common patterns

### Verify a file checksum

```scheme
(import (scheme base) (scheme file) (kaappi crypto))

(define (file-sha256 path)
  (call-with-input-file path
    (lambda (port)
      (sha256 (read-string 1000000 port)))))

(string=? (file-sha256 "download.tar.gz")
          "expected-sha256-hex-string")
```

### API request signing

```scheme
(import (kaappi crypto) (kaappi http) (kaappi json))

(define (signed-request url api-key api-secret)
  (let* ((timestamp (number->string (exact (current-second))))
         (signature (hmac-sha256 api-secret
                      (string-append timestamp url))))
    (http-get url
      `(("X-API-Key" . ,api-key)
        ("X-Timestamp" . ,timestamp)
        ("X-Signature" . ,signature)))))
```

### Password hashing

For password storage, hash with a unique salt per user:

```scheme
(define (hash-password password salt)
  (sha256 (string-append salt password)))

(define (verify-password password salt expected-hash)
  (string=? (hash-password password salt) expected-hash))
```

!!! note "Production password hashing"
    SHA-256 is fast, which makes it weak for password hashing against brute
    force. For production, use a dedicated password hashing algorithm
    (bcrypt, scrypt, Argon2) via FFI if available.

### Webhook signature verification

```scheme
(define (verify-webhook-signature body secret signature)
  (string=? (hmac-sha256 secret body) signature))

;; In a web handler:
(POST "/webhook"
  (lambda (req params)
    (let ((body (request-body req))
          (sig (request-header req "x-signature")))
      (if (verify-webhook-signature body webhook-secret sig)
          (begin (process-webhook body)
                 (json-response '(("ok" . #t))))
          (json-response '(("error" . "invalid signature")) 403)))))
```

## API reference

### Hashing

| Procedure | Description |
|-----------|-------------|
| `(sha256 string)` | SHA-256 hash, returns hex |
| `(sha512 string)` | SHA-512 hash, returns hex |
| `(sha1 string)` | SHA-1 hash, returns hex |
| `(md5 string)` | MD5 hash, returns hex |

### HMAC

| Procedure | Description |
|-----------|-------------|
| `(hmac-sha256 key message)` | HMAC-SHA256 |
| `(hmac-sha512 key message)` | HMAC-SHA512 |
| `(hmac-sha1 key message)` | HMAC-SHA1 |
| `(hmac-md5 key message)` | HMAC-MD5 |
