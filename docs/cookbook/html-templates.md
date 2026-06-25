# Serve HTML with Templates

This recipe builds a web application that serves dynamic HTML pages using
the template engine with auto-escaping, layouts, and data from a database.

## Setup

```bash
thottam install kaappi-web
thottam install kaappi-template
thottam install kaappi-sqlite
```

## A minimal template server

```scheme
(import (scheme base) (kaappi web) (kaappi template))

(define page-template "
<html>
<head><title>{{.title}}</title></head>
<body>
  <h1>{{.title}}</h1>
  <p>{{.message}}</p>
</body>
</html>")

(define app
  (routes
    (GET "/"
      (lambda (req params)
        (html-response
          (template-render-html page-template
            '(("title" . "Home")
              ("message" . "Welcome to Kaappi!"))))))))

(serve (wrap app wrap-errors) 8080)
```

`template-render-html` auto-escapes all values — any `<`, `>`, `&`, `"`, or
`'` in the data is replaced with HTML entities, preventing XSS.

## Template syntax

### Variables

```
{{.name}}              key from the data alist
{{.user.email}}        nested dotted path
{{.}}                  current value (inside range)
```

### Conditionals

```
{{if .logged_in}}
  <p>Welcome back, {{.username}}!</p>
{{else}}
  <p>Please <a href="/login">log in</a>.</p>
{{end}}
```

Falsy values: `#f`, `'null`, `""`, `()`, `0`.

### Loops

```
{{range .items}}
<li>{{.name}} — ${{.price}}</li>
{{end}}
```

Inside `range`, `{{.}}` refers to the current item. Use `{{.field}}` to
access fields of each item.

## Layout pattern

Build a reusable layout by composing templates:

```scheme
(define layout "
<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\">
  <title>{{.title}} — My App</title>
  <style>
    body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
    nav a { margin-right: 15px; }
  </style>
</head>
<body>
  <nav>
    <a href=\"/\">Home</a>
    <a href=\"/contacts\">Contacts</a>
  </nav>
  <hr>
  {{.body}}
</body>
</html>")

(define (render-page title body-html)
  (template-render-html layout
    `(("title" . ,title)
      ("body"  . ,body-html))))
```

Then each page renders its body and wraps it in the layout:

```scheme
(define contact-list-template "
<h1>Contacts</h1>
{{if .contacts}}
<table>
  <tr><th>Name</th><th>Email</th></tr>
  {{range .contacts}}
  <tr><td>{{.name}}</td><td>{{.email}}</td></tr>
  {{end}}
</table>
{{else}}
<p>No contacts yet.</p>
{{end}}
")
```

## Full example: contact book

A complete app with SQLite storage, listing, and adding contacts:

```scheme
(import (scheme base) (kaappi web) (kaappi template) (kaappi sqlite))

;; --- Templates ---

(define layout "<!DOCTYPE html>
<html><head><meta charset=\"utf-8\">
<title>{{.title}}</title>
<style>
  body { font-family: system-ui; max-width: 700px; margin: 40px auto; padding: 0 20px; }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
  input, button { padding: 8px; margin: 4px 0; }
  input { width: 200px; }
  nav a { margin-right: 12px; }
</style></head>
<body><nav><a href=\"/\">Home</a> <a href=\"/contacts\">Contacts</a></nav>
<hr>{{.body}}</body></html>")

(define home-body "<h1>Contact Book</h1><p>A simple contact manager.</p>")

(define list-body "
<h1>Contacts ({{.count}})</h1>
{{if .contacts}}
<table><tr><th>Name</th><th>Email</th></tr>
{{range .contacts}}<tr><td>{{.name}}</td><td>{{.email}}</td></tr>{{end}}
</table>
{{else}}<p>No contacts yet.</p>{{end}}
<h2>Add Contact</h2>
<form method=\"POST\" action=\"/contacts\">
  <input name=\"name\" placeholder=\"Name\" required>
  <input name=\"email\" placeholder=\"Email\" required>
  <button type=\"submit\">Add</button>
</form>")

(define (render title body-html)
  (template-render-html layout
    `(("title" . ,title) ("body" . ,body-html))))

;; --- Database ---

(define db (sqlite-open "contacts.db"))
(sqlite-exec db "CREATE TABLE IF NOT EXISTS contacts (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL)")

;; --- Routes ---

(define app
  (routes
    (GET "/"
      (lambda (req params)
        (html-response (render "Home" home-body))))

    (GET "/contacts"
      (lambda (req params)
        (let* ((rows (sqlite-query db "SELECT name, email FROM contacts ORDER BY name"))
               (contacts (map (lambda (r)
                                `(("name" . ,(vector-ref r 0))
                                  ("email" . ,(vector-ref r 1))))
                              rows)))
          (html-response
            (render "Contacts"
              (template-render-html list-body
                `(("count" . ,(length contacts))
                  ("contacts" . ,contacts))))))))

    (POST "/contacts"
      (lambda (req params)
        (let ((body (request-body req)))
          (let* ((parts (parse-query-string body))
                 (name (cdr (assoc "name" parts)))
                 (email (cdr (assoc "email" parts))))
            (sqlite-exec db "INSERT INTO contacts (name, email) VALUES (?, ?)"
              name email)
            (redirect "/contacts")))))))

(serve
  (wrap app wrap-logging wrap-errors)
  8080)
```

Run it:

```bash
kaappi app.scm
# Open http://localhost:8080 in a browser
```

## Pre-parse templates for performance

If a template is rendered on every request, parse it once and reuse the AST:

```scheme
(define list-ast (template-parse list-body))

;; In the handler:
(template-execute list-ast data html-escape)
```

`template-parse` returns an AST. `template-execute` runs it with a custom
escape function — use `html-escape` for HTML output or `values` for no
escaping.
