from copy import deepcopy
from datetime import datetime, timedelta
from unittest.mock import patch

from esculator import escp, npv

from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.esco.procedure.utils import to_decimal
from openprocurement.tender.esco.tests.base import (
    NBU_DISCOUNT_RATE,
    test_tender_esco_bids,
)


def create_tender_bid_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/bids",
        {"data": {"tenderers": [self.test_bids_data[0]["tenderers"][0]], "value": {"amount": 500}}},
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

    response = self.app.post_json(request_path, {"data": {"tenderers": [{"identifier": {}}]}}, status=422)
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
        {"data": {"selfEligible": False, "tenderers": [{"name": "name", "identifier": {"uri": "invalid_value"}}]}},
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
    del bid_data["lotValues"]

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
        [{"description": ["This field is required."], "location": "body", "name": "lotValues"}],
    )

    bid_data["lotValues"] = [{"value": {}}]

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
                "location": "body",
                "name": "lotValues",
                "description": [
                    {
                        "relatedLot": ["This field is required."],
                        "value": {
                            "yearlyPaymentsPercentage": ["This field is required."],
                            "annualCostsReduction": ["This field is required."],
                            "contractDuration": ["This field is required."],
                        },
                    }
                ],
            }
        ],
    )

    bid_data["lotValues"][0]["relatedLot"] = self.tender_lots[0]["id"]
    bid_data["lotValues"][0]["value"] = {"amount": 500}
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
                "location": "body",
                "name": "lotValues",
                "description": [
                    {
                        "value": {
                            "yearlyPaymentsPercentage": ["This field is required."],
                            "annualCostsReduction": ["This field is required."],
                            "contractDuration": ["This field is required."],
                        }
                    }
                ],
            }
        ],
    )

    bid_data["lotValues"][0]["value"] = {"contractDuration": {"years": 20}}
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
                "location": "body",
                "name": "lotValues",
                "description": [
                    {
                        "value": {
                            "annualCostsReduction": ["This field is required."],
                            "yearlyPaymentsPercentage": ["This field is required."],
                            "contractDuration": {"years": ["Int value should be less than 15."]},
                        }
                    }
                ],
            }
        ],
    )

    bid_data["lotValues"][0]["value"] = {"contractDuration": {"years": 15, "days": 10}}

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
                "location": "body",
                "name": "lotValues",
                "description": [
                    {
                        "value": {
                            "annualCostsReduction": ["This field is required."],
                            "yearlyPaymentsPercentage": ["This field is required."],
                            "contractDuration": {"days": ["max contract duration 15 years"]},
                        }
                    }
                ],
            }
        ],
    )

    bid_data["lotValues"][0]["value"] = {"contractDuration": {"years": 0, "days": 0}}

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
                "location": "body",
                "name": "lotValues",
                "description": [
                    {
                        "value": {
                            "annualCostsReduction": ["This field is required."],
                            "yearlyPaymentsPercentage": ["This field is required."],
                            "contractDuration": {"days": ["min contract duration 1 day"]},
                        }
                    }
                ],
            }
        ],
    )

    bid_data["lotValues"][0]["value"] = {
        "yearlyPaymentsPercentage": 0,
        "contractDuration": {"years": 12},
        "annualCostsReduction": [100] * 21,
    }
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
                "location": "body",
                "name": "lotValues",
                "description": [
                    {
                        "value": {
                            "yearlyPaymentsPercentage": [
                                "yearlyPaymentsPercentage should be greater than 0.8 and less than 1"
                            ],
                        }
                    }
                ],
            }
        ],
    )

    bid_data["lotValues"][0]["value"] = {
        "yearlyPaymentsPercentage": 0.8,
        "contractDuration": {"years": 12},
        "annualCostsReduction": [100] * 10,
    }

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
                "location": "body",
                "name": "lotValues",
                "description": [
                    {"value": {"annualCostsReduction": ["annual costs reduction should be set for 21 period"]}}
                ],
            }
        ],
    )

    bid_data["lotValues"][0]["value"] = {
        "yearlyPaymentsPercentage": 0.8,
        "contractDuration": {"years": 12},
        "annualCostsReduction": [100] * 21,
        "currency": "USD",
    }

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
                "location": "body",
                "name": "lotValues",
                "description": [{"value": ["currency of bid should be identical to currency of minValue of lot"]}],
            }
        ],
    )

    bid_data["lotValues"][0]["value"] = {
        "yearlyPaymentsPercentage": 0.8,
        "contractDuration": {"years": 12},
        "annualCostsReduction": [100] * 21,
        "currency": "UAH",
        "valueAddedTaxIncluded": False,
    }
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
                "location": "body",
                "name": "lotValues",
                "description": [
                    {
                        "value": [
                            "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of minValue of lot"
                        ]
                    }
                ],
            }
        ],
    )

    # create bid with given value.amount
    # comment this test while minValue = 0
    # response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': {
    #     'selfEligible': True, 'selfQualified': True, 'tenderers': [self.test_bids_data[0]['tenderers'][0]],
    #     'value': {'contractDuration': 6,
    #               'annualCostsReduction': 300.6,
    #               'yearlyPayments': 0.9,
    #               'amount': 1000}}}, status=422)
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    #     {u'location': u'body', u'name': u'value',
    #      u'description': [u'value of bid should be greater than minValue of tender']}
    # ])


