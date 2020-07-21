# -*- coding: utf-8 -*-
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
