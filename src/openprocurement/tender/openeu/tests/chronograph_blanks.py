# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.tests.base import test_claim, test_author
from copy import deepcopy

# TenderSwitchPreQualificationResourceTest


def active_tendering_to_pre_qual(self):
    response = self.set_status("active.pre-qualification", {"status": "active.tendering"})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


def pre_qual_switch_to_auction(self):
    response = self.set_status("active.auction", {"status": "active.pre-qualification"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


def pre_qual_switch_to_stand_still(self):
    response = self.set_status("active.pre-qualification.stand-still", {"status": "active.pre-qualification"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


# TenderSwitchAuctionResourceTest


def switch_to_auction(self):
    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]  # it's empty
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active"}},
        )

    response = self.set_status("active.auction", {"status": "active.pre-qualification.stand-still"})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")


# TenderComplaintSwitchResourceTest


def switch_to_complaint(self):
    claim_data = deepcopy(test_claim)
    claim_data["author"] = getattr(self, "author_data", test_author)
    for status in ["invalid", "resolved", "declined"]:
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": claim_data
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")
        complaint = response.json["data"]

        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
            {"data": {"status": "answered", "resolution": status * 4, "resolutionType": status}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "answered")
        self.assertEqual(response.json["data"]["resolutionType"], status)
    response = self.set_status("active.pre-qualification", {"status": self.initial_status})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
    self.assertEqual(response.json["data"]["complaints"][-1]["status"], status)
