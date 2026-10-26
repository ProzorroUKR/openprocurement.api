from datetime import timedelta

from freezegun import freeze_time

from openprocurement.api.constants_env import RELEASE_2020_04_19, RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.utils import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso

ACTIVE_BID_VISIBLE_FIELDS = [
    "status",
    "documents",
    "tenderers",
    "id",
    "eligibilityDocuments",
    "lotValues",
    "date",
    "financialDocuments",
    "qualificationDocuments",
    "submissionDate",
    "items",
]


def bids_on_tender_cancellation_in_qualification(self):
    self.bid_visible_fields = list(ACTIVE_BID_VISIBLE_FIELDS)
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        self.bid_visible_fields.append("selfEligible")

    deleted_bid_id = self._mark_one_bid_deleted()

    self.set_status("active.auction", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self._set_auction_results()

    tender = self._cancel_tender()

    self.app.authorization = ("Basic", ("broker", ""))
    for bid in tender["bids"]:
        if bid["id"] in self.valid_bids:
            self.assertEqual(bid["status"], "active")
            self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))

    for bid_id in self.initial_bids_tokens:
        if bid_id in self.valid_bids:
            response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_id))
            self.assertEqual(set(response.json["data"].keys()), set(self.bid_visible_fields))

            for doc_resource in [
                "documents",
                "eligibility_documents",
                "financial_documents",
                "qualification_documents",
            ]:
                self._bid_document_is_accessible(bid_id, doc_resource)
        elif bid_id != deleted_bid_id:
            for doc_resource in ["documents", "eligibility_documents"]:
                self._bid_document_is_accessible(bid_id, doc_resource)


def bids_on_tender_cancellation_in_awarded(self):
    self.bid_visible_fields = list(ACTIVE_BID_VISIBLE_FIELDS)
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        self.bid_visible_fields.append("selfEligible")

    self._mark_one_bid_deleted()

    self.set_status("active.auction", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self._set_auction_results()

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    if "milestones" in response.json["data"][0]:
        milestone_due_date = dt_from_iso(response.json["data"][0]["milestones"][0]["dueDate"])
        with freeze_time((milestone_due_date + timedelta(minutes=10)).isoformat()):
            self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
    else:
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    if RELEASE_2020_04_19 < get_now():
        self.set_all_awards_complaint_period_end()

    tender = self._cancel_tender()

    self.app.authorization = ("Basic", ("broker", ""))
    for bid in tender["bids"]:
        self.assertEqual(bid["status"], "active")
        self.assertEqual(set(bid.keys()), set(self.bid_visible_fields))

    for bid_id in self.initial_bids_tokens:
        if bid_id in self.valid_bids:
            response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_id))
            self.assertEqual(set(response.json["data"].keys()), set(self.bid_visible_fields))

            for doc_resource in [
                "documents",
                "eligibility_documents",
                "financial_documents",
                "qualification_documents",
            ]:
                self._bid_document_is_accessible(bid_id, doc_resource)
