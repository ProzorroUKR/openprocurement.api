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
    with open("src/openprocurement/contracting/api/tests/data/contract_to_mask.json") as f:
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
def test_mask_contract_by_identifier(app):
    set_now()
    with open(f"src/openprocurement/contracting/api/tests/data/contract_to_mask.json") as f:
        data = json.load(f)
    app.app.registry.mongodb.contracts.store.save_data(
        app.app.registry.mongodb.contracts.collection,
        data,
        insert=True,
    )

    id = data['_id']

    # Check contract masked
    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert data["items"][0]["description"] == "00000000000000000000000000000000"
    assert "mode" not in data

    # Patch contract as excluded from masking role
    with change_auth(app, ("Basic", ("administrator", ""))):
        response = app.patch_json(f"/contracts/{id}", {"data": {"mode": "test"}})
    assert response.status_code == 200
    data = response.json["data"]
    assert data["items"][0]["description"] != "00000000000000000000000000000000"

    # Check that after modification contract is still masked
    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert data["items"][0]["description"] == "00000000000000000000000000000000"
    assert data["mode"] == "test"


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
@patch("openprocurement.api.mask.MASK_IDENTIFIER_IDS", [])
def test_mask_contract_by_is_masked(app):
    set_now()
    with open(f"src/openprocurement/contracting/api/tests/data/contract_to_mask.json") as f:
        data = json.load(f)
    data["is_masked"] = True
    app.app.registry.mongodb.contracts.store.save_data(
        app.app.registry.mongodb.contracts.collection,
        data,
        insert=True,
    )

    id = data['_id']

    # Check contract masked
    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert "mode" not in data
    assert data["items"][0]["description"] == "0" * len(data["items"][0]["description"])

    # Check field is hidden
    assert "is_masked" not in data

    # Patch contract as excluded from masking role
    with change_auth(app, ("Basic", ("administrator", ""))):
        response = app.patch_json(f"/contracts/{id}", {"data": {"mode": "test"}})
    assert response.status_code == 200
    data = response.json["data"]
    assert data["mode"] == "test"
    assert data["items"][0]["description"] != "0" * len(data["items"][0]["description"])

    # Check field is hidden
    assert "is_masked" not in response.json["data"]

    # Check that after modification contract is still masked
    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert data["mode"] == "test"
    assert data["items"][0]["description"] == "0" * len(data["items"][0]["description"])


@patch("openprocurement.api.mask.MASK_OBJECT_DATA", True)
@patch("openprocurement.api.mask.MASK_IDENTIFIER_IDS", [])
def test_mask_contract_skipped(app):
    set_now()
    with open(f"src/openprocurement/contracting/api/tests/data/contract_to_mask.json") as f:
        data = json.load(f)
    app.app.registry.mongodb.contracts.store.save_data(
        app.app.registry.mongodb.contracts.collection,
        data,
        insert=True,
    )

    id = data['_id']

    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert data["items"][0]["description"] != "00000000000000000000000000000000"
