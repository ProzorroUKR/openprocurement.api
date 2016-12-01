# -*- coding: utf-8 -*-
import json
import os
from datetime import timedelta
from copy import deepcopy

from openprocurement.api.models import get_now
import openprocurement.contracting.api.tests.base as base_test
from openprocurement.api.tests.base import PrefixedRequestClass, BaseTenderWebTest
from openprocurement.contracting.api.tests.base import test_contract_data
from webtest import TestApp
from openprocurement.api.tests.base import test_tender_data, test_organization


class DumpsTestAppwebtest(TestApp):
    def do_request(self, req, status=None, expect_errors=None):
        req.headers.environ["HTTP_HOST"] = "api-sandbox.openprocurement.org"
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            self.file_obj.write(req.as_bytes(True))
            self.file_obj.write("\n")
            if req.body:
                try:
                    self.file_obj.write(
                            'DATA:\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8'))
                    self.file_obj.write("\n")
                except:
                    pass
            self.file_obj.write("\n")
        resp = super(DumpsTestAppwebtest, self).do_request(req, status=status, expect_errors=expect_errors)
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            headers = [(n.title(), v)
                       for n, v in resp.headerlist
                       if n.lower() != 'content-length']
            headers.sort()
            self.file_obj.write(str('Response: %s\n%s\n') % (
                resp.status,
                str('\n').join([str('%s: %s') % (n, v) for n, v in headers]),
            ))

            if resp.testbody:
                try:
                    self.file_obj.write(json.dumps(json.loads(resp.testbody), indent=2, ensure_ascii=False).encode('utf8'))
                except:
                    pass
            self.file_obj.write("\n\n")
        return resp


