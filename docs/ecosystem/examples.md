# Examples

Complete example applications demonstrating how to build real programs
with Kaappi and its ecosystem libraries.

```bash
git clone https://github.com/kaappi/kaappi-examples
cd kaappi-examples
```

## Setup

Install the required libraries:

```bash
thottam install kaappi-web     # also installs kaappi-http, kaappi-json, kaappi-net
thottam install kaappi-redis
thottam install kaappi-pg
```

## REST API

Full REST API server with PostgreSQL storage, Redis caching, and JSON
request/response handling via the kaappi-web framework.

**Uses:** kaappi-web, kaappi-pg, kaappi-redis, kaappi-json

```bash
createdb kaappi_demo
redis-server --daemonize yes
cd rest-api && kaappi app.scm
```

```bash
# Create a user
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"Alice","email":"alice@example.com"}' \
     http://localhost:8080/users

# List users
curl http://localhost:8080/users

# Get user (cached in Redis)
curl http://localhost:8080/users/1
```

## Redis Task Queue

Producer/consumer job queue using Redis lists.

**Uses:** kaappi-redis

```bash
cd redis-task-queue
kaappi app.scm producer   # enqueue 10 tasks
kaappi app.scm worker     # process all tasks
kaappi app.scm status     # show results
```

## PostgreSQL CRUD

Interactive contact book with full CRUD, search, and statistics.

**Uses:** kaappi-pg

```bash
cd pg-crud
createdb kaappi_demo
kaappi app.scm seed           # insert sample data
kaappi app.scm list           # list all contacts
kaappi app.scm search alice   # search by name/email
kaappi app.scm stats          # show statistics
```

## HTTP File Server

Serves static files from a directory with MIME type detection.

**Uses:** kaappi-http

```bash
cd http-file-server
kaappi app.scm 8080 .    # serve current directory on port 8080
```
