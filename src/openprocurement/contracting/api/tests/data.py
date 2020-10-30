# -*- coding: utf-8 -*-
from copy import deepcopy
from hashlib import sha512

from uuid import uuid4

from openprocurement.api.utils import get_now

test_tender_token = uuid4().hex
test_contract_data = {
    u"items": [
        {
            u"description": u"футляри до державних нагород",
            u"classification": {u"scheme": u"CPV", u"description": u"Cartons", u"id": u"44617100-9"},
            u"additionalClassifications": [
                {
                    u"scheme": u"ДКПП",
                    u"id": u"17.21.1",
                    u"description": u"папір і картон гофровані, паперова й картонна тара",
                }
            ],
            u"deliveryAddress": {
                u"postalCode": u"79000",
                u"countryName": u"Україна",
                u"streetAddress": u"вул. Банкова 1",
                u"region": u"м. Київ",
                u"locality": u"м. Київ",
            },
            u"deliveryDate": {
                u"startDate": u"2016-03-20T18:47:47.136678+02:00",
                u"endDate": u"2016-03-23T18:47:47.136678+02:00",
            },
            u"id": u"c6c6e8ed4b1542e4bf13d3f98ec5ab59",
            u"unit": {u"code": u"44617100-9", u"name": u"item"},
            u"quantity": 5,
        }
    ],
    u"procuringEntity": {
        u"name": u"Державне управління справами",
        u"identifier": {u"scheme": u"UA-EDR", u"id": u"00037256", u"uri": u"http://www.dus.gov.ua/"},
        u"address": {
            u"countryName": u"Україна",
            u"postalCode": u"01220",
            u"region": u"м. Київ",
            u"locality": u"м. Київ",
            u"streetAddress": u"вул. Банкова, 11, корпус 1",
        },
        u"contactPoint": {u"name": u"Державне управління справами", u"telephone": u"0440000000"},
    },
    u"suppliers": [
        {
            u"contactPoint": {
                u"email": u"aagt@gmail.com",
                u"telephone": u"+380 (322) 91-69-30",
                u"name": u"Андрій Олексюк",
            },
            u"identifier": {u"scheme": u"UA-EDR", u"id": u"00137226", u"uri": u"http://www.sc.gov.ua/"},
            u"name": u"ДКП «Книга»",
            u"address": {
                u"postalCode": u"79013",
                u"countryName": u"Україна",
                u"streetAddress": u"вул. Островського, 34",
                u"region": u"Львівська область",
                u"locality": u"м. Львів",
            },
        }
    ],
    u"contractNumber": u"contract #13111",
    u"period": {u"startDate": u"2016-03-18T18:47:47.155143+02:00", u"endDate": u"2017-03-18T18:47:47.155143+02:00"},
    u"value": {u"currency": u"UAH", u"amount": 238.0, u"amountNet": 237.0, u"valueAddedTaxIncluded": True},
    u"dateSigned": get_now().isoformat(),
    u"awardID": u"8481d7eb01694c25b18658036c236c5d",
    u"id": uuid4().hex,
    u"contractID": u"UA-2016-03-18-000001-1",
    u"tender_id": uuid4().hex,
    u"tender_token": sha512(test_tender_token).hexdigest(),
    u"owner": u"broker",
}

test_contract_data_wo_items = deepcopy(test_contract_data)
del test_contract_data_wo_items["items"]

test_contract_data_wo_value_amount_net = deepcopy(test_contract_data)
del test_contract_data_wo_value_amount_net["value"]["amountNet"]

documents = [
    {
        "hash": "md5:00000000000000000000000000000000",
        "title": "contract.pdf",
        "url": "http://localhost/get/e34c262322ff41e2bd59c3eafa901bdc?KeyID=a8968c46&Signature=GlqQYqhRk3%2FC3eT1jvOQIyT%2FlJLDsJ9NYUXUUUOOcuawVQlBFJAq7xrkveZ0pvLrYUmjGlyecw1K9sZsMOKHAA%253D%253D",
        "format": "application/pdf",
        "author": "renderer_bots",
        "documentOf": "document",
        "datePublished": "2020-08-17T09:05:20.087293+03:00",
        "documentType": "contract",
        "id": "45df405492a14429a475b5c3e44f400f",
        "relatedItem": "d20fa28dc41340978b86ad562ad85860",
        "dateModified": "2020-08-17T09:05:20.087311+03:00"
    },
    {
        "hash": "md5:00000000000000000000000000000000",
        "title": "contractData.json",
        "url": "http://localhost/get/9870e6b6e2cf4832923b1132f49f6454?KeyID=a8968c46&Signature=D6XBAwehqKX%2FcQZDDnbkgiU64J4zV7qPi5ovM2vJ2VqlplbmMCI2xlB2AxRNJNiwEotqZdpkLP1C%2FEIBNenIBw%253D%253D",
        "format": "application/json",
        "author": "renderer_bots",
        "documentOf": "document",
        "datePublished": "2020-08-17T09:05:20.168888+03:00",
        "documentType": "contractData",
        "id": "ffc355b192524833b60b80ebf72c7cd6",
        "relatedItem": "45df405492a14429a475b5c3e44f400f",
        "dateModified": "2020-08-17T09:05:20.168906+03:00"
    },
    {
        "title": "contract_first_document.doc",
        "url": "http://api-sandbox.openprocurement.org/api/0.12/tenders/ce536c5f46d543ec81ffa86ce4c77c8b/contracts/1359720ade994a56b488a92f2fa577b2/documents/f4f9338cda06496f9f2e588660a5203e?download=711bc63427c444d3a0638616e559996a",
        "format": "application/msword",
        "documentOf": "tender",
        "datePublished": "2016-03-18T18:48:06.238010+02:00",
        "id": "f4f9338cda06496f9f2e588660a5203e",
        "dateModified": "2016-03-18T18:48:06.238047+02:00",
    },
    {
        "title": "contract_second_document.doc",
        "url": "http://api-sandbox.openprocurement.org/api/0.12/tenders/ce536c5f46d543ec81ffa86ce4c77c8b/contracts/1359720ade994a56b488a92f2fa577b2/documents/9c8b66120d4c415cb334bbad33f94ba9?download=da839a4c3d7a41d2852d17f90aa14f47",
        "format": "application/msword",
        "documentOf": "tender",
        "datePublished": "2016-03-18T18:48:06.477792+02:00",
        "id": "9c8b66120d4c415cb334bbad33f94ba9",
        "dateModified": "2016-03-18T18:48:06.477829+02:00",
    },
]
