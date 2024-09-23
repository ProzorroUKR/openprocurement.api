from copy import deepcopy

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
    test_tender_below_claim,
    test_tender_below_complaint,
    test_tender_below_draft_claim,
    test_tender_below_draft_complaint,
    test_tender_below_organization,
)
from openprocurement.tender.core.tests.utils import change_auth

# TenderAwardResourceTest
from openprocurement.tender.openua.tests.award_blanks import (
    bot_patch_tender_award_complaint as bot_patch_tender_award_complaint_base,
)
from openprocurement.tender.openua.tests.award_blanks import (
    bot_patch_tender_award_complaint_forbidden as bot_patch_tender_award_complaint_forbidden_base,
)


def create_tender_award_invalid(self):
    self.app.authorization = ("Basic", ("token", ""))
    request_path = "/tenders/{}/awards".format(self.tender_id)
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

    response = self.app.post_json(request_path, {"data": {"suppliers": [{"identifier": "invalid_value"}]}}, status=422)
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
                "name": "suppliers",
            }
        ],
    )

    response = self.app.post_json(request_path, {"data": {"suppliers": [{"identifier": {"id": 0}}]}}, status=422)
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
                        "identifier": {"scheme": ["This field is required."]},
                        "name": ["This field is required."],
                        "address": ["This field is required."],
                        "scale": ["This field is required."],
                    }
                ],
                "location": "body",
                "name": "suppliers",
            },
            {"description": ["This field is required."], "location": "body", "name": "bid_id"},
        ],
    )

    response = self.app.post_json(
        request_path, {"data": {"suppliers": [{"name": "name", "identifier": {"uri": "invalid_value"}}]}}, status=422
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
                "name": "suppliers",
            },
            {"description": ["This field is required."], "location": "body", "name": "bid_id"},
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": "0" * 32,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["lotID should be one of lots"], "location": "body", "name": "lotID"}],
    )

    response = self.app.post_json(
        "/tenders/some_id/awards",
        {"data": {"suppliers": [test_tender_below_organization], "bid_id": self.initial_bids[0]["id"]}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/some_id/awards", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    self.set_status("complete")

    bid = self.initial_bids[0]
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": bid["lotValues"][0]["relatedLot"],
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't create award in current (complete) tender status"
    )


def patch_tender_award(self):
    response = self.app.patch_json(
        "/tenders/{}/awards/some_id".format(self.tender_id), {"data": {"status": "unsuccessful"}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "award_id"}])

    response = self.app.patch_json("/tenders/some_id/awards/some_id", {"data": {"status": "unsuccessful"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.awards_ids[0], self.tender_token),
        {"data": {"awardStatus": "unsuccessful"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "awardStatus", "description": "Rogue field"}]
    )

    #  make all awards active
    for award_id in self.awards_ids:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    # patch first award from active to cancelled
    count_cancelled_awards = 1
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.awards_ids[0], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # cant patch cancelled award
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.awards_ids[0], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update award in current (cancelled) status")

    # get all awards and check that new award is created
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), len(self.awards_ids) + count_cancelled_awards)  # + 1 award
    self.assertEqual(response.json["data"][0]["bid_id"], response.json["data"][-1]["bid_id"])
    self.assertEqual(response.json["data"][-1]["status"], "pending")

    # patch second award from active to cancelled
    count_cancelled_awards += 1
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.awards_ids[1], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # cant patch cancelled award
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.awards_ids[1], self.tender_token),
        {"data": {"status": "unsuccessful", "eligible": False}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update award in current (cancelled) status")

    # get all awards and check that new award is created
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), len(self.awards_ids) + count_cancelled_awards)  # + 1 award
    self.assertEqual(response.json["data"][1]["bid_id"], response.json["data"][-1]["bid_id"])
    self.assertEqual(response.json["data"][-1]["status"], "pending")

    self.set_status("active.awarded")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.awards_ids[1], self.tender_token),
        {"data": {"status": "unsuccessful", "eligible": False}},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update award in current (active.awarded) tender status"
    )


