from copy import deepcopy
from datetime import timedelta
from unittest.mock import Mock, patch

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
)
from openprocurement.tender.core.tests.utils import (
    get_contract_template_name,
    set_bid_items,
)
from openprocurement.tender.pricequotation.tests.base import (
    test_tender_pq_organization,
    test_tender_pq_requirement_response,
    test_tender_pq_requirement_response_valid,
    test_tender_pq_response_1,
    test_tender_pq_response_2,
    test_tender_pq_response_3,
    test_tender_pq_response_4,
)
from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_short_profile,
)
from openprocurement.tender.pricequotation.tests.utils import (
    copy_criteria_req_id,
    copy_tender_items,
)


def create_tender_bid_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/bids",
        {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500}}},
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

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [{"identifier": {}}], "requirementResponses": test_tender_pq_requirement_response}},
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
                "tenderers": [{"name": "name", "identifier": {"uri": "invalid_value"}}],
                "requirementResponses": test_tender_pq_requirement_response,
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

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "requirementResponses": test_tender_pq_requirement_response,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "value"}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500, "valueAddedTaxIncluded": False},
                "requirementResponses": test_tender_pq_requirement_response,
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
                    "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of tender"
                ],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500, "currency": "USD"},
                "requirementResponses": test_tender_pq_requirement_response,
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

    non_shortlist_org = deepcopy(test_tender_pq_organization)
    non_shortlist_org["identifier"]["id"] = "69"
    bid_data = {
        "tenderers": [non_shortlist_org],
        "value": {"amount": 500},
        "requirementResponses": test_tender_pq_requirement_response,
    }
    set_bid_items(self, bid_data)
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(
        response.json,
        {
            'status': 'error',
            'errors': [{'location': 'body', 'name': 'data', 'description': "Bid is not a member of agreement"}],
        },
    )


def create_tender_bid(self):
    data = self.mongodb.tenders.get(self.tender_id)
    criteria = data.pop('criteria')

    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]

    # Revert tender to draft status
    data['status'] = 'draft'
    self.mongodb.tenders.save(data)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": test_tender_pq_requirement_response_valid,
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json['errors'],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't add bid in current (draft) tender status",
            }
        ],
    )

    # Restore tender to 'active' status
    data['status'] = "active.tendering"
    data['criteria'] = criteria
    self.mongodb.tenders.save(data)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": test_tender_pq_requirement_response,
                "documents": None,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], test_tender_pq_organization["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])

    # post second
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 501},
                "requirementResponses": test_tender_pq_requirement_response,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": test_tender_pq_requirement_response,
            }
        },
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
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": rr,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[0]['values'] = ['ivalid']
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": test_response,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [f'Values are not in requirement {test_response[0]["requirement"]["id"]}'],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[1]['value'] = '4'
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": test_response,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [
                    'Value 4 is lower then minimal required 5 '
                    f'in requirement {test_response[1]["requirement"]["id"]}'
                ],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    missed_response = test_response.pop()
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": test_response,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    missed_criterion = None
    for criterion in tender["criteria"]:
        for rg in criterion.get("requirementGroups", ""):
            for req in rg.get("requirements", ""):
                if req["id"] == missed_response["requirement"]["id"]:
                    missed_criterion = criterion
                    break
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [
                    "Responses are required for all criteria with source tenderer/winner, "
                    f"failed for criteria {missed_criterion['id']}"
                ],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    del test_response[2]["values"]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": test_response,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [{"value": "Response required at least one of field [\"value\", \"values\"]"}],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[2]["value"] = "ivalid"
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": test_response,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [{"value": "Field 'value' conflicts with 'values'"}],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[2]["values"] = ["Відповідь1", "Відповідь2", "Відповідь3", "Відповідь4"]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": test_response,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [
                    f'Count of items higher then maximum required 3 '
                    f'in requirement {test_response[2]["requirement"]["id"]}'
                ],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    test_response = deepcopy(test_tender_pq_response_1)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[2]["values"] = ["Відповідь1", "Відповідь2", "Відповідь5"]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": test_response,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [f'Values are not in requirement {test_response[2]["requirement"]["id"]}'],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_profile",
    Mock(return_value=test_tender_pq_short_profile),
)
def requirement_response_value_validation_for_expected_values(self):
    data = self.initial_data.copy()
    data.update({"status": "draft", "contractTemplateName": get_contract_template_name(self, tender=data)})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_token = response.json["access"]["token"]
    criteria_data = [
        {
            "description": "Форма випуску",
            "source": "tenderer",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES1",
            },
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
            "requirementGroups": [
                {
                    "description": "Форма випуску",
                    "requirements": [
                        {
                            "dataType": "string",
                            "expectedValues": ["Розчин для інфузій"],
                            "title": "Форма випуску",
                            "expectedMinItems": 1,
                        },
                    ],
                }
            ],
            "title": "Форма випуску",
        },
        {
            "description": "Доза діючої речовини",
            "source": "tenderer",
            "classification": {
                "scheme": " espd211",
                "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES2",
            },
            "legislation": [
                {
                    "version": "2020-04-19",
                    "identifier": {
                        "id": "922-VIII",
                        "legalName": "Закон України \"Про публічні закупівлі\"",
                        "uri": "https://zakon.rada.gov.ua/laws/show/922-19",
                    },
                    "type": "NATIONAL_LEGISLATION",
                }
            ],
            "requirementGroups": [
                {
                    "description": "Доза діючої речовини",
                    "requirements": [
                        {
                            "dataType": "integer",
                            "minValue": 5,
                            "title": "Доза діючої речовини",
                            "unit": {"code": "KGM", "name": "кілограми"},
                        }
                    ],
                }
            ],
            "title": "Доза діючої речовини",
        },
    ]
    # switch to tendering and add criteria with expectedValues array
    self.add_sign_doc(tender['id'], tender_token)
    response = self.app.patch_json(
        f"/tenders/{tender['id']}?acc_token={tender_token}",
        {
            "data": {
                "status": "active.tendering",
                "criteria": criteria_data,
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]

    # try to response value on expectedValues
    rr = [
        {
            "requirement": {"id": tender['criteria'][0]['requirementGroups'][0]['requirements'][0]['id']},
            "value": "Розчин для інфузій",
        },
        {
            "requirement": {"id": tender['criteria'][1]['requirementGroups'][0]['requirements'][0]['id']},
            "values": [5, 7, 6],
        },
    ]
    copy_criteria_req_id(tender["criteria"], rr)

    response = self.app.post_json(
        f"/tenders/{tender['id']}/bids",
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": rr,
            }
        },
        status=422,
    )
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': f"only 'values' allowed in response for requirement {tender['criteria'][0]['requirementGroups'][0]['requirements'][0]['id']}",
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    rr[0] = {
        "requirement": {"id": tender['criteria'][0]['requirementGroups'][0]['requirements'][0]['id']},
        "values": ["Розчин для інфузій"],
    }

    response = self.app.post_json(
        f"/tenders/{tender['id']}/bids",
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": rr,
            }
        },
        status=422,
    )
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': f"only 'value' allowed in response for requirement {tender['criteria'][1]['requirementGroups'][0]['requirements'][0]['id']}",
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    rr[1] = {"requirement": {"id": tender['criteria'][1]['requirementGroups'][0]['requirements'][0]['id']}, "value": 5}

    response = self.app.post_json(
        f"/tenders/{tender['id']}/bids",
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": rr,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # invalid value in response
    test_response = deepcopy(rr)
    copy_criteria_req_id(tender["criteria"], test_response)
    test_response[0]['values'] = ['ivalid']
    response = self.app.post_json(
        f"/tenders/{tender['id']}/bids",
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": test_response,
            }
        },
        status=422,
    )
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [f'Values are not in requirement {test_response[0]["requirement"]["id"]}'],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )


