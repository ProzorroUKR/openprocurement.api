from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
)
from openprocurement.tender.core.tests.utils import set_bid_items


def create_document_active_tendering_status(self):
    self.set_status("active.tendering")
    bid_data = {
        "tenderers": [test_tender_below_organization],
        "value": {"amount": 500},
        "lotValues": None,
        "parameters": None,
        "documents": None,
        "subcontractingDetails": "test",
    }
    set_bid_items(self, bid_data)
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    bid = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{bid['id']}?acc_token={token}", {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    bid = response.json["data"]
    self.assertEqual(bid["status"], "pending")

    response = self.app.get(f"/tenders/{self.tender_id}")
    tender_before = response.json["data"]
    self.assertNotIn("invalidationDate", tender_before["enquiryPeriod"])

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(f"/tenders/{self.tender_id}?acc_token={self.tender_token}")
    tender_after = response.json["data"]
    self.assertIn("invalidationDate", tender_after["enquiryPeriod"])
    response = self.app.get(f"/tenders/{self.tender_id}/bids/{bid['id']}?acc_token={token}")
    self.assertEqual(response.json["data"]["status"], "invalid")
