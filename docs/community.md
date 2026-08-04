# Community

Kaappi is an open-source project under the MIT license. Contributions,
questions, and feedback are welcome.

The full guide to getting involved — communication channels, how org access
works, the typical path for a new contributor, governance, and how to report
a security vulnerability — lives in
[kaappi/community](https://github.com/kaappi/community). Start with its
[CONTRIBUTING.md](https://github.com/kaappi/community/blob/main/CONTRIBUTING.md).

## Contribute code

Quick start for the core interpreter — see
[kaappi/kaappi's CONTRIBUTING.md](https://github.com/kaappi/kaappi/blob/main/CONTRIBUTING.md)
for the complete workflow.

```bash
git clone https://github.com/kaappi/kaappi
cd kaappi
zig build          # build the interpreter
zig build test     # run all unit tests
```

Requires Zig 0.16+.

- **Bug fixes** — include a test that fails without the fix
- **New built-in procedures** — follow the pattern in `src/primitives_*.zig`
- **SRFI implementations** — pure Scheme SRFIs go in `lib/srfi/`
- **Documentation** — edit files in this
  [kaappi.github.io](https://github.com/kaappi/kaappi.github.io) repo
- **Ecosystem libraries** — new or improved packages, see
  [Library Authoring](guide/library-authoring.md)

Each ecosystem library (kaappi-json, kaappi-web, etc.) is its own repo under
the [kaappi GitHub org](https://github.com/kaappi) and follows the same
fork-and-branch workflow (org membership required).

## Support

Kaappi is free and open source, and most of it happens outside of any
company's time. If it's been useful to you, consider
[buying me a coffee](https://www.buymeacoffee.com/baiju).

## License

Kaappi and all ecosystem libraries are released under the
[MIT License](https://opensource.org/licenses/MIT).
