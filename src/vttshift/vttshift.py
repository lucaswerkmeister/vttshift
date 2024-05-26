import datetime
import re
import sys

from . import (
    timedelta_to_timestamp,
    timestamp_to_timedelta,
)


Adjustment = tuple[
    datetime.timedelta,
    datetime.timedelta,
]  # TODO use `type` statement in Python 3.12


def parse_adjustment(input: str) -> Adjustment:
    """Parse an adjustment to the subtitles.

    An adjustment consists of a WebVTT timestamp
    and a positive or negative number of milliseconds,
    with the sign of the milliseconds (+ or -) serving as the separator,
    as in 00:11:22.333+4444 or 00:11:22.333-4444."""
    m = re.fullmatch(
        r"([^+-]*)([+-].*)",
        input,
    )
    assert m
    timestamp, milliseconds = m.groups()
    return (
        timestamp_to_timedelta(timestamp),
        datetime.timedelta(milliseconds=int(milliseconds)),
    )


def process_line(line: str, adjustments: list[Adjustment]) -> str:
    """Process one line of subtitles (which includes a trailing \n)
    according to the given adjustments.

    The adjustments must be in descending order,
    and only the first matching adjustment is used,
    so that each adjustment is considered independently."""
    if "-->" not in line:
        return line
    m = re.fullmatch(
        r"([^ \t]+)([ \t]+)(-->)([ \t]+)([^ \t\n]+)(.*)",
        line,
        re.DOTALL,
    )
    assert m
    ts_from, ws1, arrow, ws2, ts_to, rest = m.groups()
    td_from = timestamp_to_timedelta(ts_from)
    td_to = timestamp_to_timedelta(ts_to)
    for adj_td_from, adj_td_add in adjustments:
        if td_from >= adj_td_from:
            td_from += adj_td_add
            td_to += adj_td_add
            break
    ts_from = timedelta_to_timestamp(td_from)
    ts_to = timedelta_to_timestamp(td_to)
    return ts_from + ws1 + arrow + ws2 + ts_to + rest


def main() -> None:
    """Parse adjustments from argv,
    read subtitles on stdin
    and write adjusted subtitles on stdout."""
    adjustments = [parse_adjustment(arg) for arg in sys.argv[1:]]
    adjustments.sort(reverse=True)
    for line in sys.stdin:
        print(process_line(line, adjustments), end="")
