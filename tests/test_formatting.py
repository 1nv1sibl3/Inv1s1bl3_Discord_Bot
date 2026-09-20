from src.bot.utils.formatting import (
    text_to_owo,
    create_progress_bar,
    format_timespan,
    format_currency,
)


def test_text_to_owo():
    assert "UwU" in text_to_owo("")
    res = text_to_owo("Hello World! How are you?")
    assert "w" in res.lower()
    assert "r" not in res.lower() or "owo" in res.lower()


def test_create_progress_bar():
    bar_half = create_progress_bar(50, 100, length=10)
    assert "50%" in bar_half
    assert "🟦" in bar_half
    assert "⬜" in bar_half

    bar_full = create_progress_bar(100, 100, length=10)
    assert "100%" in bar_full


def test_format_timespan():
    assert format_timespan(0) == "0s"
    assert format_timespan(45) == "45s"
    assert format_timespan(125) == "2m 5s"
    assert format_timespan(3665) == "1h 1m 5s"
    assert format_timespan(90000) == "1d 1h"


def test_format_currency():
    assert format_currency(1000) == "1,000 iC"
    assert format_currency(50) == "50 iC"
