import datetime
import re
import sys


def timestamp_to_timedelta(webvtt_timestamp: str) -> datetime.timedelta:
    """Parse a WebVTT timestamp into a datetime.timedelta."""
    match = re.fullmatch(
        r"(?:([0-9]{2,}):)?([0-9]{2}):([0-9]{2}).([0-9]{3})",
        webvtt_timestamp,
    )
    assert match
    hours, minutes, seconds, frac = match.groups()
    return datetime.timedelta(
        hours=int(hours or "0"),
        minutes=int(minutes),
        seconds=int(seconds),
        milliseconds=int(frac),
    )


def timedelta_to_timestamp(timedelta: datetime.timedelta) -> str:
    """Format a datetime.timedelta into a WebVTT timestamp."""
    hours = timedelta.seconds // 3600
    minutes = timedelta.seconds % 3600 // 60
    seconds = timedelta.seconds % 60
    milliseconds = timedelta.microseconds // 1000
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


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
    match = re.fullmatch(
        r"([^+-]*)([+-].*)",
        input,
    )
    assert match
    timestamp, milliseconds = match.groups()
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
    match = re.fullmatch(
        r"([^ \t]+)([ \t]+)(-->)([ \t]+)([^ \t]+)(.*)",
        line,
        re.DOTALL,
    )
    assert match
    ts_from, ws1, arrow, ws2, ts_to, rest = match.groups()
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