def patch_tender_award_active(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    # Get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    comparable = min((tender["maxAwardsCount"], len(self.initial_bids)))
    self.assertEqual(len(response.json["data"]), comparable)

    for award in response.json["data"]:
        self.assertEqual(award["status"], "pending")

    # patch all awards to active
    for award in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")


def patch_tender_award_unsuccessful(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertIn("maxAwardsCount", tender)
    max_awards = tender["maxAwardsCount"]

    for x in range(1, 4):
        # patch award to unsuccessful
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "unsuccessful")

        # get all awards and check if new award is created
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        active_awards_ids = [award["id"] for award in response.json["data"] if award["status"] in ("pending", "active")]

        comparable = min((len(self.initial_bids) - x, max_awards))
        self.assertEqual(len(active_awards_ids), comparable)
        # new award bid_id is unique
        self.assertEqual(len(active_awards_ids), len(set(active_awards_ids)))

        unsuccessful_award = self.award_id
        self.award_id = active_awards_ids[0] if active_awards_ids else None

    old_awards_ids = (award["id"] for award in response.json["data"])

    # patch unsuccessful award to cancelled, new batch of award should be created
    # old awards are cancelled
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, unsuccessful_award, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_statuses = {}
    for award in response.json["data"]:
        award_statuses[award["id"]] = award["status"]
    for award_id in old_awards_ids:
        self.assertEqual(award_statuses[award_id], "cancelled")

    active_awards_ids = [award["id"] for award in response.json["data"] if award["status"] in ("pending", "active")]

    comparable = min((max_awards, len(self.initial_bids)))
    self.assertEqual(len(active_awards_ids), comparable * len(self.initial_lots) if self.initial_lots else comparable)


def get_tender_award(self):
    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, self.award_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders/{}/awards/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "award_id"}])

    response = self.app.get("/tenders/some_id/awards/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


def patch_tender_award_Administrator_change(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]
    complaintPeriod = award["complaintPeriod"]["startDate"]

    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award["id"]),
        {"data": {"complaintPeriod": {"endDate": award["complaintPeriod"]["startDate"]}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("endDate", response.json["data"]["complaintPeriod"])
    self.assertEqual(response.json["data"]["complaintPeriod"]["endDate"], complaintPeriod)


# TenderLotAwardResourceTest


def create_tender_lot_award(self):
    self.app.authorization = ("Basic", ("token", ""))
    request_path = "/tenders/{}/awards".format(self.tender_id)
    response = self.app.post_json(
        request_path,
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "lotID", "description": ["This field is required."]}]
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]
    self.assertEqual(award["suppliers"][0]["name"], test_tender_below_organization["name"])
    self.assertEqual(award["lotID"], self.initial_lots[0]["id"])
    self.assertIn("id", award)
    self.assertIn(award["id"], response.headers["Location"])

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][-1], award)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertIn("Location", response.headers)


# Tender2LotAwardResourceTest


def create_tender_2lot_award(self):
    request_path = "/tenders/{}/awards".format(self.tender_id)
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
    self.assertEqual(response.status, "201 Created")

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        request_path,
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[0]["id"],
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can create award only in active lot status")

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "lotID": self.initial_lots[1]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    award = response.json["data"]
    self.assertEqual(award["suppliers"][0]["name"], test_tender_below_organization["name"])
    self.assertEqual(award["lotID"], self.initial_lots[1]["id"])
    self.assertIn("id", award)
    self.assertIn(award["id"], response.headers["Location"])

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][-1], award)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award["id"]),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award["id"]), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertIn("Location", response.headers)


def patch_tender_2lot_award(self):
    request_path = "/tenders/{}/awards".format(self.tender_id)
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)
    new_award = response.json["data"][-1]

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[1]["id"],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update award only in active lot status")


# TenderAwardComplaintDocumentResourceT


def patch_tender_award_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
        ),
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

    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
                self.tender_id, self.award_id, self.complaint_id, doc_id
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, self.complaint_id),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?download={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )


# Tender2LotAwardComplaintDocumentResourceTest


def create_tender_2lot_award_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents".format(self.tender_id, self.award_id, self.complaint_id),
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
        response.json["errors"][0]["description"], "Can't add document in current (draft) complaint status"
    )

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
        ),
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
    self.assertEqual("укр.doc", response.json["data"]["title"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents".format(self.tender_id, self.award_id, self.complaint_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents?all=true".format(
            self.tender_id, self.award_id, self.complaint_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?download=some_id".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?download={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, b"content")

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]["id"],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations".format(self.tender_id),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents".format(self.tender_id, self.award_id, self.complaint_id),
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
        response.json["errors"][0]["description"], "Can't add document in current (unsuccessful) tender status"
    )


def put_tender_2lot_award_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
        ),
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

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        ),
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
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?download={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, b"content2")

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?download={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, b"content3")

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, self.complaint_id),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?download={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, b"content4")

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]["id"],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations".format(self.tender_id),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.put_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
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
        response.json["errors"][0]["description"], "Can't update document in current (unsuccessful) tender status"
    )


