from datetime import date

from benzatracker.cli import build_tenth_windows


def test_build_tenth_windows_mid_month():
    windows = build_tenth_windows(date(2024, 3, 15))
    labels, start, end = windows[0]
    assert start == date(2024, 2, 10)
    assert end == date(2024, 3, 10)
    assert "10 Feb" in labels

    _, start, end = windows[1]
    assert start == date(2024, 3, 10)
    assert end == date(2024, 4, 10)

    _, start, end = windows[2]
    assert start == date(2024, 4, 10)
    assert end == date(2024, 5, 10)


def test_build_tenth_windows_year_boundary():
    windows = build_tenth_windows(date(2025, 1, 5))
    assert windows[0][1] == date(2024, 12, 10)
    assert windows[0][2] == date(2025, 1, 10)
    assert windows[1][1] == date(2025, 1, 10)
    assert windows[1][2] == date(2025, 2, 10)
    assert windows[2][1] == date(2025, 2, 10)
    assert windows[2][2] == date(2025, 3, 10)
