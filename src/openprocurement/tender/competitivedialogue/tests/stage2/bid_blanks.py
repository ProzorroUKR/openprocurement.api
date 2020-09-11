# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta

from openprocurement.tender.belowthreshold.tests.base import test_organization, now

# TenderStage2EUBidResourceTest


def create_tender_bidder_firm(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    bid_data["tenderers"] = [test_organization]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"location": u"body", "name": u"data", "description": u"Firm can't create bid"}]
    )


def delete_tender_bidder_eu(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["id"], bid["id"])
    self.assertEqual(response.json["data"]["status"], "deleted")
    # deleted bid does not contain bid information
    self.assertFalse("value" in response.json["data"])
    self.assertFalse("tenderers" in response.json["data"])
    self.assertFalse("date" in response.json["data"])

    # try to add documents to bid
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, bid["id"], doc_resource, bid_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can't add document at 'deleted' bid status")

    revisions = self.db.get(self.tender_id).get("revisions")
    self.assertTrue(any([i for i in revisions[-2][u"changes"] if i["op"] == u"remove" and i["path"] == u"/bids"]))
    self.assertTrue(
        any([i for i in revisions[-1][u"changes"] if i["op"] == u"replace" and i["path"] == u"/bids/0/status"])
    )

    response = self.app.delete("/tenders/{}/bids/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"bid_id"}])

    response = self.app.delete("/tenders/some_id/bids/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    # create new bid
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["id"], bid["id"])
    self.assertEqual(response.json["data"]["status"], "deleted")

    bid_data["value"] = {"amount": 100}
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )

    bid_data["value"] = {"amount": 101}
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.app.authorization = ("Basic", ("token", ""))
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {"bids": auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    self.app.authorization = ("Basic", ("token", ""))
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

    # sign contract
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]
    self.app.authorization = ("Basic", ("token", ""))
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": {"valueAddedTaxIncluded": False}}},
    )
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")

    # finished tender does not show deleted bid info
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["bids"]), 4)
    bid_data = response.json["data"]["bids"][1]
    self.assertEqual(bid_data["id"], bid["id"])
    self.assertEqual(bid_data["status"], "deleted")
    self.assertFalse("value" in bid_data)
    self.assertFalse("tenderers" in bid_data)
    self.assertFalse("date" in bid_data)


def bids_invalidation_on_tender_change_eu(self):
    bids_access = {}

    for data in deepcopy(self.test_bids_data[:2]):
        data["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        bids_access[response.json["data"]["id"]] = response.json["access"]["token"]

    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")

    # update tender. we can set value that is less than a value in bids as
    # they will be invalidated by this request
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"amount": 300.0}, "minimalStep": {"amount": 9.0}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 500)

    # check bids status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")
    # try to add documents to bid
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, bid_id, doc_resource, token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can't add document at 'invalid' bid status")

    # check that tender status change does not invalidate bids
    # submit one more bid. check for invalid value first
    test_bid = deepcopy(self.test_bids_data[0])
    test_bid["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    test_bid["value"] = {"amount": 3000}
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": test_bid}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"value of bid should be less than value of tender"],
                u"location": u"body",
                u"name": u"value",
            }
        ],
    )
    # and submit valid bid
    data = deepcopy(self.test_bids_data[0])
    data["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    data["value"]["amount"] = 299
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
    self.assertEqual(response.status, "201 Created")
    valid_bid_id = response.json["data"]["id"]
    valid_bid_token = response.json["access"]["token"]
    valid_bid_date = response.json["data"]["date"]

    test_bid["value"] = {"amount": 101}

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": test_bid},
    )

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.app.authorization = ("Basic", ("token", ""))
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, valid_bid_id, valid_bid_token))
    self.assertEqual(response.json["data"]["status"], "active")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json(
        "/tenders/{}".format(self.tender_id), {"data": {"status": "active.pre-qualification.stand-still"}}
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {"bids": auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    # tender should display all bids
    self.assertEqual(len(response.json["data"]["bids"]), 4)
    self.assertEqual(response.json["data"]["bids"][2]["date"], valid_bid_date)
    # invalidated bids should show only 'id' and 'status' fields
    for bid in response.json["data"]["bids"]:
        if bid["status"] == "invalid":
            self.assertTrue("id" in bid)
            self.assertFalse("value" in bid)
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)

    # invalidated bids stay invalidated
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")
        # invalidated bids displays only 'id' and 'status' fields
        self.assertFalse("value" in response.json["data"])
        self.assertFalse("tenderers" in response.json["data"])
        self.assertFalse("date" in response.json["data"])

    # and valid bid is not invalidated
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, valid_bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    # and displays all his data
    self.assertTrue("value" in response.json["data"])
    self.assertTrue("tenderers" in response.json["data"])
    self.assertTrue("date" in response.json["data"])

    # check bids availability on finished tender
    self.set_status("complete")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]["bids"]), 4)
    for bid in response.json["data"]["bids"]:
        if bid["id"] in bids_access:  # previously invalidated bids
            self.assertEqual(bid["status"], "invalid")
            self.assertFalse("value" in bid)
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)
        else:  # valid bid
            self.assertEqual(bid["status"], "active")
            self.assertTrue("value" in bid)
            self.assertTrue("tenderers" in bid)
            self.assertTrue("date" in bid)


