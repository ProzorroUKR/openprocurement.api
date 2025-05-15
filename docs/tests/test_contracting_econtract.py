import os
from copy import deepcopy
from datetime import datetime, timedelta
from uuid import uuid4

from dateutil.parser import parse
from tests.base.constants import DOCS_URL, MOCK_DATETIME
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

from openprocurement.api.utils import get_now
from openprocurement.contracting.econtract.tests.data import (
    test_contract_data,
    test_signer_info,
)
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest as BaseBelowWebTest,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_multi_buyers_data,
    test_tender_below_organization,
)
from openprocurement.tender.core.tests.mock import patch_market
from openprocurement.tender.core.tests.utils import set_tender_criteria
from openprocurement.tender.pricequotation.tests.base import BaseTenderWebTest
from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_category,
    test_tender_pq_criteria_1,
    test_tender_pq_data,
    test_tender_pq_organization,
    test_tender_pq_response_1,
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


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
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
        with open(TARGET_DIR + 'contracts-listing-0.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/contracts')
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        self.app.authorization = ('Basic', ('broker', ''))
        # empty tenders listing
        response = self.app.get('/tenders')
        self.assertEqual(response.json['data'], [])

        # create tender
        test_tender_data['items'].append(deepcopy(test_tender_data['items'][0]))
        for item in test_tender_data['items']:
            item["id"] = uuid4().hex
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat(),
            }
        tender_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_1))
        set_tender_criteria(
            tender_criteria,
            test_tender_data.get("lots", []),
            test_tender_data.get("items", []),
        )
        test_tender_data.update(
            {
                "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()},
                "criteria": tender_criteria,
            }
        )

        agreement = {"id": self.agreement_id}
        test_tender_data["agreement"] = agreement

        response = self.app.post_json('/tenders', {'data': test_tender_data, 'config': self.initial_config})
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
        bid, bid_token = self.create_bid(
            self.tender_id,
            {
                'tenderers': [test_tender_pq_organization],
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
                    },
                    {
                        "id": tender_items[1]["id"],
                        "description": "Комп’ютерне обладнання",
                        "quantity": 5,
                        "unit": {
                            "name": "кг",
                            "code": "KGM",
                            "value": {"amount": 10, "valueAddedTaxIncluded": False},
                        },
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
        contract_id = contract['id']

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'example_contract.http', 'w') as self.app.file_obj:
            self.app.get(f'/tenders/{tender_id}/contracts/{contract_id}')

        request_path = '/contracts'

        #### Exploring basic rules

        # with open(TARGET_DIR + 'contracts-listing-0.http', 'w') as self.app.file_obj:
        #     self.app.authorization = None
        #     response = self.app.get(request_path)
        #     self.assertEqual(response.status, '200 OK')
        #     self.app.file_obj.write("\n")

        # Getting contract
        self.app.authorization = None

        with open(TARGET_DIR + 'contract-view.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts/{contract_id}')
        self.assertEqual(response.status, '200 OK')
        contract = response.json['data']
        self.assertEqual(contract['status'], 'pending')

        # Getting access
        # Deprecated method
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'deprecated-contract-credentials.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(f'/contracts/{contract_id}/credentials?acc_token={tender_token}')
        self.assertEqual(response.status, '200 OK')
        self.app.get(request_path)

        with open(TARGET_DIR + 'contracts-listing-1.http', 'w') as self.app.file_obj:
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 1)

        # Getting access for contract
        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'contracts-access-invalid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f"/contracts/{contract_id}/access",
                {
                    "data": {
                        "identifier": {"scheme": "UA-EDR", "id": "123456780"},
                    }
                },
                status=403,
            )

        with open(TARGET_DIR + 'contracts-access-by-buyer-1.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f"/contracts/{contract_id}/access",
                {
                    "data": {
                        "identifier": contract["buyer"]["identifier"],
                    }
                },
            )
            buyer_token_1 = response.json["access"]["token"]

        with open(TARGET_DIR + 'contracts-access-by-buyer-2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f"/contracts/{contract_id}/access",
                {
                    "data": {
                        "identifier": contract["buyer"]["identifier"],
                    }
                },
            )
            buyer_token_2 = owner_token = response.json["access"]["token"]

        with open(TARGET_DIR + 'contracts-access-by-buyer-2-submit.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f"/contracts/{contract_id}/access?acc_token={buyer_token_2}",
                {
                    "data": {
                        "identifier": contract["buyer"]["identifier"],
                        "active": True,
                    }
                },
            )
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'contracts-access-by-buyer-3.http', 'w') as self.app.file_obj:
            self.app.post_json(
                f"/contracts/{contract_id}/access",
                {
                    "data": {
                        "identifier": contract["buyer"]["identifier"],
                    }
                },
                status=403,
            )

        with open(TARGET_DIR + 'contracts-access-by-buyer-1-submit.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                f"/contracts/{contract_id}/access?acc_token={buyer_token_1}",
                {
                    "data": {
                        "identifier": contract["buyer"]["identifier"],
                        "active": True,
                    }
                },
                status=403,
            )

        with open(TARGET_DIR + 'contracts-access-by-supplier.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f"/contracts/{contract_id}/access",
                {
                    "data": {
                        "identifier": contract["suppliers"][0]["identifier"],
                    }
                },
            )
            supplier_token = bid_token = response.json["access"]["token"]

        with open(TARGET_DIR + 'contracts-access-by-supplier-submit.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f"/contracts/{contract_id}/access?acc_token={supplier_token}",
                {
                    "data": {
                        "identifier": contract["suppliers"][0]["identifier"],
                        "active": True,
                    }
                },
            )
            self.assertEqual(response.status, "200 OK")

        # Modifying pending contract

        with open(TARGET_DIR + 'contract-modify-forbidden-with-old-token.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                f"/contracts/{contract_id}?acc_token={tender_token}",
                {"data": {"title": "Updated contract"}},
                status=403,
            )

        contract["value"]["amount"] = 238
        contract["value"]["amountNet"] = 230

        ####  Set contract value

        with open(TARGET_DIR + 'contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}', {"data": {"value": contract["value"]}}
            )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        contract["items"][0]["unit"]["value"] = {
            "amount": 12,
            "currency": contract["value"]["currency"],
            "valueAddedTaxIncluded": contract["value"]["valueAddedTaxIncluded"],
        }

        #### Set contact.item.unit value

        with open(TARGET_DIR + 'contract-set-contract_items_unit-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}', {"data": {"items": contract["items"]}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['items'][0]['unit']['value']['amount'], 12)

        #### Setting contract signature date

        with open(TARGET_DIR + 'contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}', {'data': {"dateSigned": get_now().isoformat()}}
            )
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {
            "period": {"startDate": get_now().isoformat(), "endDate": (get_now() + timedelta(days=365)).isoformat()}
        }
        with open(TARGET_DIR + 'contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}', {'data': {'period': period_dates["period"]}}
            )
        self.assertEqual(response.status, '200 OK')

        #### Uploading Contract documentation

        with open(TARGET_DIR + 'contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/contracts/{contract_id}/documents?acc_token={owner_token}',
                {
                    "data": {
                        "title": "contract_first_document.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'contract-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts/{contract_id}/documents?acc_token={owner_token}')
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'contract-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/contracts/{contract_id}/documents?acc_token={owner_token}',
                {
                    "data": {
                        "title": "contract_second_document.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'contract-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts/{contract_id}/documents?acc_token={owner_token}')
        self.assertEqual(response.status, '200 OK')

        # Cancelling contract

        with open(TARGET_DIR + 'contract-cancelling-error.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}',
                {'data': {'status': 'cancelled'}},
                status=403,
            )
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(
            response.json['errors'],
            [
                {
                    'location': 'body',
                    'name': 'data',
                    'description': 'Can\'t update contract status',
                }
            ],
        )

        with open(TARGET_DIR + 'award-cancelling.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{tender_id}/awards/{award_id}?acc_token={tender_token}',
                {"data": {"status": "cancelled"}},
            )

        self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'tender-contract-cancelled.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/tenders/{tender_id}/contracts/{contract_id}')
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "cancelled")

        with open(TARGET_DIR + 'contract-cancelled.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts/{contract_id}')
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "cancelled")

        # Rollback cancelling contract
        tender_document = self.mongodb.tenders.get(tender_id)
        tender_document['awards'][0]['status'] = 'active'
        tender_document['contracts'][0]['status'] = 'pending'
        self.mongodb.tenders.save(tender_document)

        contract_document = self.mongodb.contracts.get(contract_id)
        contract_document['status'] = 'pending'
        contract_document["items"][0]["unit"]["value"][
            "amount"
        ] = 18  # to correct sum of items not be less than 20% of contract.value
        self.mongodb.contracts.save(contract_document)

        # Set contractTemplateName
        contract_document = self.mongodb.contracts.get(contract_id)
        contract_document['contractTemplateName'] = "00000000-0.0002.01"
        self.mongodb.contracts.save(contract_document)

        # Getting contract with contractTemplateName
        with open(TARGET_DIR + 'tender-with-contract-template-name.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts/{contract_id}')
        self.assertEqual(response.status, '200 OK')
        contract = response.json['data']
        self.assertEqual(contract['status'], 'pending')

        # Activating contract
        with open(TARGET_DIR + 'contract-activating-error.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}',
                {"data": {"status": "active"}},
                status=422,
            )

        with open(TARGET_DIR + 'contract-owner-add-signer-info.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                f'/contracts/{contract_id}/buyer/signer_info?acc_token={owner_token}', {"data": test_signer_info}
            )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'contract-supplier-add-signer-info.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                f'/contracts/{contract_id}/suppliers/signer_info?acc_token={bid_token}', {"data": test_signer_info}
            )
        self.assertEqual(response.status, '200 OK')

        update_signer_info = deepcopy(test_signer_info)
        update_signer_info["iban"] = "234" * 5
        with open(TARGET_DIR + 'update-contract-owner-add-signer-info.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                f'/contracts/{contract_id}/buyer/signer_info?acc_token={owner_token}', {"data": update_signer_info}
            )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'contract-activating-error-fields.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}',
                {"data": {"status": "active"}},
                status=422,
            )

        with open(TARGET_DIR + 'contract-activate.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}',
                {"data": {"status": "active", "contractNumber": "contract #13111"}},
            )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], 'active')

        with open(TARGET_DIR + 'tender-complete.http', 'w') as self.app.file_obj:
            response = self.app.get(
                f'/tenders/{tender_id}',
            )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], 'complete')

        with open(TARGET_DIR + 'tender-contract-activated.http', 'w') as self.app.file_obj:
            response = self.app.get(
                f'/tenders/{tender_id}/contracts/{contract_id}',
            )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], 'active')

        # Modifying contract

        # Submitting contract change add contract change
        with open(TARGET_DIR + 'add-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/contracts/{contract_id}/changes?acc_token={owner_token}',
                {
                    'data': {
                        'rationale': 'Опис причини змін контракту',
                        'rationale_en': 'Contract change cause',
                        'rationaleTypes': ['volumeCuts', 'priceReduction'],
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            change = response.json['data']

        with open(TARGET_DIR + 'view-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts/{contract_id}/changes/{change["id"]}')
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['id'], change['id'])

        with open(TARGET_DIR + 'patch-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}/changes/{change["id"]}?acc_token={owner_token}',
                {'data': {'rationale': 'Друга і третя поставка має бути розфасована'}},
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            change = response.json['data']

        # add contract change document
        with open(TARGET_DIR + 'add-contract-change-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/contracts/{contract_id}/documents?acc_token={owner_token}',
                {
                    "data": {
                        "title": "contract_changes.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            doc_id = response.json["data"]['id']

        with open(TARGET_DIR + 'set-document-of-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}/documents/{doc_id}?acc_token={owner_token}',
                {
                    'data': {
                        "documentOf": "change",
                        "relatedItem": change['id'],
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        # updating contract properties
        with open(TARGET_DIR + 'contracts-patch.http', 'w') as self.app.file_obj:
            custom_period_start_date = get_now().isoformat()
            custom_period_end_date = (get_now() + timedelta(days=30)).isoformat()
            response = self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}',
                {
                    "data": {
                        "value": {"amount": 240, "amountNet": 200},
                        "period": {'startDate': custom_period_start_date, 'endDate': custom_period_end_date},
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        # update item
        contract["items"][0]["quantity"] = 20
        contract["items"][0]["unit"]["value"]["amount"] = 9
        # contract["items"][1] = {}
        with open(TARGET_DIR + 'update-contract-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}',
                {
                    "data": {"items": contract["items"]},
                },
            )
            self.assertEqual(response.status, '200 OK')
            item2 = response.json['data']['items'][0]
            self.assertEqual(item2['quantity'], 20)

        # apply contract change
        with open(TARGET_DIR + 'apply-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}/changes/{change["id"]}?acc_token={owner_token}',
                {'data': {'status': 'active', 'dateSigned': get_now().isoformat()}},
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')

        with open(TARGET_DIR + 'view-all-contract-changes.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}/changes'.format(contract_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 1)

        with open(TARGET_DIR + 'view-contract.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts/{contract_id}')
            self.assertEqual(response.status, '200 OK')
            self.assertIn('changes', response.json['data'])

        # Uploading documentation
        with open(TARGET_DIR + 'upload-contract-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/contracts/{contract_id}/documents?acc_token={owner_token}',
                {
                    "data": {
                        "title": "contract.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )

        with open(TARGET_DIR + 'contract-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts/{contract_id}/documents?acc_token={owner_token}')

        with open(TARGET_DIR + 'upload-contract-document-2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/contracts/{contract_id}/documents?acc_token={owner_token}',
                {
                    "data": {
                        "title": "contract_additional_docs.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )

        doc_id = response.json['data']['id']

        with open(TARGET_DIR + 'upload-contract-document-3.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                f'/contracts/{contract_id}/documents/{doc_id}?acc_token={owner_token}',
                {
                    "data": {
                        "title": "contract_additional_docs.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                },
            )

        with open(TARGET_DIR + 'get-contract-document-3.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts/{contract_id}/documents/{doc_id}?acc_token={owner_token}')

        # Finalize contract
        with open(TARGET_DIR + 'contract-termination.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contract_id}?acc_token={owner_token}',
                {
                    "data": {
                        "status": "terminated",
                        "amountPaid": {"amount": 240, "amountNet": 200, "valueAddedTaxIncluded": True},
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')


class MultiContractsTenderResourceTest(BaseBelowWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data_multi_buyers
    docservice_url = DOCS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs(self):
        self.app.authorization = ('Basic', ('broker', ''))

        tender_data = deepcopy(test_tender_below_multi_buyers_data)
        tender_data["buyers"][0]["id"] = "1" * 32
        tender_data["buyers"][1]["id"] = "2" * 32
        tender_data["items"][0]["relatedBuyer"] = "1" * 32
        tender_data["items"][1]["relatedBuyer"] = "2" * 32
        tender_data["items"][2]["relatedBuyer"] = "2" * 32

        for item in tender_data['items']:
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat(),
            }

        tender_data.update(
            {
                "enquiryPeriod": {"endDate": (get_now() + timedelta(days=7)).isoformat()},
                "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()},
            }
        )

        with open(TARGET_DIR + 'create-multiple-buyers-tender.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders', {'data': tender_data, 'config': self.initial_config})
            self.assertEqual(response.status, '201 Created')
        self.tender_id = self.tender_id = response.json['data']['id']
        self.owner_token = response.json['access']['token']

        self.process_tender_to_qualification()

        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get(f'/tenders/{self.tender_id}/awards?acc_token={self.owner_token}')

        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        # set award as active
        self.add_sign_doc(self.tender_id, self.owner_token, docs_url=f"/awards/{award_id}/documents")
        with open(TARGET_DIR + 'set-active-award.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.owner_token}',
                {"data": {"status": "active", "qualified": True}},
            )
            self.assertEqual(response.status, '200 OK')

        self.process_tender_to_awarded()

        # get contracts
        with open(TARGET_DIR + 'get-multi-contracts.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts')
            self.assertEqual(response.status, '200 OK')
        contracts = response.json['data']

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'patch-1st-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contracts[0]["id"]}?acc_token={self.owner_token}',
                {"data": {"value": {"amount": 100, "amountNet": 95}}},
            )
            self.assertEqual(response.status, '200 OK')
        with open(TARGET_DIR + 'patch-2nd-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contracts[1]["id"]}?acc_token={self.owner_token}',
                {"data": {"value": {"amount": 200, "amountNet": 190}}},
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.put_json(
            f'/contracts/{contracts[0]["id"]}/buyer/signer_info?acc_token={self.owner_token}',
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.put_json(
            f'/contracts/{contracts[0]["id"]}/suppliers/signer_info?acc_token={self.bid_token}',
            {"data": test_signer_info},
        )

        response = self.app.put_json(
            f'/contracts/{contracts[1]["id"]}/buyer/signer_info?acc_token={self.owner_token}',
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.put_json(
            f'/contracts/{contracts[1]["id"]}/suppliers/signer_info?acc_token={self.bid_token}',
            {"data": test_signer_info},
        )

        response = self.app.patch_json(
            f'/contracts/{contracts[0]["id"]}?acc_token={self.owner_token}',
            {
                "data": {
                    "status": "active",
                    "contractNumber": "contract #13111",
                    "period": {
                        "startDate": datetime(year=parse(MOCK_DATETIME).year, month=11, day=1).isoformat(),
                        "endDate": datetime(year=parse(MOCK_DATETIME).year, month=12, day=31).isoformat(),
                    },
                }
            },
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            f'/contracts/{contracts[1]["id"]}?acc_token={self.owner_token}',
            {
                "data": {
                    "status": "active",
                    "contractNumber": "contract #13111",
                    "period": {
                        "startDate": datetime(year=parse(MOCK_DATETIME).year, month=11, day=1).isoformat(),
                        "endDate": datetime(year=parse(MOCK_DATETIME).year, month=12, day=31).isoformat(),
                    },
                }
            },
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.get(f'/tenders/{self.tender_id}')
        self.assertEqual(response.json["data"]["status"], "complete")

    def test_docs_contracts_cancelled(self):
        self.app.authorization = ('Basic', ('broker', ''))

        tender_data = deepcopy(test_tender_below_multi_buyers_data)
        tender_data["buyers"][0]["id"] = "1" * 32
        tender_data["buyers"][1]["id"] = "2" * 32
        tender_data["items"][0]["relatedBuyer"] = "1" * 32
        tender_data["items"][1]["relatedBuyer"] = "2" * 32
        tender_data["items"][2]["relatedBuyer"] = "2" * 32

        for item in tender_data['items']:
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat(),
            }

        tender_data.update(
            {
                "enquiryPeriod": {"endDate": (get_now() + timedelta(days=7)).isoformat()},
                "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()},
            }
        )

        with open(TARGET_DIR + 'create-multiple-buyers-tender.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders', {'data': tender_data, 'config': self.initial_config})

        self.assertEqual(response.status, '201 Created')
        self.tender_id = response.json['data']['id']
        self.owner_token = response.json['access']['token']

        self.process_tender_to_qualification()

        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get(f'/tenders/{self.tender_id}/awards?acc_token={self.owner_token}')

        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        # set award as active
        self.add_sign_doc(self.tender_id, self.owner_token, docs_url=f"/awards/{award_id}/documents")
        response = self.app.patch_json(
            f'/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.owner_token}',
            {"data": {"status": "active", "qualified": True}},
        )
        self.assertEqual(response.status, '200 OK')

        self.process_tender_to_awarded()

        # get contracts
        with open(TARGET_DIR + 'get-multi-contracts.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/tenders/{self.tender_id}/contracts')
            self.assertEqual(response.status, '200 OK')
        contracts = response.json['data']

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'patch-to-cancelled-1st-contract.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contracts[0]["id"]}?acc_token={self.owner_token}', {"data": {"status": "cancelled"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'patch-to-cancelled-2nd-contract-error.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/contracts/{contracts[1]["id"]}?acc_token={self.owner_token}',
                {"data": {"status": "cancelled"}},
                status=403,
            )
            self.assertEqual(response.status, '403 Forbidden')

        # set award cancelled
        with open(TARGET_DIR + 'set-cancelled-award.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.owner_token}',
                {"data": {"status": "cancelled"}},
            )
            self.assertEqual(response.status, '200 OK')

        # get contracts cancelled
        with open(TARGET_DIR + 'get-multi-contracts-cancelled.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/contracts?opt_fields=status')
            self.assertEqual(response.status, '200 OK')

    def process_tender_to_qualification(self):
        # switch to active.tendering
        response = self.set_status(
            'active.tendering', {"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}}
        )
        self.assertIn("auctionPeriod", response.json['data'])

        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': {'tenderers': [test_tender_below_organization], "value": {"amount": 500}}},
        )
        self.bid_id = response.json['data']['id']
        self.bid_token = response.json['access']['token']

        response = self.app.patch_json(
            f'/tenders/{self.tender_id}/bids/{self.bid_id}?acc_token={self.bid_token}', {'data': {'status': 'pending'}}
        )

        # switch to active.qualification
        self.set_status('active.auction', {'status': 'active.tendering'})
        response = self.check_chronograph()
        self.assertNotIn('auctionPeriod', response.json['data'])

    def process_tender_to_awarded(self):
        # after stand still period
        # self.app.authorization = ('Basic', ('chronograph', ''))
        self.set_status('complete', {'status': 'active.awarded'})
        self.tick()

        # time travel
        tender = self.mongodb.tenders.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.mongodb.tenders.save(tender)
