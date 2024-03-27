from copy import deepcopy
from unittest import mock

from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_data,
    test_tender_pq_item,
    test_tender_pq_short_profile,
)


def create_tender_criteria_multi_profile(self):
    data = deepcopy(test_tender_pq_data)
    data["agreement"] = {"id": self.agreement_id}
    data["items"].append(deepcopy(test_tender_pq_item))
    data["items"][1]["profile"] = "655361-30230000-889652-40000777"

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    item_ids = [item["id"] for item in tender["items"]]
    criteria = deepcopy(test_tender_pq_short_profile["criteria"])

    criteria[0]["relatesTo"] = "item"
    criteria[0]["relatedItem"] = "invalid"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"criteria": criteria}}, status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"relatedItem": ['Hash value is wrong length.']},
                "location": "body",
                "name": "criteria",
            }
        ],
    )

    criteria[0]["relatesTo"] = "item"
    criteria[0]["relatedItem"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"criteria": criteria}}, status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedItem": ['relatedItem should be one of items']}],
                "location": "body",
                "name": "criteria",
            }
        ],
    )

    for i, cr in enumerate(criteria):
        cr["relatesTo"] = "item"
        cr["relatedItem"] = item_ids[i % 2]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"criteria": criteria}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    expected_criteria = deepcopy(criteria)
    for c in expected_criteria:
        c.update(id=mock.ANY)

        for g in c.get("requirementGroups"):
            g.update(id=mock.ANY)

            for r in g.get("requirements"):
                r.update(id=mock.ANY)
                r.update(status=mock.ANY)
                r.update(datePublished=mock.ANY)

    self.assertEqual(tender["criteria"], expected_criteria)
