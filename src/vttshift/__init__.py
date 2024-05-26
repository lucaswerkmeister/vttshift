import datetime
import re


def timestamp_to_timedelta(webvtt_timestamp: str) -> datetime.timedelta:
    """Parse a WebVTT timestamp into a datetime.timedelta."""
    m = re.fullmatch(
        r"(?:([0-9]{2,}):)?([0-9]{2}):([0-9]{2}).([0-9]{3})",
        webvtt_timestamp,
    )
    assert m
    hours, minutes, seconds, frac = m.groups()
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