def ukrainian_author_id(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    multilingual_author = bid_data["tenderers"][0]
    multilingual_author["identifier"]["id"] = u"Українська мова"
    data = self.initial_data.copy()
    data["shortlistedFirms"][0] = {
        "identifier": {
            "scheme": multilingual_author["identifier"]["scheme"],
            "id": multilingual_author["identifier"]["id"],
            "uri": multilingual_author["identifier"]["uri"],
        },
        "name": "Test org name 1",
    }
    self.create_tender(initial_data=data)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], self.test_bids_data[0]["tenderers"][0]["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])

    for status in ("active", "unsuccessful", "deleted", "invalid"):
        bid_data["status"] = status
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")

    self.set_status("complete")
    del bid_data["status"]
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (complete) tender status")


# TenderStage2EUBidFeaturesResourceTest


def features_bidder_eu(self):
    data = self.initial_data.copy()
    item = data["items"][0].copy()
    item["id"] = "1"
    data["items"] = [item]
    data["features"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": "1",
            "title": u"Потужність всмоктування",
            "title_en": u"Air Intake",
            "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.05, "title": u"До 1000 Вт"}, {"value": 0.1, "title": u"Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
            "title_en": u"Postponement of payment",
            "description": u"Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": u"До 90 днів"}, {"value": 0.1, "title": u"Більше 90 днів"}],
        },
    ]
    self.create_tender(initial_data=data)

    test_features_bids = deepcopy(self.test_bids_data[:2])
    test_features_bids[0]["parameters"] = [{"code": i["code"], "value": 0.05} for i in data["features"]]
    test_features_bids[1]["parameters"] = [{"code": i["code"], "value": 0.05} for i in data["features"]]
    test_features_bids[1]["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    test_features_bids[1]["status"] = "pending"

    for i in test_features_bids:
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": i})
        i["status"] = "pending"
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        bid = response.json["data"]
        bid.pop(u"date")
        bid.pop(u"id")
        self.assertEqual(bid, i)


# TenderStage2EUBidDocumentResourceTest


def create_tender_bidder_document_nopending_eu(self):
    test_bid = deepcopy(self.test_bids_data[0])
    test_bid["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": test_bid})
    bid = response.json["data"]
    token = response.json["access"]["token"]
    bid_id = bid["id"]

    response = self.app.post(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.app.authorization = ("Basic", ("token", ""))
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json(
        "/tenders/{}".format(self.tender_id), {"data": {"status": "active.pre-qualification.stand-still"}}
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {"bids": auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document because award of bid is not active",
    )

    response = self.app.put(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, token),
        "content3",
        content_type="application/msword",
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document because award of bid is not active",
    )

    response = self.app.post(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add document because award of bid is not active",
    )


# TenderStage2UABidResourceTest


def create_tender_biddder_invalid_ua(self):
    response = self.app.post_json(
        "/tenders/some_id/bids",
        {"data": {"tenderers": self.test_bids_data[0]["tenderers"], "value": {"amount": 500}}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    request_path = "/tenders/{}/bids".format(self.tender_id)
    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Content-Type header should be one of ['application/json']",
                u"location": u"header",
                u"name": u"Content-Type",
            }
        ],
    )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"No JSON object could be decoded", u"location": u"body", u"name": u"data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"selfEligible": True, "selfQualified": True, "tenderers": [{"identifier": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {
                    u"identifier": [u"Please use a mapping for this field or Identifier instance instead of unicode."]
                },
                u"location": u"body",
                u"name": u"tenderers",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"selfEligible": True, "selfQualified": True, "tenderers": [{"identifier": {}}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [
                    {
                        u"contactPoint": [u"This field is required."],
                        u"identifier": {u"scheme": [u"This field is required."], u"id": [u"This field is required."]},
                        u"name": [u"This field is required."],
                        u"address": [u"This field is required."],
                    }
                ],
                u"location": u"body",
                u"name": u"tenderers",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "selfEligible": True,
                "selfQualified": True,
                "tenderers": [{"name": "name", "identifier": {"uri": "invalid_value"}}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [
                    {
                        u"contactPoint": [u"This field is required."],
                        u"identifier": {
                            u"scheme": [u"This field is required."],
                            u"id": [u"This field is required."],
                            u"uri": [u"Not a well formed URL."],
                        },
                        u"address": [u"This field is required."],
                    }
                ],
                u"location": u"body",
                u"name": u"tenderers",
            }
        ],
    )

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"value"}],
    )

    bid_data["value"] = {"amount": 500, "valueAddedTaxIncluded": False}
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [
                    u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of tender"
                ],
                u"location": u"body",
                u"name": u"value",
            }
        ],
    )

    bid_data["value"] = {"amount": 500, "currency": "USD"}
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"currency of bid should be identical to currency of value of tender"],
                u"location": u"body",
                u"name": u"value",
            }
        ],
    )

    bid_data["value"] = {"amount": 500}
    bid_data["tenderers"] = self.test_bids_data[0]["tenderers"][0]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(u"invalid literal for int() with base 10", response.json["errors"][0]["description"])

    bid_data["tenderers"] = [test_organization]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"location": u"body", "name": u"data", "description": u"Firm can't create bid"}]
    )