def patch_tender_2lot_award_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
        ),
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

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, self.complaint_id),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description2"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["description"], "document description2")

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[0]["id"],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations".format(self.tender_id),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (unsuccessful) tender status"
    )


def create_tender_award_claim(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, self.award_id), {"data": {"status": "cancelled"}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    cancelled_award_id = response.json["data"]["id"]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    pending_awards_ids = [i["id"] for i in response.json["data"] if i["status"] == "pending"]
    unsuccessful_award_id = pending_awards_ids[-1]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{unsuccessful_award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, unsuccessful_award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    self.app.authorization = auth
    bid_token = self.initial_bids_tokens[self.initial_bids[1]["id"]]

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, unsuccessful_award_id, bid_token),
        {"data": test_tender_below_claim},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't add complaint in current (active.qualification) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    pending_awards_ids = [i["id"] for i in response.json["data"] if i["status"] == "pending"]

    self.app.authorization = auth
    for award_id in pending_awards_ids:
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, unsuccessful_award_id, bid_token),
        {"data": test_tender_below_claim},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can add claim only on unsuccessful award of your bid",
                "location": "body",
                "name": "data",
            }
        ],
    )

    # post claim for cancelled award, cancelled award.complaintPeriod doesnt allow this
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, cancelled_award_id, bid_token),
        {"data": test_tender_below_claim},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Can add complaint only in complaintPeriod", "location": "body", "name": "data"}],
    )

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, unsuccessful_award_id, bid_token),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, unsuccessful_award_id, complaint["id"], owner_token
        ),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can add claim only on unsuccessful award of your bid",
                "location": "body",
                "name": "data",
            }
        ],
    )


def get_tender_award_complaints(self):
    self.set_status("active.qualification.stand-still")
    bid_token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    response = self.app.get("/tenders/{}/awards/{}/complaints".format(self.tender_id, self.award_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], complaint)

    response = self.app.get("/tenders/some_id/awards/some_id/complaints", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_draft_claim},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add complaint only in complaintPeriod")


def patch_tender_award_complaint(self):
    self.set_status("active.qualification.stand-still")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], self.tender_token
        ),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"title": "claim title"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "claim title")

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"status": "stopping", "cancellationReason": "reason"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "stopping")
    self.assertEqual(response.json["data"]["cancellationReason"], "reason")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/some_id".format(self.tender_id, self.award_id),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}])

    response = self.app.patch_json(
        "/tenders/some_id/awards/some_id/complaints/some_id",
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint from stopping to cancelled status"
    )

    response = self.app.patch_json(
        "/tenders/{}/awards/some_id/complaints/some_id".format(self.tender_id),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "award_id"}])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"])
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "stopping")
    self.assertEqual(response.json["data"]["cancellationReason"], "reason")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint in current (complete) tender status"
    )


def review_tender_award_claim(self):
    self.set_status("active.qualification.stand-still")
    for status in ["invalid", "resolved", "declined"]:
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={self.bid_token}",
            {"data": test_tender_below_claim},
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        complaint = response.json["data"]
        complaint_token = response.json["access"]["token"]

        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], self.tender_token
            ),
            {
                "data": {
                    "status": "answered",
                    "resolutionType": status,
                    "resolution": "resolution text for {} status".format(status),
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["resolutionType"], status)

        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], complaint_token
            ),
            {"data": {"satisfied": "i" in status}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["satisfied"], "i" in status)


