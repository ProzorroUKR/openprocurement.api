from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
)


def create_tender_complaint(self):
    # complaint
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"], {"currency": "UAH", "amount": 2000})

    self.cancel_tender()

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_tender_below_draft_complaint},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (cancelled) tender status"
    )
