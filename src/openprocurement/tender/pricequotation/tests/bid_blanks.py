from copy import deepcopy
from openprocurement.tender.pricequotation.tests.base import (
    test_tender_pq_organization,
    test_tender_pq_requirement_response_valid,
    test_tender_pq_requirement_response,
    test_tender_pq_response_1,
    test_tender_pq_response_2,
    test_tender_pq_response_3,
    test_tender_pq_response_4,
)
from openprocurement.tender.pricequotation.tests.utils import copy_criteria_req_id
from openprocurement.tender.core.tests.utils import change_auth


def create_tender_bid_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/bids", {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500}}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
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

    response = self.app.post_json(request_path, {"data": {"tenderers": [{"identifier": "invalid_value"}]}}, status=422)
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

    response = self.app.post_json(request_path, {"data": {"tenderers": [{"identifier": {}}],
                                                          "requirementResponses": test_tender_pq_requirement_response}},
                                  status=422)
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
                    }
                ],
                "location": "body",
                "name": "tenderers",
            }
        ],
    )

    response = self.app.post_json(
        request_path, {"data": {"tenderers": [{"name": "name", "identifier": {"uri": "invalid_value"}}],
                                "requirementResponses": test_tender_pq_requirement_response}}, status=422
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
                "name": "tenderers",
            }
        ],
    )

    response = self.app.post_json(request_path,
                                  {"data": {"tenderers": [test_tender_pq_organization],
                                            "requirementResponses": test_tender_pq_requirement_response}},
                                  status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "value"}],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500, "valueAddedTaxIncluded": False},
                  "requirementResponses": test_tender_pq_requirement_response}},
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
                    "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of tender"
                ],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500, "currency": "USD"},
                  "requirementResponses": test_tender_pq_requirement_response}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["currency of bid should be identical to currency of value of tender"],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.post_json(
        request_path, {"data": {"tenderers": test_tender_pq_organization, "value": {"amount": 500}}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("invalid literal for int() with base 10", response.json["errors"][0]["description"])

    response = self.app.post_json(
        request_path, {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500}}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "requirementResponses"}],
    )

    non_shortlist_org = deepcopy(test_tender_pq_organization)
    non_shortlist_org["identifier"]["id"] = "69"
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [non_shortlist_org], "value": {"amount": 500},
                  "requirementResponses": test_tender_pq_requirement_response}},
        status=403,
    )
    self.assertEqual(
        response.json,
        {'status': 'error', 'errors': [
            {'location': 'body', 'name': 'data', 'description': "Can't add bid if tenderer not in shortlistedFirms"}]}
    )


def create_tender_bid(self):

    # Revert tender to statuses ('draft', 'draft.unsuccessful', 'draft.publishing')
    data = self.mongodb.tenders.get(self.tender_id)
    current_status = data.get('status')
    criteria = data.pop('criteria')

    for status in ('draft', 'draft.publishing', 'draft.unsuccessful'):
        data['status'] = status
        self.mongodb.tenders.save(data)

        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "tenderers": [test_tender_pq_organization],
                    "value": {"amount": 500},
                    "requirementResponses": test_tender_pq_requirement_response_valid
                }
            },
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json['errors'],
                         [{"location": "body",
                           "name": "data",
                           "description": "Can't add bid in current ({}) tender status".format(status)}])

    # Restore tender to 'draft' status
    data['status'] = "draft.publishing"
    data['criteria'] = criteria
    self.mongodb.tenders.save(data)

    # switch to tendering
    with change_auth(self.app, ("Basic", ("pricequotation", ""))):
        response = self.app.patch_json(
            "/tenders/{}".format(self.tender_id),
            {"data": {"status": "active.tendering"}}
        )
        date_modified = response.json["data"].get("dateModified")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_tender_pq_requirement_response,
            "documents": None,
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], test_tender_pq_organization["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])

    self.assertEqual(self.mongodb.tenders.get(self.tender_id).get("dateModified"), date_modified)

    # post second
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 501},
                  "requirementResponses": test_tender_pq_requirement_response}},
    )
    self.assertEqual(response.status, "201 Created")

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500},
                  "requirementResponses": test_tender_pq_requirement_response}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (complete) tender status")


def requirement_response_validation_multiple_criterias(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    rr = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], rr)

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": rr,
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[0]['value'] = 'ivalid'
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response
        }},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'], [{
            'description': ['Value "ivalid" does not match expected value "Розчин для інфузій" '
                            f'in requirement {test_response[0]["requirement"]["id"]}'],
            'location': 'body',
            'name': 'requirementResponses'
        }]
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[1]['value'] = '4'
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response
        }},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'], [{
            'description': ['Value 4 is lower then minimal required 5 '
                            f'in requirement {test_response[1]["requirement"]["id"]}'],
            'location': 'body',
            'name': 'requirementResponses'
        }]
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    missed = test_response.pop()
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response
        }},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'], [{
            'description': [f"Missing references for criterias: ['{missed['requirement']['id']}']"],
            'location': 'body',
            'name': 'requirementResponses'
        }]
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    del test_response[2]["values"]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response
        }},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'], [{
            'description': ['response required at least one of field ["value", "values"]'],
            'location': 'body',
            'name': 'requirementResponses'
        }]
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[2]["value"] = "ivalid"
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response
        }},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'], [{
            'description': ["field 'value' conflicts with 'values'"],
            'location': 'body',
            'name': 'requirementResponses'
        }]
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[2]["values"] = ["Відповідь4"]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response
        }},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'], [{
            'description': [f'Count of items lower then minimal required 2 '
                            f'in requirement {test_response[2]["requirement"]["id"]}'],
            'location': 'body',
            'name': 'requirementResponses'
        }]
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[2]["values"] = ["Відповідь1", "Відповідь2", "Відповідь3", "Відповідь4"]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response
        }},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'], [{
            'description': [f'Count of items higher then maximum required 3 '
                            f'in requirement {test_response[2]["requirement"]["id"]}'],
            'location': 'body',
            'name': 'requirementResponses'
        }]
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[2]["values"] = ["Відповідь1", "Відповідь2", "Відповідь5"]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response
        }},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'], [{
            'description': [f'Values isn\'t in requirement {test_response[2]["requirement"]["id"]}'],
            'location': 'body',
            'name': 'requirementResponses'
        }]
    )



