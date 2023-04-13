# -*- coding: utf-8 -*-
from datetime import timedelta
from webtest import AppError
import mock

from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.pricequotation.constants import QUALIFICATION_DURATION
from openprocurement.tender.pricequotation.tests.base import test_tender_pq_organization


def create_tender_award_invalid(self):
    self.app.authorization = ("Basic", ("token", ""))
    request_path = "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token)
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
                    }
                ],
                "location": "body",
                "name": "suppliers",
            },
            {"description": ["This field is required."], "location": "body", "name": "bid_id"},
        ],
    )

    response = self.app.post_json(
        "/tenders/some_id/awards",
        {"data": {"suppliers": [test_tender_pq_organization], "bid_id": self.initial_bids[0]["id"]}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/some_id/awards", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {"data": {"suppliers": [test_tender_pq_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't create award in current (complete) tender status"
    )


def create_tender_award(self):
    with change_auth(self.app, ("Basic", ("token", ""))):
        request_path = "/tenders/{}/awards".format(self.tender_id)
        response = self.app.post_json(
            request_path,
            {"data": {"suppliers": [test_tender_pq_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        award = response.json["data"]
        self.assertEqual(award["suppliers"][0]["name"], test_tender_pq_organization["name"])
        self.assertIn("id", award)
        self.assertIn(award["id"], response.headers["Location"])

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][-1], award)

    award_request_path = "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token)

    response = self.app.patch_json(award_request_path, {"data": {"status": "active"}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json['status'], "error")
    self.assertEqual(
        response.json['errors'],
        [{
            'description': "Can't change award status to active from pending",
            'location': 'body',
            'name': 'data'
        }]
    )

    response = self.app.patch_json(award_request_path, {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def patch_tender_award(self):
    request_path = "/tenders/{}/awards".format(self.tender_id)
    response = self.app.patch_json(
        "/tenders/{}/awards/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "award_id"}]
    )

    response = self.app.patch_json(
        "/tenders/some_id/awards/some_id?acc_token={}".format(self.tender_token),
        {"data": {"status": "unsuccessful"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )
    award_id = self.award_ids[-1]
    token = self.initial_bids_tokens[0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, token),
        {"data": {"awardStatus": "unsuccessful"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "awardStatus", "description": "Rogue field"}]
    )

    token = self.initial_bids_tokens[0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)
    new_award = response.json["data"][-1]

    token = self.initial_bids_tokens[1]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], token),
        {"data": {"title": "title", "description": "description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["title"], "title")
    self.assertEqual(response.json["data"]["description"], "description")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Location", response.headers)

    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)

    tender_token = self.mongodb.tenders.get(self.tender_id)['owner_token']
    tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
    gen_award_id = tender['awards'][-1]['id']

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, gen_award_id, tender_token),
        {"data": {"title": "one"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "one")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, gen_award_id, tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "one")

    self.set_status("complete")

    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], 469.0)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update award in current (complete) tender status"
    )


def tender_award_transitions(self):
    award_id = self.award_ids[-1]
    tender_token = self.mongodb.tenders.get(self.tender_id)['owner_token']
    bid_token = self.initial_bids_tokens[0]
    # pending -> cancelled
    for token_ in (tender_token, bid_token):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, token_),
            {"data": {"status": "cancelled"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")

    # first award: tender_owner: forbidden
    for status in ('active', 'unsuccessful'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"], [{
                "location": "url",
                "name": "permission",
                "description": "Forbidden"
            }]
        )
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
        {"data": {"status": 'unsuccessful'}},
    )
    self.assertEqual(response.status, "200 OK")
    # bidOwner: unsuccessful -> ('active', 'cancelled', 'pending') must be forbidden
    for status in ('active', 'cancelled', 'pending'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
            {"data": {"status": status}},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"], [{
                "location": "url",
                "name": "permission",
                "description": "Forbidden"
            }]
        )
    # tenderOwner: unsuccessful -> ('active', 'cancelled', 'pending') must be forbidden
    for status in ('active', 'cancelled', 'pending'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
            {"data": {"status": status}},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"], [{
                "location": "body",
                "name": "data",
                "description": "Can't update award in current (unsuccessful) status"
            }]
        )
    tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']

    award_id = tender['awards'][-1]['id']
    bid_token = self.initial_bids_tokens[1]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": 'active'}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
        {"data": {"status": 'active'}},
    )
    self.assertEqual(response.status, "200 OK")
    for status in ('unsuccessful', 'cancelled', 'pending'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
            {"data": {"status": status}},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
    for status in ('unsuccessful', 'pending'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
            {"data": {"status": status}},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": 'cancelled'}},
    )
    self.assertEqual(response.status, "200 OK")
    tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
    award_id = tender['awards'][-1]['id']
    for status in ('unsuccessful', 'cancelled', 'active'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
            {"data": {"status": status}},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": 'cancelled'}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": 'unsuccessful'}},
    )
    self.assertEqual(response.status, "200 OK")