def create_tender_bid_invalid_funding_kind_budget(self):
    lots = deepcopy(self.tender_lots)
    lots[0]["yearlyPaymentsPercentageRange"] = 0.5
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"fundingKind": "budget", "lots": lots}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["fundingKind"], "budget")
    self.assertEqual(response.json["data"]["yearlyPaymentsPercentageRange"], 0.5)

    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = {
        "selfQualified": True,
        "tenderers": [self.test_bids_data[0]["tenderers"][0]],
        "lotValues": [
            {
                "relatedLot": self.tender_lots[0]["id"],
                "value": {
                    "yearlyPaymentsPercentage": 0.6,
                    "contractDuration": {"years": 12},
                    "annualCostsReduction": [100] * 21,
                },
            }
        ],
    }
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        bid_data["selfEligible"] = True

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
                "location": "body",
                "name": "lotValues",
                "description": [
                    {
                        "value": {
                            "yearlyPaymentsPercentage": [
                                "yearlyPaymentsPercentage should be greater than 0 and less than 0.5"
                            ]
                        }
                    }
                ],
            }
        ],
    )

    lots[0]["yearlyPaymentsPercentageRange"] = 0.8
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"fundingKind": "other", "lots": lots, "yearlyPaymentsPercentageRange": 0.8}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["fundingKind"], "other")
    self.assertEqual(response.json["data"]["yearlyPaymentsPercentageRange"], 0.8)


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
    get_now() + timedelta(days=1),
)
def create_tender_bid(self):
    tender = self.mongodb.tenders.get(self.tender_id)
    items = tender.get("items")
    data = deepcopy(self.test_bids_data[0])
    data.update(
        {
            "value": None,
            "parameters": None,
            "documents": None,
            "financialDocuments": None,
            "eligibilityDocuments": None,
            "qualificationDocuments": None,
            "items": [  # add items without quantity
                {
                    "description": "футляри до державних нагород",
                    "id": items[0]['id'],
                },
            ],
        }
    )
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], self.test_bids_data[0]["tenderers"][0]["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])
    self.assertIn("lotValues", bid)
    self.assertEqual(
        bid["lotValues"][0]["value"]["contractDuration"]["years"],
        self.test_bids_data[0]["lotValues"][0]["value"]["contractDuration"]["years"],
    )
    self.assertEqual(
        bid["lotValues"][0]["value"]["contractDuration"]["days"],
        self.test_bids_data[0]["lotValues"][0]["value"]["contractDuration"]["days"],
    )
    self.assertEqual(
        bid["lotValues"][0]["value"]["annualCostsReduction"],
        self.test_bids_data[0]["lotValues"][0]["value"]["annualCostsReduction"],
    ),
    self.assertEqual(
        bid["lotValues"][0]["value"]["yearlyPaymentsPercentage"],
        self.test_bids_data[0]["lotValues"][0]["value"]["yearlyPaymentsPercentage"],
    )
    self.assertEqual(bid["lotValues"][0]["value"]["amount"], self.expected_bid_amount)
    self.assertEqual(bid["lotValues"][0]["value"]["amountPerformance"], self.expected_bid_amount_performance)

    data = deepcopy(self.test_bids_data[0])
    data["selfQualified"] = False

    ecriteria_released = get_now() < RELEASE_ECRITERIA_ARTICLE_17
    if ecriteria_released:
        data["selfEligible"] = False
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["selfQualified"], False)
    if ecriteria_released:
        self.assertEqual(response.json["data"]["selfEligible"], False)

    del data["selfQualified"]
    if ecriteria_released:
        del data["selfEligible"]
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("selfQualified", response.json["data"])
    if ecriteria_released:
        self.assertNotIn("selfEligible", response.json["data"])

    for status in ("active", "unsuccessful", "deleted", "invalid"):
        data = deepcopy(self.test_bids_data[0])
        data.update({"status": status})
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")

    self.set_status("complete")

    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add bid in current (complete) tender status",
    )


