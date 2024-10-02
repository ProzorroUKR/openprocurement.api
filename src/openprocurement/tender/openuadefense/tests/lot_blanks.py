from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import (
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
    RELEASE_2020_04_19,
)
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_cancellation,
)
from openprocurement.tender.belowthreshold.tests.utils import (
    activate_contract,
    set_bid_lotvalues,
)
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_with_complaints_after_2020_04_19,
)


# TenderLotEdgeCasesTest
def question_blocking(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": test_tender_below_author,
            }
        },
    )

    question = response.json["data"]
    self.assertEqual(question["questionOf"], "lot")
    self.assertEqual(question["relatedItem"], self.initial_lots[0]["id"])

    self.set_status("active.auction", extra={"status": "active.tendering"})
    response = self.check_chronograph()

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]["id"],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )

    cancellation_id = response.json["data"]["id"]
    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)

    self.check_chronograph()

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.auction")


def next_check_value_with_unanswered_question(self):
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": test_tender_below_author,
            }
        },
    )
    question = response.json["data"]
    self.assertEqual(question["questionOf"], "lot")
    self.assertEqual(question["relatedItem"], self.initial_lots[0]["id"])

    self.set_status("active.auction", extra={"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertNotIn("next_check", response.json["data"])

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]["id"],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)
    else:
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertIn("next_check", response.json["data"])
        self.assertEqual(
            parse_date(response.json["data"]["next_check"]),
            parse_date(response.json["data"]["tenderPeriod"]["endDate"]),
        )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.assertIn("next_check", response.json["data"])
    self.assertGreater(
        parse_date(response.json["data"]["next_check"]), parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )


# TenderLotProcessTest


def one_lot_1bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    # add relatedLot for item
    items = deepcopy(self.initial_data["items"])
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(self.days_till_auction_starts)
    response = self.set_status("active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}}]})
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": lot_id}]
    bid, bid_token = self.create_bid(tender_id, bid_data)
    # switch to active.qualification
    self.set_status("active.auction", {"lots": [{"auctionPeriod": {"startDate": None}}], "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["lots"][0]["status"], "active")
    self.assertEqual(response.json["data"]["status"], "active.qualification")


def two_lot_1bid_0com_1can(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(self.days_till_auction_starts)
    self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}} for i in lots]}
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    set_bid_lotvalues(bid_data, [{"id": lot_id} for lot_id in lots])
    bid, bid_token = self.create_bid(tender_id, bid_data)
    # switch to active.qualification
    self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    # for first lot
    lot_id = lots[0]
    # cancel lot
    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": lot_id,
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id, tender_id, owner_token)
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    patch_data = {"status": "unsuccessful", "qualified": False}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = False
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": patch_data},
    )
    new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < get_now() < NEW_DEFENSE_COMPLAINTS_TO
    if not new_defence_complaints:
        # after stand slill period
        self.set_status("complete", {"status": "active.awarded"})
        # time travel
        tender = self.mongodb.tenders.get(tender_id)
        now = get_now().isoformat()
        for i in tender.get("awards", []):
            i["complaintPeriod"] = {"startDate": now, "endDate": now}
        self.mongodb.tenders.save(tender)
        # check tender status
        response = self.check_chronograph()
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual([i["status"] for i in response.json["data"]["lots"]], ["cancelled", "unsuccessful"])
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def two_lot_1bid_2com_1win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(self.days_till_auction_starts)
    self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}} for i in lots]}
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    set_bid_lotvalues(bid_data, [{"id": lot_id} for lot_id in lots])
    _, bid_token = self.create_bid(tender_id, bid_data)
    # switch to active.qualification
    self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    for lot_id in lots:
        # get awards
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
        # get pending award
        if len([i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id]) == 0:
            return
        award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]

        # set award as active
        self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
        patch_data = {"status": "active", "qualified": True}
        if self.initial_data['procurementMethodType'] != "simple.defense":
            patch_data["eligible"] = True
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
            {"data": patch_data},
        )
        # get contract id
        response = self.app.get("/tenders/{}".format(tender_id))
        contract = response.json["data"]["contracts"][-1]
        contract_id = contract["id"]
        # time travel
        tender = self.mongodb.tenders.get(tender_id)
        now = (get_now() - timedelta(minutes=1)).isoformat()
        for i in tender.get("awards", []):
            i["complaintPeriod"] = {"startDate": now, "endDate": now}
        self.mongodb.tenders.save(tender)
        # sign contract
        self.app.authorization = ("Basic", ("broker", ""))
        activate_contract(self, tender_id, contract_id, owner_token, bid_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all([i["status"] == "complete" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "complete")


def two_lot_1bid_0com_0win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    respose = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(respose.json["data"]["items"])
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(self.days_till_auction_starts)
    self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}} for i in lots]}
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    set_bid_lotvalues(bid_data, [{"id": lot_id} for lot_id in lots])
    self.create_bid(tender_id, bid_data)
    # switch to active.qualification
    self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < get_now() < NEW_DEFENSE_COMPLAINTS_TO
    for lot_id in lots:
        # get awards
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
        # get pending award
        award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
        # set award as unsuccessful
        self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
        patch_data = {"status": "unsuccessful", "qualified": False}
        if self.initial_data['procurementMethodType'] != "simple.defense":
            patch_data["eligible"] = False
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
            {"data": patch_data},
        )
        if not new_defence_complaints:
            # after stand slill period
            self.set_status("complete", {"status": "active.awarded"})
            # time travel
            tender = self.mongodb.tenders.get(tender_id)
            now = get_now().isoformat()
            for i in tender.get("awards", []):
                i["complaintPeriod"] = {"startDate": now, "endDate": now}
            self.mongodb.tenders.save(tender)

    if not new_defence_complaints:
        # check tender status
        self.set_status("complete", {"status": "active.awarded"})
        response = self.check_chronograph()

    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all([i["status"] == "unsuccessful" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def two_lot_1bid_1com_1win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(self.days_till_auction_starts)
    self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}} for i in lots]}
    )
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    set_bid_lotvalues(bid_data, [{"id": lot_id} for lot_id in lots])
    _, bid_token = self.create_bid(tender_id, bid_data)
    # switch to active.qualification
    self.set_status(
        "active.auction", {"lots": [{"auctionPeriod": {"startDate": None}} for i in lots], "status": "active.tendering"}
    )
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    patch_data = {"status": "active", "qualified": True}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = True
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": patch_data},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = get_now().isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid_token)
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    patch_data = {"status": "unsuccessful", "qualified": False}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = False
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": patch_data},
    )
    # after stand still period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # check tender status
    response = self.check_chronograph()
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual([i["status"] for i in response.json["data"]["lots"]], ["complete", "unsuccessful"])
    self.assertEqual(response.json["data"]["status"], "complete")


