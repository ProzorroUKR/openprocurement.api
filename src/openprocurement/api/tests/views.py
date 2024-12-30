import pytest
import simplejson

from openprocurement.api.views.base import compose_offset, parse_offset


@pytest.mark.parametrize(
    "offset, items, expected",
    [
        (1721512808.12, [], "1721512808.12"),
        (1721512808.199, [], "1721512808.199"),
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
