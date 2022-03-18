from openprocurement.api.mask import mask_object_data
from unittest.mock import patch
from copy import deepcopy
import json


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
def test_mask_defense_function():
    with open("src/openprocurement/tender/core/tests/data/defense_mock.json") as f:
        data = json.load(f)
    initial_data = deepcopy(data)

    mask_object_data(data)

    assert data["title"] == "*" * len(data["title"])
    assert data["_id"] == initial_data["_id"]
    # print(data)
