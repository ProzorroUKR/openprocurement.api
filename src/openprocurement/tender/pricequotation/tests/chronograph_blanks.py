# -*- coding: utf-8 -*-
from freezegun import freeze_time

from openprocurement.api.utils import get_now
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.pricequotation.constants import QUALIFICATION_DURATION
from openprocurement.tender.pricequotation.tests.data import (
    test_organization,
    test_requirement_response_valid
)


# TenderSwitchQualificationResourceTest
def switch_to_qualification(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization], "value": {"amount": 500},
            "requirementResponses": test_requirement_response_valid
        }},
    )

    bid = response.json["data"]
    bid_id = bid["id"]
    self.set_status("active.tendering", 'end')

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertEqual(len(response.json["data"]["awards"]), 1)
    self.assertEqual(response.json["data"]["awards"][0]['bid_id'], bid_id)


# TenderSwitchUnsuccessfulResourceTest
def switch_to_unsuccessful(self):
    self.set_status("active.tendering", 'end')
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    if self.initial_lots:
        self.assertEqual(
            set([i["status"] for i in response.json["data"]["lots"]]),
            set(["unsuccessful"])
        )


def switch_to_unsuccessful_by_chronograph(self):
    self.set_status("active.qualification", 'end')
    after_two_days = calculate_tender_business_date(get_now(), QUALIFICATION_DURATION)

    with freeze_time(after_two_days):
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.qualification")
        self.assertEqual(len(response.json["data"]["awards"]), 2)
        self.assertEqual(response.json["data"]["awards"][0]["status"], "unsuccessful")
        self.assertEqual(response.json["data"]["awards"][1]["status"], "pending")

    award = self.app.get("/tenders/{}/awards".format(self.tender_id)).json["data"][-1]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active"}})
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "cancelled"}})
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(len(response.json["data"]), 3)

    with freeze_time(after_two_days):
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "unsuccessful")
        self.assertEqual(len(response.json["data"]["awards"]), 3)
        self.assertEqual(response.json["data"]["awards"][0]["status"], "unsuccessful")
        self.assertEqual(response.json["data"]["awards"][1]["status"], "cancelled")
        self.assertEqual(response.json["data"]["awards"][2]["status"], "unsuccessful")
