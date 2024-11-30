import pytest
import simplejson
from bson import Timestamp

from openprocurement.api.views.base import compose_offset, parse_offset


@pytest.mark.parametrize(
    "offset, items, expected",
    [
        (Timestamp(1721512808, 12), [], "1721512808.0000000012"),
        (Timestamp(1721512808, 199_000), [], "1721512808.0000199000"),
        (Timestamp(1721512808, 1_990_000), [], "1721512808.0001990000"),
        (Timestamp(1721512808, 2**32 - 1), [], "1721512808.4294967295"),
    ],
)
def test_compose_and_parse_offset(offset, items, expected):
    # to python
    result = compose_offset(offset, items, offset_field="public_ts")
    json_str = simplejson.dumps({"offset": result})

    data = simplejson.loads(json_str)
    assert data["offset"].startswith(expected)

    parsed, *_ = parse_offset(data["offset"])
    assert parsed == offset