def review_tender_award_complaint(self):
    self.set_status("active.qualification.stand-still")
    for status in ["invalid", "stopped", "declined", "satisfied"]:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
            {"data": test_tender_below_complaint},
        )
        self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
        complaint = response.json["data"]

        if RELEASE_2020_04_19 < get_now():
            self.assertEqual(response.json["data"]["status"], "draft")
            with change_auth(self.app, ("Basic", ("bot", ""))):
                response = self.app.patch_json(
                    "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                    {"data": {"status": "pending"}},
                )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "pending")

        self.app.authorization = ("Basic", ("reviewer", ""))
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
            {"data": {"decision": "{} complaint".format(status), "rejectReasonDescription": "reject reason"}},
        )
        self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
        self.assertEqual(response.json["data"]["decision"], "{} complaint".format(status))
        self.assertEqual(response.json["data"]["rejectReasonDescription"], "reject reason")

        if status in ["declined", "satisfied", "stopped"]:
            now = get_now()
            data = {"status": "accepted"}
            if RELEASE_2020_04_19 < now:
                data.update(
                    {
                        "reviewDate": now.isoformat(),
                        "reviewPlace": "some",
                    }
                )
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": data},
            )
            self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
            self.assertEqual(response.json["data"]["status"], "accepted")
            if RELEASE_2020_04_19 < now:
                self.assertEqual(response.json["data"]["reviewPlace"], "some")
                self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

            now = get_now()
            data = {"decision": "accepted:{} complaint".format(status)}
            if RELEASE_2020_04_19 > now:
                data.update(
                    {
                        "reviewDate": now.isoformat(),
                        "reviewPlace": "some",
                    }
                )
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": data},
            )
            self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
            self.assertEqual(response.json["data"]["decision"], "accepted:{} complaint".format(status))
            if RELEASE_2020_04_19 > now:
                self.assertEqual(response.json["data"]["reviewPlace"], "some")
                self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

            self.app.authorization = ("Basic", ("token", ""))
            response = self.app.patch_json(
                "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
                status=403,
            )
            self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
            self.assertEqual(response.json["errors"][0]["description"], "Can't update award with accepted complaint")

        self.app.authorization = ("Basic", ("reviewer", ""))
        now = get_now()
        data = {"status": status}
        if RELEASE_2020_04_19 < now:
            if status in ["invalid", "stopped"]:
                data.update({"rejectReason": "tenderCancelled", "rejectReasonDescription": "reject reason description"})
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
            {"data": data},
        )
        self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
        self.assertEqual(response.json["data"]["status"], status)

        if status == "satisfied":
            response = self.app.get("/tenders/{}".format(self.tender_id))
            self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
            self.assertEqual(response.json["data"]["status"], "active.qualification")

            self.app.authorization = ("Basic", ("broker", ""))
            # try to switch to qualification.stand-still
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
                {"data": {"status": "active.qualification.stand-still"}},
                status=403,
            )
            self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
            self.assertEqual(
                response.json["errors"][0]["description"],
                "Can't switch to 'active.qualification.stand-still' before resolve all complaints",
            )

            # resolve complaint
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                    self.tender_id, self.award_id, complaint["id"], self.tender_token
                ),
                {
                    "data": {
                        "status": "resolved",
                        "tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно",
                    }
                },
            )
            self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

            # switch to qualification.stand-still after complaint resolution
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
                {"data": {"status": "active.qualification.stand-still"}},
            )
            self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))


def review_tender_award_stopping_complaint(self):
    self.set_status("active.qualification.stand-still")
    now = get_now()
    if RELEASE_2020_04_19 > now:
        statuses = ["stopped", "declined", "mistaken", "invalid", "satisfied"]
    else:
        statuses = ["declined", "invalid", "satisfied"]
    for status in statuses:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
            {"data": test_tender_below_complaint},
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        complaint = response.json["data"]
        owner_token = response.json["access"]["token"]

        if RELEASE_2020_04_19 < get_now():
            self.assertEqual(response.json["data"]["status"], "draft")
            with change_auth(self.app, ("Basic", ("bot", ""))):
                response = self.app.patch_json(
                    "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                    {"data": {"status": "pending"}},
                )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "pending")

        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")

        self.app.authorization = ("Basic", ("reviewer", ""))
        now = get_now()
        data = {"decision": "decision", "status": status}
        if RELEASE_2020_04_19 < now:
            if status in ["invalid", "stopped"]:
                data.update({"rejectReason": "tenderCancelled", "rejectReasonDescription": "reject reason description"})
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
            {"data": data},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], status)
        self.assertEqual(response.json["data"]["decision"], "decision")


def create_tender_award_complaint(self):
    self.set_status("active.qualification.stand-still")

    complaint_data = deepcopy(test_tender_below_draft_claim)
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    self.assertEqual(complaint["status"], "draft")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]
    self.assertEqual(complaint["author"]["name"], test_tender_below_organization["name"])
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])

    if RELEASE_2020_04_19 < get_now():
        self.assertEqual(response.json["data"]["status"], "draft")
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    complaint_details = response.json["data"]["awards"][0]["complaints"][0]
    self.assertNotIn("owner", complaint_details)
    self.assertNotIn("owner_token", complaint_details)  # CS-5342

    # set complaint status to invalid to be able to cancel the tender
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], complaint_token
            ),
            {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
        )
        self.assertEqual(response.status, "200 OK")

    self.set_status("active.awarded")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.cancel_tender()

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_claim},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (cancelled) tender status"
    )


