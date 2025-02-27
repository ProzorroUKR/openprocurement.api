from datetime import timedelta

from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
)
from openprocurement.tender.core.tests.utils import change_auth

# TenderContractResourceTest


def patch_tender_contract(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]

    items = contract["items"]
    items[0]["description"] = "New Description"

    value = contract["value"]
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"items": items}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Updated could be only ('unit', 'quantity') in item, description change forbidden",
    )

    old_currency = value["currency"]
    value["currency"] = "USD"
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    value["currency"] = old_currency
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Can't sign contract before stand-still period end (", response.json["errors"][0]["description"])

    self.set_status("complete", {"status": "active.awarded"})

    token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={token}",
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints/{complaint['id']}?acc_token={owner_token}",
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints/{complaint['id']}",
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"dateSigned": i["complaintPeriod"]["endDate"]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    "Contract signature date should be after award complaint period end date ({})".format(
                        i["complaintPeriod"]["endDate"]
                    )
                ],
                "location": "body",
                "name": "dateSigned",
            }
        ],
    )

    one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"dateSigned": one_hour_in_furure}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Contract signature date can't be in the future"],
                "location": "body",
                "name": "dateSigned",
            }
        ],
    )

    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"dateSigned": custom_signature_date}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't sign contract before reviewing all complaints")

    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints/{complaint['id']}?acc_token={owner_token}",
            {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
