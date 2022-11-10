from hashlib import sha224

from openprocurement.api.context import set_now
from openprocurement.api.tests.base import singleton_app, app, change_auth
from openprocurement.api.mask import mask_object_data
from unittest.mock import patch, MagicMock
from copy import deepcopy
import json


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
@patch("openprocurement.api.mask.MASK_IDENTIFIER_IDS", [
    sha224("00000000".encode()).hexdigest(),
])
def test_mask_function():
    with open("src/openprocurement/planning/api/tests/data/plan_to_mask.json") as f:
        data = json.load(f)
    initial_data = deepcopy(data)

    request = MagicMock()
    mask_object_data(request, data)

    assert data["items"][0]["description"] == "00000000000000000000000000000000"
    assert data["_id"] == initial_data["_id"]


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
@patch("openprocurement.api.mask.MASK_IDENTIFIER_IDS", [
    sha224("00000000".encode()).hexdigest(),
])
def test_mask_plan_by_identifier(app):
    set_now()
    with open(f"src/openprocurement/planning/api/tests/data/plan_to_mask.json") as f:
        initial_data = json.load(f)
    app.app.registry.mongodb.plans.store.save_data(
        app.app.registry.mongodb.plans.collection,
        initial_data,
        insert=True,
    )

    id = initial_data['_id']

    response = app.get(f"/plans/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert data["items"][0]["description"] == "00000000000000000000000000000000"


@patch("openprocurement.api.mask.MASK_OBJECT_DATA_SINGLE", True)
def test_mask_plan_by_is_masked(app):
    set_now()
    with open(f"src/openprocurement/planning/api/tests/data/plan_to_mask.json") as f:
        initial_data = json.load(f)
    app.app.registry.mongodb.plans.store.save_data(
        app.app.registry.mongodb.plans.collection,
        initial_data,
        insert=True,
    )

    id = initial_data['_id']

    # Check plan not masked
    response = app.get(f"/plans/{id}")
    assert response.status_code == 200
    data = response.json["data"]

    # Check is_masked field not appears
    assert "is_masked" not in data

    # Mask plan
    initial_data["_rev"] = app.app.registry.mongodb.plans.get(id)["_rev"]
    initial_data["is_masked"] = True
    app.app.registry.mongodb.plans.store.save_data(
        app.app.registry.mongodb.plans.collection,
        initial_data,
    )

    # Check plan masked
    response = app.get(f"/plans/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert "mode" not in data
    assert data["items"][0]["description"] == "0" * len(data["items"][0]["description"])

    # Check field
    assert "is_masked" in data

    # Patch plan as excluded from masking role
    with change_auth(app, ("Basic", ("administrator", ""))):
        response = app.patch_json(f"/plans/{id}", {"data": {"mode": "test"}})
    assert response.status_code == 200
    data = response.json["data"]
    assert data["mode"] == "test"
    assert data["items"][0]["description"] != "0" * len(data["items"][0]["description"])

    # Check field
    assert "is_masked" in data

    # Check that after modification plan is still masked
    response = app.get(f"/plans/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert data["mode"] == "test"
    assert data["items"][0]["description"] == "0" * len(data["items"][0]["description"])

    # Unmask plan
    initial_data["_rev"] = app.app.registry.mongodb.plans.get(id)["_rev"]
    initial_data["is_masked"] = False
    app.app.registry.mongodb.plans.store.save_data(
        app.app.registry.mongodb.plans.collection,
        initial_data,
    )

    # Check is_masked field was removed
    assert "is_masked" not in app.app.registry.mongodb.plans.get(id)


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
@patch("openprocurement.api.mask.MASK_IDENTIFIER_IDS", [])
@patch("openprocurement.api.mask.MASK_OBJECT_DATA_SINGLE", True)
def test_mask_plan_skipped(app):
    set_now()
    with open(f"src/openprocurement/planning/api/tests/data/plan_to_mask.json") as f:
        initial_data = json.load(f)
    app.app.registry.mongodb.plans.store.save_data(
        app.app.registry.mongodb.plans.collection,
        initial_data,
        insert=True,
    )

    id = initial_data['_id']

    response = app.get(f"/plans/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert data["items"][0]["description"] != "00000000000000000000000000000000"
