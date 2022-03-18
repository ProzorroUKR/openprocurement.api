from openprocurement.api.tests.base import singleton_app, app
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


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
def test_mask_tender_1(app):
    for i in range(5):
        with open(f"src/openprocurement/tender/core/tests/data/tender_{i}.json") as f:
            data = json.load(f)
        app.app.registry.db.save(data)

        response = app.get(f"/tenders/{data['_id']}")
        assert response.status_code == 200
