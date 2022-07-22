import mock
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19


def skip_complaint_period_2020_04_19(func):
    def wrapper(self):

        set_complaint_period_end = getattr(self, "set_complaint_period_end", None)

        if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
            set_complaint_period_end()
        return func(self)
    return wrapper


def activate_cancellation_after_2020_04_19(self, cancellation_id, tender_id=None, tender_token=None):
    if not tender_id:
        tender_id = self.tender_id

    if not tender_token:
        tender_token = self.tender_token

    tender = self.mongodb.tenders.get(self.tender_id)

    without_complaints = [
        "reporting",
        "belowThreshold",
        "closeFrameworkAgreementSelectionUA",
        "negotiation",
        "negotiation.quick",
    ]
    tender_type = tender["procurementMethodType"]

    active_award = any(i for i in tender.get("awards", []) if i.get("status") == "active")
    negotiation_with_active_award = tender_type.startswith("negotiation") and active_award

    if (tender_type not in without_complaints) or negotiation_with_active_award:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id, tender_id, tender_token)
    else:
        activate_cancellation_without_complaints_after_2020_04_19(self, cancellation_id, tender_id, tender_token)


def activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id, tender_id=None, tender_token=None):
    if not tender_id:
        tender_id = self.tender_id

    if not tender_token:
        tender_token = self.tender_token

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            tender_id, cancellation_id, tender_token
        ),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            tender_id, cancellation_id, tender_token
        ),
        {"data": {"status": "pending"}},
    )
    cancellation = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(cancellation["status"], "pending")

    # go to complaintPeriod end
    tender = self.mongodb.tenders.get(tender_id)
    for c in tender["cancellations"]:
        if c["status"] == "pending":
            c["complaintPeriod"]["endDate"] = get_now().isoformat()
    self.mongodb.tenders.save(tender)

    self.check_chronograph()

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")


def activate_cancellation_without_complaints_after_2020_04_19(self, cancellation_id, tender_id=None, tender_token=None):
    if not tender_id:
        tender_id = self.tender_id

    if not tender_token:
        tender_token = self.tender_token

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            tender_id, cancellation_id, tender_token
        ),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(
            tender_id, cancellation_id, tender_token
        ),
        {"data": {"status": "active"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
