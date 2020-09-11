# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime, timedelta
from openprocurement.tender.cfaua.constants import CLARIFICATIONS_UNTIL_PERIOD
from openprocurement.tender.cfaua.tests.base import agreement_period
from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.utils import get_now


extra = {"agreements": [{"contracts": [{"unitPrices": [{"value": {"amount": 0}}]}] * 3}]}


def get_tender_bidder(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)
    for _ in range(self.min_bids_number - 1):
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": initial_bids[0]})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": initial_bids[0]})

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bid in current (active.tendering) tender status"
    )

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], bid)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", extra={"id": self.tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(set(b.keys()), set(["id", "status", "tenderers"]))

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(set(response.json["data"].keys()), set(["id", "status", "tenderers"]))

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

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(set(b.keys()), set(["id", "status", "tenderers"]))

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(set(response.json["data"].keys()), set(["id", "status", "tenderers"]))

    # switch to active.auction
    self.set_status("active.auction", extra={"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(set(b.keys()), set(["id", "status", "tenderers"]))

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(set(response.json["data"].keys()), set(["id", "status", "tenderers"]))

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {"bids": auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(
            set(b.keys()), set([u"date", u"status", u"id", u"value", u"tenderers", "selfEligible", "selfQualified"])
        )

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set([u"date", u"status", u"id", u"value", u"tenderers", "selfEligible", "selfQualified"]),
    )

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

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(
            set(b.keys()), set([u"date", u"status", u"id", u"value", u"tenderers", "selfEligible", "selfQualified"])
        )

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set([u"date", u"status", u"id", u"value", u"tenderers", "selfEligible", "selfQualified"]),
    )

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

    # sign agreement
    response = self.app.get("/tenders/{}".format(self.tender_id))
    agreement_id = response.json["data"]["agreements"][-1]["id"]
    self.app.authorization = ("Basic", ("token", ""))
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(
            set(b.keys()), set([u"date", u"status", u"id", u"value", u"tenderers", "selfEligible", "selfQualified"])
        )

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set([u"date", u"status", u"id", u"value", u"tenderers", "selfEligible", "selfQualified"]),
    )


def bids_invalidation_on_tender_change(self):
    bids_access = {}
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    # submit bids
    for data in initial_bids:
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
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, self.initial_lots[0]["id"], self.tender_token),
        {"data": {"value": {"amount": 300.0}, "minimalStep": {"amount": 9.0}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 300)

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
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": initial_bids[0]}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"value": [u"value of bid should be less than value of lot"]}],
                u"location": u"body",
                u"name": u"lotValues",
            }
        ],
    )
    # and submit valid bid
    data = initial_bids[0]
    data["lotValues"][0]["value"]["amount"] = 299
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
    self.assertEqual(response.status, "201 Created")
    valid_bid_id = response.json["data"]["id"]
    valid_bid_token = response.json["access"]["token"]
    valid_bid_date = response.json["data"]["date"]

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": {"amount": 101}, "relatedLot": self.initial_lots[0]["id"]}]

    for i in range(1, self.min_bids_number):
        bid_data["tenderers"] = initial_bids[i]["tenderers"]
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )

    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
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
    self.set_status("active.pre-qualification.stand-still", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    # tender should display all bids
    self.assertEqual(len(response.json["data"]["bids"]), self.min_bids_number * 2)
    self.assertEqual(response.json["data"]["bids"][self.min_bids_number]["date"], valid_bid_date)
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
    self.assertTrue("value" in response.json["data"]["lotValues"][0])
    self.assertTrue("tenderers" in response.json["data"])
    self.assertTrue("date" in response.json["data"]["lotValues"][0])

    # check bids availability on finished tender
    self.set_status("complete")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]["bids"]), self.min_bids_number * 2)
    for bid in response.json["data"]["bids"]:
        if bid["id"] in bids_access:  # previously invalidated bids
            self.assertEqual(bid["status"], "invalid")
            self.assertFalse("value" in bid)
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)
        else:  # valid bid
            self.assertEqual(bid["status"], "active")
            self.assertTrue("value" in bid["lotValues"][0])
            self.assertTrue("tenderers" in bid)
            self.assertTrue("date" in bid["lotValues"][0])


