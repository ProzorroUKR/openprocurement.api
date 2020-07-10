# -*- coding: utf-8 -*-
from copy import deepcopy

import mock
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.tests.data import\
    test_criteria_1, test_criteria_2, test_criteria_3, test_criteria_4
from openprocurement.tender.pricequotation.tests.base import \
    test_organization, test_requirement_response_valid, test_response_1,\
    test_response_2_1, test_response_2_2, test_response_3_1,\
    test_response_3_2, test_response_4


def create_tender_bid_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/bids", {"data": {"tenderers": [test_organization], "value": {"amount": 500}}}, status=404
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

    response = self.app.post_json(request_path, {"data": {"tenderers": [{"identifier": {}}], "requirementResponses": test_requirement_response_valid}}, status=422)
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
        request_path, {"data": {"tenderers": [{"name": "name", "identifier": {"uri": "invalid_value"}}], "requirementResponses": test_requirement_response_valid}}, status=422
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

    response = self.app.post_json(request_path, {"data": {"tenderers": [test_organization], "requirementResponses": test_requirement_response_valid}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"value"}],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [test_organization], "value": {"amount": 500, "valueAddedTaxIncluded": False}, "requirementResponses": test_requirement_response_valid}},
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

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [test_organization], "value": {"amount": 500, "currency": "USD"}, "requirementResponses": test_requirement_response_valid}},
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

    response = self.app.post_json(
        request_path, {"data": {"tenderers": test_organization, "value": {"amount": 500}}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(u"invalid literal for int() with base 10", response.json["errors"][0]["description"])

    response = self.app.post_json(
        request_path, {"data": {"tenderers": [test_organization], "value": {"amount": 500}}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"requirementResponses"}],
    )


def create_tender_bid(self):
    dateModified = self.db.get(self.tender_id).get("dateModified")

    # Revert tender to statuses ('draft', 'draft.unsuccessful', 'draft.publishing')
    data = self.db.get(self.tender_id)
    current_status = data.get('status')
    criteria = data.pop('criteria')

    for status in ('draft', 'draft.publishing', 'draft.unsuccessful'):
        data['status'] = status
        self.db.save(data)
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "tenderers": [test_organization],
                    "value": {"amount": 500},
                    "requirementResponses": test_requirement_response_valid
                }
            },
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json['errors'],
                         [{"location": "body",
                           "name": "data",
                           "description": "Can't add bid in current ({}) tender status".format(status)}])

    # Restore tender to 'active.tendering' status
    data['status'] = current_status
    data['criteria'] = criteria
    self.db.save(data)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_organization], "value": {"amount": 500}, "requirementResponses": test_requirement_response_valid }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], test_organization["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])

    self.assertEqual(self.db.get(self.tender_id).get("dateModified"), dateModified)

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_organization], "value": {"amount": 500}, "requirementResponses": test_requirement_response_valid}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (complete) tender status")


def requirement_response_validation_multiple_criterias(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response_1
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    test_response = deepcopy(test_response_1)
    test_response[0]['value'] = 'ivalid'
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
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
            u'description': [u'Value "ivalid" does not match expected value "Розчин для інфузій" in reqirement 400496-0001-001-01'],
            u'location': u'body',
            u'name': u'requirementResponses'
        }]
    )

    test_response = deepcopy(test_response_1)
    test_response[1]['value'] = '4'
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
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
            u'description': [u'Value 4 is lower then minimal required 5 in reqirement 400496-0002-001-01'],
            u'location': u'body',
            u'name': u'requirementResponses'
        }]
    )

    test_response = deepcopy(test_response_1)
    test_response.pop()
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
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
            u'description': [u"Missing references for criterias: [u'400496-0002']"],
            u'location': u'body',
            u'name': u'requirementResponses'
        }]
    )


def requirement_response_validation_multiple_groups(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response_2_1
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response_2_2
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    test_response = deepcopy(test_response_2_2)
    test_response.extend(test_response_2_1)
    
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
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
            u'description': [u"Provided groups [u'400496-0001-002', u'400496-0001-001'] conflicting in criteria 400496-0001"],
            u'location': u'body',
            u'name': u'requirementResponses'
        }]
    )


def requirement_response_validation_multiple_groups_multiple_requirements(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response_3_1
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response_3_2
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    test_response = deepcopy(test_response_3_1)
    test_response.extend(test_response_3_2)
    
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
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
            u'description': [u"Provided groups [u'400496-0001-002', u'400496-0001-001'] conflicting in criteria 400496-0001"],
            u'location': u'body',
            u'name': u'requirementResponses'
        }]
    )


def requirement_response_validation_one_group_multiple_requirements(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response_4
        }},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    data = response.json
    self.assertEqual(data['status'], "error")
    self.assertEqual(
        data['errors'], [{
            u'description': [u'Value "Порошок" does not match expected value "Розчин" in reqirement 400496-0001-001-01'],
            u'location': u'body',
            u'name': u'requirementResponses'
        }]
    )

    test_response = deepcopy(test_response_4)
    test_response[0]['value'] = u'Розчин'
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 500},
            "requirementResponses": test_response
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def patch_tender_bid(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_organization], "status": "draft", "value": {"amount": 500}, "requirementResponses": test_requirement_response_valid}},
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
                u"description": [u"value of bid should be less than value of tender"],
                u"location": u"body",
                u"name": u"value",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"tenderers": [{"name": u"Державне управління управлінням справами"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], bid["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"value": {"amount": 500}, "tenderers": [test_organization]}},
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
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"bid_id"}])

    response = self.app.patch_json("/tenders/some_id/bids/some_id", {"data": {"value": {"amount": 400}}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
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
        {"data": {"tenderers": [test_organization], "value": {"amount": 500}, "requirementResponses": test_requirement_response_valid}},
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
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"bid_id"}])

    response = self.app.get("/tenders/some_id/bids/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
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
        {"data": {"tenderers": [test_organization], "value": {"amount": 500}, "requirementResponses": test_requirement_response_valid}},
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
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"bid_id"}])

    response = self.app.delete("/tenders/some_id/bids/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def get_tender_tenderers(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_organization], "value": {"amount": 500}, "requirementResponses": test_requirement_response_valid}},
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
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def bid_Administrator_change(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_organization], "value": {"amount": 500}, "requirementResponses": test_requirement_response_valid}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json(
        "/tenders/{}/bids/{}".format(self.tender_id, bid["id"]),
        {"data": {"tenderers": [{"identifier": {"id": "00000000"}}], "value": {"amount": 400}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["tenderers"][0]["identifier"]["id"], "00000000")


def patch_tender_bid_document(self):
    response = self.app.post(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        upload_files=[("file", "name.doc", "content")],
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
            {"data": {"tenderers": [test_organization], "value": {"amount": 500},
                      "requirementResponses": test_requirement_response_valid}},
        )
    bid = response.json['data']
    token = response.json['access']['token']
    bid_id = bid['id']

    response = self.app.post(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    self.set_status("active.tendering", 'end')
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document because award of bid is not in pending state"
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
        response.json["errors"][0]["description"], "Can't update document because award of bid is not in pending state"
    )

    response = self.app.post(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document because award of bid is not in pending state"
    )
