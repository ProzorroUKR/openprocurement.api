from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    now,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues


def create_tender_bidder_firm(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    set_bid_lotvalues(bid_data, self.initial_lots)
    bid_data["tenderers"] = [test_tender_below_organization]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "data", "description": "Firm can't create bid"}]
    )


def delete_tender_bidder_eu(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"][0]["value"] = {"amount": 500}
    bid, bid_token = self.create_bid(self.tender_id, bid_data)

    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], bid)

    revisions = self.mongodb.tenders.get(self.tender_id).get("revisions")
    self.assertTrue(any(i for i in revisions[-1]["changes"] if i["op"] == "add" and i["path"] == "/bids"))

    response = self.app.delete("/tenders/{}/bids/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.delete("/tenders/some_id/bids/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    # create new bid
    bid, bid_token = self.create_bid(self.tender_id, bid_data)

    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    bid_data["lotValues"][0]["value"] = {"amount": 100}
    self.create_bid(self.tender_id, bid_data)

    bid_data["lotValues"][0]["value"] = {"amount": 101}
    self.create_bid(self.tender_id, bid_data)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
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
    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for b in auction_bids_data:
        b.pop("status", None)
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    self.set_status("complete")

    # finished tender does not have deleted bid
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
    get_now() + timedelta(days=1),
)
def bids_invalidation_on_tender_change_eu(self):
    bids_access = {}

    for data in deepcopy(self.test_bids_data[:2]):
        data["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
        bid, bid_token = self.create_bid(self.tender_id, data)
        bids_access[bid["id"]] = bid_token

    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")

    # update tender. we can set value that is less than a value in bids as
    # they will be invalidated by this request
    response = self.app.get(f"/tenders/{self.tender_id}")
    items = deepcopy(response.json["data"]["items"])
    items[0]["deliveryDate"]["startDate"] = get_now().isoformat()
    items[0]["deliveryDate"]["endDate"] = (get_now() + timedelta(days=2)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"items": items}}
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
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, bid_id, doc_resource, token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    # check that tender status change does not invalidate bids
    # submit one more bid. check for invalid value first
    test_bid = deepcopy(self.test_bids_data[0])
    test_bid["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    test_bid["lotValues"][0]["value"] = {"amount": 3000}

    # and submit valid bid
    data = deepcopy(self.test_bids_data[0])
    data["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    data["lotValues"][0]["value"]["amount"] = 299
    bid, valid_bid_token = self.create_bid(self.tender_id, data)
    valid_bid_id = bid["id"]
    valid_bid_date = bid["date"]

    test_bid["lotValues"][0]["value"] = {"amount": 101}

    self.create_bid(self.tender_id, test_bid)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
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
    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for b in auction_bids_data:
        b.pop("status", None)
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
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
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    # tender should display all bids
    self.assertEqual(len(response.json["data"]["bids"]), 4)
    self.assertEqual(response.json["data"]["bids"][2]["date"], valid_bid_date)
    # invalidated bids should show only 'id' and 'status' fields
    for bid in response.json["data"]["bids"]:
        if bid["status"] == "invalid":
            self.assertTrue("id" in bid)
            self.assertTrue("lotValues" in bid)
            self.assertFalse("value" in bid["lotValues"][0])
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)

    # invalidated bids stay invalidated
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")
        # invalidated bids displays only 'id' and 'status' fields
        self.assertTrue("lotValues" in response.json["data"])
        self.assertFalse("value" in response.json["data"]["lotValues"][0])
        self.assertFalse("tenderers" in response.json["data"])
        self.assertFalse("date" in response.json["data"])

    # and valid bid is not invalidated
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, valid_bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    # and displays all his data
    self.assertTrue("lotValues" in response.json["data"])
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
            self.assertTrue("lotValues" in bid)
            self.assertFalse("value" in bid["lotValues"][0])
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)
        else:  # valid bid
            self.assertEqual(bid["status"], "active")
            self.assertTrue("lotValues" in bid)
            self.assertTrue("value" in bid["lotValues"][0])
            self.assertTrue("tenderers" in bid)
            self.assertTrue("date" in bid)


