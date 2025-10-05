# AGENTS

## Purpose
- Scrape the Vattenregleringsföretagen lake level page and expose the current level for lake Siljan.
- Provide a simple console interface today, with room for richer automation later.

## Components
- `lakelevel.siljan`: Handles HTTP interactions with https://login.vattenreglering.se/m/vattenstand.asp, parses river/lake tables, and exposes helpers for any available measurement.
- `lakelevel.cli`: Command-line interface that prints the most recent measurement for any river/lake combination, lists rivers or lakes, and accepts a custom timeout override. Usage examples ship with the built-in help output.
- `custom_components/lakelevel`: Home Assistant integration that schedules up to four fetches per day through a coordinator, exposes a sensor entity, and vendors the scraper so installs work on any Home Assistant deployment without extra steps.
- `tests/`: Pytest suite with fixtures emulating the live site to keep tests reliable and offline.

## Operational Notes
- The target site requires an initial GET to prime the ASP session cookie, followed by a POST where the `Ralv` parameter must be encoded using ISO-8859-1 percent-encoding for the selected river (handled automatically).
- Responses from the site are encoded using ISO-8859-1; we force that encoding before parsing.
- Network operations are wrapped in small helpers so we can substitute a mocked `requests.Session` during tests or future agent integrations.
- Default timeout per request is 180 s to accommodate the slow upstream site; the CLI flag lets operators override on demand. A single river fetch can serve multiple lake lookups without extra requests.
- Rivers can be discovered from the landing page; helpers expose both river and lake lists for reuse.
- The Home Assistant integration schedules up to four daily fetches (default one at 06:00) with retry logic to protect the slow upstream service.

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
