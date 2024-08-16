from copy import deepcopy
from uuid import uuid4

from openprocurement.contracting.core.tests.data import (
    test_contract_data as base_test_contract_data,
)

test_tender_token = uuid4().hex
test_contract_data = deepcopy(base_test_contract_data)

test_buyer = test_contract_data.pop("procuringEntity")
del test_buyer["contactPoint"]

for i in test_contract_data.get("suppliers", ""):
    del i["contactPoint"]

test_contract_data.update({"bid_owner": "broker", "bid_token": uuid4().hex, "buyer": test_buyer, "id": uuid4().hex})

del test_contract_data["period"]
del test_contract_data["contractNumber"]
del test_contract_data["dateSigned"]


test_contract_data_wo_items = deepcopy(test_contract_data)
del test_contract_data_wo_items["items"]

test_contract_data_two_items = deepcopy(test_contract_data)
test_contract_data_two_items["items"].append(
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
        "id": "c6c6e8ed4b1542e4bf13d3f98ec5ab12",
        "unit": {
            "code": "KGM",
            "name": "кг",
            "value": {"currency": "UAH", "amount": 20.8, "valueAddedTaxIncluded": True},
        },
        "quantity": 5,
    }
)

test_signer_info = {
    "name": "Test Testovich",
    "telephone": "+380950000000",
    "email": "example@email.com",
    "iban": "1" * 15,
    "authorizedBy": "Статут компанії",
    "position": "Генеральний директор",
}

test_contract_data_wo_value_amount_net = deepcopy(test_contract_data)
del test_contract_data_wo_value_amount_net["value"]["amountNet"]