def get_tender_tenderers(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": initial_bids[0]})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    response = self.app.get("/tenders/{}/bids".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bids in current (active.tendering) tender status"
    )
    for _ in range(self.min_bids_number - 1):
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": initial_bids[0]})

    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
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
    self.set_status("active.pre-qualification.stand-still", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    bid_data = response.json["data"][0]
    self.assertEqual(bid_data["id"], bid["id"])
    self.assertEqual(bid_data["status"], "active")
    self.assertTrue("value" in bid_data["lotValues"][0])
    self.assertTrue("tenderers" in bid_data)
    self.assertTrue("date" in bid_data["lotValues"][0])

    response = self.app.get("/tenders/some_id/bids", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def get_tender_bidder_document(self):

    doc_id_by_type = {}

    def document_is_unaccessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker4", ""))
        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, resource), status=403)
        self.assertEqual(response.status, "403 Forbidden")
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, resource, doc_id), status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.app.authorization = orig_auth

    def document_is_unaccessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, resource, doc_id, self.tender_token
            ),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.app.authorization = orig_auth

    def all_documents_are_accessible_for_bid_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        for resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            response = self.app.get(
                "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, self.bid_token)
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(len(response.json["data"]), 2)
            doc1 = response.json["data"][0]
            doc2 = response.json["data"][1]
            self.assertEqual(doc1["title"], "name_{}.doc".format(resource[:-1]))
            self.assertEqual(doc2["title"], "name_{}_private.doc".format(resource[:-1]))
            self.assertEqual(doc1["confidentiality"], u"public")
            self.assertEqual(doc2["confidentiality"], u"buyerOnly")
            self.assertIn("url", doc1)
            self.assertIn("url", doc2)
            doc_id = doc_id_by_type[resource]["id"]
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                    self.tender_id, self.bid_id, resource, doc_id, self.bid_token
                )
            )
            self.assertEqual(response.status, "200 OK")
            self.assertIn("previousVersions", response.json["data"])
            doc = response.json["data"]
            del doc["previousVersions"]
            self.assertEqual(doc, doc1)
            doc_id = doc_id_by_type[resource + "private"]["id"]
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                    self.tender_id, self.bid_id, resource, doc_id, self.bid_token
                )
            )
            self.assertEqual(response.status, "200 OK")
            self.assertIn("previousVersions", response.json["data"])
            doc = response.json["data"]
            del doc["previousVersions"]
            self.assertEqual(doc, doc2)
        self.app.authorization = orig_auth

    def documents_are_accessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        token = self.tender_token
        response = self.app.get(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, token)
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(len(response.json["data"]), 2)
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, doc_id, token)
        )
        self.assertIn("url", response.json["data"])
        self.assertEqual(response.status, "200 OK")
        doc_id = doc_id_by_type[resource + "private"]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, doc_id, token)
        )
        self.assertEqual(response.status, "200 OK")
        self.assertIn("url", response.json["data"])

    def public_documents_are_accessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))

        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, resource))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(len(response.json["data"]), 2)
        self.assertIn(doc_id_by_type[resource]["key"], response.json["data"][0]["url"])
        self.assertNotIn("url", response.json["data"][1])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, resource, doc_id_by_type[resource]["id"])
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], "name_{}.doc".format(resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], u"public")
        self.assertEqual(response.json["data"]["format"], u"application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(
                self.tender_id, self.bid_id, resource, doc_id_by_type[resource + "private"]["id"]
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["confidentiality"], u"buyerOnly")
        self.assertNotIn("url", response.json["data"])

        self.app.authorization = orig_auth

    def all_public_documents_are_accessible_for_others():
        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            public_documents_are_accessible_for_others(doc_resource)

    def documents_accessible_from_tender_view():
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))

        for doc_resource in ["documents", "financialDocuments", "eligibilityDocuments", "qualificationDocuments"]:
            response = self.app.get("/tenders/{}".format(self.tender_id))

            data = response.json["data"]
            bid_documents = data["bids"][0][doc_resource]
            self.assertIn("url", bid_documents[0])
            self.assertNotIn("url", bid_documents[1])

            response = self.app.get(
                "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token)
            )

            data = response.json["data"]
            bid_documents = data["bids"][0][doc_resource]
            self.assertIn("url", bid_documents[0])
            self.assertIn("url", bid_documents[1])

            response = self.app.get(
                "/tenders/{}?acc_token={}".format(self.tender_id, self.bid_token)
            )

            data = response.json["data"]
            bid_documents = data["bids"][0][doc_resource]
            self.assertIn("url", bid_documents[0])
            self.assertIn("url", bid_documents[1])

            response = self.app.get(
                "/tenders/{}?acc_token={}".format(self.tender_id, self.bid2_token)
            )

            data = response.json["data"]
            bid_documents = data["bids"][0][doc_resource]
            self.assertIn("url", bid_documents[0])
            self.assertNotIn("url", bid_documents[1])

            self.app.authorization = orig_auth

    def all_documents_accessible_for_reviewer():
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('reviewer', ''))

        for resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            camel_resource = ''.join(word.title() for word in resource.split('_'))
            camel_resource = camel_resource[:1].lower() + camel_resource[1:]
            response = self.app.get(
                "/tenders/{}".format(self.tender_id)
            )

            data = response.json["data"]
            bid_documents = data["bids"][0][camel_resource]
            self.assertIn("url", bid_documents[0])
            self.assertIn("url", bid_documents[1])

            response = self.app.get(
                "/tenders/{}/bids/{}".format(self.tender_id, self.bid_id)
            )
            data = response.json["data"]
            self.assertIn("url", data[camel_resource][0])
            self.assertIn("url", data[camel_resource][1])

            public_file_id = data[camel_resource][0]["id"]
            confident_file_id = data[camel_resource][1]["id"]

            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, resource, public_file_id)
            )
            self.assertIn("url", response.json["data"])

            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, resource, confident_file_id)
            )
            self.assertIn("url", response.json["data"])

        self.app.authorization = orig_auth


    # active.tendering
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

        # upload private document
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name_{}_private.doc".format(doc_resource[:-1]), "content")],
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}_private.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]
        doc_id_by_type[doc_resource + "private"] = {"id": doc_id, "key": key}
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")

        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )
    self.assertEqual(set(response.json["data"][1].keys()), set(["id", "status", "tenderers"]))
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )

    for doc_resource in ["documents", "eligibility_documents"]:
        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, doc_resource))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(len(response.json["data"]), 2)
        self.assertIn("url", response.json["data"][0])
        self.assertIn(doc_id_by_type[doc_resource]["key"], response.json["data"][0]["url"])
        self.assertNotIn("url", response.json["data"][1])

    for doc_resource in ["documents", "eligibility_documents"]:
        doc_id = doc_id_by_type[doc_resource]["id"]
        response = self.app.get("/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], u"name_{}.doc".format(doc_resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], u"public")
        self.assertEqual(response.json["data"]["format"], u"application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

        doc_id = doc_id_by_type[doc_resource + "private"]["id"]
        response = self.app.get("/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], u"name_{}_private.doc".format(doc_resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], u"buyerOnly")
        self.assertEqual(response.json["data"]["format"], u"application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    self.set_status("active.pre-qualification.stand-still")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )
    self.assertEqual(set(response.json["data"][1].keys()), set(["id", "status", "tenderers"]))
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )
    response = self.app.get("/tenders/{}/bids/{}/documents".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertIn(doc_id_by_type["documents"]["key"], response.json["data"][0]["url"])
    doc_id = doc_id_by_type["documents"]["id"]
    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], u"name_document.doc")
    self.assertEqual(response.json["data"]["confidentiality"], u"public")
    self.assertEqual(response.json["data"]["format"], u"application/msword")
    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to active.auction
    self.set_status("active.auction")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )
    self.assertEqual(set(response.json["data"][1].keys()), set(["id", "status", "tenderers"]))
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )
    response = self.app.get("/tenders/{}/bids/{}/documents".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertIn(doc_id_by_type["documents"]["key"], response.json["data"][0]["url"])
    doc_id = doc_id_by_type["documents"]["id"]
    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], u"name_document.doc")
    self.assertEqual(response.json["data"]["confidentiality"], u"public")
    self.assertEqual(response.json["data"]["format"], u"application/msword")
    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    self.set_status("active.qualification")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    assert_data_1 = {
        u"date",
        u"status",
        u"id",
        u"lotValues",
        u"tenderers",
        u"documents",
        u"eligibilityDocuments",
        u"qualificationDocuments",
        u"financialDocuments",
        u"selfQualified",
    }

    assert_data_2 = {u"date", u"status", u"id", u"lotValues", u"tenderers", u"selfQualified"}

    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        assert_data_1.add(u"selfEligible")
        assert_data_2.add(u"selfEligible")

    self.assertEqual(
        set(response.json["data"][0].keys()),
        assert_data_1,
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        assert_data_2,
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        assert_data_1,
    )

    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()

    # switch to active.awarded
    self.set_status("active.awarded")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        assert_data_1,
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        assert_data_2,
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        assert_data_1,
    )
    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()

    # time travel
    self.set_status("complete")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        assert_data_1,
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        assert_data_2,
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        assert_data_1,
    )
    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()
    documents_accessible_from_tender_view()
    all_documents_accessible_for_reviewer()


