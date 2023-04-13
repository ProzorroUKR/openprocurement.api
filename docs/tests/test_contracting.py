# -*- coding: utf-8 -*-
import os
from datetime import timedelta
from copy import deepcopy

from openprocurement.api.models import get_now
from openprocurement.contracting.api.tests.base import test_contract_data
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest,
    test_tender_below_multi_buyers_data,
    test_tender_below_data,
    test_tender_below_organization,
)

from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)
from tests.base.constants import DOCS_URL

test_tender_data = deepcopy(test_tender_below_data)
test_tender_data_multi_buyers = deepcopy(test_tender_below_multi_buyers_data)

TARGET_DIR = 'docs/source/contracting/http/'


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_contract_data
    docservice = True
    docservice_url = DOCS_URL

    def setUp(self):
        super(TenderResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderResourceTest, self).tearDown()

    def test_docs(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # empty tenders listing
        response = self.app.get('/tenders')
        self.assertEqual(response.json['data'], [])
        # create tender
        test_tender_below_data['items'].append(deepcopy(test_tender_below_data['items'][0]))
        for item in test_tender_below_data['items']:
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat()
            }
        test_tender_below_data.update(
            {
                "enquiryPeriod": {"endDate": (get_now() + timedelta(days=7)).isoformat()},
                "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()}
            }
        )
        response = self.app.post_json('/tenders', {'data': test_tender_below_data, 'config': self.initial_config})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # switch to active.tendering
        response = self.set_status(
            'active.tendering',
            {"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}}
        )
        self.assertIn("auctionPeriod", response.json['data'])
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        self.create_bid(self.tender_id, {'tenderers': [test_tender_below_organization], "value": {"amount": 500}})
        # switch to active.qualification
        self.set_status('active.auction', {'status': 'active.tendering'})
        response = self.check_chronograph()
        self.assertNotIn('auctionPeriod', response.json['data'])
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        # set award as active
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token),
            {"data": {"status": "active"}}
        )
        # get contract id
        response = self.app.get('/tenders/{}'.format(tender_id))
        contract = response.json['data']['contracts'][-1]
        contract_id = contract['id']
        # after stand slill period
        # self.app.authorization = ('Basic', ('chronograph', ''))
        self.set_status('complete', {'status': 'active.awarded'})
        self.tick()
        # time travel
        tender = self.mongodb.tenders.get(tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.mongodb.tenders.save(tender)
        # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        contract["value"]["amountNet"] = 490
        self.app.patch_json(
            '/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token),
            {"data": {"status": "active", "value": contract["value"]}}
        )
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'example_tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender_id))
            self.assertEqual(response.json['data']['status'], 'complete')

        with open(TARGET_DIR + 'example_contract.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/contracts/{}'.format(tender_id, response.json['data']['contracts'][0]['id'])
            )
        test_contract_data = response.json['data']

        request_path = '/contracts'

        #### Exploring basic rules

        with open(TARGET_DIR + 'contracts-listing-0.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        #### Sync contract (i.e. simulate contracting databridge sync actions)
        self.app.authorization = ('Basic', ('contracting', ''))

        response = self.app.get('/tenders/{}/extract_credentials'.format(tender_id))
        test_contract_data['owner'] = response.json['data']['owner']
        test_contract_data['tender_token'] = response.json['data']['tender_token']
        test_contract_data['tender_id'] = tender_id
        test_contract_data['procuringEntity'] = tender['procuringEntity']
        del test_contract_data['status']

        response = self.app.post_json(
            request_path,
            {'data': test_contract_data}
        )
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.json['data']['status'], 'active')

        # Getting contract
        self.app.authorization = None

        with open(TARGET_DIR + 'contract-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}'.format(test_contract_data['id']))
            self.assertEqual(response.status, '200 OK')
            contract = response.json['data']
            self.assertEqual(contract['status'], 'active')

        # Getting access
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'contract-credentials.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}/credentials?acc_token={}'.format(test_contract_data['id'], owner_token)
            )
            self.assertEqual(response.status, '200 OK')
        self.app.get(request_path)
        contract_token = response.json['access']['token']
        contract_id = test_contract_data['id']
        contract = deepcopy(test_contract_data)

        with open(TARGET_DIR + 'contracts-listing-1.http', 'w') as self.app.file_obj:
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 1)

        # Modifying contract

        # Submitting contract change add contract change
        with open(TARGET_DIR + 'add-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/contracts/{}/changes?acc_token={}'.format(contract_id, contract_token),
                {
                    'data': {
                        'rationale': 'Опис причини змін контракту',
                        'rationale_en': 'Contract change cause',
                        'rationaleTypes': ['volumeCuts', 'priceReduction']
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            change = response.json['data']

        with open(TARGET_DIR + 'view-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}/changes/{}'.format(contract_id, change['id']))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['id'], change['id'])

        with open(TARGET_DIR + 'patch-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}/changes/{}?acc_token={}'.format(contract_id, change['id'], contract_token),
                {'data': {'rationale': 'Друга і третя поставка має бути розфасована'}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            change = response.json['data']

        # add contract change document
        with open(TARGET_DIR + 'add-contract-change-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/contracts/{}/documents?acc_token={}'.format(
                    contract_id, contract_token
                ),
                {
                    "data": {
                        "title": "contract_changes.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            doc_id = response.json["data"]['id']

        with open(TARGET_DIR + 'set-document-of-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}/documents/{}?acc_token={}'.format(contract_id, doc_id, contract_token),
                {
                    'data': {
                        "documentOf": "change",
                        "relatedItem": change['id'],
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        # updating contract properties
        with open(TARGET_DIR + 'contracts-patch.http', 'w') as self.app.file_obj:
            custom_period_start_date = get_now().isoformat()
            custom_period_end_date = (get_now() + timedelta(days=30)).isoformat()
            response = self.app.patch_json(
                '/contracts/{}?acc_token={}'.format(contract_id, contract_token),
                {
                    "data": {
                        "value": {"amount": 438, "amountNet": 430},
                        "period": {
                            'startDate': custom_period_start_date,
                            'endDate': custom_period_end_date
                        }
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        # update item
        contract["items"][0]["quantity"] = 2
        # contract["items"][1] = {}
        with open(TARGET_DIR + 'update-contract-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}?acc_token={}'.format(contract_id, contract_token),
                {"data": {"items": contract["items"]}, }
            )
            self.assertEqual(response.status, '200 OK')
            item2 = response.json['data']['items'][0]
            self.assertEqual(item2['quantity'], 2)

        # apply contract change
        with open(TARGET_DIR + 'apply-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}/changes/{}?acc_token={}'.format(contract_id, change['id'], contract_token),
                {'data': {'status': 'active', 'dateSigned': get_now().isoformat()}}
            )
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')

        with open(TARGET_DIR + 'view-all-contract-changes.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}/changes'.format(contract_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 1)

        with open(TARGET_DIR + 'view-contract.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}'.format(contract_id))
            self.assertEqual(response.status, '200 OK')
            self.assertIn('changes', response.json['data'])

        # Uploading documentation
        with open(TARGET_DIR + 'upload-contract-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/contracts/{}/documents?acc_token={}'.format(
                    contract_id, contract_token
                ),
                {
                    "data": {
                        "title": "contract.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                }
            )

        with open(TARGET_DIR + 'contract-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/contracts/{}/documents?acc_token={}'.format(
                    contract_id, contract_token
                )
            )

        with open(TARGET_DIR + 'upload-contract-document-2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/contracts/{}/documents?acc_token={}'.format(
                    contract_id, contract_token
                ),
                {
                    "data": {
                        "title": "contract_additional_docs.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                }
            )

        doc_id = response.json['data']['id']

        with open(TARGET_DIR + 'upload-contract-document-3.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/contracts/{}/documents/{}?acc_token={}'.format(
                    contract_id, doc_id, contract_token
                ),
                {
                    "data": {
                        "title": "contract_additional_docs.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                }
            )

        with open(TARGET_DIR + 'get-contract-document-3.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/contracts/{}/documents/{}?acc_token={}'.format(contract_id, doc_id, contract_token)
            )

        # Finalize contract
        with open(TARGET_DIR + 'contract-termination.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}?acc_token={}'.format(contract_id, contract_token),
                {
                    "data": {
                        "status": "terminated",
                        "amountPaid": {"amount": 430, "amountNet": 420, "valueAddedTaxIncluded": True},
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')


class MultiContractsTenderResourceTest(BaseTenderWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data_multi_buyers
    docservice = False
    docservice_url = DOCS_URL

    def setUp(self):
        super(MultiContractsTenderResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(MultiContractsTenderResourceTest, self).tearDown()

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
                "endDate": (get_now() + timedelta(days=5)).isoformat()
            }

        tender_data.update(
            {
                "enquiryPeriod": {"endDate": (get_now() + timedelta(days=7)).isoformat()},
                "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()}
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
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.owner_token))

        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        # set award as active
        with open(TARGET_DIR + 'set-active-award.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.owner_token),
                {"data": {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')

        self.process_tender_to_awarded()

        # get contracts
        with open(TARGET_DIR + 'get-multi-contracts.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
        contracts = response.json['data']

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'patch-1st-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contracts[0]["id"], self.owner_token),
                {"data": {"value": {"amount": 100, "amountNet": 95}}}
            )
            self.assertEqual(response.status, '200 OK')
        with open(TARGET_DIR + 'patch-2nd-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contracts[1]["id"], self.owner_token),
                {"data": {"value": {"amount": 200, "amountNet": 190}}}
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contracts[0]["id"], self.owner_token),
            {"data": {"status": "active"}}
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contracts[1]["id"], self.owner_token),
            {"data": {"status": "active"}}
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.get(
            '/tenders/{}'.format(self.tender_id)
        )
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
                "endDate": (get_now() + timedelta(days=5)).isoformat()
            }

        tender_data.update(
            {
                "enquiryPeriod": {"endDate": (get_now() + timedelta(days=7)).isoformat()},
                "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()}
            }
        )

        response = self.app.post_json('/tenders', {'data': tender_data, 'config': self.initial_config})
        self.assertEqual(response.status, '201 Created')
        self.tender_id = response.json['data']['id']
        self.owner_token = response.json['access']['token']

        self.process_tender_to_qualification()

        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.owner_token))

        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        # set award as active
        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.owner_token),
            {"data": {"status": "active"}}
        )
        self.assertEqual(response.status, '200 OK')

        self.process_tender_to_awarded()

        # get contracts
        with open(TARGET_DIR + 'get-multi-contracts.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
        contracts = response.json['data']

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'patch-to-cancelled-1st-contract.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contracts[0]["id"], self.owner_token),
                {"data": {"status": "cancelled"}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'patch-to-cancelled-2nd-contract-error.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contracts[1]["id"], self.owner_token),
                {"data": {"status": "cancelled"}}, status=403
            )
            self.assertEqual(response.status, '403 Forbidden')

        # set award cancelled
        with open(TARGET_DIR + 'set-cancelled-award.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.owner_token),
                {"data": {"status": "cancelled"}}
            )
            self.assertEqual(response.status, '200 OK')

        # get contracts cancelled
        with open(TARGET_DIR + 'get-multi-contracts-cancelled.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

    def process_tender_to_qualification(self):
        # switch to active.tendering
        response = self.set_status(
            'active.tendering',
            {"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}}
        )
        self.assertIn("auctionPeriod", response.json['data'])

        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': {'tenderers': [test_tender_below_organization], "value": {"amount": 500}}}
        )
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']

        response = self.app.patch_json(
            f'/tenders/{self.tender_id}/bids/{bid_id}?acc_token={bid_token}',
            {'data': {'status': 'active'}}
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