def ukrainian_author_id(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    multilingual_author = bid_data["tenderers"][0]
    multilingual_author["identifier"]["id"] = "Українська мова"
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

    set_bid_lotvalues(bid_data, self.initial_lots)
    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    self.assertEqual(bid["tenderers"][0]["name"], self.test_bids_data[0]["tenderers"][0]["name"])
    self.assertIn("id", bid)

    self.set_status("complete")
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
            "title": "Потужність всмоктування",
            "title_en": "Air Intake",
            "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.05, "title": "До 1000 Вт"}, {"value": 0.1, "title": "Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": "Відстрочка платежу",
            "title_en": "Postponement of payment",
            "description": "Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": "До 90 днів"}, {"value": 0.1, "title": "Більше 90 днів"}],
        },
    ]
    self.create_tender(initial_data=data)

    test_features_bids = deepcopy(self.test_bids_data[:2])
    test_features_bids[0]["parameters"] = [{"code": i["code"], "value": 0.05} for i in data["features"]]
    test_features_bids[1]["parameters"] = [{"code": i["code"], "value": 0.05} for i in data["features"]]
    test_features_bids[1]["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    test_features_bids[1]["status"] = "pending"

    for i in test_features_bids:
        set_bid_lotvalues(i, self.initial_lots)
        bid, bid_token = self.create_bid(self.tender_id, i)
        i["status"] = "pending"
        i["lotValues"][0]["status"] = "pending"
        bid.pop("date")
        bid.pop("id")
        bid.pop("submissionDate")
        bid["lotValues"][0].pop("date")
        bid["lotValues"][0]["value"]["amount"] = int(bid["lotValues"][0]["value"]["amount"])
        self.assertEqual(bid, i)


# TenderStage2EUBidDocumentResourceTest


def create_tender_bidder_document_nopending_eu(self):
    test_bid = deepcopy(self.test_bids_data[0])
    test_bid["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    set_bid_lotvalues(test_bid, self.initial_lots)
    bid, token = self.create_bid(self.tender_id, test_bid)
    bid_id = bid["id"]

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
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
    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for b in auction_bids_data:
        b.pop("status", None)
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
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
        "Can't update document because award of bid is not in one of statuses ('active',)",
    )

    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document because award of bid is not in one of statuses ('active',)",
    )

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add document because award of bid is not in one of statuses ('active',)",
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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    request_path = "/tenders/{}/bids".format(self.tender_id)
    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Content-Type header should be one of ['application/json']",
                "location": "header",
                "name": "Content-Type",
            }
        ],
    )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Expecting value: line 1 column 1 (char 0)", "location": "body", "name": "data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
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
                "description": {
                    "identifier": ["Please use a mapping for this field or Identifier instance instead of str."]
                },
                "location": "body",
                "name": "tenderers",
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
                "description": [
                    {
                        "contactPoint": ["This field is required."],
                        "identifier": {"scheme": ["This field is required."], "id": ["This field is required."]},
                        "name": ["This field is required."],
                        "address": ["This field is required."],
                        "scale": ["This field is required."],
                    }
                ],
                "location": "body",
                "name": "tenderers",
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
                "description": [
                    {
                        "contactPoint": ["This field is required."],
                        "identifier": {
                            "scheme": ["This field is required."],
                            "id": ["This field is required."],
                            "uri": ["Not a well formed URL."],
                        },
                        "address": ["This field is required."],
                        "scale": ["This field is required."],
                    }
                ],
                "location": "body",
                "name": "tenderers",
            }
        ],
    )

    bid_data = deepcopy(self.test_bids_data[0])
    set_bid_lotvalues(bid_data, self.initial_lots)
    del bid_data["lotValues"][0]["value"]
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
        [{"description": [{"value": ["This field is required."]}], "location": "body", "name": "lotValues"}],
    )

    bid_data["lotValues"][0]["value"] = {"amount": 500, "valueAddedTaxIncluded": False}
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
                "description": [
                    {
                        "value": [
                            "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot"
                        ]
                    }
                ],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    bid_data["lotValues"][0]["value"] = {"amount": 500, "currency": "USD"}
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
                "description": [{"value": ["currency of bid should be identical to currency of value of lot"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    bid_data["lotValues"][0]["value"] = {"amount": 500}
    bid_data["tenderers"] = self.test_bids_data[0]["tenderers"][0]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("invalid literal for int() with base 10", response.json["errors"][0]["description"])

    bid_data["tenderers"] = [test_tender_below_organization]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "data", "description": "Firm can't create bid"}]
    )