def create_tender_bidder_document(self):
    doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]

        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.get(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token)
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id_by_type[doc_resource]["id"], response.json["data"][0]["id"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"][0]["title"])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}?all=true&acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, self.bid_token
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id_by_type[doc_resource]["id"], response.json["data"][0]["id"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"][0]["title"])

        doc_id = doc_id_by_type[doc_resource]["id"]
        key = doc_id_by_type[doc_resource]["key"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download=some_id&acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
        )

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?{}".format(self.tender_id, self.bid_id, doc_resource, doc_id, key), status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't view bid documents in current (active.tendering) tender status",
        )

        if self.docservice:
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?{}&acc_token={}".format(
                    self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token
                )
            )
            self.assertEqual(response.status, "302 Moved Temporarily")
            self.assertIn("http://localhost/get/", response.location)
            self.assertIn("Signature=", response.location)
            self.assertIn("KeyID=", response.location)
            self.assertIn("Expires=", response.location)
        else:
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?{}&acc_token={}".format(
                    self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token
                )
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/msword")
            self.assertEqual(response.content_length, 7)
            self.assertEqual(response.body, "content")

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, doc_resource, doc_id), status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't view bid documents in current (active.tendering) tender status",
        )

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification")

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name.doc", "content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't upload document in current (active.pre-qualification) tender status",
        )

    # list qualifications

    self.set_status("active.pre-qualification.stand-still")

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name.doc", "content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't upload document in current (active.pre-qualification.stand-still) tender status",
        )

    # switch to active.auction
    self.set_status("active.auction")

    self.app.authorization = ("Basic", ("token", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name.doc", "content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't upload document in current (active.auction) tender status"
        )

    # switch to qualification
    self.set_status("active.qualification")

    self.app.authorization = ("Basic", ("token", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name2_{}.doc".format(doc_resource[:-1]), "content")],
        )
        self.assertEqual(response.status, "201 Created")

    # switch to active.awarded
    self.set_status("active.awarded")

    for doc_resource in ["documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid2_id, doc_resource, self.bid_token),
            upload_files=[("file", "name.doc", "content")],
            status=403,
        )

        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    u"location": u"body",
                    u"name": u"data",
                    u"description": u"Can't upload document in current (active.awarded) tender status",
                }
            ],
        )

    response = self.app.post(
        "/tenders/{}/bids/{}/financial_documents?acc_token={}".format(self.tender_id, self.bid2_id, self.bid_token),
        upload_files=[("file", "name.doc", "content")],
        status=201,
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    self.set_status("complete")

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name.doc", "content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't upload document in current (complete) tender status"
        )


def put_tender_bidder_document(self):
    doc_id_by_type = {}
    doc_id_by_type2 = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": response.json["data"]["url"].split("?")[-1].split("=")[-1]}

        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid2_id, doc_resource, self.bid2_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id_by_type2[doc_resource] = {
            "id": response.json["data"]["id"],
            "key": response.json["data"]["url"].split("?")[-1].split("=")[-1],
        }

        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            status=404,
            upload_files=[("invalid_name", "name.doc", "content")],
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}]
        )

        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            upload_files=[("file", "name.doc", "content2")],
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token
            )
        )
        if self.docservice:
            self.assertEqual(response.status, "302 Moved Temporarily")
            self.assertIn("http://localhost/get/", response.location)
            self.assertIn("Signature=", response.location)
            self.assertIn("KeyID=", response.location)
            self.assertIn("Expires=", response.location)
        else:
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/msword")
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, "content2")

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual("name.doc", response.json["data"]["title"])

        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            "content3",
            content_type="application/msword",
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token
            )
        )
        if self.docservice:
            self.assertEqual(response.status, "302 Moved Temporarily")
            self.assertIn("http://localhost/get/", response.location)
            self.assertIn("Signature=", response.location)
            self.assertIn("KeyID=", response.location)
            self.assertIn("Expires=", response.location)
        else:
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/msword")
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, "content3")

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification")

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            upload_files=[("file", "name.doc", "content4")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            u"Can't upload document in current (active.pre-qualification) tender status",
        )

    self.set_status("active.pre-qualification.stand-still")

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            upload_files=[("file", "name.doc", "content4")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't upload document in current (active.pre-qualification.stand-still) tender status",
        )

    # switch to active.auction
    self.set_status("active.auction")

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            upload_files=[("file", "name.doc", "content4")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't upload document in current (active.auction) tender status"
        )

    # switch to qualification
    self.set_status("active.qualification")

    self.app.authorization = ("Basic", ("token", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"]
            ),
            upload_files=[("file", "name.doc", "content4")],
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.awarded
    self.set_status("active.awarded")

    for doc_resource in ["documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}".format(
                self.tender_id, self.bid2_id, doc_resource, doc_id_by_type2[doc_resource]["id"]
            ),
            upload_files=[("file", "name.doc", "content4")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't upload document in current (active.awarded) tender status"
        )

    response = self.app.put(
        "/tenders/{}/bids/{}/financial_documents/{}".format(
            self.tender_id, self.bid2_id, doc_id_by_type2["financial_documents"]["id"]
        ),
        upload_files=[("file", "name.doc", "content4")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.set_status("complete")

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"]
            ),
            upload_files=[("file", "name.doc", "content4")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't upload document in current (complete) tender status"
        )


def delete_tender_bidder(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": initial_bids[0]})
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
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": initial_bids[0]})
    self.assertEqual(response.status, "201 Created")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

    # update tender. we can set value that is less than a value in bid as
    # they will be invalidated by this request
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"value": {"amount": 300.0}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 300)

    # check bid 'invalid' status
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "invalid")

    # try to delete 'invalid' bid
    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["id"], bid["id"])
    self.assertEqual(response.json["data"]["status"], "deleted")

    bid_data = deepcopy(initial_bids[0])
    for i in range(self.min_bids_number):
        bid_data["lotValues"][0]["value"]["amount"] = 100 + i
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})

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
    self.set_status("active.auction", extra={"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    # switch to active.awarded
    self.set_status("active.awarded", extra=extra)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

    # sign agreement
    response = self.app.get("/tenders/{}".format(self.tender_id))
    agreement_id = response.json["data"]["agreements"][-1]["id"]
    self.app.authorization = ("Basic", ("token", ""))
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")

    # finished tender does not show deleted bid info
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["bids"]), self.min_bids_number + 2)
    bid_data = response.json["data"]["bids"][1]
    self.assertEqual(bid_data["id"], bid["id"])
    self.assertEqual(bid_data["status"], "deleted")
    self.assertFalse("value" in bid_data)
    self.assertFalse("tenderers" in bid_data)
    self.assertFalse("date" in bid_data)


def deleted_bid_do_not_locks_tender_in_state(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    bid_data = deepcopy(initial_bids[0])
    bids = []
    bids_tokens = []
    bid_amount = 400
    for _ in range(self.min_bids_number):
        bid_data["lotValues"][0]["value"]["amount"] = bid_amount
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
        bid_amount += 5
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        bids.append(response.json["data"])
        bids_tokens.append(response.json["access"]["token"])

    bid_id = bids[0]["id"]

    # delete first bid
    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bids_tokens[0]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["id"], bids[0]["id"])
    self.assertEqual(response.json["data"]["status"], "deleted")

    bid_data["lotValues"][0]["value"]["amount"] = 101
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})

    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
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
    self.set_status("active.pre-qualification.stand-still", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    # check bids
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["bids"]), self.min_bids_number + 1)
    self.assertEqual(response.json["data"]["bids"][0]["status"], "deleted")
    for i in range(1, self.min_bids_number + 1):
        self.assertEqual(response.json["data"]["bids"][i]["status"], "active")