def create_tender_bid_lot(self):
    data = deepcopy(self.test_bids_data[0])
    data["lotValues"] = [{"value": data["value"], "relatedLot": self.initial_lots[0]["id"]}]
    data.update(
        {
            "value": None,
            "parameters": None,
            "documents": None,
            "financialDocuments": None,
            "eligibilityDocuments": None,
            "qualificationDocuments": None,
        }
    )

    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], self.test_bids_data[0]["tenderers"][0]["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])
    value = bid["lotValues"][0]["value"]
    expected_value = self.test_bids_data[0]["value"]
    self.assertEqual(value["contractDuration"]["years"], self.test_bids_data[0]["value"]["contractDuration"]["years"])
    self.assertEqual(value["contractDuration"]["days"], self.test_bids_data[0]["value"]["contractDuration"]["days"])
    self.assertEqual(value["annualCostsReduction"], self.test_bids_data[0]["value"]["annualCostsReduction"])
    self.assertEqual(value["yearlyPaymentsPercentage"], self.test_bids_data[0]["value"]["yearlyPaymentsPercentage"])
    expected_bid_amount = round(
        float(
            to_decimal(
                escp(
                    expected_value["contractDuration"]["years"],
                    expected_value["contractDuration"]["days"],
                    expected_value["yearlyPaymentsPercentage"],
                    expected_value["annualCostsReduction"],
                    get_now(),
                )
            )
        ),
        2,
    )
    self.assertEqual(value["amount"], expected_bid_amount)

    expected_amount_performance = round(
        float(
            to_decimal(
                npv(
                    test_tender_esco_bids[0]["value"]["contractDuration"]["years"],
                    test_tender_esco_bids[0]["value"]["contractDuration"]["days"],
                    test_tender_esco_bids[0]["value"]["yearlyPaymentsPercentage"],
                    test_tender_esco_bids[0]["value"]["annualCostsReduction"],
                    get_now(),
                    NBU_DISCOUNT_RATE,
                )
            )
        ),
        2,
    )
    self.assertEqual(value["amountPerformance"], expected_amount_performance)


def create_tender_bid_31_12(self):
    # time travel - announce tender 31.12.17
    tender = self.mongodb.tenders.get(self.tender_id)
    tender["noticePublicationDate"] = datetime(2017, 12, 31).isoformat()
    self.mongodb.tenders.save(tender)

    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": self.test_bids_data[0]})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], self.test_bids_data[0]["tenderers"][0]["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])
    self.assertIn("lotValues", bid)
    self.assertEqual(
        bid["lotValues"][0]["value"]["contractDuration"]["years"],
        self.test_bids_data[0]["lotValues"][0]["value"]["contractDuration"]["years"],
    )
    self.assertEqual(
        bid["lotValues"][0]["value"]["contractDuration"]["days"],
        self.test_bids_data[0]["lotValues"][0]["value"]["contractDuration"]["days"],
    )
    self.assertEqual(
        bid["lotValues"][0]["value"]["annualCostsReduction"],
        self.test_bids_data[0]["lotValues"][0]["value"]["annualCostsReduction"],
    )
    self.assertEqual(
        bid["lotValues"][0]["value"]["yearlyPaymentsPercentage"],
        self.test_bids_data[0]["lotValues"][0]["value"]["yearlyPaymentsPercentage"],
    )
    self.assertIn("amount", response.json["data"]["lotValues"][0]["value"])
    self.assertIn("amountPerformance", response.json["data"]["lotValues"][0]["value"])

    data = deepcopy(self.test_bids_data[0])
    data["lotValues"][0]["value"]["yearlyPaymentsPercentage"] = 1
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["data"]["lotValues"][0]["value"]["yearlyPaymentsPercentage"],
        data["lotValues"][0]["value"]["yearlyPaymentsPercentage"],
    )
    self.assertIn("amount", response.json["data"]["lotValues"][0]["value"])
    self.assertIn("amountPerformance", response.json["data"]["lotValues"][0]["value"])

    data = deepcopy(self.test_bids_data[0])
    data["lotValues"][0]["value"]["contractDuration"]["years"] = 1
    data["lotValues"][0]["value"]["contractDuration"]["days"] = 1
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["data"]["lotValues"][0]["value"]["contractDuration"]["years"],
        data["lotValues"][0]["value"]["contractDuration"]["years"],
    )
    self.assertEqual(
        response.json["data"]["lotValues"][0]["value"]["contractDuration"]["days"],
        data["lotValues"][0]["value"]["contractDuration"]["days"],
    )
    self.assertIn("amount", response.json["data"]["lotValues"][0]["value"])
    self.assertIn("amountPerformance", response.json["data"]["lotValues"][0]["value"])


