"""Command line entrypoint for printing Siljan lake level."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

import requests

from .siljan import DEFAULT_TIMEOUT, LakeLevelError, get_siljan_level


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch Siljan lake level")
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help=f"Timeout in seconds for each HTTP request (default: {DEFAULT_TIMEOUT})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        measurement = get_siljan_level(timeout=args.timeout)
    except (LakeLevelError, requests.exceptions.RequestException) as exc:
        print(f"Error fetching Siljan level: {exc}", file=sys.stderr)
        return 1

    print(
        f"Siljan water level: {measurement.level_m} m (measured {measurement.timestamp})"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via cli
    raise SystemExit(main())
