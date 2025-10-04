"""Command line entrypoint for printing lake levels."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

import requests

from .siljan import (
    DEFAULT_LAKE,
    DEFAULT_RIVER,
    DEFAULT_TIMEOUT,
    LakeLevelError,
    get_lake_level,
    list_lakes,
    list_rivers,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch lake level measurements",
        epilog=(
            "Examples:\n"
            "  ./scripts/run --alv Dalälven --lake Siljan\n"
            "  ./scripts/run --list-rivers\n"
            "  ./scripts/run --alv Dalälven --list-lakes"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--alv",
        default=DEFAULT_RIVER,
        help=f"River/älv to query (default: {DEFAULT_RIVER})",
    )
    parser.add_argument(
        "--lake",
        default=DEFAULT_LAKE,
        help=f"Lake name to read (default: {DEFAULT_LAKE})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help=f"Timeout in seconds for each HTTP request (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--list-lakes",
        action="store_true",
        help="List all lakes for the selected river and exit",
    )
    parser.add_argument(
        "--list-rivers",
        action="store_true",
        help="List all available rivers and exit",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args_list = list(sys.argv[1:] if argv is None else argv)

    if not args_list:
        parser.print_help()
        return 0

    args = parser.parse_args(args_list)

    try:
        if args.list_rivers:
            for name in list_rivers(timeout=args.timeout):
                print(name)
            return 0

        if args.list_lakes:
            names = list_lakes(args.alv, timeout=args.timeout)
            for name in names:
                print(name)
            return 0

        measurement = get_lake_level(
            args.alv, args.lake, timeout=args.timeout
        )
    except (LakeLevelError, requests.exceptions.RequestException) as exc:
        print(f"Error fetching lake level: {exc}", file=sys.stderr)
        return 1

    print(
        f"{measurement.lake} ({measurement.river}) water level: {measurement.level_m} m "
        f"(measured {measurement.timestamp})"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via cli
    raise SystemExit(main())
