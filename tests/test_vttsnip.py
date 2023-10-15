import datetime
import pytest

from vttsnip import timestamp_to_timedelta, timedelta_to_timestamp


timestamps_timedeltas = [
    ('00:00:00.000', datetime.timedelta()),
    ('12:34:56.789', datetime.timedelta(hours=12, minutes=34, seconds=56, milliseconds=789)),
]
nonnormal_timestamps_timedeltas = [
    ('12:34.567', datetime.timedelta(minutes=12, seconds=34, milliseconds=567)),
]

@pytest.mark.parametrize(
    'timestamp, timedelta',
    timestamps_timedeltas + nonnormal_timestamps_timedeltas,
)
def test_timestamp_to_timedelta(timestamp, timedelta):
    assert timestamp_to_timedelta(timestamp) == timedelta

@pytest.mark.parametrize(
    'timestamp, timedelta',
    timestamps_timedeltas,
)
def test_timedelta_to_timestamp(timestamp, timedelta):
    assert timedelta_to_timestamp(timedelta) == timestamp