# 2023-06-16T04:27:46.617458
def two_lot_2bid_on_first_and_1_on_second_awarding(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    self.initial_lots = lots
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    items = deepcopy(response.json["data"]["items"])
    for n, l in enumerate(lots):
        items[n]["relatedLot"] = l
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    start_date = get_now() + timedelta(self.days_till_auction_starts)
    self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": start_date.isoformat()}} for i in lots]}
    )
    # create bids for first lot
    bid_tokens = []
    self.app.authorization = ("Basic", ("broker", ""))
    for i in range(2):
        bid_data = deepcopy(self.test_bids_data[0])
        set_bid_lotvalues(bid_data, [{"id": lot_id} for lot_id in lots[:1]])
        _, bid_token = self.create_bid(tender_id, bid_data)
        bid_tokens.append(bid_token)
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    set_bid_lotvalues(bid_data, [{"id": lot_id} for lot_id in lots[1:]])
    _, bid_token = self.create_bid(tender_id, bid_data)
    bid_tokens.append(bid_token)
    # switch to active.auction
    self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}?acc_token={}".format(tender_id, owner_token))
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    self.assertNotIn("auctionPeriod", response.json["data"]["lots"][1])

    # finish auction
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]

    lot_id = lots[0]
    # posting auction urls
    self.app.patch_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id),
        {
            "data": {
                "lots": [
                    {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
                ],
                "bids": [
                    {
                        "id": i["id"],
                        "lotValues": [
                            {
                                "relatedLot": j["relatedLot"],
                                "participationUrl": "https://tender.auction.url/for_bid/{}".format(i["id"]),
                            }
                            for j in i["lotValues"]
                        ],
                    }
                    for i in auction_bids_data
                ],
            }
        },
    )

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    for bid in response.json["data"]["bids"]:
        if bid["lotValues"][0]["relatedLot"] == lot_id:
            self.assertIn("participationUrl", bid["lotValues"][0])
        else:
            self.assertNotIn("participationUrl", bid["lotValues"][0])

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    self.app.post_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id),
        {
            "data": {
                "bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                    for b in auction_bids_data
                ]
            }
        },
    )

    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))

    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]

    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    patch_data = {"status": "active", "qualified": True}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = True
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": patch_data},
    )

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]

    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid_tokens[0])

    # for SECOND lot
    lot_id = lots[1]
    # get pending award
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]

    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    patch_data = {"status": "active", "qualified": True}
    if self.initial_data['procurementMethodType'] != "simple.defense":
        patch_data["eligible"] = True
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": patch_data},
    )

    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]

    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all([i["status"] == "complete" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "complete")
