import datetime
import pytest

from vttsnip import timestamp_to_timedelta, timedelta_to_timestamp, process_line


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
    assert process_line(line) == line


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
    assert process_line(line) == expected
