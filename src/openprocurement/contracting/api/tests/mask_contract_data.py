import json
from copy import deepcopy
from hashlib import sha224
from unittest.mock import MagicMock, patch

from openprocurement.api.context import set_now
from openprocurement.api.mask import MASK_STRING
from openprocurement.api.mask_deprecated import mask_object_data_deprecated
from openprocurement.api.tests.base import app, change_auth, singleton_app


@patch("openprocurement.api.mask_deprecated.MASK_OBJECT_DATA", True)
@patch(
    "openprocurement.api.mask_deprecated.MASK_IDENTIFIER_IDS",
    [
        sha224(b"00000000").hexdigest(),
    ],
)
def test_mask_function():
    with open("src/openprocurement/contracting/api/tests/data/contract_to_mask.json") as f:
        data = json.load(f)
    initial_data = deepcopy(data)

    request = MagicMock()
    mask_object_data_deprecated(request, data)

    assert data["items"][0]["description"] == "00000000000000000000000000000000"
    assert data["_id"] == initial_data["_id"]


@patch("openprocurement.api.mask_deprecated.MASK_OBJECT_DATA", True)
@patch(
    "openprocurement.api.mask_deprecated.MASK_IDENTIFIER_IDS",
    [
        sha224(b"00000000").hexdigest(),
    ],
)
def test_mask_contract_by_identifier(app):
    set_now()
    with open("src/openprocurement/contracting/api/tests/data/contract_to_mask.json") as f:
        initial_data = json.load(f)
    app.app.registry.mongodb.contracts.store.save_data(
        app.app.registry.mongodb.contracts.collection,
        initial_data,
        insert=True,
    )

    id = initial_data['_id']

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


@patch("openprocurement.api.mask_deprecated.MASK_OBJECT_DATA_SINGLE", True)
def test_mask_contract_by_is_masked(app):
    set_now()
    with open("src/openprocurement/contracting/api/tests/data/contract_to_mask.json") as f:
        initial_data = json.load(f)
    app.app.registry.mongodb.contracts.store.save_data(
        app.app.registry.mongodb.contracts.collection,
        initial_data,
        insert=True,
    )

    id = initial_data['_id']

    # Check contract not masked
    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    data = response.json["data"]

    # Check is_masked field not appears
    assert "is_masked" not in data

    # Mask contract
    initial_data["_rev"] = app.app.registry.mongodb.contracts.get(id)["_rev"]
    initial_data["is_masked"] = True
    app.app.registry.mongodb.contracts.store.save_data(
        app.app.registry.mongodb.contracts.collection,
        initial_data,
    )

    # Check contract masked
    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert "mode" not in data
    assert data["items"][0]["description"] == "0" * len(data["items"][0]["description"])

    # Check field
    assert "is_masked" in data

    # Patch contract as excluded from masking role
    with change_auth(app, ("Basic", ("administrator", ""))):
        response = app.patch_json(f"/contracts/{id}", {"data": {"mode": "test"}})
    assert response.status_code == 200
    data = response.json["data"]
    assert data["mode"] == "test"
    assert data["items"][0]["description"] != "0" * len(data["items"][0]["description"])

    # Check field
    assert "is_masked" in data

    # Check that after modification contract is still masked
    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert data["mode"] == "test"
    assert data["items"][0]["description"] == "0" * len(data["items"][0]["description"])

    # Unmask contract
    initial_data["_rev"] = app.app.registry.mongodb.contracts.get(id)["_rev"]
    initial_data["is_masked"] = False
    app.app.registry.mongodb.contracts.store.save_data(
        app.app.registry.mongodb.contracts.collection,
        initial_data,
    )

    # Check is_masked field was removed
    assert "is_masked" not in app.app.registry.mongodb.contracts.get(id)


@patch("openprocurement.api.mask_deprecated.MASK_OBJECT_DATA", True)
@patch("openprocurement.api.mask_deprecated.MASK_IDENTIFIER_IDS", [])
@patch("openprocurement.api.mask_deprecated.MASK_OBJECT_DATA_SINGLE", True)
def test_mask_contract_skipped(app):
    set_now()
    with open("src/openprocurement/contracting/api/tests/data/contract_to_mask.json") as f:
        initial_data = json.load(f)
    app.app.registry.mongodb.contracts.store.save_data(
        app.app.registry.mongodb.contracts.collection,
        initial_data,
        insert=True,
    )

    id = initial_data['_id']

    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    data = response.json["data"]
    assert data["items"][0]["description"] != "00000000000000000000000000000000"


def test_mask_contract_by_config_restricted(app):
    set_now()

    # Load initial db data
    with open("src/openprocurement/contracting/api/tests/data/contract_to_mask.json") as f:
        initial_db_data = json.load(f)
    id = initial_db_data['_id']

    # Save to db
    app.app.registry.mongodb.contracts.save(initial_db_data, insert=True)

    # Get not masked data
    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    actual_data = response.json["data"]

    # Mask data
    db_data = app.app.registry.mongodb.contracts.get(id)
    if "config" not in db_data:
        db_data["config"] = {}
    db_data["config"]["restricted"] = True
    app.app.registry.mongodb.contracts.save(db_data)

    # Get masked data
    response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    masked_data = response.json["data"]

    # Dump expected data (uncomment to update)
    # with open(f"src/openprocurement/contracting/api/tests/data/contract_masked.json", mode="w") as f:
    #     json.dump(masked_data, f, indent=4, ensure_ascii=False)

    # Load expected masked data
    with open("src/openprocurement/contracting/api/tests/data/contract_masked.json") as f:
        expected_masked_data = json.load(f)

    # Ensure dumped data is masked
    assert expected_masked_data["items"][0]["deliveryAddress"]["streetAddress"] == MASK_STRING

    # Check masked data with loaded (dumped) expected data
    expected_masked_data["dateCreated"] = masked_data["dateCreated"]
    expected_masked_data["dateModified"] = masked_data["dateModified"]
    assert masked_data == expected_masked_data

    # Broker (with no accreditation for restricted) not allowed to see masked data
    with change_auth(app, ("Basic", ("broker", ""))):
        response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    masked_data = response.json["data"]
    actual_data["dateCreated"] = masked_data["dateCreated"]
    actual_data["dateModified"] = masked_data["dateModified"]
    assert masked_data == expected_masked_data

    # Broker (with accreditation for restricted) allowed to see masked data
    with change_auth(app, ("Basic", ("brokerr", ""))):
        response = app.get(f"/contracts/{id}")
    assert response.status_code == 200
    unmasked_data = response.json["data"]
    actual_data["dateCreated"] = unmasked_data["dateCreated"]
    actual_data["dateModified"] = unmasked_data["dateModified"]
    assert unmasked_data == actual_data

    # Feed is masked
    # TODO: add check if there will be masked fields that allowed in feed
    # response = app.get(f"/contracts?mode=_all_&opt_fields=some_field")
    # assert response.status_code == 200
    # masked_feed_data = response.json["data"][0]
    # assert masked_feed_data["some_field"] == expected_masked_data["some_field"]

    # Broker (with accreditation for restricted) allowed to see masked data in feed
    # TODO: add check if there will be masked fields that allowed in feed
    # with change_auth(app, ("Basic", ("brokerr", ""))):
    #     response = app.get(f"/contracts?mode=_all_&opt_fields=some_field")
    # assert response.status_code == 200
    # unmasked_feed_data = response.json["data"][0]
    # assert unmasked_feed_data["some_field"] == data["some_field"]
