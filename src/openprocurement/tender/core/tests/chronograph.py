from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from freezegun import freeze_time

from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
    test_tender_below_draft_complaint,
)
from openprocurement.tender.core.procedure.models.cancellation import PostCancellation
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.core.utils import calculate_tender_full_date


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def switch_tender_complaints_draft(self):
    # get tender and check next_check
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_data = response.json["data"]

    # let's post a draft complaint
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.json["data"]["status"], "draft")

    # get tender and check next_check
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_data = response.json["data"]
    # assertEqual changed to assertLessEqual
    # Even though "next_check" should be "complaintPeriod.endDate",
    # in this test tender "tenderPeriod.endDate" is less than "complaintPeriod.endDate"
    # that is not the case in a real tender.
    # The test only worked
    # because complaintPeriod.endDate had been recalculated (serializable) during complaint post!
    self.assertLessEqual(
        parse_date(response.json["data"].get("next_check")), parse_date(tender_data["complaintPeriod"]["endDate"])
    )

    # and once the date passed
    tender = self.mongodb.tenders.get(self.tender_id)
    start_date = get_now() - timedelta(days=40)
    tender["complaintPeriod"] = {  # tenderPeriod was here before, must be a mistake
        "startDate": start_date.isoformat(),
        "endDate": calculate_tender_full_date(start_date, timedelta(days=30)).isoformat(),
    }
    self.mongodb.tenders.save(tender)

    # switch
    response = self.check_chronograph()
    data = response.json["data"]
    complaint = data["complaints"][0]
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "complaintPeriodEnded")
    self.assertNotEqual(data.get("next_check"), tender_data["complaintPeriod"]["endDate"])


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def switch_tender_cancellation_complaints_draft(self):
    # first we post a cancellation
    tender = self.mongodb.tenders.get(self.tender_id)
    test_cancellation = deepcopy(test_tender_below_cancellation)
    cancellation_data = PostCancellation(test_cancellation).serialize()
    cancellation_data["status"] = "pending"
    cancellation_data["complaintPeriod"] = {
        "startDate": get_now().isoformat(),
        "endDate": (get_now() + timedelta(days=10)).isoformat(),
    }
    tender.update(cancellations=[cancellation_data])
    self.mongodb.tenders.save(tender)

    # let's post a draft complaint
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, cancellation_data["id"]),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.json["data"]["status"], "draft")

    # get tender and check next_check
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(
        parse_date(response.json["data"].get("next_check")),
        parse_date(cancellation_data["complaintPeriod"]["endDate"]),
    )

    # and once the date passed
    tender = self.mongodb.tenders.get(self.tender_id)
    tender["cancellations"][0]["complaintPeriod"] = {
        "startDate": (get_now() - timedelta(days=30)).isoformat(),
        "endDate": (get_now() - timedelta(days=20)).isoformat(),
    }
    self.mongodb.tenders.save(tender)

    # switch
    response = self.check_chronograph()
    self.assertNotEqual(response.json["data"].get("next_check"), cancellation_data["complaintPeriod"]["endDate"])

    # check complaint status
    response = self.app.get("/tenders/{}/cancellations/{}/complaints".format(self.tender_id, cancellation_data["id"]))
    complaint = response.json["data"][0]
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "complaintPeriodEnded")


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def switch_qualification_complaints_draft(self):
    # generate qualifications
    self.set_status("active.pre-qualification", extra={"status": "active.tendering"})
    response = self.check_chronograph()
    qualifications = response.json["data"]["qualifications"]
    self.assertEqual(len(qualifications), 2)

    # activate qualifications
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    qualification = tender["qualifications"][0]

    # let's post a draft complaint
    token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(self.tender_id, qualification["id"], token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.json["data"]["status"], "draft")

    # get tender and check next_check
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(
        parse_date(response.json["data"].get("next_check")), parse_date(tender["qualificationPeriod"]["endDate"])
    )

    # and once the date passed
    tender = self.mongodb.tenders.get(self.tender_id)
    tender["qualificationPeriod"] = {
        "startDate": (get_now() - timedelta(days=20)).isoformat(),
        "endDate": (get_now() - timedelta(days=10)).isoformat(),
    }
    self.mongodb.tenders.save(tender)

    # switch
    response = self.check_chronograph()
    data = response.json["data"]
    complaint = data["qualifications"][0]["complaints"][0]
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "complaintPeriodEnded")
    self.assertNotEqual(data.get("next_check"), tender["qualificationPeriod"]["endDate"])


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def switch_award_complaints_draft(self):
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.json["data"]["status"], "active")
    award_data = response.json["data"]

    # let's post a draft complaint
    token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.json["data"]["status"], "draft")

    # get tender and check next_check
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(
        parse_date(response.json["data"].get("next_check")),
        parse_date(award_data["complaintPeriod"]["endDate"]),
    )

    # and once the date passed
    tender = self.mongodb.tenders.get(self.tender_id)
    tender["awards"][0]["complaintPeriod"] = {
        "startDate": (get_now() - timedelta(days=20)).isoformat(),
        "endDate": (get_now() - timedelta(days=10)).isoformat(),
    }
    self.mongodb.tenders.save(tender)

    # switch
    response = self.check_chronograph()
    data = response.json["data"]
    complaint = data["awards"][0]["complaints"][0]
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "complaintPeriodEnded")
    self.assertNotEqual(data.get("next_check"), award_data["complaintPeriod"]["endDate"])


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def switch_tender_after_cancellation_unsuccessful(self):
    """
    https://jira.prozorro.org/browse/CS-11455
    """
    # cancellation
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations?acc_token={self.tender_token}",
        {
            "data": {
                "reason": "cancellation reason",
                "cancellationOf": "tender",
                "reasonType": "noDemand",
            }
        },
    )
    cancellation_id = response.json["data"]["id"]
    self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations/{cancellation_id}/documents?acc_token={self.tender_token}",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/cancellations/{cancellation_id}?acc_token={self.tender_token}",
        {"data": {"status": "pending"}},
    )
    self.assertEqual("pending", response.json["data"]["status"])

    # complaint
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations/{cancellation_id}/complaints",
        {"data": test_tender_below_draft_complaint},
    )
    complaint_id = response.json["data"]["id"]
    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
            {"data": {"status": "pending"}},
        )
    self.assertEqual("pending", response.json["data"]["status"])

    # review complaint
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
            {
                "data": {
                    "status": "accepted",
                    "reviewDate": get_now().isoformat(),
                    "reviewPlace": "there",
                }
            },
        )
        self.assertEqual("accepted", response.json["data"]["status"])

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
            {"data": {"status": "satisfied"}},
        )
        self.assertEqual("satisfied", response.json["data"]["status"])

    # check tender state
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_data = response.json["data"]
    self.assertEqual("active.tendering", tender_data["status"])
    self.assertEqual("pending", tender_data["cancellations"][0]["status"])
    self.assertEqual("satisfied", tender_data["cancellations"][0]["complaints"][0]["status"])

    with freeze_time(response.json["data"]["tenderPeriod"]["endDate"]):
        response = self.check_chronograph()

    # !!! check tender is blocked
    self.assertEqual("active.tendering", response.json["data"]["status"])
