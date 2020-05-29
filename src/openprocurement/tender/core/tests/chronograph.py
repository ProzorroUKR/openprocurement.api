# -*- coding: utf-8 -*-
from datetime import timedelta
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_draft_complaint, test_cancellation
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.openeu.models import Cancellation
from copy import deepcopy
from mock import patch


@patch("openprocurement.tender.core.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def switch_tender_complaints_draft(self):
    # let's post a draft complaint
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_draft_complaint},
    )
    self.assertEqual(response.json["data"]["status"], "draft")

    # get tender and check next_check
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_data = response.json["data"]
    self.assertEqual(response.json["data"].get("next_check"), tender_data["complaintPeriod"]["endDate"])

    # and once the date passed
    tender = self.db.get(self.tender_id)
    start_date = get_now() - timedelta(days=40)
    tender["tenderPeriod"] = dict(
        startDate=start_date.isoformat(),
        endDate=calculate_tender_business_date(start_date, timedelta(days=30)).isoformat()
    )
    self.db.save(tender)

    # switch
    response = self.check_chronograph()
    data = response.json["data"]
    complaint = data["complaints"][0]
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "complaintPeriodEnded")
    self.assertNotEqual(data.get("next_check"), tender_data["complaintPeriod"]["endDate"])


@patch("openprocurement.tender.core.utils.RELEASE_2020_04_19", get_now() - timedelta(1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def switch_tender_cancellation_complaints_draft(self):
    # first we post a cancellation
    tender = self.db.get(self.tender_id)
    cancellation = deepcopy(test_cancellation)
    cancellation["status"] = "pending"
    cancellation["complaintPeriod"] = dict(
        startDate=get_now(),
        endDate=get_now() + timedelta(days=10),
    )
    cancellation = Cancellation(cancellation)
    cancellation_data = cancellation.serialize("embedded")
    tender.update(cancellations=[cancellation_data])
    self.db.save(tender)

    # let's post a draft complaint
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/complaints".format(self.tender_id, cancellation.id),
        {"data": test_draft_complaint},
    )
    self.assertEqual(response.json["data"]["status"], "draft")

    # get tender and check next_check
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"].get("next_check"),
                     cancellation_data["complaintPeriod"]["endDate"])

    # and once the date passed
    tender = self.db.get(self.tender_id)
    tender["cancellations"][0]["complaintPeriod"] = dict(
        startDate=(get_now() - timedelta(days=30)).isoformat(),
        endDate=(get_now() - timedelta(days=20)).isoformat()
    )
    self.db.save(tender)

    # switch
    response = self.check_chronograph()
    self.assertNotEqual(response.json["data"].get("next_check"), cancellation_data["complaintPeriod"]["endDate"])

    # check complaint status
    response = self.app.get("/tenders/{}/cancellations/{}/complaints".format(self.tender_id, cancellation.id))
    complaint = response.json["data"][0]
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "complaintPeriodEnded")


@patch("openprocurement.tender.core.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def switch_qualification_complaints_draft(self):
    # generate qualifications
    self.set_status("active.pre-qualification", extra={"status": "active.tendering"})
    response = self.check_chronograph()
    qualifications = response.json["data"]["qualifications"]
    self.assertEqual(len(qualifications), 2)

    # activate qualifications
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(
                self.tender_id, qualification["id"], self.tender_token
            ),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    qualification = tender["qualifications"][0]

    # let's post a draft complaint
    token = self.initial_bids_tokens.values()[0]
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(self.tender_id, qualification["id"], token),
        {"data": test_draft_complaint},
    )
    self.assertEqual(response.json["data"]["status"], "draft")

    # get tender and check next_check
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"].get("next_check"), tender["qualificationPeriod"]["endDate"])

    # and once the date passed
    tender = self.db.get(self.tender_id)
    tender["qualificationPeriod"] = dict(
        startDate=(get_now() - timedelta(days=20)).isoformat(),
        endDate=(get_now() - timedelta(days=10)).isoformat()
    )
    self.db.save(tender)

    # switch
    response = self.check_chronograph()
    data = response.json["data"]
    complaint = data["qualifications"][0]["complaints"][0]
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "complaintPeriodEnded")
    self.assertNotEqual(data.get("next_check"), tender["qualificationPeriod"]["endDate"])


@patch("openprocurement.tender.core.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def switch_award_complaints_draft(self):
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.json["data"]["status"], "active")
    award_data = response.json["data"]

    # let's post a draft complaint
    token = self.initial_bids_tokens.values()[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {"data": test_draft_complaint},
    )
    self.assertEqual(response.json["data"]["status"], "draft")

    # get tender and check next_check
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"].get("next_check"), award_data["complaintPeriod"]["endDate"])

    # and once the date passed
    tender = self.db.get(self.tender_id)
    tender["awards"][0]["complaintPeriod"] = dict(
        startDate=(get_now() - timedelta(days=20)).isoformat(),
        endDate=(get_now() - timedelta(days=10)).isoformat()
    )
    self.db.save(tender)

    # switch
    response = self.check_chronograph()
    data = response.json["data"]
    complaint = data["awards"][0]["complaints"][0]
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "complaintPeriodEnded")
    self.assertNotEqual(data.get("next_check"), award_data["complaintPeriod"]["endDate"])