def patch_tender_bid(self):
    bid, bid_token = self.create_bid(self.tender_id, self.test_bids_data[0], "pending")

    # Comment this test while minValue = 0
    # response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token), {'data': {
    #     'value': {'contractDuration': 6,
    #               'annualCostsReduction': 300.6,
    #               'yearlyPayments': 0.9}
    # }}, status=422)
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    #     {u'location': u'body', u'name': u'value',
    #      u'description': [u'value of bid should be greater than minValue of tender']}
    # ])
    lot_values = deepcopy(bid["lotValues"])
    lot_values[0]["value"]["currency"] = "USD"

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"lotValues": lot_values}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "lotValues",
                "description": [{"value": ["currency of bid should be identical to currency of minValue of lot"]}],
            }
        ],
    )

    lot_values[0]["value"] = deepcopy(self.test_bids_data[0]["lotValues"])[0]["value"]
    lot_values[0]["value"]["valueAddedTaxIncluded"] = False

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"lotValues": lot_values}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "lotValues",
                "description": [
                    {
                        "value": [
                            "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of minValue of lot"
                        ]
                    }
                ],
            }
        ],
    )

    tenderer = deepcopy(test_tender_below_organization)
    tenderer["name"] = "Державне управління управлінням справами"
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"tenderers": [tenderer]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.activate_bid(self.tender_id, bid['id'], bid_token)
    doc_id = response.json["data"]["documents"][-1]["id"]
    self.assertNotEqual(response.json["data"]["date"], bid["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], self.expected_bid_amount)
    self.assertEqual(
        response.json["data"]["lotValues"][0]["value"]["amountPerformance"],
        self.expected_bid_amount_performance,
    )

    lot_values[0]["value"] = (deepcopy(self.test_bids_data[0]["lotValues"]))[0]["value"]
    lot_values[0]["value"]["amountPerformance"] = 500
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"lotValues": lot_values, "tenderers": self.test_bids_data[0]["tenderers"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.activate_bid(self.tender_id, bid['id'], bid_token, doc_id)
    self.assertEqual(response.json["data"]["lotValues"][0]["value"], bid["lotValues"][0]["value"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["amountPerformance"], 500)
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], self.expected_bid_amount)
    self.assertEqual(
        response.json["data"]["lotValues"][0]["value"]["amountPerformance"],
        self.expected_bid_amount_performance,
    )

    lot_values[0]["value"]["annualCostsReduction"] = [200] * 21
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"lotValues": lot_values, "tenderers": self.test_bids_data[0]["tenderers"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.activate_bid(self.tender_id, bid['id'], bid_token, doc_id)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"], bid["lotValues"][0]["value"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])
    # checking that annualCostsReduction change affected npv and escp
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["amount"], self.expected_bid_amount)
    self.assertNotEqual(
        response.json["data"]["lotValues"][0]["value"]["amountPerformance"], self.expected_bid_amount_performance
    )

    lot_values[0]["value"]["yearlyPaymentsPercentage"] = 0.91111
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"lotValues": lot_values, "tenderers": self.test_bids_data[0]["tenderers"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.activate_bid(self.tender_id, bid['id'], bid_token, doc_id)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"], bid["lotValues"][0]["value"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["yearlyPaymentsPercentage"], 0.91111)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["amount"], self.expected_bid_amount)
    self.assertNotEqual(
        response.json["data"]["lotValues"][0]["value"]["amountPerformance"],
        self.expected_bid_amount_performance,
    )

    lot_values[0]["value"]["amount"] = 400
    response = self.app.patch_json(
        "/tenders/{}/bids/some_id?acc_token={}".format(self.tender_id, bid_token),
        {"data": {"lotValues": lot_values}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.patch_json("/tenders/some_id/bids/some_id", {"data": {"lotValues": lot_values}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    for status in ("invalid", "active", "unsuccessful", "deleted", "draft"):
        response = self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"], "Can't update bid to ({}) status".format(status))

    d1 = self.app.app.registry.mongodb.tenders.get(self.tender_id)

    lot_values[0]["value"]["amount"] = 400
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"lotValues": lot_values}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.activate_bid(self.tender_id, bid['id'], bid_token, doc_id)

    d2 = self.app.app.registry.mongodb.tenders.get(self.tender_id)
    self.assertEqual(d1["bids"][0]["lotValues"][0]["value"], d2["bids"][0]["lotValues"][0]["value"])

    self.set_status("complete")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["amount"], self.expected_bid_amount)
    self.assertNotEqual(
        response.json["data"]["lotValues"][0]["value"]["amountPerformance"],
        self.expected_bid_amount_performance,
    )

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"lotValues": lot_values}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid in current (complete) tender status")


def delete_tender_bidder(self):
    bid_data = deepcopy(self.test_bids_data[0])

    bid, bid_token = self.create_bid(self.tender_id, bid_data, "pending")

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
    bid, bid_token = self.create_bid(self.tender_id, bid_data, "pending")
    self.assertEqual(bid["lotValues"][0]["value"]["amount"], self.expected_bid_amount)
    self.assertEqual(bid["lotValues"][0]["value"]["amountPerformance"], self.expected_bid_amount_performance)

    # update tender. we can set value that is less than a value in bid as
    # they will be invalidated by this request
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"description": "new description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["description"], "new description")

    # check bid 'invalid' status
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "invalid")

    # try to delete 'invalid' bid
    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    bid_data["lotValues"][0]["value"] = {
        "annualCostsReduction": [100] * 21,
        "yearlyPaymentsPercentage": 0.8,
        "contractDuration": {"years": 10},
    }

    self.create_bid(self.tender_id, bid_data, "pending")
    self.create_bid(self.tender_id, bid_data, "pending")

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    with change_auth(self.app, ("Basic", ("token", ""))):
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
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
    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        response = self.app.post_json(
            "/tenders/{}/auction".format(self.tender_id),
            {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}},
        )
        self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    with change_auth(self.app, ("Basic", ("broker", ""))):
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


def bid_Administrator_change(self):
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": self.test_bids_data[0]})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    self.app.authorization = ("Basic", ("administrator", ""))

    bid_data = deepcopy(test_tender_esco_bids[0])
    bid_data.update(
        {
            "lotValues": [
                {
                    **bid["lotValues"][0],
                    "value": {
                        "annualCostsReduction": [300] * 21,
                        "yearlyPaymentsPercentage": 0.8,
                        "contractDuration": {"years": 8},
                    },
                }
            ]
        }
    )
    bid_data["tenderers"][0]["identifier"]["id"] = "00000000"

    response = self.app.patch_json(
        "/tenders/{}/bids/{}".format(self.tender_id, bid["id"]),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["annualCostsReduction"], [200] * 21)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["yearlyPaymentsPercentage"], 0.8)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["contractDuration"]["years"], 8)
    self.assertEqual(response.json["data"]["tenderers"][0]["identifier"]["id"], "00000000")