def patch_tender_bidder_document(self):
    doc_id_by_type = {}
    doc_id_by_type2 = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid2_id, doc_resource, self.bid2_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id_by_type2[doc_resource] = {
            "id": response.json["data"]["id"],
            "key": response.json["data"]["url"].split("?")[-1],
        }

        # upload private document
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name_{}_private.doc".format(doc_resource[:-1]), "content")],
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}_private.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        doc_id_by_type[doc_resource + "private"] = {"id": doc_id, "key": key}
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")

        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid2_id, doc_resource, self.bid2_token),
            upload_files=[("file", "name_{}_private.doc".format(doc_resource[:-1]), "content")],
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}_private.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        doc_id_by_type2[doc_resource + "private"] = {"id": doc_id, "key": key}
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid2_id, doc_resource, doc_id, self.bid2_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")


def patch_tender_bidder_document_private(self):
    doc_id_by_type = {}
    private_doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual("buyerOnly", response.json["data"]["confidentiality"])
        self.assertEqual(
            "Only our company sells badgers with pink hair.", response.json["data"]["confidentialityRationale"]
        )
        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            upload_files=[("file", "name.doc", "content2")],
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.assertEqual("buyerOnly", response.json["data"]["confidentiality"])
        self.assertEqual(
            "Only our company sells badgers with pink hair.", response.json["data"]["confidentialityRationale"]
        )


def download_tender_bidder_document(self):
    doc_id_by_type = {}
    private_doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        private_doc_id_by_type[doc_resource] = {
            "id": response.json["data"]["id"],
            "key": response.json["data"]["url"].split("?")[-1],
        }

        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )

        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        doc_id_by_type[doc_resource] = {
            "id": response.json["data"]["id"],
            "key": response.json["data"]["url"].split("?")[-1],
        }

        for container in private_doc_id_by_type, doc_id_by_type:
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}&{}".format(
                    self.tender_id,
                    self.bid_id,
                    doc_resource,
                    container[doc_resource]["id"],
                    self.bid_token,
                    container[doc_resource]["key"],
                )
            )
            if self.docservice:
                self.assertEqual(response.status, "302 Moved Temporarily")
                self.assertIn("http://localhost/get/", response.location)
                self.assertIn("Signature=", response.location)
                self.assertIn("KeyID=", response.location)
                self.assertIn("Expires=", response.location)
            else:
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.body, "content")
                self.assertEqual(
                    response.headers["Content-Disposition"],
                    "attachment; filename=name_{}.doc".format(doc_resource[:-1]),
                )
                self.assertEqual(response.headers["Content-Type"], "application/msword; charset=UTF-8")

            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}&{}".format(
                    self.tender_id,
                    self.bid_id,
                    doc_resource,
                    container[doc_resource]["id"],
                    self.tender_token,
                    container[doc_resource]["key"],
                ),
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertEqual(
                response.json["errors"][0]["description"],
                "Can't view bid documents in current (active.tendering) tender status",
            )

            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?{}".format(
                    self.tender_id,
                    self.bid_id,
                    doc_resource,
                    container[doc_resource]["id"],
                    container[doc_resource]["key"],
                ),
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertEqual(
                response.json["errors"][0]["description"],
                "Can't view bid documents in current (active.tendering) tender status",
            )

    self.set_status("active.pre-qualification")
    self.check_chronograph()

    def test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, status):
        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?acc_token={}&{}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        self.bid_token,
                        container[doc_resource]["key"],
                    )
                )
                if self.docservice:
                    self.assertEqual(response.status, "302 Moved Temporarily")
                    self.assertIn("http://localhost/get/", response.location)
                    self.assertIn("Signature=", response.location)
                    self.assertIn("KeyID=", response.location)
                else:
                    self.assertEqual(response.status, "200 OK")
                    self.assertEqual(response.body, "content")
                    self.assertEqual(
                        response.headers["Content-Disposition"],
                        "attachment; filename=name_{}.doc".format(doc_resource[:-1]),
                    )
                    self.assertEqual(response.headers["Content-Type"], "application/msword; charset=UTF-8")

        for doc_resource in ["documents", "eligibility_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?acc_token={}&{}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        self.tender_token,
                        container[doc_resource]["key"],
                    )
                )
                if self.docservice:
                    self.assertEqual(response.status, "302 Moved Temporarily")
                    self.assertIn("http://localhost/get/", response.location)
                    self.assertIn("Signature=", response.location)
                    self.assertIn("KeyID=", response.location)
                else:
                    self.assertEqual(response.status, "200 OK")

        for doc_resource in ["financial_documents", "qualification_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?acc_token={}&{}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        self.tender_token,
                        container[doc_resource]["key"],
                    ),
                    status=403,
                )
                self.assertEqual(response.status, "403 Forbidden")
                self.assertEqual(
                    response.json["errors"][0]["description"],
                    "Can't view bid documents in current ({}) tender status".format(status),
                )

        # for doc_resource in ['documents', 'eligibility_documents']:
        # for container in private_doc_id_by_type, doc_id_by_type:
        # response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
        # self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']))
        # self.assertEqual(response.status, '200 OK')

        for doc_resource in ["financial_documents", "qualification_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?{}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        container[doc_resource]["key"],
                    ),
                    status=403,
                )
                self.assertEqual(response.status, "403 Forbidden")
                self.assertEqual(
                    response.json["errors"][0]["description"],
                    "Can't view bid documents in current ({}) tender status".format(status),
                )

    test_bids_documents_after_tendering_resource(
        self, doc_id_by_type, private_doc_id_by_type, "active.pre-qualification"
    )

    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    # qualify bids
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
    test_bids_documents_after_tendering_resource(
        self, doc_id_by_type, private_doc_id_by_type, "active.pre-qualification.stand-still"
    )

    self.time_shift("active.auction")
    self.check_chronograph()
    test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]

    # posting auction urls
    response = self.app.patch_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {
            "data": {
                "lots": [{"auctionUrl": "https://tender.auction.url"}],
                "bids": [
                    {
                        "lotValues": [
                            {
                                "participationUrl": "https://tender.auction.url/for_bid/{}".format(i["id"]),
                                "relatedLot": self.initial_lots[0]["id"],
                            }
                        ],
                        "id": i["id"],
                    }
                    for i in auction_bids_data
                ],
            }
        },
    )
    # posting auction results
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("broker", ""))

    def test_bids_documents_after_auction_resource(self, doc_id_by_type, private_doc_id_by_type, status):
        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?acc_token={}&{}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        self.bid_token,
                        container[doc_resource]["key"],
                    )
                )
                if self.docservice:
                    self.assertEqual(response.status, "302 Moved Temporarily")
                    self.assertIn("http://localhost/get/", response.location)
                    self.assertIn("Signature=", response.location)
                    self.assertIn("KeyID=", response.location)
                else:
                    self.assertEqual(response.status, "200 OK")
                    self.assertEqual(response.body, "content")
                    self.assertEqual(
                        response.headers["Content-Disposition"],
                        "attachment; filename=name_{}.doc".format(doc_resource[:-1]),
                    )
                    self.assertEqual(response.headers["Content-Type"], "application/msword; charset=UTF-8")

        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?acc_token={}&{}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        self.tender_token,
                        container[doc_resource]["key"],
                    )
                )
                if self.docservice:
                    self.assertEqual(response.status, "302 Moved Temporarily")
                    self.assertIn("http://localhost/get/", response.location)
                    self.assertIn("Signature=", response.location)
                    self.assertIn("KeyID=", response.location)
                else:
                    self.assertEqual(response.status, "200 OK")
                    self.assertEqual(response.body, "content")
                    self.assertEqual(
                        response.headers["Content-Disposition"],
                        "attachment; filename=name_{}.doc".format(doc_resource[:-1]),
                    )
                    self.assertEqual(response.headers["Content-Type"], "application/msword; charset=UTF-8")

        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?{}".format(
                    self.tender_id,
                    self.bid_id,
                    doc_resource,
                    doc_id_by_type[doc_resource]["id"],
                    doc_id_by_type[doc_resource]["key"],
                )
            )
            if self.docservice:
                self.assertEqual(response.status, "302 Moved Temporarily")
                self.assertIn("http://localhost/get/", response.location)
                self.assertIn("Signature=", response.location)
                self.assertIn("KeyID=", response.location)
            else:
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.body, "content")
                self.assertEqual(
                    response.headers["Content-Disposition"],
                    "attachment; filename=name_{}.doc".format(doc_resource[:-1]),
                )
                self.assertEqual(response.headers["Content-Type"], "application/msword; charset=UTF-8")

            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?{}".format(
                    self.tender_id,
                    self.bid_id,
                    doc_resource,
                    private_doc_id_by_type[doc_resource]["id"],
                    private_doc_id_by_type[doc_resource]["key"],
                ),
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")

    test_bids_documents_after_auction_resource(self, doc_id_by_type, private_doc_id_by_type, "active.pre-qualification")

    # switch to active.awarded
    self.set_status("active.awarded", extra=extra)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    test_bids_documents_after_auction_resource(self, doc_id_by_type, private_doc_id_by_type, "active.pre-qualification")


