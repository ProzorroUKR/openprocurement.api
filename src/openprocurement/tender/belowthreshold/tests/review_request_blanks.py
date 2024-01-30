from datetime import timedelta
from uuid import uuid4

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_organization
from openprocurement.contracting.econtract.tests.data import test_signer_info


def create_review_request(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender_status = response.json["data"]["status"]

    if tender_status == "active.qualification":
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "value": {"amount": 500},
                    "lotID": self.initial_lots[0]["id"],
                }
            },
        )
        award_id = response.json["data"]["id"]
        self.assertEqual(response.status, "201 Created")

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.app.authorization = auth

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token=wrong_token",
        {"data": {}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{'location': 'url', 'name': 'permission', 'description': 'Forbidden'}])

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("broker2", ""))

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token={self.tender_token}",
        {"data": {}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{'location': 'url', 'name': 'permission', 'description': 'Forbidden'}])

    self.app.authorization = auth

    tender_data = self.mongodb.tenders.get(self.tender_id)
    tender_data["status"] = "active.tendering"
    self.mongodb.tenders.save(tender_data)

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token={self.tender_token}",
        {"data": {}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Review request can be created only in "
                "('active.enquiries', 'active.qualification', 'active.awarded') tender statuses",
            }
        ],
    )

    tender_data["status"] = self.initial_status
    inspector = tender_data["inspector"]
    del tender_data["inspector"]
    self.mongodb.tenders.save(tender_data)

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token={self.tender_token}",
        {"data": {}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't create reviewRequest without inspector",
            }
        ],
    )

    tender_data["inspector"] = inspector
    self.mongodb.tenders.save(tender_data)

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token={self.tender_token}", {"data": {}}
    )
    self.assertEqual(response.status, "201 Created")
    base_fields_set = {
        "id",
        "tenderStatus",
        "dateCreated",
    }
    self.assertEqual(set(response.json["data"].keys()), base_fields_set)
    self.assertEqual(response.json["data"]["tenderStatus"], self.initial_status)

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertIn("reviewRequests", response.json["data"])

    response = self.app.get(f"/tenders/{self.tender_id}/review_requests")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)
    self.assertNotIn("next_check", response.json["data"])

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token={self.tender_token}",
        {"data": {}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Disallowed create review request while existing another unanswered review request",
            }
        ],
    )


def patch_review_request(self):
    response = self.check_chronograph()
    self.assertNotIn("next_check", response.json["data"])

    response = self.app.get(f"/tenders/{self.tender_id}")
    tender_status = response.json["data"]["status"]

    if tender_status == "active.qualification":
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
            {
                "data": {
                    "suppliers": [test_tender_below_organization],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "value": {"amount": 500},
                    "lotID": self.initial_lots[0]["id"],
                }
            },
        )
        award_id = response.json["data"]["id"]
        self.assertEqual(response.status, "201 Created")

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.app.authorization = auth

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token={self.tender_token}",
        {"data": {}},
    )
    self.assertEqual(response.status, "201 Created")
    review_request_id = response.json["data"]["id"]

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/review_requests/{review_request_id}?acc_token={self.tender_token}",
        {"data": {"approved": False}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "url", "name": "permission", "description": "Forbidden"}],
    )

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("inspector", ""))

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/review_requests/not_found?acc_token={self.tender_token}",
        {"data": {"approved": False}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "url",
                "name": "reviewRequest_id",
                "description": "Not Found",
            }
        ],
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/review_requests/{review_request_id}",
        {"data": {"approved": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["approved"], False)
    self.assertIn("date", response.json["data"])
    fields_set = {
        "id",
        "tenderStatus",
        "approved",
        "dateCreated",
        "date",
    }
    self.assertEqual(set(response.json["data"].keys()), fields_set)

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("nex_check", response.json["data"])

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/review_requests/{review_request_id}",
        {"data": {"approved": True}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Disallowed re-patching review request",
            }
        ],
    )

    self.app.authorization = auth
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token={self.tender_token}",
        {"data": {}},
    )
    self.assertEqual(response.status, "201 Created")
    review_request_id = response.json["data"]["id"]

    self.app.authorization = ("Basic", ("inspector", ""))

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/review_requests/{review_request_id}",
        {"data": {"approved": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["approved"], True)

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    if response.json["data"]["status"] != "active.qualification":
        self.assertIn("next_check", response.json["data"])
    else:
        self.assertNotIn("next_check", response.json["data"])


def patch_tender_with_review_request(self):
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token={self.tender_token}",
        {"data": {}},
    )
    self.assertEqual(response.status, "201 Created")
    review_request_id = response.json["data"]["id"]

    response = self.app.get(f"/tenders/{self.tender_id}/review_requests")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {"data": {"description": "Updated description"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "With unanswered review request can be patched only ('tenderPeriod',) fields",
            }
        ],
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {
            "data": {
                "description": "Updated description",
                "tenderPeriod": {
                    "startDate": (get_now() + timedelta(days=10)).isoformat(),
                    "endDate": (get_now() + timedelta(days=16)).isoformat(),
                },
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "With unanswered review request can be patched only ('tenderPeriod',) fields",
            }
        ],
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {
            "data": {
                "tenderPeriod": {
                    "startDate": (get_now() + timedelta(days=10)).isoformat(),
                    "endDate": (get_now() + timedelta(days=16)).isoformat(),
                }
            }
        },
    )
    self.assertEqual(response.status, "200 OK")

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("inspector", ""))

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/review_requests/{review_request_id}?acc_token={self.tender_token}",
        {"data": {"approved": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["approved"], False)
    self.app.authorization = auth

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {"data": {"description": "Updated description"}},
    )
    self.assertEqual(response.status, "200 OK")


def activate_contract_with_without_approve(self):
    tender_data = self.mongodb.tenders.get(self.tender_id)
    tender_data["reviewRequests"] = [
        {
            "id": uuid4().hex,
            "tenderStatus": "active.enquiries",
            "approved": False,
        },
    ]
    self.mongodb.tenders.save(tender_data)

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards?acc_token={self.tender_token}",
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
                "value": {"amount": 500},
                "lotID": self.initial_lots[0]["id"],
            }
        },
    )
    award_id = response.json["data"]["id"]
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.app.authorization = auth

    response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    self.assertEqual(response.status, "200 OK")
    contract_id = response.json["data"][0]["id"]

    bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]

    response = self.app.put_json(
        f"/contracts/{contract_id}/buyer/signer_info?acc_token={self.tender_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{contract_id}/suppliers/signer_info?acc_token={bid_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}", {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can\'t update contract to active till inspector approve",
            }
        ],
    )

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token={self.tender_token}",
        {"data": {}},
    )
    self.assertEqual(response.status, "201 Created")
    review_request_id = response.json["data"]["id"]

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}", {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can\'t update contract to active till inspector approve",
            }
        ],
    )

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("inspector", ""))

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/review_requests/{review_request_id}",
        {"data": {"approved": False}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = auth

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}", {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can\'t update contract to active till inspector approve",
            }
        ],
    )

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/review_requests?acc_token={self.tender_token}",
        {"data": {}},
    )
    self.assertEqual(response.status, "201 Created")
    review_request_id = response.json["data"]["id"]

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("inspector", ""))

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/review_requests/{review_request_id}",
        {"data": {"approved": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["approved"], True)

    self.app.authorization = auth

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
