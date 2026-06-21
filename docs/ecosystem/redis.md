# Redis

`(kaappi redis)` — Redis client with pure Scheme RESP2 protocol.

```bash
thottam install kaappi-redis
```

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
(redis-connect host port)              ; connect
(redis-connect host port password)     ; connect with AUTH
(redis-disconnect! conn)               ; close
(redis-connected? conn)                ; check connection
(redis-ping conn)                      ; => "PONG"
```

## String commands

```scheme
(redis-set conn "key" "value")         ;=> "OK"
(redis-get conn "key")                 ;=> "value" or #f
(redis-del conn "key" ...)             ;=> number deleted
(redis-exists conn "key")              ;=> #t or #f
(redis-incr conn "counter")            ;=> new value
(redis-decr conn "counter")            ;=> new value
(redis-expire conn "key" 60)           ;=> #t if set
(redis-ttl conn "key")                 ;=> seconds remaining
(redis-keys conn "user:*")             ;=> list of matching keys
(redis-mset conn "a" "1" "b" "2")     ;=> "OK"
(redis-mget conn "a" "b")             ;=> ("1" "2")
(redis-setnx conn "key" "value")       ;=> #t if set (key didn't exist)
(redis-setex conn "key" 60 "value")    ;=> "OK" (with TTL)
(redis-append conn "key" " world")     ;=> new length
(redis-strlen conn "key")              ;=> length
```

## List commands

```scheme
(redis-lpush conn "list" "a" "b" "c")  ;=> length
(redis-rpush conn "list" "x" "y")      ;=> length
(redis-lpop conn "list")               ;=> value or #f
(redis-rpop conn "list")               ;=> value or #f
(redis-lrange conn "list" 0 -1)        ;=> all elements
(redis-llen conn "list")               ;=> length
(redis-lindex conn "list" 0)           ;=> element at index
(redis-lset conn "list" 0 "new")       ;=> "OK"
```

## Hash commands

```scheme
(redis-hset conn "hash" "field" "val") ;=> 1
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
(redis-zrange conn "zset" 0 -1)        ;=> list (by score)
(redis-zscore conn "zset" "a")         ;=> score string
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
    #t))  ; return #f to unsubscribe
```

## Pipelining

Send multiple commands at once, read all replies together:

```scheme
(redis-pipeline conn
  '("SET" "a" "1")
  '("SET" "b" "2")
  '("GET" "a")
  '("GET" "b"))
;=> ("OK" "OK" "1" "2")
```

## Generic command

For any Redis command not covered by convenience functions:

```scheme
(redis-command conn "INFO" "server")
(redis-command conn "FLUSHDB")
(redis-command conn "SELECT" "1")
```

## Reply mapping

| Redis reply | Scheme value |
|-------------|-------------|
| Simple string (`+OK`) | `"OK"` |
| Bulk string | string |
| Null | `#f` |
| Integer | exact integer |
| Array | list |
| Error | raises Scheme error |
