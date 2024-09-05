from copy import deepcopy
from math import ceil

from openprocurement.api.constants import RELEASE_2020_04_19, SANDBOX_MODE
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_complaint,
    test_tender_below_draft_claim,
)
from openprocurement.tender.core.tests.utils import change_auth


def create_tender_lot_qualification_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, list(self.initial_bids_tokens.values())[0]
        ),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(complaint["author"]["name"], self.author_data["name"])

    else:
        self.assertEqual(response.json["data"]["status"], "draft")
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}".format(
                    self.tender_id, self.qualification_id, complaint["id"]
                ),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    # set complaint status to invalid to be able to cancel the tender
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], complaint_token
            ),
            {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
        )
        self.assertEqual(response.status, "200 OK")

    if RELEASE_2020_04_19 > get_now():
        # Test for old rules
        # In new rules there will be 403 error
        self.cancel_tender()

        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
                self.tender_id, self.qualification_id, list(self.initial_bids_tokens.values())[0]
            ),
            {"data": test_tender_below_draft_claim},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't add complaint in current (cancelled) tender status"
        )


def create_tender_qualification_complaint(self):
    complaint_data = deepcopy(test_tender_below_draft_claim)
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, list(self.initial_bids_tokens.values())[0]
        ),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "draft")

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, list(self.initial_bids_tokens.values())[0]
        ),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])
    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(complaint["author"]["name"], self.author_data["name"])

    if RELEASE_2020_04_19 < get_now():
        self.assertEqual(response.json["data"]["status"], "draft")
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}".format(
                    self.tender_id, self.qualification_id, complaint["id"]
                ),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    # set complaint status to invalid to be able to cancel the tender
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], complaint_token
            ),
            {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
        )
        self.assertEqual(response.status, "200 OK")

    if RELEASE_2020_04_19 > get_now():
        # Test for old rules
        # In new rules there will be 403 error
        self.cancel_tender()

        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
                self.tender_id, self.qualification_id, list(self.initial_bids_tokens.values())[0]
            ),
            {"data": test_tender_below_draft_claim},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't add complaint in current (cancelled) tender status"
        )


def switch_bid_status_unsuccessul_to_active(self):
    bid_id, bid_token = list(self.initial_bids_tokens.items())[0]

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 3)
    qualification_id = ""
    for qualification in qualifications:
        status = "active"
        if qualification["bidID"] == bid_id:
            status = "unsuccessful"
            qualification_id = qualification["id"]
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": status, "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], status)
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json["data"]["qualifications"]
    for qualification in qualifications:
        end_date = parse_date(qualification["complaintPeriod"]["endDate"])
        start_date = parse_date(qualification["complaintPeriod"]["startDate"])
        duration = (end_date - start_date).total_seconds()
        if SANDBOX_MODE:
            duration = ceil(duration) * 1440
        duration = duration / 86400  # days float
        self.assertEqual(int(duration), 5)

    # create complaint
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(self.tender_id, qualification_id, bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]

    if RELEASE_2020_04_19 < get_now():
        self.assertEqual(response.json["data"]["status"], "draft")
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, qualification_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ("Basic", ("reviewer", ""))
    now = get_now()
    data = {"status": "accepted"}
    if RELEASE_2020_04_19 < now:
        data.update(
            {
                "reviewDate": now.isoformat(),
                "reviewPlace": "some",
            }
        )
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, qualification_id, complaint["id"]),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "accepted")
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["reviewPlace"], "some")
        self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, qualification_id, complaint["id"]),
        {"data": {"status": "satisfied"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "satisfied")

    # Cancell qualification
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    new_qualification_id = response.headers["location"].split("/")[-1]
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, new_qualification_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    for b in response.json["data"]:
        self.assertEqual(b["status"], "active")


def check_sign_doc_qualifications_before_stand_still(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json["data"]
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
    # try to move to stand-still status without docs
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "documents",
                "description": "Document with type 'evaluationReports' and format pkcs7-signature is required",
            }
        ],
    )
    # let's add sign doc
    sign_doc = {
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pdf",
        "documentType": "evaluationReports",
    }
    # try to add 2 sign docs
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {"data": [sign_doc, sign_doc]},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "evaluationReports document in tender should be only one",
    )

    # try to add doc with another documentType in pre-qualification
    sign_doc["documentType"] = "notice"
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {"data": sign_doc},
        status=403,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add document in current (active.pre-qualification) tender status",
    )

    # add right document for tender
    sign_doc["documentType"] = "evaluationReports"
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {"data": sign_doc},
    )
    self.assertEqual(response.status, "201 Created")
    doc_1_id = response.json["data"]["id"]

    # move to stand-still successfully
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to patch doc in active.pre-qualification.stand-still status
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/documents/{doc_1_id}?acc_token={self.tender_token}",
        {"data": {"title": "test"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document in current (active.pre-qualification.stand-still) tender status",
    )
