from decimal import Decimal

import requests

from lakelevel.cli import main
from lakelevel.siljan import LakeMeasurement


def test_main_success(monkeypatch, capsys) -> None:
    measurement = LakeMeasurement(
        river="Dalälven", lake="Siljan", level_m=Decimal("161.65"), timestamp="12:55 okt 04"
    )

    def fake_get(river, lake, timeout=None):
        assert river == "Dalälven"
        assert lake == "Siljan"
        assert timeout == 123.0
        return measurement

    monkeypatch.setattr("lakelevel.cli.get_lake_level", fake_get)

    exit_code = main(["--timeout", "123"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Siljan" in captured.out
    assert captured.err == ""


def test_main_handles_request_exception(monkeypatch, capsys) -> None:
    def fake_get(river, lake, timeout=None):
        raise requests.exceptions.Timeout("boom")

    monkeypatch.setattr("lakelevel.cli.get_lake_level", fake_get)

    exit_code = main(["--lake", "Siljan"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error fetching lake level" in captured.err
    assert captured.out == ""


def test_main_lists_lakes(monkeypatch, capsys) -> None:
    def fake_list(river, timeout=None):
        assert river == "Dalälven"
        assert timeout is None
        return ["Siljan", "Orsasjön"]

    monkeypatch.setattr("lakelevel.cli.list_lakes", fake_list)

    exit_code = main(["--list-lakes"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Siljan" in captured.out
    assert "Orsasjön" in captured.out


def test_main_lists_rivers(monkeypatch, capsys) -> None:
    def fake_list(timeout=None):
        assert timeout is None
        return ["Umeälven", "Dalälven"]

    monkeypatch.setattr("lakelevel.cli.list_rivers", fake_list)

    exit_code = main(["--list-rivers"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Umeälven" in captured.out


def test_main_without_args_shows_help(capsys) -> None:
    exit_code = main([])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Fetch lake level measurements" in captured.out
