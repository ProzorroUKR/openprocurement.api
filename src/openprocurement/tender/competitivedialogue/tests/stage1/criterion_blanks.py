from copy import deepcopy

from openprocurement.api.constants import BID_GUARANTEE_ALLOWED_TENDER_TYPES
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_cdeu_criteria,
)
from openprocurement.tender.core.tests.base import test_tender_guarantee_criteria
from openprocurement.tender.core.tests.utils import set_tender_criteria, set_tender_lots


def tender_with_guarantee_multilot(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"
    lots = deepcopy(self.initial_lots)
    lots.append(
        {
            "title": "invalid lot title",
            "description": "invalid lot description",
            "value": {"amount": 500},
            "minimalStep": {"amount": 15},
        }
    )
    set_tender_lots(data, lots)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    tender = response.json["data"]
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    related_lot_id = response.json["data"]["lots"][0]["id"]
    self.add_sign_doc(self.tender_id, self.tender_token)

    self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, related_lot_id, self.tender_token),
        {"data": {"guarantee": {"amount": 1, "currency": "UAH"}}},
        status=200,
    )
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.tendering"}},
        status=403,
    )
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Should be specified CRITERION.OTHER.BID.GUARANTEE for 'guarantee.amount' more than 0 to lot",
            }
        ],
    )

    criteria = []
    criteria.extend(test_tender_cdeu_criteria)
    set_tender_criteria(criteria, tender["lots"], tender["items"])

    self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": criteria,
        },
    )

    criteria = []
    criteria.extend(test_tender_guarantee_criteria)
    set_tender_criteria(criteria, tender["lots"], tender["items"])

    for criterion in criteria:
        if criterion["classification"]["id"] == "CRITERION.OTHER.BID.GUARANTEE":
            criterion["relatesTo"] = "lot"
            criterion["relatedItem"] = related_lot_id

    response = self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": criteria,
        },
        status=422,
    )
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "classification",
                "description": {
                    "id": [f"CRITERION.OTHER.BID.GUARANTEE is available only in {BID_GUARANTEE_ALLOWED_TENDER_TYPES}"]
                },
            }
        ],
    )

    self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, related_lot_id, self.tender_token),
        {"data": {"guarantee": {"amount": 0, "currency": "UAH"}}},
        status=200,
    )
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.tendering"}},
    )
