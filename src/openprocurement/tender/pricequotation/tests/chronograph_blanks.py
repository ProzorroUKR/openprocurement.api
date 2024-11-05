from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_organization,
    test_tender_pq_requirement_response,
)
from openprocurement.tender.pricequotation.tests.utils import copy_tender_items


# TenderSwitchQualificationResourceTest
def switch_to_qualification(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]

    bid, token = self.create_bid(
        self.tender_id,
        {
            "tenderers": [test_tender_pq_organization],
            "items": copy_tender_items(tender["items"]),
            "value": {"amount": 500},
            "requirementResponses": test_tender_pq_requirement_response,
        },
    )

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
        self.assertEqual({i["status"] for i in response.json["data"]["lots"]}, {"unsuccessful"})


def ensure_no_auction_period(self):
    self.check_chronograph()
    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertNotIn("auctionPeriod", response.json["data"])
