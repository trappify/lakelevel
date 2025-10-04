# Lake Level

CLI utility to fetch the latest lake level for Siljan.

## Quick start

- `./scripts/run [--timeout SECONDS]` — prints the latest Siljan level (default timeout 180 s).
- `./scripts/test` — runs the pytest suite.

Both scripts automatically use `.venv/bin/python` when the virtualenv is present, falling back to the system `python3` otherwise.
