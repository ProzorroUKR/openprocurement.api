# -*- coding: utf-8 -*-
from datetime import timedelta
from mock import patch

from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.utils import change_auth

from openprocurement.tender.openua.tests.chronograph_blanks import (
    switch_to_unsuccessful as switch_to_unsuccessful_ua,
    switch_to_unsuccessful_lot as switch_to_unsuccessful_lot_ua,
)


# TenderSwitchAuctionResourceTest
def switch_to_auction(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")


# TenderLotSwitch1BidResourceTest
def switch_to_qualification(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")


# TenderSwitchAuctionResourceTest

@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def switch_to_unsuccessful_before_new(self):
    return switch_to_unsuccessful_ua(self)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
def switch_to_unsuccessful_after_new(self):
    return switch_to_unsuccessful_ua(self)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def switch_to_unsuccessful_new(self):
    self.set_status("active.auction", {"status": self.initial_status})
    self.check_chronograph()

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{} for b in response.json["data"]["bids"]]}}
    )
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}}
    )

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}}
    )

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        if i["status"] != "cancelled" and i.get("complaintPeriod", None):
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def switch_to_active_to_unsuccessful(self):
    self.set_status("active.auction", {"status": self.initial_status})
    self.check_chronograph()

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{} for b in response.json["data"]["bids"]]}}
    )
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}}
    )

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award_id),
        {
            "data": {
                "status": "active",
                "qualified": True,
                "eligible": True
            }
        }
    )

    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "cancelled"}}
    )

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}}
    )

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        if i["status"] != "cancelled" and i.get("complaintPeriod", None):
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


# TenderLotSwitchAuctionResourceTest

@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def switch_to_unsuccessful_lot_before_new(self):
    return switch_to_unsuccessful_lot_ua(self)

@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
def switch_to_unsuccessful_lot_after_new(self):
    return switch_to_unsuccessful_lot_ua(self)


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def switch_to_unsuccessful_lot_new(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()

    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        for lot in response.json["data"]["lots"]:
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, lot["id"]),
                {"data": {"bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                    for b in auction_bids_data]}}
            )
            self.assertEqual(response.status, "200 OK")

    self.assertEqual(response.json["data"]["status"], "active.qualification")

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        while any([i["status"] == "pending" for i in response.json["data"]]):
            award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
            self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}}
            )
            response = self.app.get("/tenders/{}/awards".format(self.tender_id))

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", None):
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.procedure.state.award.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.state.tender.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.procedure.awarding.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def switch_to_active_to_unsuccessful_lot(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()

    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        for lot in response.json["data"]["lots"]:
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, lot["id"]),
                {"data": {"bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                    for b in auction_bids_data]}}
            )
            self.assertEqual(response.status, "200 OK")

    self.assertEqual(response.json["data"]["status"], "active.qualification")

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        award_ids = [i["id"] for i in response.json["data"] if i["status"] == "pending"]
        for award_id in award_ids:
            response = self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}}
            )

        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        award_ids = [i["id"] for i in response.json["data"] if i["status"] == "pending"]
        for award_id in award_ids:
            response = self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, award_id),
                {
                    "data": {
                        "status": "active",
                        "qualified": True,
                        "eligible": True
                    }
                }
            )
            response = self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "cancelled"}}
            )

        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        while any([i["status"] == "pending" for i in response.json["data"]]):
            award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
            self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}}
            )
            response = self.app.get("/tenders/{}/awards".format(self.tender_id))

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", None):
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
