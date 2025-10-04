# AGENTS

## Purpose
- Scrape the Vattenregleringsföretagen lake level page and expose the current level for lake Siljan.
- Provide a simple console interface today, with room for richer automation later.

## Components
- `lakelevel.siljan`: Handles HTTP interactions with https://login.vattenreglering.se/m/vattenstand.asp and parses the Dalälven table.
- `lakelevel.cli`: Command-line interface that prints the most recent Siljan measurement to stdout and accepts a custom timeout override.
- `tests/`: Pytest suite with fixtures emulating the live site to keep tests reliable and offline.

## Operational Notes
- The target site requires an initial GET to prime the ASP session cookie, followed by a POST where the `Ralv` parameter must be encoded as `Dal%E4lven` (ISO-8859-1 percent-encoding) for the Dalälven data to load.
- Responses from the site are encoded using ISO-8859-1; we force that encoding before parsing.
- Network operations are wrapped in small helpers so we can substitute a mocked `requests.Session` during tests or future agent integrations.
- Default timeout per request is 180 s to accommodate the slow upstream site; the CLI flag lets operators override on demand.

## Usage
```bash
python -m lakelevel
```

## Testing
```bash
python -m venv .venv
source .venv/bin/activate
pip install .[dev]
pytest
```
