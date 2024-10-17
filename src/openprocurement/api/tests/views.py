import pytest
import simplejson
from bson import Timestamp

from openprocurement.api.views.base import compose_offset, parse_offset


@pytest.mark.parametrize(
    "offset, expected",
    [
        # bson timestamps
        (Timestamp(1721512808, 12), "1721512808.0000000012"),
        (Timestamp(1721512808, 199_000), "1721512808.0000199000"),
        (Timestamp(1721512808, 1_990_000), "1721512808.0001990000"),
        (Timestamp(1721512808, 2**32 - 1), "1721512808.4294967295"),  # max possible ordinal
        # floats
        (1721512808.123, "1721512808.123"),
        (1721512808.123456, "1721512808.123456"),  # some old tenders has microseconds
        # this is unexpected format that defaults to public_modified format
        (1721512808.123456789, "1721512808.1234567"),
    ],
)
def test_compose_and_parse_offset(offset, expected):
    # to python
    result = compose_offset(offset)
    json_str = simplejson.dumps({"offset": result})

    data = simplejson.loads(json_str)
    assert data["offset"] == expected

    parsed = parse_offset(data["offset"])
    assert parsed == offset