def requirement_response_validation_multiple_groups(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    rr = deepcopy(test_tender_pq_response_2)
    criteria = response.json["data"]["criteria"]
    copy_criteria_req_id(criteria, rr)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": rr,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [
                    "Responses are allowed for only one group of requirements per criterion, "
                    f"failed for criteria {criteria[0]['id']}"
                ],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )


def requirement_response_validation_multiple_groups_multiple_requirements(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    rr = deepcopy(test_tender_pq_response_3)
    criteria = response.json["data"]["criteria"]
    copy_criteria_req_id(criteria, rr)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": rr,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [
                    "Responses are allowed for only one group of requirements per criterion, "
                    f"failed for criteria {criteria[0]['id']}"
                ],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )


def requirement_response_validation_one_group_multiple_requirements(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    rr = deepcopy(test_tender_pq_response_4)
    copy_criteria_req_id(tender["criteria"], rr)

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {
            "data": {
                "status": "active",
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": rr,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'],
        [
            {
                'description': [f'Values are not in requirement {rr[0]["requirement"]["id"]}'],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    rr = deepcopy(test_tender_pq_response_4)
    copy_criteria_req_id(tender["criteria"], rr)
    rr[0]['values'] = ['Розчин']
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": rr,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def patch_tender_bid(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "status": "draft",
                "value": {"amount": 500},
                "requirementResponses": test_tender_pq_requirement_response,
            }
        },
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

    tenderer = deepcopy(test_tender_below_organization)
    tenderer["name"] = "Державне управління управлінням справами"
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"tenderers": [tenderer]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], bid["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"value": {"amount": 500}, "tenderers": [test_tender_pq_organization]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], bid["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    bid["items"][0]["quantity"] = 4  # items values 4 * 100
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"value": {"amount": 400}, "items": bid["items"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 4)
    self.assertEqual(response.json["data"]["date"], bid["date"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token), {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")
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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

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
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": test_tender_pq_requirement_response,
            }
        },
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
    bid["status"] = "active"
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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.delete(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't delete bid in current (active.qualification) tender status"
    )


def delete_tender_bid(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": test_tender_pq_requirement_response,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], bid)

    revisions = self.mongodb.tenders.get(self.tender_id).get("revisions")
    self.assertTrue(any(i for i in revisions[-2]["changes"] if i["op"] == "remove" and i["path"] == "/bids"))
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

    self.set_status("complete")

    # finished tender does not have deleted bid
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])


def get_tender_tenderers(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": test_tender_pq_requirement_response,
            }
        },
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
    bid["status"] = "active"
    self.assertEqual(response.json["data"][0], bid)

    response = self.app.get("/tenders/some_id/bids", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


def bid_Administrator_change(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "items": copy_tender_items(tender["items"]),
                "value": {"amount": 500},
                "requirementResponses": test_tender_pq_requirement_response,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    self.app.authorization = ("Basic", ("administrator", ""))
    tenderer = deepcopy(test_tender_pq_organization)
    tenderer["identifier"]["legalName"] = "ТМ Валєра"
    response = self.app.patch_json(
        "/tenders/{}/bids/{}".format(self.tender_id, bid["id"]),
        {"data": {"tenderers": [tenderer]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tenderers"][0]["identifier"]["legalName"], "ТМ Валєра")


def patch_tender_bid_document(self):
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
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
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])


def create_tender_bid_document_invalid_award_status(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": test_tender_pq_requirement_response_valid,
            }
        },
    )

    bid = response.json['data']
    token = response.json['access']['token']
    bid_id = bid['id']

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{bid_id}?acc_token={token}",
        {"data": {"status": "pending"}},
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
        {
            "data": {
                "title": "name_3.doc",
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
        response.json["errors"][0]["description"], "Can't update document because award of bid is not in pending state"
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
        response.json["errors"][0]["description"], "Can't add document because award of bid is not in pending state"
    )


def invalidate_not_agreement_member_bid_via_chronograph(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "items": copy_tender_items(tender["items"]),
                "tenderers": [test_tender_pq_organization],
                "status": "draft",
                "value": {"amount": 500},
                "requirementResponses": test_tender_pq_requirement_response,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    token = response.json["access"]["token"]

    # disqualify supplier from agreement
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["contracts"][0]["status"] = "terminated"
    self.mongodb.agreements.save(agreement)

    # patch bid to pending status
    self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{bid['id']}?acc_token={token}",
        {"data": {"status": "pending"}},
    )

    self.set_status("active.tendering", 'end')
    self.check_chronograph()
    response = self.app.get(f"/tenders/{self.tender_id}/bids")
    self.assertEqual(response.json["data"][0]["status"], "invalid")


def bid_items_unit_value_validations(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    bid_data = {
        "tenderers": [test_tender_pq_organization],
        "value": {"amount": 500},
        "requirementResponses": test_tender_pq_requirement_response,
    }
    set_bid_items(self, bid_data)
    self.assertEqual(tender["value"]["valueAddedTaxIncluded"], True)
    bid_data["items"][0]["unit"]["value"]["valueAddedTaxIncluded"] = True
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.json["errors"][0]["description"], "valueAddedTaxIncluded of bid unit should be False")

    bid_data["items"][0].update(
        {
            "quantity": 4,
            "unit": {
                "name": "Item",
                "code": "KGM",
                "value": {"amount": 99.0, "currency": "UAH", "valueAddedTaxIncluded": False},
            },
        }
    )

    # quantity * value.amount is less than bid net amount 500/1.2 = 416, 396 < 416
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Total amount of unit values must be no more than bid.value.amount and no less than net bid amount",
    )

    # value.amount is 0
    bid_data["items"][0]["unit"]["value"]["amount"] = 0
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Total amount of unit values must be no more than bid.value.amount and no less than net bid amount",
    )

    # quantity * value.amount is not less than bid net amount
    bid_data["items"][0]["unit"]["value"][
        "amount"
    ] = 104.165  # 104.165 * 4 = 416.66, and amount net of bid 416 - it is in 20% delta
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")

    # bid value with VAT
    data = self.mongodb.tenders.get(self.tender_id)
    data['value']['valueAddedTaxIncluded'] = False
    self.mongodb.tenders.save(data)
    bid_data["value"]["valueAddedTaxIncluded"] = False
    # items sum 104.165 * 4 = 416.66, as bid.value doesn't include VAT we will see an error
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Total amount of unit values should be equal bid.value.amount if VAT is not included in bid",
    )

    bid_data["items"][0]["unit"]["value"][
        "amount"
    ] = 125.15  # 125.15 * 4 = 500.6, and amount of bid 500 (without coins it is valid items unit value)
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")

    with patch(
        "openprocurement.tender.core.procedure.validation.ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM",
        get_now() + timedelta(days=1),
    ):
        bid_data["items"][0]["unit"]["value"]["amount"] = 0
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        self.assertEqual(response.status, "201 Created")
