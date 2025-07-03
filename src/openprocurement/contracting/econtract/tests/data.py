from copy import deepcopy
from uuid import uuid4

from openprocurement.contracting.core.tests.data import (
    test_contract_data as base_test_contract_data,
)
from openprocurement.contracting.core.tests.data import test_signer_info

test_tender_token = uuid4().hex
test_econtract_data = deepcopy(base_test_contract_data)
test_econtract_data.update(
    {
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
                "signerInfo": test_signer_info,
            }
        ],
        "contractNumber": "contract #13111",
        "period": {"startDate": "2016-03-18T18:47:47.155143+02:00", "endDate": "2017-03-18T18:47:47.155143+02:00"},
    }
)

test_buyer = test_econtract_data.pop("buyer")
test_buyer["signerInfo"] = test_signer_info

test_econtract_data.update({"buyer": test_buyer})
