from copy import deepcopy

from openprocurement.tender.core.tests.utils import change_auth
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
        "/tenders/some_id/awards",
        {"data": {"suppliers": [test_tender_pq_organization], "bid_id": self.initial_bids[0]["id"]}},
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

    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_pq_organization],
                "status": "pending",
                "bid_id": self.initial_bids[0]["id"],
            }
        },
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
            {
                "data": {
                    "suppliers": [test_tender_pq_organization],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                }
            },
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

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award['id']}/documents")
    response = self.app.patch_json(
        award_request_path,
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(award_request_path, {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, "200 OK")

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = response.json["data"][-1]['id']
    award_request_path = f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}"

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(award_request_path, {"data": {"status": "unsuccessful", "qualified": False}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get next bidder pending award
    award_id = response.json["data"][-1]['id']
    award_request_path = f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}"
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(award_request_path, {"data": {"status": "unsuccessful", "qualified": False}})
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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "award_id"}])

    response = self.app.patch_json(
        "/tenders/some_id/awards/some_id?acc_token={}".format(self.tender_token),
        {"data": {"status": "unsuccessful"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])
    award_id = self.award_ids[-1]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"awardStatus": "unsuccessful"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "awardStatus", "description": "Rogue field"}]
    )

    token = list(self.initial_bids_tokens.values())[0]
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
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

    token = list(self.initial_bids_tokens.values())[1]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], token),
        {"data": {"title": "title", "description": "description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"title": "title", "description": "description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["title"], "title")
    self.assertEqual(response.json["data"]["description"], "description")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], token),
        {"data": {"status": "active", "qualified": True}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{new_award['id']}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True}},
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

    self.add_sign_doc(self.tender_id, tender_token, docs_url=f"/awards/{gen_award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, gen_award_id, tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
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
        {"data": {"status": "unsuccessful", "qualified": False}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update award in current (complete) tender status"
    )


def move_award_contract_to_contracting(self):
    tender = self.mongodb.tenders.get(self.tender_id)

    criterion = tender["criteria"][0]
    criterion["relatesTo"] = "item"
    criterion["relatedItem"] = tender["items"][0]["id"]

    requirement_group = criterion["requirementGroups"][0]

    requirement = requirement_group["requirements"][0]
    self.assertEqual(requirement["status"], "active")

    # Cancelled requirement with the same id
    # that should be ignored on attributes generation
    cancelled_requirement = deepcopy(requirement)
    cancelled_requirement["status"] = "cancelled"
    requirement_group["requirements"].append(cancelled_requirement)

    self.mongodb.tenders.save(tender)

    award_id = self.award_ids[-1]

    bid_token = list(self.initial_bids_tokens.values())[0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"title": "title", "description": "description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["title"], "title")
    self.assertEqual(response.json["data"]["description"], "description")

    tender_data = self.mongodb.tenders.get(self.tender_id)
    tender_data["bids"][0]["items"] = [
        {
            "id": tender_data["items"][0]["id"],
            "description": "Комп’ютерне обладнання для біда",
            "quantity": 10,
            "unit": {
                "name": "кг",
                "code": "KGM",
                "value": {"amount": 45},
            },
        }
    ]
    self.mongodb.tenders.save(tender_data)

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract_id = response.json["data"]["contracts"][0]["id"]

    response = self.app.get(f"/contracts/{contract_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    contract_fields = {
        "id",
        "awardID",
        "contractID",
        "dateCreated",
        "dateModified",
        "items",
        "tender_id",
        "owner",
        "status",
        "suppliers",
        "value",
        "buyer",
        "contractTemplateName",
    }

    self.assertEqual(contract_fields, set(response.json["data"].keys()))
    item = response.json["data"]["items"][0]
    self.assertIn("attributes", item)
    self.assertEqual(len(item["attributes"]), 9)
    self.assertIn("value", item["attributes"][0])
    self.assertEqual(item["description"], "Комп’ютерне обладнання для біда")
    self.assertEqual(item["quantity"], 10)
    self.assertEqual(item["unit"]["value"]["amount"], 45)

    response = self.app.put_json(
        f"/contracts/{contract_id}/buyer/signer_info?acc_token={self.tender_token}",
        {
            "data": {
                "name": "Test Testovich",
                "telephone": "+380950000000",
                "email": "example@email.com",
                "iban": "1" * 15,
                "authorizedBy": "документ який дозволяє",
                "position": "статус",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.put_json(
        f"/contracts/{contract_id}/suppliers/signer_info?acc_token={bid_token}",
        {
            "data": {
                "name": "Test Testovich",
                "telephone": "+380950000000",
                "email": "example@email.com",
                "iban": "1" * 15,
                "authorizedBy": "документ який дозволяє",
                "position": "статус",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    item["unit"]["value"] = {"amount": 10, "currency": "UAH", "valueAddedTaxIncluded": False}

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {
            "data": {
                "items": [item],
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Total amount of unit values must be no more than contract.value.amount and no less than net contract amount",
    )

    item["unit"]["value"] = {"amount": 46.9, "currency": "UAH", "valueAddedTaxIncluded": False}  # contract.value 469

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {
            "data": {
                "items": [item],
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["contracts"][0]["status"], "active")
    self.assertEqual(response.json["data"]["status"], "complete")


def tender_award_transitions(self):
    award_id = self.award_ids[-1]
    tender_token = self.mongodb.tenders.get(self.tender_id)['owner_token']
    bid_token = list(self.initial_bids_tokens.values())[0]
    # pending -> cancelled: forbidden
    for token_ in (tender_token, bid_token):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, token_),
            {"data": {"status": "cancelled"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")

    # first award: bid_owner: forbidden
    for status in ('active', 'unsuccessful'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"], [{"location": "url", "name": "permission", "description": "Forbidden"}]
        )

    # bidOwner: unsuccessful -> ('active', 'cancelled', 'pending') must be forbidden
    for status in ('active', 'cancelled', 'pending'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"], [{"location": "url", "name": "permission", "description": "Forbidden"}]
        )
    # activate award
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
        {"data": {"status": "active", "qualified": True}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    for status in ('unsuccessful', 'cancelled', 'pending'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, bid_token),
            {"data": {"status": status, "qualified": False}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
    for status in ('unsuccessful', 'pending'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
            {"data": {"status": status, "qualified": False}},
            status=403,
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
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")

    # tenderOwner: unsuccessful -> ('active', 'cancelled', 'pending') must be forbidden
    for status in ('active', 'cancelled', 'pending'):
        patch_data = {"status": status}
        if status == 'active':
            patch_data["qualified"] = True
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
            {"data": patch_data},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Can't update award in current (unsuccessful) status",
                }
            ],
        )

    # first bidder became unsuccessful, the second one has pending award
    tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
    award_id = tender['awards'][-1]['id']

    # activate second award
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")

    # check that we have second contract
    tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
    self.assertEqual(len(tender.get("contracts")), 2)

    # cancel second winner
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": 'cancelled'}},
    )
    self.assertEqual(response.status, "200 OK")

    # first bidder became unsuccessful, the second one was cancelled and new pending award was generated
    tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
    award_id = tender['awards'][-1]['id']
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")

    # the procedure should become unsuccessful
    self.check_chronograph()
    tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
    self.assertEqual(tender["status"], "unsuccessful")


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
    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
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


def check_tender_award_cancellation(self):
    # get bids
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    bids = response.json["data"]
    bid_token = list(self.initial_bids_tokens.values())[0]
    tender_token = self.mongodb.tenders.get(self.tender_id)['owner_token']
    sorted_bids = sorted(bids, key=lambda bid: bid["value"]['amount'])

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award = [i for i in response.json["data"] if i["status"] == "pending"][0]
    award_id = award['id']
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
        {"data": {"status": "active", "qualified": True}},
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
        {"data": {"status": "active", "qualified": True}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json['status'], "error")
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")

    for status in ('active', 'cancelled'):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, tender_token),
            {"data": {"status": status, "qualified": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    # next bidder award was generated
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.json["data"][-1]["status"], "pending")
