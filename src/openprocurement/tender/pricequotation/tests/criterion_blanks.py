import mock
from copy import deepcopy
from datetime import timedelta
from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.tests.base import (
    test_tender_pq_short_profile,
    test_tender_pq_data_before_multiprofile,
    test_tender_pq_data_after_multiprofile,
    test_tender_pq_item_after_multiprofile,
)


def create_tender_criteria_multi_profile(self):
    with mock.patch("openprocurement.tender.pricequotation.procedure.models.tender.PQ_MULTI_PROFILE_FROM",
                    get_now() + timedelta(days=1)):
        with mock.patch("openprocurement.tender.pricequotation.procedure.models.item.PQ_MULTI_PROFILE_FROM",
                        get_now() + timedelta(days=1)):
            with mock.patch("openprocurement.tender.pricequotation.procedure.models.criterion.PQ_MULTI_PROFILE_FROM",
                            get_now() + timedelta(days=1)):
                data = deepcopy(test_tender_pq_data_before_multiprofile)

                response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
                self.assertEqual(response.status, "201 Created")
                self.assertEqual(response.content_type, "application/json")
                tender = response.json["data"]
                token = response.json["access"]["token"]

                item_id = tender["items"][0]["id"]
                criteria = deepcopy(test_tender_pq_short_profile["criteria"])
                criteria[0]["relatesTo"] = "item"
                criteria[0]["relatedItem"] = item_id
                response = self.app.patch_json(
                    "/tenders/{}?acc_token={}".format(tender["id"], token),
                    {"data": {"criteria": criteria}},
                    status=422,
                )
                self.assertEqual(response.status, '422 Unprocessable Entity')
                self.assertEqual(response.content_type, "application/json")
                self.assertEqual(response.json["status"], "error")
                self.assertEqual(
                    response.json["errors"], [{
                        "description": [
                            {
                                "relatesTo": [
                                    "Rogue field."
                                ],
                                "relatedItem": [
                                    "Rogue field."
                                ]
                            }
                        ],
                        "location": "body",
                        "name": "criteria"
                    }],
                )

    with mock.patch("openprocurement.tender.pricequotation.procedure.models.tender.PQ_MULTI_PROFILE_FROM",
                    get_now() - timedelta(days=1)):
        with mock.patch("openprocurement.tender.pricequotation.procedure.models.item.PQ_MULTI_PROFILE_FROM",
                        get_now() - timedelta(days=1)):
            with mock.patch("openprocurement.tender.pricequotation.procedure.models.criterion.PQ_MULTI_PROFILE_FROM",
                            get_now() - timedelta(days=1)):
                data = deepcopy(test_tender_pq_data_after_multiprofile)
                data["items"].append(deepcopy(test_tender_pq_item_after_multiprofile))
                data["items"][1]["profile"] = "655361-30230000-889652-40000777"

                response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
                self.assertEqual(response.status, "201 Created")
                self.assertEqual(response.content_type, "application/json")
                tender = response.json["data"]
                token = response.json["access"]["token"]

                item_ids = [item["id"] for item in tender["items"]]
                criteria = deepcopy(test_tender_pq_short_profile["criteria"])
                criteria[0]["relatesTo"] = "tender"
                criteria[0]["relatedItem"] = item_ids[0]

                response = self.app.patch_json(
                    "/tenders/{}?acc_token={}".format(tender["id"], token),
                    {"data": {"criteria": criteria}},
                    status=422
                )
                self.assertEqual(response.status, '422 Unprocessable Entity')
                self.assertEqual(response.content_type, "application/json")
                self.assertEqual(response.json["status"], "error")
                self.assertEqual(
                    response.json["errors"], [{
                        "description": [{"relatesTo": ["Value must be one of ['item']."]}],
                        "location": "body",
                        "name": "criteria"
                    }],
                )

                criteria[0]["relatesTo"] = "item"
                criteria[0]["relatedItem"] = "invalid"
                response = self.app.patch_json(
                    "/tenders/{}?acc_token={}".format(tender["id"], token),
                    {"data": {"criteria": criteria}},
                    status=422
                )
                self.assertEqual(response.status, '422 Unprocessable Entity')
                self.assertEqual(response.content_type, "application/json")
                self.assertEqual(response.json["status"], "error")
                self.assertEqual(
                    response.json["errors"], [{
                        "description": {"relatedItem": ['Hash value is wrong length.']},
                        "location": "body",
                        "name": "criteria"
                    }],
                )

                criteria[0]["relatesTo"] = "item"
                criteria[0]["relatedItem"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                response = self.app.patch_json(
                    "/tenders/{}?acc_token={}".format(tender["id"], token),
                    {"data": {"criteria": criteria}},
                    status=422
                )
                self.assertEqual(response.status, '422 Unprocessable Entity')
                self.assertEqual(response.content_type, "application/json")
                self.assertEqual(response.json["status"], "error")
                self.assertEqual(
                    response.json["errors"], [{
                        "description": ["relatedItem should be one of items"],
                        "location": "body",
                        "name": "criteria"
                    }],
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

                self.assertEqual(tender["criteria"], expected_criteria)
