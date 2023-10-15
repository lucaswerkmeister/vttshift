import datetime
import re
import sys

def timestamp_to_timedelta(webvtt_timestamp: str) -> datetime.timedelta:
    match = re.fullmatch(r'(?:([0-9]{2,}):)?([0-9]{2}):([0-9]{2}).([0-9]{3})', webvtt_timestamp)
    assert match
    hours, minutes, seconds, frac = match.groups()
    return datetime.timedelta(
        hours=int(hours or '0'),
        minutes=int(minutes),
        seconds=int(seconds),
        milliseconds=int(frac),
    )

def timedelta_to_timestamp(timedelta: datetime.timedelta) -> str:
    hours = timedelta.seconds // 3600
    minutes = timedelta.seconds % 3600 // 60
    seconds = timedelta.seconds % 60
    milliseconds = timedelta.microseconds // 1000
    return f'{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}'

adjustments_ = [
    ('14:50.000', 5000),
    ('27:02.000', 8800 - 5000),
]
adjustments = [
    (timestamp_to_timedelta(ts), datetime.timedelta(milliseconds=ms))
    for ts, ms in adjustments_
]
adjustments.sort(reverse=True)

def process_line(line: str) -> str:
    if '-->' not in line:
        return line
    match = re.fullmatch(r'([^ \t]+)([ \t]+)(-->)([ \t]+)([^ \t]+)(.*)', line, re.DOTALL)
    assert match
    ts_from, ws1, arrow, ws2, ts_to, rest = match.groups()
    td_from = timestamp_to_timedelta(ts_from)
    td_to = timestamp_to_timedelta(ts_to)
    for adj_td_from, adj_td_add in adjustments:
        if td_from >= adj_td_from:
            td_from += adj_td_add
            td_to += adj_td_add
    ts_from = timedelta_to_timestamp(td_from)
    ts_to = timedelta_to_timestamp(td_to)
    return ts_from + ws1 + arrow + ws2 + ts_to + rest

def main() -> None:
    for line in sys.stdin:
        print(process_line(line), end='')