def create_tender_bidder_ua(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], self.test_bids_data[0]["tenderers"][0]["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])

    # set tender period in future
    data = deepcopy(self.initial_data)
    tenderPeriod = {
        "startDate": (now + timedelta(days=1)).isoformat(),
        "endDate": (now + timedelta(days=17)).isoformat(),
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"tenderPeriod": tenderPeriod}}
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Bid can be added only during the tendering period", response.json["errors"][0]["description"])

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (complete) tender status")


def bids_invalidation_on_tender_change_ua(self):
    bids_access = {}

    # submit bids
    for data in self.test_bids_data[:2]:
        data["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        bids_access[response.json["data"]["id"]] = response.json["access"]["token"]

    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    # update tender. we can set value that is less than a value in bids as
    # they will be invalidated by this request
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"amount": 300.0}, "minimalStep": {"amount": 9.0}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 500)

    # check bids status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")

    # check that tender status change does not invalidate bids
    # submit one more bid. check for invalid value first
    test_bid = deepcopy(self.test_bids_data[0])
    test_bid["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    test_bid["value"]["amount"] = 3000
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": test_bid}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"value of bid should be less than value of tender"],
                u"location": u"body",
                u"name": u"value",
            }
        ],
    )
    # and submit valid bid
    data = deepcopy(self.test_bids_data[0])
    data["value"]["amount"] = 299
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
    self.assertEqual(response.status, "201 Created")
    valid_bid_id = response.json["data"]["id"]

    # change tender status
    self.set_status("active.qualification")

    # check tender status
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    # tender should display all bids
    self.assertEqual(len(response.json["data"]["bids"]), 3)
    # invalidated bids should show only 'id' and 'status' fields
    for bid in response.json["data"]["bids"]:
        if bid["status"] == "invalid":
            self.assertTrue("id" in bid)
            self.assertFalse("value" in bid)
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)

    # invalidated bids stay invalidated
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")
        # invalidated bids displays only 'id' and 'status' fields
        self.assertFalse("value" in response.json["data"])
        self.assertFalse("tenderers" in response.json["data"])
        self.assertFalse("date" in response.json["data"])

    # and valid bid is not invalidated
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, valid_bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    # and displays all his data
    self.assertTrue("value" in response.json["data"])
    self.assertTrue("tenderers" in response.json["data"])
    self.assertTrue("date" in response.json["data"])

    # check bids availability on finished tender
    self.set_status("complete")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]["bids"]), 3)
    for bid in response.json["data"]["bids"]:
        if bid["id"] in bids_access:  # previously invalidated bids
            self.assertEqual(bid["status"], "invalid")
            self.assertFalse("value" in bid)
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)
        else:  # valid bid
            self.assertEqual(bid["status"], "active")
            self.assertTrue("value" in bid)
            self.assertTrue("tenderers" in bid)
            self.assertTrue("date" in bid)


