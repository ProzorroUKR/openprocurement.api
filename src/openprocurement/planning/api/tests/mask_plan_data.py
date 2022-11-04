from hashlib import sha224

from openprocurement.api.context import set_now
from openprocurement.api.tests.base import singleton_app, app
from openprocurement.api.mask import mask_object_data
from unittest.mock import patch, MagicMock
from copy import deepcopy
import json


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
@patch("openprocurement.api.mask.MASK_IDENTIFIER_IDS", [
    sha224("00000000".encode()).hexdigest(),
])
def test_mask_function():
    with open("src/openprocurement/planning/api/tests/data/plan_0.json") as f:
        data = json.load(f)
    initial_data = deepcopy(data)

    request = MagicMock()
    mask_object_data(request, data)

    assert data["items"][0]["description"] == "00000000000000000000000000000000"
    assert data["_id"] == initial_data["_id"]


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
@patch("openprocurement.api.mask.MASK_IDENTIFIER_IDS", [
    sha224("00000000".encode()).hexdigest(),
    sha224("00000001".encode()).hexdigest(),
])
def test_mask_plan_by_identifier(app):
    set_now()
    for i in range(2):
        with open(f"src/openprocurement/planning/api/tests/data/plan_{i}.json") as f:
            data = json.load(f)
        app.app.registry.mongodb.plans.store.save_data(
            app.app.registry.mongodb.plans.collection,
            data,
            insert=True,
        )

        response = app.get(f"/plans/{data['_id']}")
        assert response.status_code == 200
        assert response.json["data"]["items"][0]["description"] == "00000000000000000000000000000000"


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
@patch("openprocurement.api.mask.MASK_IDENTIFIER_IDS", [])
def test_mask_plan_by_is_masked(app):
    set_now()
    for i in range(2):
        with open(f"src/openprocurement/planning/api/tests/data/plan_{i}.json") as f:
            data = json.load(f)
        data["is_masked"] = True
        app.app.registry.mongodb.plans.store.save_data(
            app.app.registry.mongodb.plans.collection,
            data,
            insert=True,
        )

        response = app.get(f"/plans/{data['_id']}")
        assert response.status_code == 200
        assert response.json["data"]["items"][0]["description"] == "00000000000000000000000000000000"
        assert "is_masked" not in response.json["data"]


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
@patch("openprocurement.api.mask.MASK_IDENTIFIER_IDS", [])
def test_mask_plan_skipped(app):
    set_now()
    for i in range(2):
        with open(f"src/openprocurement/planning/api/tests/data/plan_{i}.json") as f:
            data = json.load(f)
        app.app.registry.mongodb.plans.store.save_data(
            app.app.registry.mongodb.plans.collection,
            data,
            insert=True,
        )

        response = app.get(f"/plans/{data['_id']}")
        assert response.status_code == 200
        assert response.json["data"]["items"][0]["description"] != "00000000000000000000000000000000"

