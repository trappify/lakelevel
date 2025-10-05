# Changelog

All notable changes to this project are documented here. Releases follow [Semantic Versioning](https://semver.org/).

## [0.3.2] - 2025-10-05
- Ensure config flow schema serializes correctly across all Home Assistant versions.

## [0.3.1] - 2025-10-05
- Fix config flow schema serialization so setup works on a fresh install.
- Add debug logging around lake loading to aid troubleshooting.

## [0.3.0] - 2025-10-04
- Allow up to four fetches per day with configurable times and options flow.
- Add config entry migration and daily scheduler improvements.
- Fix coordinator refresh scheduling to avoid missed updates.

## [0.2.0] - 2025-10-04
- Bundle the scraper inside the Home Assistant integration for offline installs.
- Add config flow, coordinator scheduling fix, and daily retry logic.
- Provide documentation for installation, configuration, usage, and disclaimers.

## [0.1.0] - 2025-10-04
- Initial release with CLI scraper, tests, and Home Assistant integration scaffolding.
