# Cookbook

Practical recipes for building real programs with Kaappi. Each recipe is a
self-contained guide that solves one problem end-to-end.

## Recipes

### Web & API

- [Build a REST API](rest-api.md) — full CRUD API with PostgreSQL, Redis
  caching, validation, and error handling
- [Call HTTP APIs](http-client.md) — GET/POST requests, JSON decoding,
  error handling, retries, and downloads
- [Serve HTML with Templates](html-templates.md) — dynamic HTML pages with the
  template engine, layouts, and auto-escaping

### Data Processing

- [Process JSON Data](json-processing.md) — read, transform, filter, and write
  JSON from files and APIs
- [Parse and Generate CSV](csv-processing.md) — read CSV files, process rows,
  write results, and handle edge cases
- [Store Data in SQLite](sqlite-storage.md) — local persistence with schemas,
  CRUD helpers, transactions, and streaming

### Application Patterns

- [Read Configuration Files](config-files.md) — TOML/YAML config with
  defaults, environment overrides, and validation
- [Run Concurrent Tasks](concurrent-tasks.md) — fibers, channels, pipelines,
  and worker pools
- [Write Tests](testing.md) — test organization, assertions, error testing,
  and CI integration
- [Build a CLI Tool](cli-tool.md) — argument parsing, subcommands,
  and help generation

Each recipe assumes you have [installed Kaappi](../guide/installation.md) and
know the basics from the [tutorial](../guide/tutorial.md). If a recipe uses
ecosystem libraries, installation commands are shown at the top.