def create_tender_bidder_document_nopending(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    bid_data = deepcopy(initial_bids[0])
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
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
    self.set_status("active.tendering", "end")
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
    self.set_status("active.pre-qualification.stand-still", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, token),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.put(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, token),
        "content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.post(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def bid_Administrator_change(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}]
    del bid_data["value"]
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    self.app.authorization = ("Basic", ("administrator", ""))

    bid_data.update({
        "tenderers": [{"identifier": {"id": "00000000"}}],
        "lotValues": [{"value": {"amount": 400}, "relatedLot": self.initial_lots[0]["id"]}],
    })
    response = self.app.patch_json(
        "/tenders/{}/bids/{}".format(self.tender_id, bid["id"]),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["tenderers"][0]["identifier"]["id"], "00000000")


def bids_activation_on_tender_documents(self):
    bids_access = {}
    # submit bids
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)
    for data in initial_bids:
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        bids_access[response.json["data"]["id"]] = response.json["access"]["token"]

    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")

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

    # activate bids
    for bid_id, token in bids_access.items():
        response = self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token), {"data": {"status": "pending"}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")


def create_tender_biddder_invalid(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)
    response = self.app.post_json("/tenders/some_id/bids", {"data": initial_bids[0]}, status=404)
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

    response = self.app.post_json(request_path, {"data": {"tenderers": [{"identifier": "invalid_value"}]}}, status=422)
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

    response = self.app.post_json(request_path, {"data": {"tenderers": [{"identifier": {}}]}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    assert_data = [
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"selfQualified"},
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
        },
    ]
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        assert_data.insert(0, {u"description": [u"This field is required."], u"location": u"body", u"name": u"selfEligible"})
    self.assertEqual(
        response.json["errors"],
        assert_data
    )

    response = self.app.post_json(
        request_path,
        {"data": {"selfEligible": False, "tenderers": [{"name": "name", "identifier": {"uri": "invalid_value"}}]}},
        status=422,
    )
    assert_data = [
        {u"description": [u"Value must be one of [True]."], u"location": u"body", u"name": u"selfEligible"},
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"selfQualified"},
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
        },
    ]

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        assert_data,
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
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"lotValues"}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "selfEligible": True,
                "selfQualified": True,
                "tenderers": initial_bids[0]["tenderers"],
                "lotValues": [
                    {"value": {"amount": 500, "valueAddedTaxIncluded": False}, "relatedLot": self.initial_lots[0]["id"]}
                ],
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
                        u"value": [
                            u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot"
                        ]
                    }
                ],
                u"location": u"body",
                u"name": u"lotValues",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "selfEligible": True,
                "selfQualified": True,
                "tenderers": initial_bids[0]["tenderers"],
                "lotValues": [{"value": {"amount": 500, "currency": "USD"}, "relatedLot": self.initial_lots[0]["id"]}],
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
                u"description": [{u"value": [u"currency of bid should be identical to currency of value of lot"]}],
                u"location": u"body",
                u"name": u"lotValues",
            }
        ],
    )


def create_tender_bidder(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    bid_data = deepcopy(initial_bids[0])
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], initial_bids[0]["tenderers"][0]["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])

    for status in ("active", "unsuccessful", "deleted", "invalid"):
        bid_data["lotValues"][0]["value"]["amount"] = 500
        bid_data["status"] = status
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")

    bid_without_lotvalues_value = deepcopy(bid_data)
    del bid_without_lotvalues_value["lotValues"][0]["value"]
    bid_without_lotvalues_value["status"] = "pending"
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id), {"data": bid_without_lotvalues_value}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.set_status("complete")

    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (complete) tender status")


def deleted_bid_is_not_restorable(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": initial_bids[0]})
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
        {"data": {"status": "pending"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"lotValues"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {
            "data": {
                "status": "pending",
                "lotValues": [{"value": {"amount": 100}, "relatedLot": self.initial_lots[0]["id"]}],
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid in (deleted) status")

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "deleted")


def patch_tender_bidder(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": initial_bids[0]})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

    bid_data = deepcopy(initial_bids[0])
    bid_data["lotValues"][0]["value"]["amount"] = 600
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token), {"data": bid_data}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"value": [u"value of bid should be less than value of lot"]}],
                u"location": u"body",
                u"name": u"lotValues",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"tenderers": [{"name": u"Державне управління управлінням справами"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], bid["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token), {"data": initial_bids[0]}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], bid["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    bid_data["lotValues"][0]["value"]["amount"] = 400
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token), {"data": bid_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], bid["date"])

    response = self.app.patch_json(
        "/tenders/{}/bids/some_id?acc_token={}".format(self.tender_id, bid_token), {"data": bid_data}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"bid_id"}])

    response = self.app.patch_json("/tenders/some_id/bids/some_id", {"data": bid_data}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    for status in ("invalid", "active", "unsuccessful", "deleted", "draft"):
        response = self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"], "Can't update bid to ({}) status".format(status))

    self.set_status("complete")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token), {"data": bid_data}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid in current (complete) tender status")


