# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_claim
from copy import deepcopy


def next_check_field_in_active_qualification(self):

    response = self.set_status("active.pre-qualification", "end")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    response = self.set_status("active.pre-qualification.stand-still", "end")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.assertIn("next_check", list(response.json["data"].keys()))

    response = self.set_status("active.auction", "end")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.assertNotIn("next_check", list(response.json["data"].keys()))


def active_tendering_to_pre_qual(self):
    response = self.set_status("active.tendering", "end")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


def pre_qual_switch_to_stand_still(self):
    self.set_status("active.pre-qualification", "end")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


# TenderSwitchAuctionResourceTest


def switch_to_auction(self):
    response = self.set_status("active.pre-qualification.stand-still", "end")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")


# TenderComplaintSwitchResourceTest


def switch_to_complaint(self):
    user_data = deepcopy(self.author_data)
    for status in ["invalid", "resolved", "declined"]:
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": test_tender_below_claim
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
    response = self.set_status(self.initial_status, "end")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
    self.assertEqual(response.json["data"]["complaints"][-1]["status"], status)


def switch_to_unsuccessful(self):
    self.set_status(self.initial_status, "end")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    if self.initial_lots:
        self.assertEqual(set([i["status"] for i in response.json["data"]["lots"]]), {"unsuccessful"})


def switch_to_unsuccessful_from_qualification_stand_still(self):
    self.set_status("active.qualification")
    # check if number of active awards is less than 3
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    awards = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, awards[0]["id"], self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    self.set_status("active.qualification.stand-still", "end")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


# TenderSwitchPreQualificationStandStillResourceTest


def switch_to_awarded(self):
    self.set_status(self.initial_status, "end")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    response = self.app.get(f'/tenders/{self.tender_id}')
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertEqual(len(response.json["data"]["agreements"]), 1)
    self.app.authorization = ("Basic", ("broker", ""))
    self.assertEqual(response.json["data"]["features"], response.json["data"]["agreements"][0]["features"])

    bids_parameters = {
        bid["id"]: bid["parameters"] for bid in response.json["data"]["bids"] if bid["status"] == "active"
    }
    contract_parameters = {
        contract["bidID"]: contract["parameters"] for contract in response.json["data"]["agreements"][0]["contracts"]
    }
    self.assertEqual(bids_parameters, contract_parameters)


def set_auction_period_0bid(self):
    response = self.check_chronograph()
    should_start_after = response.json["data"]["lots"][0]["auctionPeriod"]["shouldStartAfter"]

    start_date = "9999-01-01T00:00:00+00:00"
    response = self.check_chronograph({"data": {"auctionPeriod": {"startDate": start_date}}}, status=422)
    self.assertEqual(
        response.json,
        {"status": "error", "errors": [
            {"location": "body", "name": "auctionPeriod", "description": ["Auction url at tender lvl forbidden"]}]}
    )

    response = self.check_chronograph()
    self.assertEqual(should_start_after, response.json["data"]["lots"][0]["auctionPeriod"]["shouldStartAfter"])
