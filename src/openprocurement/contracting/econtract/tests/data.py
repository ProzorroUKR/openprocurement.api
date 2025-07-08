from copy import deepcopy
from uuid import uuid4

from openprocurement.api.utils import get_now
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
        "period": {
            "startDate": get_now().isoformat(),
            "endDate": get_now().replace(month=12, day=31, hour=23, minute=59, second=59).isoformat(),
        },
    }
)
test_econtract_data["contractNumber"] = f"{test_econtract_data['suppliers'][0]['name']} {get_now().year}/..."

test_buyer = test_econtract_data.pop("buyer")
test_buyer["signerInfo"] = test_signer_info

test_econtract_data.update({"buyer": test_buyer})