def features_bidder(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    test_features_bids = initial_bids[:2]
    test_features_bids[0]["parameters"] = [{"code": i["code"], "value": 0.1} for i in self.initial_data["features"]]
    test_features_bids[0]["lotValues"] = [
        {
            "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
            "relatedLot": self.initial_lots[0]["id"],
        }
    ]
    test_features_bids[1]["parameters"] = [{"code": i["code"], "value": 0.15} for i in self.initial_data["features"]]
    test_features_bids[1]["lotValues"] = [
        {
            "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
            "relatedLot": self.initial_lots[0]["id"],
        }
    ]

    for i in test_features_bids:
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": i})
        i["status"] = "pending"
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        bid = response.json["data"]
        bid.pop(u"date")
        bid.pop(u"id")
        bid["lotValues"][0].pop("date")
        bid["lotValues"][0].pop("status")
        self.assertEqual(bid, i)


def features_bidder_invalid(self):
    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{
        "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
        "relatedLot": self.initial_lots[0]["id"],
    }]
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"All features parameters is required."], u"location": u"body", u"name": u"parameters"}],
    )
    bid_data["parameters"] = [{"code": "OCDS-123454-AIR-INTAKE", "value": 0.1}]
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"All features parameters is required."], u"location": u"body", u"name": u"parameters"}],
    )
    bid_data["parameters"].append({"code": "OCDS-123454-AIR-INTAKE", "value": 0.1})
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
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
    bid_data["parameters"][1]["code"] = "OCDS-123454-YEARS"
    bid_data["parameters"][1]["value"] = 0.2
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
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


def create_tender_bid_with_documents(self):
    # test requires bid data stored on `bid_data_wo_docs` attribute of test class
    docs = [
        {
            "title": "first.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        },
        {
            "title": "second.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        },
        {
            "title": "third.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        },
    ]
    docs_container = self.docs_container if hasattr(self, "docs_container") else "documents"
    docs_container_url = self.docs_container_url if hasattr(self, "docs_container_url") else "documents"

    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    bid_data = deepcopy(initial_bids[0])
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], self.author_data["name"])
    self.assertIn("id", bid)
    self.bid_id = bid["id"]
    self.bid_token = response.json["access"]["token"]
    self.assertIn(bid["id"], response.headers["Location"])
    documents = bid[docs_container]
    ids = [doc["id"] for doc in documents]
    self.assertEqual(["first.doc", "second.doc", "third.doc"], [document["title"] for document in documents])

    response = self.app.get(
        "/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, docs_container_url), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't view bid documents in current (active.tendering) tender status",
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, docs_container_url, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(ids, [doc["id"] for doc in response.json["data"]])

    response = self.app.get(
        "/tenders/{}/bids/{}/{}?all=true&acc_token={}".format(
            self.tender_id, self.bid_id, docs_container_url, self.bid_token
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(ids, [doc["id"] for doc in response.json["data"]])

    for index, document in enumerate(documents):
        key = document["url"].split("?")[-1].split("=")[-1]

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download=some_id&acc_token={}".format(
                self.tender_id, self.bid_id, docs_container_url, document["id"], self.bid_token
            ),
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
        )

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download={}".format(
                self.tender_id, self.bid_id, docs_container_url, document["id"], key
            ),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't view bid documents in current (active.tendering) tender status",
        )

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}".format(
                self.tender_id, self.bid_id, docs_container_url, document["id"], key, self.bid_token
            )
        )
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertIn("Expires=", response.location)

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, docs_container_url, document["id"]),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't view bid documents in current (active.tendering) tender status",
        )

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, docs_container_url, document["id"], self.bid_token
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(document["id"], response.json["data"]["id"])


