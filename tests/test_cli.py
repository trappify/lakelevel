from decimal import Decimal

import requests

from lakelevel.cli import main
from lakelevel.siljan import LakeMeasurement


def test_main_success(monkeypatch, capsys) -> None:
    measurement = LakeMeasurement("Siljan", Decimal("161.65"), "12:55 okt 04")

    def fake_get(timeout=None):
        assert timeout == 123.0
        return measurement

    monkeypatch.setattr("lakelevel.cli.get_siljan_level", fake_get)

    exit_code = main(["--timeout", "123"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "161.65" in captured.out
    assert captured.err == ""


def test_main_handles_request_exception(monkeypatch, capsys) -> None:
    def fake_get(timeout=None):
        raise requests.exceptions.Timeout("boom")

    monkeypatch.setattr("lakelevel.cli.get_siljan_level", fake_get)

    exit_code = main([])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error fetching Siljan level" in captured.err
    assert captured.out == ""
