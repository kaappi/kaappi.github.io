# kaappi-template — Template Engine

```bash
thottam install kaappi-template
```

Pure Scheme — no dependencies.

## Quick start

```scheme
(import (kaappi template))

;; Plain text
(template-render "Hello, {{.name}}!" '(("name" . "Alice")))
;=> "Hello, Alice!"

;; HTML (auto-escapes <>&"')
(template-render-html "<p>{{.content}}</p>"
  '(("content" . "<script>alert('xss')</script>")))
;=> "<p>&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;</p>"
```

## Template syntax

### Variables

```
{{.name}}           key from data
{{.user.email}}     nested dotted path
{{.}}               current value (inside range)
```

### Conditionals

```
{{if .logged_in}}Welcome!{{else}}Please log in.{{end}}
```

### Loops

```
{{range .items}}  {{.name}}: ${{.price}}
{{end}}
```

## API

```scheme
(template-render tmpl data)        ; plain text
(template-render-html tmpl data)   ; HTML with auto-escaping
(template-parse tmpl)              ; parse to reusable AST
(template-execute ast data esc)    ; execute with custom escape
(html-escape str)                  ; HTML entity escaping
```

Data is an alist. Nested data uses nested alists. Falsy: `#f`, `'null`, `""`, `()`, `0`.
