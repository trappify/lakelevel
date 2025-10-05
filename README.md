# Lake Level

CLI utility to fetch the latest lake level for Siljan (or any other lake exposed on Vattenregleringsföretagen). A Home Assistant custom integration (with the scraper bundled for offline installs) lives in `custom_components/lakelevel` and supports up to four scheduled fetches per day.

## Quick start

- `./scripts/run [--alv RIVER] [--lake LAKE] [--timeout SECONDS]` — prints the latest lake level (defaults to Dalälven/Siljan, timeout 180 s).
- `./scripts/test` — runs the pytest suite.

Both scripts automatically use `.venv/bin/python` when the virtualenv is present, falling back to the system `python3` otherwise.

Running without any flags prints the help text with usage examples (Siljan included).

## Home Assistant integration

- Manual/HACS installation instructions live in `docs/installation.md`.
- Configuration flow details are documented in `docs/configuration.md`.
- Sensor behavior and attributes are covered in `docs/usage.md`.
- Disclaimer: this project is an unofficial community integration and is not affiliated with Vattenregleringsföretagen. Use at your own risk.

To install via HACS, add `https://github.com/trappify/lakelevel` as a custom repository (category **Integration**), install **Lake Level**, restart Home Assistant, then add the integration from the UI.

Release process is documented in `docs/releasing.md`. See `CHANGELOG.md` for version history.

List available rivers or lakes:

```
./scripts/run --list-rivers
./scripts/run --alv Dalälven --list-lakes
```
