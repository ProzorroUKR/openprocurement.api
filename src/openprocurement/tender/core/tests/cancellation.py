from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.utils import get_now


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
    if tender["config"]["hasCancellationComplaints"]:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id, tender_id, tender_token)
    else:
        activate_cancellation_without_complaints_after_2020_04_19(self, cancellation_id, tender_id, tender_token)


def activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id, tender_id=None, tender_token=None):
    if not tender_id:
        tender_id = self.tender_id

    if not tender_token:
        tender_token = self.tender_token

    self.add_sign_doc(
        tender_id,
        tender_token,
        docs_url=f"/cancellations/{cancellation_id}/documents",
        document_type="cancellationReport",
    )

    tender = self.mongodb.tenders.get(tender_id)

    if tender["config"]["hasCancellationComplaints"] is True:
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(tender_id, cancellation_id, tender_token),
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

    else:
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(tender_id, cancellation_id, tender_token),
            {"data": {"status": "pending"}},
        )
        cancellation = response.json["data"]
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(cancellation["status"], "active")

        self.check_chronograph()


def activate_cancellation_without_complaints_after_2020_04_19(self, cancellation_id, tender_id=None, tender_token=None):
    if not tender_id:
        tender_id = self.tender_id

    if not tender_token:
        tender_token = self.tender_token

    self.add_sign_doc(
        tender_id,
        tender_token,
        docs_url=f"/cancellations/{cancellation_id}/documents",
        document_type="cancellationReport",
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(tender_id, cancellation_id, tender_token),
        {"data": {"status": "active"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
