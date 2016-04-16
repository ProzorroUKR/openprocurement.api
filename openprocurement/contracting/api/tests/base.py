# -*- coding: utf-8 -*-
import os
import unittest
import webtest
from copy import deepcopy
from datetime import datetime

from openprocurement.api.utils import VERSION


now = datetime.now()

test_contract_data = {
    "status": "active",
    "items": [
        {
        "description": "футляри до державних нагород",
        "classification": {
                        "scheme": "CPV",
                        "description": "Cartons",
                        "id": "44617100-9"
                    },
        "additionalClassifications": [
                        {
                                        "scheme": "ДКПП",
                                        "id": "17.21.1",
                                        "description": "папір і картон гофровані, паперова й картонна тара"
                                    }
                    ],
        "deliveryAddress": {
                        "postalCode": "79000",
                        "countryName": "Україна",
                        "streetAddress": "вул. Банкова 1",
                        "region": "м. Київ",
                        "locality": "м. Київ"
                    },
        "deliveryDate": {
                        "startDate": "2016-03-20T18:47:47.136678+02:00",
                        "endDate": "2016-03-23T18:47:47.136678+02:00"
                    },
        "id": "c6c6e8ed4b1542e4bf13d3f98ec5ab59",
        "unit": {
            "code": "44617100-9",
            "name": "item"
        },
        "quantity": 5
        }
    ],
    "suppliers": [
        {
        "contactPoint": {
            "email": "aagt@gmail.com",
            "telephone": "+380 (322) 91-69-30",
            "name": "Андрій Олексюк"
        },
        "identifier": {
            "scheme": "UA-EDR",
            "id": "00137226",
            "uri": "http://www.sc.gov.ua/"
        },
        "name": "ДКП «Книга»",
                    "address": {
                                "postalCode": "79013",
                                "countryName": "Україна",
                                "streetAddress": "вул. Островського, 34",
                                "region": "м. Львів",
                                "locality": "м. Львів"
                                }
                }
            ],
    "contractNumber": "contract #13111",
        "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2017-03-18T18:47:47.155143+02:00"
                },
    "value": {
        "currency": "UAH",
        "amount": 238.0,
        "valueAddedTaxIncluded": True
        },
    "dateSigned": "2016-03-18T18:48:05.762961+02:00",
    "awardID": "8481d7eb01694c25b18658036c236c5d",
    "id": "2359720ade994a56b488a92f2fa577b2",
    "contractID": "UA-2016-03-18-000001-1",
    "tender_token": "4555720ade994a56b488a92f2fa577b2",
    "owner": "broker"
}

documents = [
    {
        "title": "contract_first_document.doc",
        "url": "http://api-sandbox.openprocurement.org/api/0.12/tenders/ce536c5f46d543ec81ffa86ce4c77c8b/contracts/1359720ade994a56b488a92f2fa577b2/documents/f4f9338cda06496f9f2e588660a5203e?download=711bc63427c444d3a0638616e559996a",
        "format": "application/msword",
        "documentOf": "tender",
        "datePublished": "2016-03-18T18:48:06.238010+02:00",
        "id": "f4f9338cda06496f9f2e588660a5203e",
        "dateModified": "2016-03-18T18:48:06.238047+02:00"
        },
    {
        "title": "contract_second_document.doc",
        "url": "http://api-sandbox.openprocurement.org/api/0.12/tenders/ce536c5f46d543ec81ffa86ce4c77c8b/contracts/1359720ade994a56b488a92f2fa577b2/documents/9c8b66120d4c415cb334bbad33f94ba9?download=da839a4c3d7a41d2852d17f90aa14f47",
        "format": "application/msword",
        "documentOf": "tender",
        "datePublished": "2016-03-18T18:48:06.477792+02:00",
        "id": "9c8b66120d4c415cb334bbad33f94ba9",
        "dateModified": "2016-03-18T18:48:06.477829+02:00"
        }
]


class PrefixedRequestClass(webtest.app.TestRequest):

    @classmethod
    def blank(cls, path, *args, **kwargs):
        path = '/api/%s%s' % (VERSION, path)
        return webtest.app.TestRequest.blank(path, *args, **kwargs)


class BaseWebTest(unittest.TestCase):
    """Base Web Test to test openprocurement.contractning.api.

    It setups the database before each test and delete it after.
    """
    initial_auth = ('Basic', ('token', ''))

    def setUp(self):
        self.app = webtest.TestApp(
            "config:tests.ini", relative_to=os.path.dirname(__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = self.initial_auth
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def tearDown(self):
        del self.couchdb_server[self.db.name]


class BaseContractWebTest(BaseWebTest):
    initial_data = test_contract_data

    def setUp(self):
        super(BaseContractWebTest, self).setUp()
        self.create_contract()

    def create_contract(self):
        data = deepcopy(self.initial_data)

        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('databridge', ''))
        response = self.app.post_json('/contracts', {'data': data})
        contract = response.json['data']
        self.contract_token = response.json['access']['token']
        self.contract_id = contract['id']
        self.app.authorization = orig_auth

    def tearDown(self):
        del self.db[self.contract_id]
        super(BaseContractWebTest, self).tearDown()