class TenderResourceTest(BaseTenderWebTest):

    # ('Basic', ('broker', ''))
    initial_data = test_contract_data

    def setUp(self):
        self.app = DumpsTestAppwebtest(
                "config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def tearDown(self):
        self.couchdb_server.delete(self.db.name)

    def test_docs(self):

        self.app.authorization = ('Basic', ('broker', ''))
        # empty tenders listing
        response = self.app.get('/tenders')
        self.assertEqual(response.json['data'], [])
        # create tender
        response = self.app.post_json('/tenders',
                                      {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # switch to active.tendering
        response = self.set_status('active.tendering', {"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}})
        self.assertIn("auctionPeriod", response.json['data'])
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'tenderers': [test_organization], "value": {"amount": 500}}})
        # switch to active.qualification
        self.set_status('active.auction', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
        self.assertNotIn('auctionPeriod', response.json['data'])
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "active"}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand slill period
        self.app.authorization = ('Basic', ('chronograph', ''))
        self.set_status('complete', {'status': 'active.awarded'})
        # time travel
        tender = self.db.get(tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token), {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/example_tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender_id))
            self.assertEqual(response.json['data']['status'], 'complete')

        with open('docs/source/tutorial/example_contract.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}'.format(tender_id, response.json['data']['contracts'][0]['id']))
        test_contract_data = response.json['data']

        request_path = '/contracts'
        #### Exploring basic rules
        #

        with  open('docs/source/tutorial/contracts-listing-0.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        #### Sync contract (i.e. simulate contracting databridge sync actions)
        #
        self.app.authorization = ('Basic', ('contracting', ''))

        response = self.app.get('/tenders/{}/extract_credentials'.format(tender_id))
        test_contract_data['owner'] = response.json['data']['owner']
        test_contract_data['tender_token'] = response.json['data']['tender_token']
        test_contract_data['tender_id'] = tender_id
        test_contract_data['procuringEntity'] = tender['procuringEntity']
        del test_contract_data['status']

        response = self.app.post_json(request_path, {"data": test_contract_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.json['data']['status'], 'active')

        # Getting contract
        self.app.authorization = None

        with open('docs/source/tutorial/contract-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}'.format(test_contract_data['id']))
            self.assertEqual(response.status, '200 OK')
            contract = response.json['data']
            self.assertEqual(contract['status'], 'active')

        # Getting access
        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/contract-credentials.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/contracts/{}/credentials?acc_token={}'.format(test_contract_data['id'], owner_token))
            self.assertEqual(response.status, '200 OK')
        self.app.get(request_path)
        contract_token = response.json['access']['token']
        contract_id = test_contract_data['id']

        with open('docs/source/tutorial/contracts-listing-1.http', 'w') as self.app.file_obj:
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 1)

        # Modifying contract

        # Submitting contract change
        # add contract change
        with open('docs/source/tutorial/add-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(contract_id, contract_token),
                                          {'data': {'rationale': u'Опис причини змін контракту',
                                                    'rationale_en': 'Contract change cause',
                                                    'rationaleTypes': ['volumeCuts', 'priceReduction']}})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            change = response.json['data']

        with open('docs/source/tutorial/view-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}/changes/{}'.format(contract_id, change['id']))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['id'], change['id'])

        with open('docs/source/tutorial/patch-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(contract_id, change['id'], contract_token),
                                          {'data': {'rationale': u'Друга і третя поставка має бути розфасована'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            change = response.json['data']

        # add contract change document
        with open('docs/source/tutorial/add-contract-change-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
                contract_id, contract_token), upload_files=[('file', 'contract_changes.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            doc_id = response.json["data"]['id']

        with open('docs/source/tutorial/set-document-of-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/contracts/{}/documents/{}?acc_token={}'.format(contract_id, doc_id, contract_token), {"data": {
                "documentOf": "change",
                "relatedItem": change['id'],
            }})
            self.assertEqual(response.status, '200 OK')

        # updating contract properties
        with open('docs/source/tutorial/contracts-patch.http', 'w') as self.app.file_obj:
            custom_period_start_date = get_now().isoformat()
            custom_period_end_date = (get_now() + timedelta(days=30)).isoformat()
            response = self.app.patch_json('/contracts/{}?acc_token={}'.format(contract_id, contract_token),
                                           {"data": {"value": {"amount": 438},
                                                     "period": {'startDate': custom_period_start_date,
                                                                'endDate': custom_period_end_date}}})
            self.assertEqual(response.status, '200 OK')

        # add item
        with open('docs/source/tutorial/add-contract-item.http', 'w') as self.app.file_obj:
            item = deepcopy(response.json['data']['items'][0])
            del item['id']
            item["description"] = u"коробки для футлярів до державних нагород"
            response = self.app.patch_json('/contracts/{}?acc_token={}'.format(contract_id, contract_token),
                                           {"data": {"items": [{}, item]}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']['items']), 2)

        # update item
        with open('docs/source/tutorial/update-contract-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/contracts/{}?acc_token={}'.format(contract_id, contract_token),
                                           {"data": {"items": [{}, {'quantity': 2}]}, })
            self.assertEqual(response.status, '200 OK')
            item2 = response.json['data']['items'][1]
            self.assertEqual(item2['quantity'], 2)

        # delete item
        with open('docs/source/tutorial/delete-contract-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/contracts/{}?acc_token={}'.format(contract_id, contract_token),
                                           {"data": {"items": [item2]}, })
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']['items']), 1)

        # apply contract change
        with open('docs/source/tutorial/apply-contract-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(contract_id, change['id'], contract_token),
                                           {'data': {'status': 'active', 'dateSigned': get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')

        with open('docs/source/tutorial/view-all-contract-changes.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}/changes'.format(contract_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 1)

        with open('docs/source/tutorial/view-contract.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}'.format(contract_id))
            self.assertEqual(response.status, '200 OK')
            self.assertIn('changes', response.json['data'])

        # Uploading documentation
        with open('docs/source/tutorial/upload-contract-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
                                     contract_id, contract_token), upload_files=[('file', u'contract.doc', 'content')])

        with open('docs/source/tutorial/contract-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}/documents?acc_token={}'.format(
                                     contract_id, contract_token))

        with open('docs/source/tutorial/upload-contract-document-2.http', 'w') as self.app.file_obj:
            response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
                                     contract_id, contract_token), upload_files=[('file', u'contract_additional_docs.doc', 'additional info')])

        doc_id = response.json['data']['id']

        with open('docs/source/tutorial/upload-contract-document-3.http', 'w') as self.app.file_obj:
            response = self.app.put('/contracts/{}/documents/{}?acc_token={}'.format(
                                    contract_id, doc_id, contract_token),
                                    upload_files=[('file', 'contract_additional_docs.doc', 'extended additional info')])

        with open('docs/source/tutorial/get-contract-document-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}/documents/{}?acc_token={}'.format(contract_id, doc_id, contract_token))


        # Finalize contract
        with open('docs/source/tutorial/contract-termination.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/contracts/{}?acc_token={}'.format(contract_id, contract_token),
                                           {"data": {"status": "terminated", "amountPaid": {"amount": 430}}})
            self.assertEqual(response.status, '200 OK')
