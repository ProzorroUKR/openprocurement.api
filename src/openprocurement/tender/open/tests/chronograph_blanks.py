from openprocurement.api.procedure.utils import parse_date
from openprocurement.tender.core.tests.utils import change_auth


def switch_to_unsuccessful_lot_0bid(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertEqual({i["status"] for i in response.json["data"]["lots"]}, {"unsuccessful"})


def set_auction_period_lot_0bid(self):
    start_date = "9999-01-01T00:00:00+00:00"
    data = {"data": {"lots": [{"auctionPeriod": {"startDate": start_date}} for i in self.initial_lots]}}
    response = self.check_chronograph(data)
    self.assertEqual(response.json["data"]["lots"][0]["auctionPeriod"]["startDate"], start_date)

    response = self.check_chronograph({"data": {"lots": [{"auctionPeriod": None}]}})
    self.assertEqual(response.json["data"]["lots"][0]["auctionPeriod"]["startDate"], start_date)


def not_switch_to_unsuccessful_lot_1bid(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertEqual(len(response.json["data"]["awards"]), 1)


def not_switch_to_unsuccessful_2lot_1bid(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertEqual(len(response.json["data"]["awards"]), 2)


def switch_to_auction_lot(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")


def switch_to_unsuccessful_lot(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()

    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        for lot in response.json["data"]["lots"]:
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, lot["id"]),
                {
                    "data": {
                        "bids": [
                            {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                            for b in auction_bids_data
                        ]
                    }
                },
            )
            self.assertEqual(response.status, "200 OK")

    self.assertEqual(response.json["data"]["status"], "active.qualification")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    while any(i["status"] == "pending" for i in response.json["data"]):
        award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
            {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        )
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def set_auction_period_lot(self):
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    item = response.json["data"]["lots"][0]
    self.assertIn("auctionPeriod", item)
    self.assertIn("shouldStartAfter", item["auctionPeriod"])
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertEqual(
        parse_date(response.json["data"]["next_check"]), parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    start_date = "9999-01-01T00:00:00+00:00"
    data = {"data": {"lots": [{"auctionPeriod": {"startDate": start_date}} for i in self.initial_lots]}}
    response = self.check_chronograph(data)
    item = response.json["data"]["lots"][0]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(item["auctionPeriod"]["startDate"], start_date)