def bids_activation_on_tender_documents(self):
    bids_access = {}

    # submit bids
    for _ in range(2):
        bid, bid_token = self.create_bid(self.tender_id, self.test_bids_data[0], "pending")
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
                "title": "укр.doc",
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

    # activate bids
    for bid_id, token in bids_access.items():
        response = self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token), {"data": {"status": "pending"}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")


def bids_invalidation_on_tender_change(self):
    bids_access = {}

    # submit bids
    for data in self.test_bids_data:
        bid, bid_token = self.create_bid(self.tender_id, data, "pending")
        bids_access[bid["id"]] = bid_token

    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")

    # update tender. we can set yearlyPaymentsPercentageRange value
    # that is less than a value in bids as they will be invalidated by this request
    lots = deepcopy(self.tender_lots)
    lots[0]["yearlyPaymentsPercentageRange"] = 0.7
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"yearlyPaymentsPercentageRange": 0.7, "fundingKind": "budget", "lots": lots}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["yearlyPaymentsPercentageRange"], 0.7)
    self.assertEqual(response.json["data"]["fundingKind"], "budget")

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
    # comment test while minValue = 0
    # response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': self.test_bids_data[0]},
    #                               status=422)
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    #     {u'description': [u'value of bid should be greater than minValue of tender'], u'location': u'body',
    #      u'name': u'value'}
    # ])
    # and submit valid bid
    data = deepcopy(self.test_bids_data[0])
    data["lotValues"][0]["value"] = {
        "annualCostsReduction": [200] * 21,
        "yearlyPaymentsPercentage": 0.7,
        "contractDuration": {"years": 10, "days": 15},
    }
    bid, valid_bid_token = self.create_bid(self.tender_id, data, "pending")
    valid_bid_id = bid["id"]
    valid_bid_date = bid["date"]

    self.create_bid(self.tender_id, data, "pending")

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    with change_auth(self.app, ("Basic", ("token", ""))):
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, valid_bid_id, valid_bid_token))
    self.assertEqual(response.json["data"]["status"], "active")

    # switch to active.pre-qualification.stand-still
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
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
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


