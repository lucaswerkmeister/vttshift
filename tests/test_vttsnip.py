import datetime
import pytest

from vttshift.vttsnip import (
    parse_snip,
    process_block,
)


def test_parse_snip() -> None:
    input = "00:11:22.333-44:55:66.777"
    expected = (
        datetime.timedelta(hours=00, minutes=11, seconds=22, milliseconds=333),
        datetime.timedelta(hours=44, minutes=55, seconds=66, milliseconds=777),
    )
    assert parse_snip(input) == expected


@pytest.mark.parametrize(
    "lines, expected",
    [
        (
            ["00:00:00.000 --> 00:10:00.000\n", "noop\n"],
            ["00:00:00.000 --> 00:10:00.000\n", "noop\n"],
        ),
        (
            ["00:05:00.000 --> 00:15:00.000\n", "snap to start of snip\n"],
            ["00:05:00.000 --> 00:10:00.000\n", "snap to start of snip\n"],
        ),
        (
            ["00:05:00.000 --> 00:25:00.000\n", "subtract snip length\n"],
            ["00:05:00.000 --> 00:15:00.000\n", "subtract snip length\n"],
        ),
        (
            ["00:13:00.000 --> 00:17:00.000\n", "fully snipped\n"],
            [],
        ),
        (
            ["00:15:00.000 --> 00:25:00.000\n", "snap to stop of snip\n"],
            ["00:10:00.000 --> 00:15:00.000\n", "snap to stop of snip\n"],
        ),
        (
            ["00:23:00.000 --> 00:28:00.000\n", "subtract snip length\n"],
            ["00:13:00.000 --> 00:18:00.000\n", "subtract snip length\n"],
        ),
        (
            ["00:25:00.000 --> 00:35:00.000\n", "snap to start of snip\n"],
            ["00:15:00.000 --> 00:20:00.000\n", "snap to start of snip\n"],
        ),
        (
            ["00:25:00.000 --> 00:45:00.000\n", "subtract snip length\n"],
            ["00:15:00.000 --> 00:25:00.000\n", "subtract snip length\n"],
        ),
        (
            ["00:33:00.000 --> 00:37:00.000\n", "fully snipped\n"],
            [],
        ),
        (
            ["00:35:00.000 --> 00:45:00.000\n", "snap to stop of snip\n"],
            ["00:20:00.000 --> 00:25:00.000\n", "snap to stop of snip\n"],
        ),
        (
            ["00:43:00.000 --> 00:48:00.000\n", "subtract snip length\n"],
            ["00:23:00.000 --> 00:28:00.000\n", "subtract snip length\n"],
        ),
    ],
)
def test_process_block(lines: list[str], expected: list[str]) -> None:
    snips = [
        (datetime.timedelta(minutes=10), datetime.timedelta(minutes=20)),
        (datetime.timedelta(minutes=30), datetime.timedelta(minutes=40)),
    ]
    assert process_block(lines, snips) == expected