def check_tender_award(self):
    # get bids
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    bids = response.json["data"]
    sorted_bids = sorted(bids, key=lambda bid: bid["value"]['amount'])

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # check award
    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["suppliers"][0]["name"], sorted_bids[0]["tenderers"][0]["name"])
    self.assertEqual(
        response.json["data"]["suppliers"][0]["identifier"]["id"], sorted_bids[0]["tenderers"][0]["identifier"]["id"]
    )
    self.assertEqual(response.json["data"]["bid_id"], sorted_bids[0]["id"])

    # cancel award
    token = self.initial_bids_tokens[0]
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # check new award
    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["suppliers"][0]["name"], sorted_bids[1]["tenderers"][0]["name"])
    self.assertEqual(
        response.json["data"]["suppliers"][0]["identifier"]["id"], sorted_bids[1]["tenderers"][0]["identifier"]["id"]
    )
    self.assertEqual(response.json["data"]["bid_id"], sorted_bids[1]["id"])


def check_tender_award_disqualification(self):
    # get bids
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    bids = response.json["data"]
    sorted_bids = sorted(bids, key=lambda bid: bid["value"]['amount'])

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award = [i for i in response.json["data"] if i["status"] == "pending"][0]
    award_id = award['id']
    # check award
    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["suppliers"][0]["name"], sorted_bids[0]["tenderers"][0]["name"])
    self.assertEqual(
        response.json["data"]["suppliers"][0]["identifier"]["id"], sorted_bids[0]["tenderers"][0]["identifier"]["id"]
    )
    self.assertEqual(response.json["data"]["bid_id"], sorted_bids[0]["id"])

    # wait 2 days
    tender = self.mongodb.tenders.get(self.tender_id)
    date = calculate_tender_business_date(get_now(), -QUALIFICATION_DURATION, tender, working_days=True).isoformat()
    tender['awards'][0]['date'] = date
    self.mongodb.tenders.save(tender)

    self.check_chronograph()

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # # get pending award
    awards = response.json['data']
    self.assertEqual(len(awards), 2)
    self.assertEqual(awards[0]['status'], "unsuccessful")
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # check new award
    response = self.app.get("/tenders/{}/awards/{}".format(self.tender_id, award_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["suppliers"][0]["name"], sorted_bids[1]["tenderers"][0]["name"])
    self.assertEqual(
        response.json["data"]["suppliers"][0]["identifier"]["id"], sorted_bids[1]["tenderers"][0]["identifier"]["id"]
    )
    self.assertEqual(response.json["data"]["bid_id"], sorted_bids[1]["id"])


def check_tender_award_cancellation(self):
    # get bids
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    bids = response.json["data"]
    bid_token = self.initial_bids_tokens[0]
    tender_token = self.mongodb.tenders.get(self.tender_id)['owner_token']
    sorted_bids = sorted(bids, key=lambda bid: bid["value"]['amount'])

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award = [i for i in response.json["data"] if i["status"] == "pending"][0]
    award_id = award['id']
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json['data']['status'], "active")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": "cancelled"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json['data']['status'], "cancelled")
    old_award = response.json['data']

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))

    award = [i for i in response.json["data"] if i["status"] == "pending"][-1]
    award_id = award['id']
    self.assertEqual(old_award['bid_id'], award['bid_id'])

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json['status'], "error")

    for status in ('active', 'cancelled'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
            {"data": {"status": status}},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json['status'], "error")
        self.assertEqual(response.json['errors'], [{
            'description': "Can't change award status to {} from pending".format(status),
            'location': 'body',
            'name': 'data'
        }])
