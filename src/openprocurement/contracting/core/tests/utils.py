from types import SimpleNamespace
from uuid import uuid4

from openprocurement.api.context import get_request, set_request, set_request_now
from openprocurement.api.utils import get_now
from openprocurement.contracting.core.procedure.models.contract import PostContract
from openprocurement.tender.open.tests.above_threshold.base import test_tender_open_config


def create_minimal_tender_for_contract(mongodb, contract):
    # FIXME: This is a temporary solution to create a minimal tender for the contract
    mongodb.tenders.store.save_data(
        mongodb.tenders.collection,
        {
            "_id": contract["tender_id"],
            "doc_type": "Tender",
            "tenderID": "UA-2024-01-01-000001-a",
            "status": "complete",
            "procurementMethodType": "aboveThreshold",
            "awards": [
                {
                    "id": contract["awardID"],
                    "status": "active",
                    "complaintPeriod": {
                        "startDate": "2024-01-01T00:00:00+02:00",
                        "endDate": "2024-01-01T00:00:00+02:00",
                    },
                    "value": {
                        "amount": 1000,
                    },
                }
            ],
            "contracts": [contract],
            "config": test_tender_open_config,
        },
        insert=True,
    )


def create_contract(self, data, config=None):
    if "id" not in data and "_id" not in data:
        data["id"] = uuid4().hex

    set_request_now(get_now())

    tender = self.mongodb.tenders.get(data["tender_id"])
    if not tender:
        create_minimal_tender_for_contract(self.mongodb, data)
        tender = self.mongodb.tenders.get(data["tender_id"])

    # the model validators take the tender from the request (in the API they run within the request of the tender),
    # not from whatever request a previous test left in the thread context
    previous_request = get_request()
    set_request(SimpleNamespace(validated={"tender": tender}))
    try:
        contract = PostContract.model_validate(data).serialize()
    finally:
        set_request(previous_request)
    if config:
        contract["config"] = config
    self.mongodb.contracts.save(contract, insert=True)

    response = self.app.get(f"/contracts/{data['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    return response.json["data"]
