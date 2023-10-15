import datetime
import pytest

from vttsnip import (
    timestamp_to_timedelta,
    timedelta_to_timestamp,
    Adjustment,
    parse_adjustment,
    process_line,
)


timestamps_timedeltas = [
    ("00:00:00.000", datetime.timedelta()),
    (
        "12:34:56.789",
        datetime.timedelta(hours=12, minutes=34, seconds=56, milliseconds=789),
    ),
]
nonnormal_timestamps_timedeltas = [
    ("12:34.567", datetime.timedelta(minutes=12, seconds=34, milliseconds=567)),
]


@pytest.mark.parametrize(
    "timestamp, timedelta",
    timestamps_timedeltas + nonnormal_timestamps_timedeltas,
)
def test_timestamp_to_timedelta(timestamp: str, timedelta: datetime.timedelta) -> None:
    assert timestamp_to_timedelta(timestamp) == timedelta


@pytest.mark.parametrize(
    "timestamp, timedelta",
    timestamps_timedeltas,
)
def test_timedelta_to_timestamp(timestamp: str, timedelta: datetime.timedelta) -> None:
    assert timedelta_to_timestamp(timedelta) == timestamp


@pytest.mark.parametrize(
    "input, adjustment",
    [
        ("00:00:00.000+0000", (datetime.timedelta(), datetime.timedelta())),
        (
            "01:23:45.678+9876",
            (
                datetime.timedelta(
                    hours=1,
                    minutes=23,
                    seconds=45,
                    milliseconds=678,
                ),
                datetime.timedelta(milliseconds=9876),
            ),
        ),
        (
            "55:44:33.222-1111",
            (
                datetime.timedelta(
                    hours=55,
                    minutes=44,
                    seconds=33,
                    milliseconds=222,
                ),
                datetime.timedelta(milliseconds=-1111),
            ),
        ),
    ],
)
def test_parse_adjustment(input: str, adjustment: Adjustment) -> None:
    assert parse_adjustment(input) == adjustment


@pytest.mark.parametrize(
    "line",
    [
        "WEBVTT\n",
        "\n",
        "NOTE: foobar\n",
        "::cue(.red){ color: red; }\n",
        "1\n",
        "<c.red>random subtitle</c>\n",
    ],
)
def test_process_line_unmodified(line: str) -> None:
    adjustments = [
        (
            datetime.timedelta(seconds=1),
            datetime.timedelta(milliseconds=1000),
        ),
    ]
    assert process_line(line, adjustments) == line


@pytest.mark.parametrize(
    "line, expected",
    [
        (
            "00:00:00.000 --> 00:00:01.000 line:83% position:50% align:middle\n",
            "00:00:00.000 --> 00:00:01.000 line:83% position:50% align:middle\n",
        ),
        (
            "00:15:01.234 --> 00:15:56.789 line:83% position:50% align:middle\n",
            "00:15:06.234 --> 00:16:01.789 line:83% position:50% align:middle\n",
        ),
        (
            "00:30:01.234 --> 00:30:56.789 line:83% position:50% align:middle\n",
            "00:30:10.034 --> 00:31:05.589 line:83% position:50% align:middle\n",
        ),
    ],
)
def test_process_line(line: str, expected: str) -> None:
    adjustments = [
        (
            datetime.timedelta(minutes=27, seconds=2),
            datetime.timedelta(milliseconds=8800),
        ),
        (
            datetime.timedelta(minutes=14, seconds=50),
            datetime.timedelta(milliseconds=5000),
        ),
    ]
    assert process_line(line, adjustments) == expected