def bids_activation_on_tender_documents_ua(self):
    bids_access = {}

    # submit bids
    for data in deepcopy(self.test_bids_data):
        data["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        bids_access[response.json["data"]["id"]] = response.json["access"]["token"]
    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.post(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        upload_files=[("file", u"укр.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")


# TenderStage2UABidFeaturesResourceTest


def features_bidder_ua(self):
    data = self.initial_data.copy()
    item = data["items"][0].copy()
    item["id"] = "1"
    data["items"] = [item]
    data["features"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": "1",
            "title": u"Потужність всмоктування",
            "title_en": u"Air Intake",
            "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.05, "title": u"До 1000 Вт"}, {"value": 0.1, "title": u"Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
            "title_en": u"Postponement of payment",
            "description": u"Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": u"До 90 днів"}, {"value": 0.1, "title": u"Більше 90 днів"}],
        },
    ]
    self.create_tender(initial_data=data)
    test_features_bids = deepcopy(self.test_bids_data[:2])
    test_features_bids[0]["parameters"] = [{"code": i["code"], "value": 0.05} for i in data["features"]]
    test_features_bids[1]["parameters"] = [{"code": i["code"], "value": 0.05} for i in data["features"]]
    test_features_bids[1]["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    test_features_bids[1]["status"] = "active"
    for i in test_features_bids:
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": i})
        i["status"] = "active"
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        bid = response.json["data"]
        bid.pop(u"date")
        bid.pop(u"id")
        self.assertEqual(bid, i)


# TenderStage2UABidDocumentResourceTest


def put_tender_bidder_document_ua(self):
    response = self.app.post(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.put(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?{}&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content2")

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        "content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?{}&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content3")

    self.set_status("active.awarded")

    response = self.app.put(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        upload_files=[("file", "name.doc", "content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document because award of bid is not active",
    )


# TenderStage2BidResourceTest


def deleted_bid_is_not_restorable(self):

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["id"], bid["id"])
    self.assertEqual(response.json["data"]["status"], "deleted")

    # try to restore deleted bid
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid in (deleted) status")

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "deleted")


# TenderStage2BidFeaturesResourceTest


def features_bidder_invalid(self):
    tender_data = self.initial_data.copy()
    item = tender_data["items"][0].copy()
    item["id"] = "1"
    tender_data["items"] = [item]
    tender_data["features"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": "1",
            "title": u"Потужність всмоктування",
            "title_en": u"Air Intake",
            "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.05, "title": u"До 1000 Вт"}, {"value": 0.1, "title": u"Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
            "title_en": u"Postponement of payment",
            "description": u"Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": u"До 90 днів"}, {"value": 0.1, "title": u"Більше 90 днів"}],
        },
    ]
    self.create_tender(initial_data=tender_data)
    data = deepcopy(self.test_bids_data[0])
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"parameters"}],
    )
    data["parameters"] = [{"code": tender_data["features"][0]["code"], "value": 0.05}]
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"All features parameters is required."], u"location": u"body", u"name": u"parameters"}],
    )
    data["parameters"].append({"code": tender_data["features"][0]["code"], "value": 0.05})
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Parameter code should be uniq for all parameters"],
                u"location": u"body",
                u"name": u"parameters",
            }
        ],
    )
    data["parameters"][1]["code"] = tender_data["features"][0]["code"]
    data["parameters"][1]["value"] = 0.2
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"value": [u"value should be one of feature value."]}],
                u"location": u"body",
                u"name": u"parameters",
            }
        ],
    )
