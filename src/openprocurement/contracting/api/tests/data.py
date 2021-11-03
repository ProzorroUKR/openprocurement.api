# -*- coding: utf-8 -*-
from copy import deepcopy
from hashlib import sha512

from uuid import uuid4

from openprocurement.api.utils import get_now

test_tender_token = uuid4().hex
test_contract_data = {
    "items": [
        {
            "description": "футляри до державних нагород",
            "classification": {"scheme": "CPV", "description": "Cartons", "id": "44617100-9"},
            "additionalClassifications": [
                {
                    "scheme": "ДКПП",
                    "id": "17.21.1",
                    "description": "папір і картон гофровані, паперова й картонна тара",
                }
            ],
            "deliveryAddress": {
                "postalCode": "79000",
                "countryName": "Україна",
                "streetAddress": "вул. Банкова 1",
                "region": "м. Київ",
                "locality": "м. Київ",
            },
            "deliveryDate": {
                "startDate": "2016-03-20T18:47:47.136678+02:00",
                "endDate": "2016-03-23T18:47:47.136678+02:00",
            },
            "id": "c6c6e8ed4b1542e4bf13d3f98ec5ab59",
            "unit": {
                "code": "KGM",
                "name": "кг",
                "value": {
                    "currency": "UAH",
                    "amount": 20.8,
                    "valueAddedTaxIncluded": True
                }
            },
            "quantity": 5,
        }
    ],
    "procuringEntity": {
        "name": "Державне управління справами",
        "identifier": {"scheme": "UA-EDR", "id": "00037256", "uri": "http://www.dus.gov.ua/"},
        "address": {
            "countryName": "Україна",
            "postalCode": "01220",
            "region": "м. Київ",
            "locality": "м. Київ",
            "streetAddress": "вул. Банкова, 11, корпус 1",
        },
        "contactPoint": {"name": "Державне управління справами", "telephone": "+0440000000"},
    },
    "suppliers": [
        {
            "contactPoint": {
                "email": "aagt@gmail.com",
                "telephone": "+380322916930",
                "name": "Андрій Олексюк",
            },
            "identifier": {"scheme": "UA-EDR", "id": "00137226", "uri": "http://www.sc.gov.ua/"},
            "name": "ДКП «Книга»",
            "address": {
                "postalCode": "79013",
                "countryName": "Україна",
                "streetAddress": "вул. Островського, 34",
                "region": "Львівська область",
                "locality": "м. Львів",
            },
        }
    ],
    "contractNumber": "contract #13111",
    "period": {"startDate": "2016-03-18T18:47:47.155143+02:00", "endDate": "2017-03-18T18:47:47.155143+02:00"},
    "value": {"currency": "UAH", "amount": 238.0, "amountNet": 237.0, "valueAddedTaxIncluded": True},
    "dateSigned": get_now().isoformat(),
    "awardID": "8481d7eb01694c25b18658036c236c5d",
    "id": uuid4().hex,
    "contractID": "UA-2016-03-18-000001-1",
    "tender_id": uuid4().hex,
    "tender_token": sha512(test_tender_token.encode()).hexdigest(),
    "owner": "broker",
}

test_contract_data_wo_items = deepcopy(test_contract_data)
del test_contract_data_wo_items["items"]

test_contract_data_two_items = deepcopy(test_contract_data)
test_contract_data_two_items["items"].append({
    "description": "футляри до державних нагород",
    "classification": {"scheme": "CPV", "description": "Cartons", "id": "44617100-9"},
    "additionalClassifications": [
        {
            "scheme": "ДКПП",
            "id": "17.21.1",
            "description": "папір і картон гофровані, паперова й картонна тара",
        }
    ],
    "deliveryAddress": {
        "postalCode": "79000",
        "countryName": "Україна",
        "streetAddress": "вул. Банкова 1",
        "region": "м. Київ",
        "locality": "м. Київ",
    },
    "deliveryDate": {
        "startDate": "2016-03-20T18:47:47.136678+02:00",
        "endDate": "2016-03-23T18:47:47.136678+02:00",
    },
    "id": "c6c6e8ed4b1542e4bf13d3f98ec5ab12",
    "unit": {
        "code": "KGM",
        "name": "кг",
        "value": {
            "currency": "UAH",
            "amount": 20.8,
            "valueAddedTaxIncluded": True
        }
    },
    "quantity": 5,
})


test_contract_data_wo_value_amount_net = deepcopy(test_contract_data)
del test_contract_data_wo_value_amount_net["value"]["amountNet"]

documents = [
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