def create_tender_bid_with_document(self):
    # test requires bid data stored on `bid_data_wo_docs` attribute of test class
    docs = [
        {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    docs_container = self.docs_container if hasattr(self, "docs_container") else "documents"
    docs_container_url = self.docs_container_url if hasattr(self, "docs_container_url") else "documents"

    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    bid_data = deepcopy(initial_bids[0])
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], self.author_data["name"])
    self.assertIn("id", bid)
    self.bid_id = bid["id"]
    self.bid_token = response.json["access"]["token"]
    self.assertIn(bid["id"], response.headers["Location"])
    document = bid[docs_container][0]
    self.assertEqual("name.doc", document["title"])
    key = document["url"].split("?")[-1].split("=")[-1]

    response = self.app.get(
        "/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, docs_container_url), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't view bid documents in current (active.tendering) tender status",
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, docs_container_url, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(document["id"], response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/bids/{}/{}?all=true&acc_token={}".format(
            self.tender_id, self.bid_id, docs_container_url, self.bid_token
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(document["id"], response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/bids/{}/{}/{}?download=some_id&acc_token={}".format(
            self.tender_id, self.bid_id, docs_container_url, document["id"], self.bid_token
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/{}/{}?download={}".format(
            self.tender_id, self.bid_id, docs_container_url, document["id"], key
        ),
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bid documents in current (active.tendering) tender status"
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}".format(
            self.tender_id, self.bid_id, docs_container_url, document["id"], key, self.bid_token
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.get(
        "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, docs_container_url, document["id"]), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bid documents in current (active.tendering) tender status"
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
            self.tender_id, self.bid_id, docs_container_url, document["id"], self.bid_token
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(document["id"], response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])


def create_tender_bid_with_document_invalid(self):
    # test requires bid data stored on `bid_data_wo_docs` attribute of test class
    docs = [
        {
            "title": "name.doc",
            "url": "http://invalid.docservice.url/get/uuid",
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    docs_container = self.docs_container if hasattr(self, "docs_container") else "documents"

    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    bid_data = deepcopy(initial_bids[0])
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only from document service.")

    docs = [
        {
            "title": "name.doc",
            "url": "/".join(self.generate_docservice_url().split("/")[:4]),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only from document service.")

    docs = [
        {
            "title": "name.doc",
            "url": self.generate_docservice_url().split("?")[0],
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only from document service.")

    docs = [{"title": "name.doc", "url": self.generate_docservice_url(), "format": "application/msword"}]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["location"], docs_container)
    self.assertEqual(response.json["errors"][0]["name"], "hash")
    self.assertEqual(response.json["errors"][0]["description"], "This field is required.")

    docs = [
        {
            "title": "name.doc",
            "url": self.generate_docservice_url().replace(self.app.app.registry.keyring.keys()[-1], "0" * 8),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Document url expired.")

    docs = [
        {
            "title": "name.doc",
            "url": self.generate_docservice_url().replace("Signature=", "Signature=ABC"),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Document url signature invalid.")

    docs = [
        {
            "title": "name.doc",
            "url": self.generate_docservice_url().replace("Signature=", "Signature=bw%3D%3D"),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Document url invalid.")


def get_tender_bidder_document_ds(self):
    doc_id_by_type = {}

    def document_is_unaccessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker4", ""))
        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, resource), status=403)
        self.assertEqual(response.status, "403 Forbidden")
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, resource, doc_id), status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.app.authorization = orig_auth

    def document_is_unaccessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, resource, doc_id, self.tender_token
            ),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.app.authorization = orig_auth

    def all_documents_are_accessible_for_bid_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        for resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            response = self.app.get(
                "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, self.bid_token)
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(len(response.json["data"]), 2)
            doc1 = response.json["data"][0]
            doc2 = response.json["data"][1]
            self.assertEqual(doc1["title"], "name_{}.doc".format(resource[:-1]))
            self.assertEqual(doc2["title"], "name_{}_private.doc".format(resource[:-1]))
            self.assertEqual(doc1["confidentiality"], u"public")
            self.assertEqual(doc2["confidentiality"], u"buyerOnly")
            self.assertIn("url", doc1)
            self.assertIn("url", doc2)
            doc_id = doc_id_by_type[resource]["id"]
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                    self.tender_id, self.bid_id, resource, doc_id, self.bid_token
                )
            )
            self.assertEqual(response.status, "200 OK")
            self.assertIn("previousVersions", response.json["data"])
            doc = response.json["data"]
            del doc["previousVersions"]
            self.assertEqual(doc, doc1)
            doc_id = doc_id_by_type[resource + "private"]["id"]
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                    self.tender_id, self.bid_id, resource, doc_id, self.bid_token
                )
            )
            self.assertEqual(response.status, "200 OK")
            self.assertIn("previousVersions", response.json["data"])
            doc = response.json["data"]
            del doc["previousVersions"]
            self.assertEqual(doc, doc2)
        self.app.authorization = orig_auth

    def documents_are_accessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        token = self.tender_token
        response = self.app.get(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, token)
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(len(response.json["data"]), 2)
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, doc_id, token)
        )
        self.assertIn("url", response.json["data"])
        self.assertEqual(response.status, "200 OK")
        doc_id = doc_id_by_type[resource + "private"]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, doc_id, token)
        )
        self.assertEqual(response.status, "200 OK")
        self.assertIn("url", response.json["data"])
        self.app.authorization = orig_auth

    def public_documents_are_accessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker4", ""))

        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, resource))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(len(response.json["data"]), 2)
        self.assertIn(doc_id_by_type[resource]["key"], response.json["data"][0]["url"])
        self.assertNotIn("url", response.json["data"][1])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, resource, doc_id_by_type[resource]["id"])
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], "name_{}.doc".format(resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], u"public")
        self.assertEqual(response.json["data"]["format"], u"application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(
                self.tender_id, self.bid_id, resource, doc_id_by_type[resource + "private"]["id"]
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["confidentiality"], u"buyerOnly")
        self.assertNotIn("url", response.json["data"])

        self.app.authorization = orig_auth

    def all_public_documents_are_accessible_for_others():
        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            public_documents_are_accessible_for_others(doc_resource)

    # active.tendering
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:

        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "public",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}_private.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        doc_id = response.json["data"]["id"]
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]
        doc_id_by_type[doc_resource + "private"] = {"id": doc_id, "key": key}
        doc_id_by_type[doc_resource + "private"] = {"id": doc_id, "key": key}

        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )
    self.assertEqual(set(response.json["data"][1].keys()), set(["id", "status", "tenderers"]))
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )

    for doc_resource in ["documents", "eligibility_documents"]:
        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, doc_resource))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(len(response.json["data"]), 2)
        self.assertIn("url", response.json["data"][0])
        self.assertIn(doc_id_by_type[doc_resource]["key"], response.json["data"][0]["url"])
        self.assertNotIn("url", response.json["data"][1])

    for doc_resource in ["documents", "eligibility_documents"]:
        doc_id = doc_id_by_type[doc_resource]["id"]
        response = self.app.get("/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], u"name_{}.doc".format(doc_resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], u"public")
        self.assertEqual(response.json["data"]["format"], u"application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

        doc_id = doc_id_by_type[doc_resource + "private"]["id"]
        response = self.app.get("/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], u"name_{}_private.doc".format(doc_resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], u"buyerOnly")
        self.assertEqual(response.json["data"]["format"], u"application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

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

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )
    self.assertEqual(set(response.json["data"][1].keys()), set(["id", "status", "tenderers"]))
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )
    response = self.app.get("/tenders/{}/bids/{}/documents".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertIn(doc_id_by_type["documents"]["key"], response.json["data"][0]["url"])
    doc_id = doc_id_by_type["documents"]["id"]
    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], u"name_document.doc")
    self.assertEqual(response.json["data"]["confidentiality"], u"public")
    self.assertEqual(response.json["data"]["format"], u"application/msword")
    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to active.auction
    self.set_status("active.pre-qualification.stand-still", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )
    self.assertEqual(set(response.json["data"][1].keys()), set(["id", "status", "tenderers"]))
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()), set(["id", "status", "documents", "eligibilityDocuments", "tenderers"])
    )
    response = self.app.get("/tenders/{}/bids/{}/documents".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertIn(doc_id_by_type["documents"]["key"], response.json["data"][0]["url"])
    doc_id = doc_id_by_type["documents"]["id"]
    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], u"name_document.doc")
    self.assertEqual(response.json["data"]["confidentiality"], u"public")
    self.assertEqual(response.json["data"]["format"], u"application/msword")
    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    assert_data_1 = {
        u"date",
        u"status",
        u"id",
        u"lotValues",
        u"tenderers",
        u"documents",
        u"eligibilityDocuments",
        u"qualificationDocuments",
        u"financialDocuments",
        u"selfQualified",
    }

    assert_data_2 = {u"date", u"status", u"id", u"lotValues", u"tenderers", u"selfQualified"}

    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        assert_data_1.add(u"selfEligible")
        assert_data_2.add(u"selfEligible")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        assert_data_1,
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        assert_data_2,
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        assert_data_1,
    )

    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()

    self.set_status("active.awarded")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        assert_data_1,
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        assert_data_2,
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        assert_data_1,
    )
    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()

    # time travel
    tender = self.db.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

    # set unitPrices in contracts
    response = self.app.get("/tenders/{}".format(self.tender_id))
    contracts = response.json["data"]["agreements"][-1]["contracts"]
    agreement_id = response.json["data"]["agreements"][-1]["id"]
    self.app.authorization = ("Basic", ("token", ""))
    for contract in contracts:
        unit_prices = contract["unitPrices"]
        for unit_price in unit_prices:
            unit_price["value"]["amount"] = 60
        response = self.app.patch_json(
            "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
                self.tender_id, agreement_id, contract["id"], self.tender_token
            ),
            {"data": {"unitPrices": unit_prices}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    tender = self.db.get(self.tender_id)
    tender["contractPeriod"]["startDate"] = (
        datetime.now() - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1)
    ).isoformat()
    tender["contractPeriod"]["clarificationsUntil"] = (datetime.now() - timedelta(days=1)).isoformat()
    self.db.save(tender)

    # sign agreement
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement_id, self.tender_token),
        {"data": {"status": "active", "period": agreement_period}},
    )
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        assert_data_1,
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        assert_data_2,
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        assert_data_1,
    )
    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()