def create_tender_award_complaint_not_active(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, self.award_id), {"data": {"status": "cancelled"}}
    )
    self.app.authorization = auth

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][-1]

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_id, self.bid_token),
        {"data": test_tender_below_complaint},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't add complaint in current (active.qualification) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    awards_ids = [award["id"] for award in response.json["data"] if award["status"] == "pending"]

    for award_id in awards_ids:
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
    # switch to qualification.stand-still
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.qualification.stand-still"}},
    )

    # time shift
    # make post complaint not in complaintPeriod
    tender = self.mongodb.tenders.get(self.tender_id)
    tender["awards"][-1]["complaintPeriod"]["endDate"] = tender["awards"][-1]["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, award_id, self.bid_token),
        {"data": test_tender_below_complaint},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Can add complaint only in complaintPeriod", "location": "body", "name": "data"}],
    )


def get_tender_award_complaint(self):
    self.set_status("active.qualification.stand-still")
    bid_token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"])
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], complaint)

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/some_id".format(self.tender_id, self.award_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}])

    response = self.app.get("/tenders/some_id/awards/some_id/complaints/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


def bot_patch_tender_award_complaint(self):
    self.set_status("active.qualification.stand-still")
    bot_patch_tender_award_complaint_base(self)


def bot_patch_tender_award_complaint_forbidden(self):
    self.set_status("active.qualification.stand-still")
    bot_patch_tender_award_complaint_forbidden_base(self)


# TenderLotAwardComplaintResourceTest


def create_tender_lot_award_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_complaint},
    )
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]
    self.assertEqual(complaint["author"]["name"], test_tender_below_organization["name"])
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])
    self.assertIn("relatedLot", complaint)
    self.assertEqual(complaint["relatedLot"], self.initial_bids[0]["lotValues"][0]["relatedLot"])

    if RELEASE_2020_04_19 < get_now():
        self.assertEqual(response.json["data"]["status"], "draft")

        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    # set complaint status to invalid to be able to cancel the tender
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], complaint_token
            ),
            {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
        )
        self.assertEqual(response.status, "200 OK")

    self.set_status("active.awarded")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.cancel_tender()

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_claim},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (cancelled) tender status"
    )


def patch_tender_lot_award_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )

    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"status": "stopping", "cancellationReason": "reason"}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "stopping")
    self.assertEqual(response.json["data"]["cancellationReason"], "reason")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/some_id?acc_token={}".format(self.tender_id, self.award_id, owner_token),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual((response.status, response.content_type), ("404 Not Found", "application/json"))
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}])

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint from stopping to cancelled status"
    )

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"])
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "stopping")
    self.assertEqual(response.json["data"]["cancellationReason"], "reason")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    self.set_status("complete")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint in current (complete) tender status"
    )


def patch_tender_award_in_qualification_st_st(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    # Get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    comparable = min((tender["maxAwardsCount"], len(self.initial_bids)))
    self.assertEqual(len(response.json["data"]), comparable)

    for award in response.json["data"]:
        self.assertEqual(award["status"], "pending")

    # patch all awards to active
    for award in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    for award in response.json["data"]:
        self.assertEqual(award["status"], "active")
    len_award = len(response.json["data"])

    # patch all award to cancelled in active.qualification.stand-still status
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, response.json["data"][0]["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(len(response.json["data"]), len_award * 2)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertNotIn("endDate", response.json["data"]["awardPeriod"])


def award_complaint_document_in_active_qualification(self):
    self.set_status("active.qualification")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, self.tender_token
        ),
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
        response.json["errors"][0]["description"], "Can't add document in current (draft) complaint status"
    )
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
        ),
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
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents".format(self.tender_id, self.award_id, self.complaint_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents?all=true".format(
            self.tender_id, self.award_id, self.complaint_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?download=some_id".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}])

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}?download={}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.get(
        "/tenders/{}/awards/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.award_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token
        ),
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
        response.json["errors"][0]["description"], "Can't add document in current (complete) tender status"
    )


def patch_tender_lot_award_lots_none(self):
    request_path = "/tenders/{}/awards".format(self.tender_id)
    bid = {"suppliers": [test_tender_below_organization], "status": "pending", "lotID": self.initial_lots[0]["id"]}
    if getattr(self, "initial_bids", None):
        bid["bid_id"] = self.initial_bids[0]["id"]

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json(request_path, {"data": bid})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"lots": [None]}}, status=422
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "lots", "description": [["This field is required."]]}]
    )