def requirement_response_validation_multiple_groups(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    rr = deepcopy(test_tender_pq_response_2)
    copy_criteria_req_id(response.json["data"]["criteria"], rr)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": rr,
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def requirement_response_validation_multiple_groups_multiple_requirements(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    rr = deepcopy(test_tender_pq_response_3)
    copy_criteria_req_id(response.json["data"]["criteria"], rr)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": rr,
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def requirement_response_validation_one_group_multiple_requirements(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    rr = deepcopy(test_tender_pq_response_4)
    copy_criteria_req_id(tender["criteria"], rr)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": rr,
        }},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'], [{
            'description': ['Value "Порошок" does not match expected value "Розчин" '
                            f'in requirement {rr[0]["requirement"]["id"]}'],
            'location': 'body',
            'name': 'requirementResponses'
        }]
    )

    rr = deepcopy(test_tender_pq_response_4)
    copy_criteria_req_id(tender["criteria"], rr)
    rr[0]['value'] = 'Розчин'
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": rr,
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def patch_tender_bid(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_pq_organization], "status": "draft", "value": {"amount": 500},
                  "requirementResponses": test_tender_pq_requirement_response}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"value": {"amount": 60000}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["value of bid should be less than value of tender"],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"tenderers": [{"name": "Державне управління управлінням справами"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], bid["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    non_shortlist_org = deepcopy(test_tender_pq_organization)
    non_shortlist_org["identifier"]["id"] = "69"
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{bid['id']}?acc_token={token}",
        {"data": {"tenderers": [non_shortlist_org]}},
        status=403,
    )
    self.assertEqual(
        response.json,
        {'status': 'error', 'errors': [
            {'location': 'body', 'name': 'data',
             'description': "Can't update bid if tenderer not in shortlistedFirms"}]}
    )

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"value": {"amount": 500}, "tenderers": [test_tender_pq_organization]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], bid["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"value": {"amount": 400}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], 400)
    self.assertNotEqual(response.json["data"]["date"], bid["date"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotEqual(response.json["data"]["date"], bid["date"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"status": "draft"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid to (draft) status")

    response = self.app.patch_json(
        "/tenders/{}/bids/some_id".format(self.tender_id), {"data": {"value": {"amount": 400}}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.patch_json("/tenders/some_id/bids/some_id", {"data": {"value": {"amount": 400}}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    self.set_status("complete")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], 400)

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"value": {"amount": 400}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid in current (complete) tender status")


def get_tender_bid(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500},
                  "requirementResponses": test_tender_pq_requirement_response}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

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

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    bid_data = response.json["data"]
    self.assertEqual(bid_data, bid)

    response = self.app.get("/tenders/{}/bids/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.get("/tenders/some_id/bids/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.delete(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't delete bid in current (active.qualification) tender status"
    )


def delete_tender_bid(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500},
                  "requirementResponses": test_tender_pq_requirement_response}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

    response = self.app.delete(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], 'error')
    self.assertEqual(response.json["errors"], [
        {"location": "body", "name": "data", "description": "Can't delete bid in Price Quotation tender"}
    ])

    response = self.app.delete("/tenders/{}/bids/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.delete("/tenders/some_id/bids/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def get_tender_tenderers(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500},
                  "requirementResponses": test_tender_pq_requirement_response}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    response = self.app.get("/tenders/{}/bids".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bids in current (active.tendering) tender status"
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], bid)

    response = self.app.get("/tenders/some_id/bids", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def bid_Administrator_change(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_pq_organization],
                  "value": {"amount": 500},
                  "requirementResponses": test_tender_pq_requirement_response}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    self.app.authorization = ("Basic", ("administrator", ""))
    self.app.patch_json(
        "/tenders/{}/bids/{}".format(self.tender_id, bid["id"]),
        {"data": {"tenderers": [{"identifier": {"id": "00000000"}}]}},
        status=403
    )

    response = self.app.patch_json(
        "/tenders/{}/bids/{}".format(self.tender_id, bid["id"]),
        {"data": {"tenderers": [{"identifier": {"legalName": "ТМ Валєра"}}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tenderers"][0]["identifier"]["legalName"], "ТМ Валєра")


def patch_tender_bid_document(self):
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    
    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    self.set_status("active.awarded")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (active.awarded) tender status"
    )


def create_tender_bid_document_nopending(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500},
                  "requirementResponses": test_tender_pq_requirement_response_valid}},
    )

    bid = response.json['data']
    token = response.json['access']['token']
    bid_id = bid['id']

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{bid_id}?acc_token={token}",
        {"data": {"status": "active"}},
    )

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    self.set_status("active.tendering", 'end')
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, token),
        {"data": {
            "title": "name_3.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document because award of bid is not in pending state"
    )

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document because award of bid is not in pending state"
    )