def create_tender_bid_no_scale_invalid(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = {
        "data": {
            "lotValues": [
                {
                    "relatedLot": self.tender_lots[0]["id"],
                    "value": {
                        "annualCostsReduction": [950] * 21,
                        "yearlyPaymentsPercentage": 0.9,
                        "contractDuration": {"years": 10},
                    },
                }
            ],
            "tenderers": [{key: value for key, value in self.author_data.items() if key != "scale"}],
        }
    }
    response = self.app.post_json(request_path, bid_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": [{"scale": ["This field is required."]}], "location": "body", "name": "tenderers"}],
    )


# TenderBidFeaturesResourceTest


def features_bid_invalid(self):
    data = deepcopy(self.test_bids_data[0])
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "parameters"}],
    )
    data["parameters"] = [{"code": "OCDS-123454-AIR-INTAKE", "value": 0.03}]
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["All features parameters is required."], "location": "body", "name": "parameters"}],
    )
    data["parameters"].append({"code": "OCDS-123454-AIR-INTAKE", "value": 0.03})
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
    data["parameters"][1]["code"] = "OCDS-123454-YEARS"
    data["parameters"][1]["value"] = 0.2
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": data}, status=422)
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


def features_bid(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update({"parameters": [{"code": i["code"], "value": 0.03} for i in self.initial_data["features"]]})
    for i in [bid_data] * 2:
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": i})
        i["status"] = "pending"
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        bid = response.json["data"]
        bid.pop("date")
        bid.pop("id")
        bid.pop("submissionDate", None)
        self.assertEqual(set(bid), set(i))


def patch_and_put_document_into_invalid_bid(self):
    doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
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
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split("?")[-1]
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

    # update tender. we can set value that is less than a value in bids as
    # they will be invalidated by this request
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"description": "new description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["description"], "new description")

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
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
