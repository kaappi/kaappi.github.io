# Redis

`(kaappi redis)` — Redis client with strings, lists, hashes, sets, sorted
sets, pub/sub, and pipelining.

```bash
thottam install kaappi-redis
```

Depends on [kaappi-net](net.md) (auto-installed). Uses the RESP2 protocol
(pure Scheme, no C dependencies beyond kaappi-net).

## Quick start

```scheme
(import (kaappi redis))

(define conn (redis-connect "127.0.0.1" 6379))

(redis-set conn "greeting" "hello!")
(redis-get conn "greeting")  ;=> "hello!"

(redis-disconnect! conn)
```

## Connection

```scheme
(redis-connect host port)              ;; connect
(redis-connect host port password)     ;; connect with AUTH
(redis-disconnect! conn)               ;; close
(redis-connected? conn)                ;; check connection
(redis-ping conn)                      ;=> "PONG"
```

## String commands

```scheme
(redis-set conn "key" "value")         ;=> "OK"
(redis-get conn "key")                 ;=> "value" or #f if missing
(redis-del conn "key" ...)             ;=> number deleted
(redis-exists conn "key")              ;=> #t or #f
(redis-incr conn "counter")            ;=> new value (integer)
(redis-decr conn "counter")            ;=> new value (integer)
(redis-expire conn "key" 60)           ;=> #t if timeout was set
(redis-ttl conn "key")                 ;=> seconds remaining, -1 if no expiry
(redis-keys conn "user:*")             ;=> list of matching keys
(redis-mset conn "a" "1" "b" "2")     ;=> "OK"
(redis-mget conn "a" "b")             ;=> ("1" "2")
(redis-setnx conn "key" "value")       ;=> #t if key was set (didn't exist)
(redis-setex conn "key" 60 "value")    ;=> "OK" (set with TTL in seconds)
(redis-append conn "key" " world")     ;=> new string length
(redis-strlen conn "key")              ;=> string length
```

## List commands

```scheme
(redis-lpush conn "list" "a" "b" "c")  ;=> list length
(redis-rpush conn "list" "x" "y")      ;=> list length
(redis-lpop conn "list")               ;=> value or #f
(redis-rpop conn "list")               ;=> value or #f
(redis-lrange conn "list" 0 -1)        ;=> all elements
(redis-llen conn "list")               ;=> length
(redis-lindex conn "list" 0)           ;=> element at index
(redis-lset conn "list" 0 "new")       ;=> "OK"
```

## Hash commands

```scheme
(redis-hset conn "hash" "field" "val") ;=> 1 (new field) or 0 (updated)
(redis-hget conn "hash" "field")       ;=> "val" or #f
(redis-hdel conn "hash" "field")       ;=> number deleted
(redis-hgetall conn "hash")            ;=> (("f1" . "v1") ("f2" . "v2"))
(redis-hexists conn "hash" "field")    ;=> #t or #f
(redis-hkeys conn "hash")             ;=> list of field names
(redis-hvals conn "hash")             ;=> list of values
(redis-hlen conn "hash")              ;=> number of fields
```

## Set commands

```scheme
(redis-sadd conn "set" "a" "b" "c")   ;=> number added
(redis-srem conn "set" "a")           ;=> number removed
(redis-smembers conn "set")           ;=> list of members
(redis-sismember conn "set" "a")       ;=> #t or #f
(redis-scard conn "set")              ;=> cardinality
```

## Sorted set commands

```scheme
(redis-zadd conn "zset" 1.0 "a")      ;=> 1
(redis-zrem conn "zset" "a")          ;=> number removed
(redis-zrange conn "zset" 0 -1)        ;=> list ordered by score
(redis-zscore conn "zset" "a")         ;=> score as string
(redis-zcard conn "zset")             ;=> cardinality
(redis-zrank conn "zset" "a")          ;=> 0-based rank
```

## Pub/Sub

```scheme
;; Publish
(redis-publish conn "channel" "message")  ;=> number of receivers

;; Subscribe (blocking)
(redis-subscribe conn "channel"
  (lambda (channel message)
    (display message) (newline)
    #t))  ;; return #f to unsubscribe
```

The subscribe callback receives each message. Return `#t` to keep
listening, `#f` to unsubscribe and return.

## Pipelining

Send multiple commands at once to reduce round trips:

```scheme
(redis-pipeline conn
  '("SET" "a" "1")
  '("SET" "b" "2")
  '("GET" "a")
  '("GET" "b"))
;=> ("OK" "OK" "1" "2")
```

Pipelining sends all commands before reading any replies. This is much
faster than individual commands when you have many operations.

## Generic command

For Redis commands not covered by convenience functions:

```scheme
(redis-command conn "INFO" "server")
(redis-command conn "FLUSHDB")
(redis-command conn "SELECT" "1")
(redis-command conn "TYPE" "mykey")
```

