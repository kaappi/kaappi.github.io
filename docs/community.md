# Community

Kaappi is an open-source project under the MIT license. Contributions,
questions, and feedback are welcome.

## Get help

**[GitHub Discussions](https://github.com/orgs/kaappi/discussions)** is the
primary community channel. Use it for:

- Questions about using Kaappi
- Ideas and feature suggestions
- Show and tell — share what you've built
- General discussion about Scheme and language implementation

## Report a bug

Open an issue at
[github.com/kaappi/kaappi/issues](https://github.com/kaappi/kaappi/issues).

Include:

- Kaappi version (`kaappi --version`)
- Operating system and architecture
- A minimal reproducing example
- Expected vs. actual behavior

For **ecosystem library** bugs (kaappi-json, kaappi-web, etc.), open the
issue in that library's repo:
`github.com/kaappi/<library-name>/issues`

## Report a security vulnerability

See
[SECURITY.md](https://github.com/kaappi/kaappi/blob/main/SECURITY.md).
Do not open a public issue for security reports.

## Contribute code

The [Contributing Guide](https://github.com/kaappi/kaappi/blob/main/CONTRIBUTING.md)
covers the full workflow. Here is the short version:

### Setup

```bash
git clone https://github.com/kaappi/kaappi
cd kaappi
zig build          # build the interpreter
zig build test     # run all unit tests
```

Requires Zig 0.16+.

### Workflow

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Run `zig fmt src/` (CI enforces formatting)
4. Run `zig build test` and `bash tests/scheme/run-all.sh`
5. Open a pull request

### What to contribute

- **Bug fixes** — include a test that fails without the fix
- **New built-in procedures** — follow the pattern in `src/primitives_*.zig`
- **SRFI implementations** — pure Scheme SRFIs go in `lib/srfi/`
- **Documentation** — edit files in the
  [kaappi.github.io](https://github.com/kaappi/kaappi.github.io) repo
- **Ecosystem libraries** — new or improved packages, see
  [Library Authoring](guide/library-authoring.md)

### Code style

- **Zig**: enforced by `zig fmt`, checked in CI
- **Scheme**: 2-space indentation, R7RS conventions
- Keep files under 1500 lines; split into sub-modules when they grow

## Ecosystem library contributions

Each ecosystem library (kaappi-json, kaappi-web, etc.) is its own repo
under the [kaappi GitHub org](https://github.com/kaappi). PRs follow the
same fork-and-branch workflow.

To create a new ecosystem library, see
[Library Authoring](guide/library-authoring.md) for the project layout and
`kaappi.pkg` manifest format.

## Code of conduct

This project follows the
[Contributor Covenant](https://github.com/kaappi/kaappi/blob/main/CODE_OF_CONDUCT.md).
Be respectful and constructive in all interactions.

## License

Kaappi and all ecosystem libraries are released under the
[MIT License](https://opensource.org/licenses/MIT).
