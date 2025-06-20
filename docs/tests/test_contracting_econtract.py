import os
from copy import deepcopy
from datetime import timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

from tests.base.constants import DOCS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

from openprocurement.api.utils import get_now
from openprocurement.contracting.core.tests.data import (
    test_contract_data,
    test_signer_info,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_multi_buyers_data,
)
from openprocurement.tender.core.tests.mock import patch_market
from openprocurement.tender.core.tests.utils import change_auth, set_tender_criteria
from openprocurement.tender.pricequotation.tests.base import (
    BaseTenderWebTest as BasePQWebTest,
)
from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_category,
    test_tender_pq_criteria_1,
    test_tender_pq_data,
    test_tender_pq_response_1,
    test_tender_pq_supplier,
)
from openprocurement.tender.pricequotation.tests.utils import (
    copy_criteria_req_id,
    criteria_drop_uuids,
)

test_contract_data = deepcopy(test_contract_data)
test_tender_data = deepcopy(test_tender_pq_data)
test_tender_data["procuringEntity"]["identifier"]["id"] = "00037257"
test_tender_data_multi_buyers = deepcopy(test_tender_below_multi_buyers_data)

TARGET_DIR = 'docs/source/contracting/econtract/http/'


class TenderPQResourceTest(BasePQWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    docservice_url = DOCS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    @patch_market(
        {
            "id": "1" * 32,
            "relatedCategory": "655360-30230000-889652",
            "criteria": deepcopy(test_tender_pq_criteria_1),
        },
        test_tender_pq_category,
    )
    def test_docs(self):
        tender_data = deepcopy(test_tender_pq_data)
        tender_data["procuringEntity"]["identifier"]["id"] = "00037257"
        self.app.authorization = ('Basic', ('broker', ''))
        # empty tenders listing
        response = self.app.get('/tenders')
        self.assertEqual(response.json['data'], [])

        # create tender
        tender_data['items'].append(deepcopy(tender_data['items'][0]))
        for item in tender_data['items']:
            item["id"] = uuid4().hex
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat(),
            }
        tender_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_1))
        set_tender_criteria(
            tender_criteria,
            tender_data.get("lots", []),
            tender_data.get("items", []),
        )
        tender_data.update(
            {
                "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()},
                "criteria": tender_criteria,
            }
        )

        agreement = {"id": self.agreement_id}
        tender_data["agreement"] = agreement

        tender_data["procuringEntity"]["contract_owner"] = "broker6"
        response = self.app.post_json('/tenders', {'data': tender_data, 'config': self.initial_config})
        tender_id = self.tender_id = response.json['data']['id']
        tender_token = response.json['access']['token']
        tender_items = response.json['data']['items']
        # switch to active.tendering
        response = self.set_status(
            'active.tendering', extra={'auctionPeriod': {'startDate': (get_now() + timedelta(days=10)).isoformat()}}
        )
        tender = response.json["data"]
        self.assertIn("auctionPeriod", response.json['data'])
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        supplier = deepcopy(test_tender_pq_supplier)
        supplier["contract_owner"] = "broker"
        product = {"id": "1" * 32, "status": "active"}
        with patch(
            "openprocurement.api.utils.requests.get",
            Mock(return_value=Mock(status_code=200, json=Mock(return_value={"data": product}))),
        ):
            bid, bid_token = self.create_bid(
                self.tender_id,
                {
                    'tenderers': [supplier],
                    'value': {'amount': 500},
                    'requirementResponses': copy_criteria_req_id(tender["criteria"], test_tender_pq_response_1),
                    'items': [
                        {
                            "id": tender_items[0]["id"],
                            "description": "Комп’ютерне обладнання для біда",
                            "quantity": 10,
                            "unit": {
                                "name": "кг",
                                "code": "KGM",
                                "value": {"amount": 40, "valueAddedTaxIncluded": False},
                            },
                            "product": product['id'],
                        },
                        {
                            "id": tender_items[1]["id"],
                            "description": "Комп’ютерне обладнання",
                            "quantity": 5,
                            "unit": {
                                "name": "кг",
                                "code": "KGM",
                                "value": {"amount": 20, "valueAddedTaxIncluded": False},
                            },
                            "product": product['id'],
                        },
                    ],
                },
            )
        # switch to active.qualification
        self.set_status('active.qualification')
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get(f'/tenders/{tender_id}/awards?acc_token={tender_token}')
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        # set award as active
        self.add_sign_doc(tender_id, tender_token, docs_url=f"/awards/{award_id}/documents")
        self.app.patch_json(
            f'/tenders/{tender_id}/awards/{award_id}?acc_token={tender_token}',
            {"data": {"status": "active", "qualified": True}},
        )
        # get contract id
        response = self.app.get(f'/tenders/{tender_id}')
        contract = response.json['data']['contracts'][-1]
        self.contract_id = contract['id']

        with open(TARGET_DIR + 'example-contract.http', 'w') as self.app.file_obj:
            self.app.get(f'/tenders/{tender_id}/contracts/{self.contract_id}')

        with open(TARGET_DIR + 'contract-view.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts/{self.contract_id}')
            self.contract = response.json["data"]
            self.assertEqual(self.contract["buyer"]["contract_owner"], "broker6")
            self.assertEqual(self.contract["suppliers"][0]["contract_owner"], "broker")

        # Getting access for contract
        self.app.authorization = ('Basic', ('broker6', ''))

        with open(TARGET_DIR + 'contract-access-invalid.http', 'w') as self.app.file_obj:
            self.app.post_json(
                f"/contracts/{self.contract_id}/access",
                {
                    "data": {
                        "identifier": {"scheme": "UA-EDR", "id": "123456780"},
                    }
                },
                status=403,
            )

        with open(TARGET_DIR + 'contract-access-owner-invalid.http', 'w') as self.app.file_obj, change_auth(
            self.app, ("Basic", ("token", ""))
        ):
            self.app.post_json(
                f"/contracts/{self.contract_id}/access",
                {
                    "data": {
                        "identifier": self.contract["buyer"]["identifier"],
                    }
                },
                status=403,
            )

        with open(TARGET_DIR + 'contract-access-by-buyer.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f"/contracts/{self.contract_id}/access",
                {
                    "data": {
                        "identifier": self.contract["buyer"]["identifier"],
                    }
                },
            )
            buyer_token_1 = response.json["access"]["token"]
        with open(TARGET_DIR + 'contract-access-by-buyer-2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f"/contracts/{self.contract_id}/access",
                {
                    "data": {
                        "identifier": self.contract["buyer"]["identifier"],
                    }
                },
            )
            buyer_token_2 = response.json["access"]["token"]

        with open(TARGET_DIR + 'contract-patch-by-buyer-1-forbidden.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                f"/contracts/{self.contract_id}?acc_token={buyer_token_1}",
                {
                    "data": {
                        "title": "test title",
                    }
                },
                status=403,
            )

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'contract-access-by-supplier.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f"/contracts/{self.contract_id}/access",
                {
                    "data": {
                        "identifier": self.contract["suppliers"][0]["identifier"],
                    }
                },
            )
            supplier_token = response.json["access"]["token"]

        # add signer info from supplier
        response = self.app.put_json(
            f'/contracts/{self.contract_id}/suppliers/signer_info?acc_token={supplier_token}',
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, '200 OK')

        # add signer info from buyer
        self.app.authorization = ('Basic', ('broker6', ''))

        response = self.app.put_json(
            f'/contracts/{self.contract_id}/buyer/signer_info?acc_token={buyer_token_2}', {"data": test_signer_info}
        )
        self.assertEqual(response.status, '200 OK')

        contract_sign_data = {
            "documentType": "contractSignature",
            "title": "sign.p7s",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/pkcs7-signature",
        }

        with open(TARGET_DIR + 'contract-add-signature-in-not-ready-contract.http', 'w') as self.app.file_obj:
            self.app.post_json(
                f'/contracts/{self.contract_id}/documents?acc_token={buyer_token_2}',
                {"data": contract_sign_data},
                status=422,
            )

        # add required fields
        self.app.patch_json(
            f'/contracts/{self.contract_id}?acc_token={buyer_token_2}',
            {
                "data": {
                    "contractNumber": "contract #13111",
                    "period": {
                        "startDate": get_now().isoformat(),
                        "endDate": (get_now() + timedelta(days=365)).isoformat(),
                    },
                }
            },
        )

        with open(TARGET_DIR + 'contract-activating-wo-signature-error.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                f'/contracts/{self.contract_id}?acc_token={buyer_token_2}',
                {"data": {"status": "active"}},
                status=422,
            )

        with change_auth(self.app, ("Basic", ("broker", ""))), open(
            TARGET_DIR + 'contract-supplier-add-signature-doc.http', 'w'
        ) as self.app.file_obj:
            response = self.app.post_json(
                f'/contracts/{self.contract_id}/documents?acc_token={supplier_token}', {"data": contract_sign_data}
            )
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'patch-contract-forbidden.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                f'/contracts/{self.contract_id}?acc_token={buyer_token_2}',
                {"data": {"contractNumber": "contract #13112"}},
                status=403,
            )

        with open(TARGET_DIR + 'contract-buyer-add-signature-doc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/contracts/{self.contract_id}/documents?acc_token={buyer_token_2}', {"data": contract_sign_data}
            )
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'get-active-contract.http', 'w') as self.app.file_obj:
            self.app.get(f'/contracts/{self.contract_id}?acc_token={buyer_token_2}')