def create_tender_bid_with_eligibility_document_invalid(self):
    self.docs_container = "eligibilityDocuments"
    self.docs_container_url = "eligibility_documents"
    create_tender_bid_with_document_invalid(self)


def create_tender_bid_with_financial_document_invalid(self):
    self.docs_container = "financialDocuments"
    self.docs_container_url = "financial_documents"
    create_tender_bid_with_document_invalid(self)


def create_tender_bid_with_qualification_document_invalid(self):
    self.docs_container = "qualificationDocuments"
    self.docs_container_url = "qualification_documents"
    create_tender_bid_with_document_invalid(self)


def create_tender_bid_with_eligibility_document(self):
    self.docs_container = "eligibilityDocuments"
    self.docs_container_url = "eligibility_documents"
    create_tender_bid_with_document(self)


def create_tender_bid_with_qualification_document(self):
    self.docs_container = "qualificationDocuments"
    self.docs_container_url = "qualification_documents"
    create_tender_bid_with_document(self)


def create_tender_bid_with_financial_document(self):
    self.docs_container = "financialDocuments"
    self.docs_container_url = "financial_documents"
    create_tender_bid_with_document(self)


def create_tender_bid_with_financial_documents(self):
    self.docs_container = "financialDocuments"
    self.docs_container_url = "financial_documents"
    create_tender_bid_with_documents(self)


def create_tender_bid_with_eligibility_documents(self):
    self.docs_container = "eligibilityDocuments"
    self.docs_container_url = "eligibility_documents"
    create_tender_bid_with_documents(self)


def create_tender_bid_with_qualification_documents(self):
    self.docs_container = "qualificationDocuments"
    self.docs_container_url = "qualification_documents"
    create_tender_bid_with_documents(self)


def patch_and_put_document_into_invalid_bid(self):
    doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            upload_files=[("file", "name_{}.doc".format(doc_resource[:-1]), "content")],
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

    # update tender. we can set value that is less than a value in bids as
    # they will be invalidated by this request
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, self.initial_lots[0]["id"], self.tender_token),
        {"data": {"value": {"amount": 300.0}, "minimalStep": {"amount": 9.0}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 300)

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        doc_id = doc_id_by_type[doc_resource]["id"]
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can't update document at 'invalid' bid status")
        response = self.app.put(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            "updated",
            content_type="application/msword",
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"], "Can't update document at 'invalid' bid status")


def create_tender_bid_with_all_documents(self):
    docs = [
        {
            "title": "first.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        },
        {
            "title": "second.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        },
        {
            "title": "third.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        },
    ]

    initial_bids = deepcopy(self.test_bids_data)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)

    bid_data = deepcopy(initial_bids[0])
    bid_data["documents"] = docs
    bid_data["qualificationDocuments"] = deepcopy(docs)
    bid_data["eligibilityDocuments"] = deepcopy(docs)
    bid_data["financialDocuments"] = deepcopy(docs)
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bidder = response.json["data"]
    self.assertEqual(bidder["tenderers"][0]["name"], initial_bids[0]["tenderers"][0]["name"])
    self.assertIn("id", bidder)
    self.bid_id = bidder["id"]
    self.bid_token = response.json["access"]["token"]
    self.assertIn(bidder["id"], response.headers["Location"])

    documents = bidder["documents"]
    ids = [doc["id"] for doc in documents]
    self.assertEqual(["first.doc", "second.doc", "third.doc"], [document["title"] for document in documents])

    eligibility_documents = bidder["eligibilityDocuments"]
    eligibility_ids = [doc["id"] for doc in eligibility_documents]
    self.assertEqual(
        ["first.doc", "second.doc", "third.doc"], [document["title"] for document in eligibility_documents]
    )

    qualification_documents = bidder["qualificationDocuments"]
    qualification_ids = [doc["id"] for doc in qualification_documents]
    self.assertEqual(
        ["first.doc", "second.doc", "third.doc"], [document["title"] for document in qualification_documents]
    )

    financial_documents = bidder["financialDocuments"]
    financial_ids = [doc["id"] for doc in financial_documents]
    self.assertEqual(["first.doc", "second.doc", "third.doc"], [document["title"] for document in financial_documents])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(ids, [doc["id"] for doc in response.json["data"]])

    response = self.app.get(
        "/tenders/{}/bids/{}/eligibility_documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(eligibility_ids, [doc["id"] for doc in response.json["data"]])

    response = self.app.get(
        "/tenders/{}/bids/{}/qualification_documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(qualification_ids, [doc["id"] for doc in response.json["data"]])

    response = self.app.get(
        "/tenders/{}/bids/{}/financial_documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(financial_ids, [doc["id"] for doc in response.json["data"]])


def put_tender_bidder_document_private_json(self):
    doc_id_by_type = {}
    private_doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}
        self.assertEqual("buyerOnly", response.json["data"]["confidentiality"])
        self.assertEqual(
            "Only our company sells badgers with pink hair.", response.json["data"]["confidentialityRationale"]
        )
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "title": "name_{}_v2.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "public",
                    "confidentialityRationale": None,
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.assertEqual("public", response.json["data"]["confidentiality"])
        self.assertNotIn("confidentialityRationale", response.json["data"])

    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
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
    self.set_status("active.pre-qualification.stand-still", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        doc_id = doc_id_by_type[doc_resource]["id"]
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "title": "name_{}_v3.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document confidentiality in current (active.qualification) tender status",
        )


def change_bid_document_in_qualification_st_st(self):
    self.set_status("active.qualification.stand-still", "end")
    doc_id_by_type = {}
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}
        self.assertEqual("buyerOnly", response.json["data"]["confidentiality"])
        self.assertEqual(
            "Only our company sells badgers with pink hair.", response.json["data"]["confidentialityRationale"]
        )
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "title": "name_{}_v2.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "public",
                    "confidentialityRationale": None,
                }
            },
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document confidentiality in current (active.qualification.stand-still) tender status",
        )


def view_bid_in_qualification_st_st(self):   # CS-5342
    self.set_status("active.qualification.stand-still", "end")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")
    bids = response.json["data"]["bids"]
    expected_keys = {"id", "status", "selfQualified", "lotValues", "tenderers", "date"}
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        expected_keys.add("selfEligible")
    self.assertEqual(set(bids[0].keys()), expected_keys)

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bids[0]["id"]))
    self.assertEqual(set(response.json["data"].keys()), expected_keys)


def post_winningBid_document_in_awarded(self):
    self.set_status("active.awarded")
    response = self.app.post_json(
        "/tenders/{}/bids/{}/{}?acc_token={}".format(
            self.tender_id, self.bid_id, "financial_documents", self.bid_token
        ),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentType": "winningBid",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual(u"укр.doc", response.json["data"]["title"])
    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
