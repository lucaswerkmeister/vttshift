import datetime
import re
import sys

from . import (
    timedelta_to_timestamp,
    timestamp_to_timedelta,
)


Snip = tuple[
    datetime.timedelta,
    datetime.timedelta,
]


def parse_snip(input: str) -> Snip:
    """Parse a snip for the subtitles.

    A snip consists of two WebVTT timestamps,
    separated by a hyphen.
    All subtitles between these two timestamps should be snipped out.
    """
    m = re.fullmatch(
        r"([^-]*)-([^-]*)",
        input,
    )
    assert m
    start, stop = m.groups()
    return (
        timestamp_to_timedelta(start),
        timestamp_to_timedelta(stop),
    )


def process_block(lines: list[str], snips: list[Snip]) -> list[str]:
    """Process one block of subtitles according to the given snips.

    The block may be a cue block or a comment block.

    The snips must be in ascending order.
    """
    if not lines:
        return []
    if lines[0].startswith("NOTE"):
        # comment block
        return lines
    cue_identifier_lines: list[str] = []
    cue_timings_line: str | None = None
    cue_payload_lines: list[str] = []
    for line in lines:
        if cue_timings_line is None:
            if "-->" in line:
                cue_timings_line = line
            else:
                cue_identifier_lines.append(line)
        else:
            cue_payload_lines.append(line)
    if cue_timings_line is None:
        # probably some other part of the file
        return lines
    m = re.fullmatch(
        r"([^ \t]+)([ \t]+)(-->)([ \t]+)([^ \t\n]+)(.*)",
        cue_timings_line,
        re.DOTALL,
    )
    assert m
    ts_from, ws1, arrow, ws2, ts_to, rest = m.groups()
    td_from = timestamp_to_timedelta(ts_from)
    td_to = timestamp_to_timedelta(ts_to)
    td_snipped = datetime.timedelta()
    for snip_td_start, snip_td_stop in snips:
        if td_from < snip_td_start:
            # cue starts before snip
            if td_to < snip_td_start:
                # cue is fully before snip, noop
                pass
            elif td_to < snip_td_stop:
                # cue ends in snip, snap to start of snip
                td_to = snip_td_start
            else:
                # cue spans across snip, subtract snip length
                td_to -= snip_td_stop - snip_td_start
        elif td_from < snip_td_stop:
            # cue starts in snip
            if td_to < snip_td_stop:
                # cue fully snipped
                return []
            else:
                # cue not fully snipped, snap to stop of snip
                td_from = snip_td_stop
                # and subtract snip length
                td_snipped += snip_td_stop - snip_td_start
        else:
            # cue starts after snip, subtract snip length
            td_snipped += snip_td_stop - snip_td_start
    td_from -= td_snipped
    td_to -= td_snipped
    ts_from = timedelta_to_timestamp(td_from)
    ts_to = timedelta_to_timestamp(td_to)
    cue_timings_line = ts_from + ws1 + arrow + ws2 + ts_to + rest
    return cue_identifier_lines + [cue_timings_line] + cue_payload_lines


def main() -> None:
    """Parse snips from argv,
    read subtitles on stdin
    and write snipped subtitles on stdout.
    """
    snips = [parse_snip(arg) for arg in sys.argv[1:]]
    snips.sort()
    block: list[str] = []
    for line in sys.stdin:
        if line in ["\n", "\r", "\r\n"]:
            block = process_block(block, snips)
            if block:
                for block_line in block:
                    print(block_line, end="")
                print(line, end="")
            block = []
        else:
            block.append(line)
    block = process_block(block, snips)
    if block:
        for block_line in block:
            print(block_line, end="")