def create_tender_bidder_ua(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    set_bid_lotvalues(bid_data, self.initial_lots)
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
    tender = self.mongodb.tenders.get(self.tender_id)
    tender["tenderPeriod"] = {
        "startDate": (now + timedelta(days=1)).isoformat(),
        "endDate": (now + timedelta(days=17)).isoformat(),
    }
    self.mongodb.tenders.save(tender)

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


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
    get_now() + timedelta(days=1),
)
def bids_invalidation_on_tender_change_ua(self):
    bids_access = {}

    # submit bids
    for data in deepcopy(self.test_bids_data[:2]):
        data["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
        set_bid_lotvalues(data, self.initial_lots)
        bid, bid_token = self.create_bid(self.tender_id, data)
        bids_access[bid["id"]] = bid_token

    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")

    # update tender. we can set value that is less than a value in bids as
    # they will be invalidated by this request
    response = self.app.get(f"/tenders/{self.tender_id}")
    items = deepcopy(response.json["data"]["items"])
    items[0]["deliveryDate"]["startDate"] = get_now().isoformat()
    items[0]["deliveryDate"]["endDate"] = (get_now() + timedelta(days=2)).isoformat()
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"items": items}}
    )

    # check bids status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")

    # check that tender status change does not invalidate bids
    # submit one more bid. check for invalid value first
    test_bid = deepcopy(self.test_bids_data[0])
    set_bid_lotvalues(test_bid, self.initial_lots)
    test_bid["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    test_bid["lotValues"][0]["value"]["amount"] = 3000

    # and submit valid bid
    data = deepcopy(self.test_bids_data[0])
    data["value"]["amount"] = 299
    set_bid_lotvalues(data, self.initial_lots)
    bid, bid_token = self.create_bid(self.tender_id, data)
    valid_bid_id = bid["id"]

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
            self.assertTrue("lotValues" in bid)
            self.assertFalse("value" in bid["lotValues"][0])
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)

    # invalidated bids stay invalidated
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")
        # invalidated bids displays only 'id' and 'status' fields
        self.assertTrue("lotValues" in response.json["data"])
        self.assertFalse("value" in response.json["data"]["lotValues"][0])
        self.assertFalse("tenderers" in response.json["data"])
        self.assertFalse("date" in response.json["data"])

    # and valid bid is not invalidated
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, valid_bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    # and displays all his data
    self.assertTrue("value" in response.json["data"]["lotValues"][0])
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
            self.assertTrue("lotValues" in bid)
            self.assertFalse("value" in bid["lotValues"][0])
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)
        else:  # valid bid
            self.assertEqual(bid["status"], "active")
            self.assertTrue("lotValues" in bid)
            self.assertTrue("value" in bid["lotValues"][0])
            self.assertTrue("tenderers" in bid)
            self.assertTrue("date" in bid)


def bids_activation_on_tender_documents_ua(self):
    bids_access = {}

    # submit bids
    for data in deepcopy(self.test_bids_data):
        data["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
        set_bid_lotvalues(data, self.initial_lots)
        bid, bid_token = self.create_bid(self.tender_id, data)
        bids_access[bid["id"]] = bid_token
    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "укрґ.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
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
            "title": "Потужність всмоктування",
            "title_en": "Air Intake",
            "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.05, "title": "До 1000 Вт"}, {"value": 0.1, "title": "Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": "Відстрочка платежу",
            "title_en": "Postponement of payment",
            "description": "Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": "До 90 днів"}, {"value": 0.1, "title": "Більше 90 днів"}],
        },
    ]
    self.create_tender(initial_data=data)
    test_features_bids = deepcopy(self.test_bids_data[:2])
    test_features_bids[0]["parameters"] = [{"code": i["code"], "value": 0.05} for i in data["features"]]
    test_features_bids[1]["parameters"] = [{"code": i["code"], "value": 0.05} for i in data["features"]]
    test_features_bids[1]["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    test_features_bids[1]["status"] = "pending"
    for i in test_features_bids:
        set_bid_lotvalues(i, self.initial_lots)
        bid, bid_token = self.create_bid(self.tender_id, i)
        i["status"] = "pending"
        i["lotValues"][0]["status"] = "pending"
        bid.pop("date")
        bid.pop("id")
        bid.pop("submissionDate")
        bid["lotValues"][0]["value"]["amount"] = int(bid["lotValues"][0]["value"]["amount"])
        bid["lotValues"][0].pop("date")
        self.assertEqual(bid, i)


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
            "title": "Потужність всмоктування",
            "title_en": "Air Intake",
            "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.05, "title": "До 1000 Вт"}, {"value": 0.1, "title": "Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": "Відстрочка платежу",
            "title_en": "Postponement of payment",
            "description": "Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": "До 90 днів"}, {"value": 0.1, "title": "Більше 90 днів"}],
        },
    ]
    self.create_tender(initial_data=tender_data)
    data = deepcopy(self.test_bids_data[0])
    set_bid_lotvalues(data, self.initial_lots)
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["All features parameters is required."], "location": "body", "name": "parameters"}],
    )
    data["parameters"] = [{"code": tender_data["features"][0]["code"], "value": 0.05}]
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["All features parameters is required."], "location": "body", "name": "parameters"}],
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
                "description": ["Parameter code should be uniq for all parameters"],
                "location": "body",
                "name": "parameters",
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
                "description": [{"value": ["value should be one of feature value."]}],
                "location": "body",
                "name": "parameters",
            }
        ],
    )
