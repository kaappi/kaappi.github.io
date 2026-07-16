# Editor Support

Kaappi includes a Language Server Protocol (LSP) server for IDE integration.

## VS Code

Install the [Kaappi Scheme extension](https://github.com/kaappi/vscode-kaappi):

### From source

```bash
git clone https://github.com/kaappi/vscode-kaappi
cd vscode-kaappi
npm install
npm run compile
```

Then press **F5** in VS Code to launch an Extension Development Host, or copy the folder to `~/.vscode/extensions/`.

### Features

- **Syntax highlighting** for `.scm`, `.sld`, `.ss`, `.sls` files
- **Auto-completion** of all 600+ built-in procedures and your definitions
- **Hover information** showing type and arity of procedures
- **Go to Definition** — jump to where a symbol is defined (Ctrl+Click or F12)
- **Find References** — find all uses of a symbol (Shift+F12)
- **Document outline** — lists all `define`, `define-syntax`, `define-record-type` forms (breadcrumbs and outline view)
- **Real-time diagnostics** for parse and compile errors
- **Bracket matching** and auto-closing for parentheses
- **Comment toggling** — line (`;`) and block (`#| |#`)

### Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `kaappi.lspPath` | `kaappi-lsp` | Path to the kaappi-lsp binary |

If `kaappi-lsp` is not in your PATH:

```json
{
  "kaappi.lspPath": "/usr/local/bin/kaappi-lsp"
}
```

## Language Server (kaappi-lsp)

The `kaappi-lsp` binary is included with Kaappi and built alongside the main interpreter. It communicates via JSON-RPC over stdin/stdout following the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/).

### Capabilities

| Feature | Description |
|---------|-------------|
| **Diagnostics** | Parse and compile errors on every file change |
| **Completion** | All global symbols, filtered by prefix at cursor |
| **Hover** | Type name and arity for any symbol |
| **Go to Definition** | Jump to `define`, `define-syntax`, or `define-record-type` for a symbol |
| **Find References** | Find all occurrences of a symbol in the document |
| **Document Symbols** | Outline of all top-level definitions |
| **Document sync** | Full text synchronization |

### Using with other editors

Any editor with LSP support can use `kaappi-lsp`. Configure it as a stdio language server for `.scm` files:

**Neovim (nvim-lspconfig):**

```lua
vim.api.nvim_create_autocmd("FileType", {
  pattern = "scheme",
  callback = function()
    vim.lsp.start({
      name = "kaappi-lsp",
      cmd = { "kaappi-lsp" },
    })
  end,
})
```

**Emacs (eglot):**

```elisp
(add-to-list 'eglot-server-programs '(scheme-mode . ("kaappi-lsp")))
```

**Helix (`languages.toml`):**

```toml
[[language]]
name = "scheme"
language-servers = ["kaappi-lsp"]

[language-server.kaappi-lsp]
command = "kaappi-lsp"
```

## Formatting

`kaappi fmt` canonically formats Scheme source: 2-space R7RS
indentation, 80-column reflow, comments preserved. Every write is
guarded by a reader round-trip check — the formatted output must read
back `equal?` to the original — so it can never change a program's
meaning:

```bash
kaappi fmt src/           # format files in place
kaappi fmt --check src/   # list files needing formatting, exit 1 (for CI)
```

With no file arguments, `kaappi fmt` reads stdin and writes formatted
source to stdout — the shape editor filter commands expect:

- **Vim / Neovim** — `:%!kaappi fmt` filters the buffer; wire it to a
  `BufWritePre` autocmd for format-on-save.
- **Emacs** — `C-u M-|` (`shell-command-on-region` with replacement)
  running `kaappi fmt`.
- **Helix** — add a formatter to the `languages.toml` entry above:

  ```toml
  [[language]]
  name = "scheme"
  language-servers = ["kaappi-lsp"]
  formatter = { command = "kaappi", args = ["fmt"] }
  auto-format = true
  ```

- **VS Code** — use a run-on-save extension to run `kaappi fmt ${file}`
  after saving.

---

Next: [C Extensions](c-extensions.md)