## Reply mapping

| Redis reply | Scheme value |
|-------------|-------------|
| Simple string (`+OK`) | `"OK"` |
| Bulk string | string |
| Null bulk string | `#f` |
| Integer | exact integer |
| Array | list |
| Error | raises Scheme error |

## Common patterns

### Caching with expiry

```scheme
(define (cache-get conn key)
  (redis-get conn key))

(define (cache-set conn key value ttl-seconds)
  (redis-setex conn key ttl-seconds value))

(define (cache-or-compute conn key ttl compute)
  (or (cache-get conn key)
      (let ((val (compute)))
        (cache-set conn key val ttl)
        val)))
```

### Rate limiting

```scheme
(define (rate-limited? conn client-id max-requests window-seconds)
  (let ((key (string-append "rate:" client-id)))
    (let ((count (redis-incr conn key)))
      (when (= count 1)
        (redis-expire conn key window-seconds))
      (> count max-requests))))
```

### Job queue

```scheme
;; Producer
(define (enqueue conn queue job-data)
  (redis-rpush conn queue (json-write-string job-data)))

;; Consumer
(define (dequeue conn queue)
  (let ((data (redis-lpop conn queue)))
    (if data (json-read-string data) #f)))
```

### Session store

```scheme
(define (session-save conn session-id data ttl)
  (redis-setex conn
    (string-append "session:" session-id)
    ttl
    (json-write-string data)))

(define (session-load conn session-id)
  (let ((data (redis-get conn (string-append "session:" session-id))))
    (if data (json-read-string data) #f)))
```

## API reference

### Connection

| Procedure | Description |
|-----------|-------------|
| `(redis-connect host port [password])` | Connect to Redis |
| `(redis-disconnect! conn)` | Close connection |
| `(redis-connected? conn)` | Check connection |
| `(redis-ping conn)` | Ping server |

### Strings

| Procedure | Description |
|-----------|-------------|
| `(redis-get conn key)` | Get value |
| `(redis-set conn key value)` | Set value |
| `(redis-del conn key ...)` | Delete keys |
| `(redis-exists conn key)` | Check existence |
| `(redis-incr conn key)` | Increment |
| `(redis-decr conn key)` | Decrement |
| `(redis-expire conn key seconds)` | Set TTL |
| `(redis-ttl conn key)` | Get TTL |
| `(redis-keys conn pattern)` | Find keys |
| `(redis-mset conn k v ...)` | Set multiple |
| `(redis-mget conn k ...)` | Get multiple |
| `(redis-setnx conn key value)` | Set if not exists |
| `(redis-setex conn key seconds value)` | Set with TTL |
| `(redis-append conn key value)` | Append to string |
| `(redis-strlen conn key)` | String length |

### Lists

| Procedure | Description |
|-----------|-------------|
| `(redis-lpush conn key val ...)` | Push to head |
| `(redis-rpush conn key val ...)` | Push to tail |
| `(redis-lpop conn key)` | Pop from head |
| `(redis-rpop conn key)` | Pop from tail |
| `(redis-lrange conn key start stop)` | Get range |
| `(redis-llen conn key)` | List length |
| `(redis-lindex conn key index)` | Get by index |
| `(redis-lset conn key index value)` | Set by index |

### Hashes

| Procedure | Description |
|-----------|-------------|
| `(redis-hset conn key field value)` | Set field |
| `(redis-hget conn key field)` | Get field |
| `(redis-hdel conn key field)` | Delete field |
| `(redis-hgetall conn key)` | Get all as alist |
| `(redis-hexists conn key field)` | Check field |
| `(redis-hkeys conn key)` | All field names |
| `(redis-hvals conn key)` | All values |
| `(redis-hlen conn key)` | Field count |

### Sets

| Procedure | Description |
|-----------|-------------|
| `(redis-sadd conn key val ...)` | Add members |
| `(redis-srem conn key val)` | Remove member |
| `(redis-smembers conn key)` | All members |
| `(redis-sismember conn key val)` | Check membership |
| `(redis-scard conn key)` | Cardinality |

### Sorted sets

| Procedure | Description |
|-----------|-------------|
| `(redis-zadd conn key score val)` | Add with score |
| `(redis-zrem conn key val)` | Remove |
| `(redis-zrange conn key start stop)` | Range by rank |
| `(redis-zscore conn key val)` | Get score |
| `(redis-zcard conn key)` | Cardinality |
| `(redis-zrank conn key val)` | Get rank |

### Pub/Sub and pipeline

| Procedure | Description |
|-----------|-------------|
| `(redis-publish conn channel message)` | Publish |
| `(redis-subscribe conn channel callback)` | Subscribe (blocking) |
| `(redis-pipeline conn cmd ...)` | Pipeline commands |
| `(redis-command conn cmd arg ...)` | Generic command |
