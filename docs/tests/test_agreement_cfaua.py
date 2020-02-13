# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from uuid import uuid4

from openprocurement.api.utils import get_now
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderWebTest, test_tender_data, test_lots
)



from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.base.constants import DOCS_URL

TARGET_DIR = 'docs/source/agreementcfaua/tutorial/'


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
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

        # create cfaua tender, first prepare data
        lot = deepcopy(test_lots[0])
        lot['id'] = uuid4().hex
        test_tender_data['lots'] = [lot]
        test_tender_data['items'][0]['relatedLot'] = lot['id']

        response = self.app.post_json('/tenders', {'data': test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']

        # switch to complete - dirty hack
        self.set_status('complete')

        # check status
        with open(TARGET_DIR + 'example_tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender_id))
            self.assertEqual(response.json['data']['status'], 'complete')
            tender = response.json['data']

        with open(TARGET_DIR + 'example_agreement.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements/{}'.format(
                tender_id, response.json['data']['agreements'][0]['id']))
        test_agreement_data = response.json['data']

        # empty agreements listing
        request_path = '/agreements'

        #### Exploring basic rules
        with open(TARGET_DIR + 'agreements-listing-0.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        #### Sync agreement (i.e. simulate agreement databridge sync actions)

        self.app.authorization = ('Basic', ('contracting', ''))

        response = self.app.get('/tenders/{}/extract_credentials'.format(tender_id))
        test_agreement_data['owner'] = response.json['data']['owner']
        test_agreement_data['tender_token'] = response.json['data']['tender_token']
        test_agreement_data['tender_id'] = tender_id
        test_agreement_data['procuringEntity'] = tender['procuringEntity']

        self.app.authorization = ('Basic', ('agreements', ''))
        response = self.app.post_json(request_path, {'data': test_agreement_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.json['data']['status'], 'active')
        self.app.get(request_path)  # need to start couchdb indexing views, so next request gives results

        # Getting agreement
        self.app.authorization = None

        with open(TARGET_DIR + 'agreement-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}'.format(test_agreement_data['id']))
            self.assertEqual(response.status, '200 OK')
            agreement = response.json['data']

        # Getting access
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'agreement-credentials.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/agreements/{}/credentials?acc_token={}'.format(
                    test_agreement_data['id'], owner_token))
            self.assertEqual(response.status, '200 OK')
        agreement_token = response.json['access']['token']
        agreement_id = test_agreement_data['id']

        with open(TARGET_DIR + 'agreements-listing-1.http', 'w') as self.app.file_obj:
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 1)

        # Modifying agreement

        # Submitting agreement change
        with open(TARGET_DIR + 'add-agreement-change.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/agreements/{}/changes?acc_token={}'.format(
                    agreement_id, agreement_token),
                {'data': {
                    'rationale': u'Опис причини змін егріменту',
                    'rationale_en': 'Agreement change cause',
                    'rationaleType': 'taxRate'
                }})
            self.assertEqual(response.status, '201 Created')
            change = response.json['data']

        with open(TARGET_DIR + 'view-agreement-change.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}/changes/{}'.format(agreement_id, change['id']))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['id'], change['id'])

        with open(TARGET_DIR + 'patch-agreement-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/agreements/{}/changes/{}?acc_token={}'.format(
                    agreement_id, change['id'], agreement_token),
                {'data': {'rationale': u'Друга і третя поставка має бути розфасована'}})
            self.assertEqual(response.status, '200 OK')
            change = response.json['data']

        # add agreement change document
        with open(TARGET_DIR + 'add-agreement-change-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/agreements/{}/documents?acc_token={}'.format(
                agreement_id, agreement_token),
                upload_files=[('file', u'agreement_changes.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            doc_id = response.json["data"]['id']

        with open(TARGET_DIR + 'set-document-of-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/agreements/{}/documents/{}?acc_token={}'.format(
                    agreement_id, doc_id, agreement_token),
                {"data": {
                    "documentOf": "change",
                    "relatedItem": change['id'],
                }})
            self.assertEqual(response.status, '200 OK')

        # patching change with modification
        with open(TARGET_DIR + 'add-agreement-change-modification.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/agreements/{}/changes/{}?acc_token={}'.format(
                    agreement_id, change['id'], agreement_token),
                {'data': {
                    'modifications': [{
                        'itemId': agreement['items'][0]['id'],
                        'factor': 0.1605
                    }]
                }})
            self.assertEqual(response.status, '200 OK')
            change = response.json['data']

        # preview agreement
        with open(TARGET_DIR + 'agreement_preview.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}/preview?acc_token={}'.format(agreement_id, agreement_token))
            self.assertEqual(response.status, '200 OK')

        # apply agreement change
        with open(TARGET_DIR + 'apply-agreement-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/agreements/{}/changes/{}?acc_token={}'.format(
                    agreement_id, change['id'], agreement_token),
                {'data': {'status': 'active', 'dateSigned': get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'view-all-agreement-changes.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}/changes'.format(agreement_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 1)

        with open(TARGET_DIR + 'view-agreement.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}'.format(agreement_id))
            self.assertEqual(response.status, '200 OK')
            self.assertIn('changes', response.json['data'])

        # Uploading documentation
        with open(TARGET_DIR + 'upload-agreement-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/agreements/{}/documents?acc_token={}'.format(
                agreement_id, agreement_token),
                upload_files=[('file', u'agreement.doc', 'content')])

        with open(TARGET_DIR + 'agreement-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}/documents?acc_token={}'.format(
                agreement_id, agreement_token))

        with open(TARGET_DIR + 'upload-agreement-document-2.http', 'w') as self.app.file_obj:
            response = self.app.post('/agreements/{}/documents?acc_token={}'.format(
                agreement_id, agreement_token),
                upload_files=[('file', u'agreement_additional_docs.doc', 'additional info')])

        doc_id = response.json['data']['id']

        with open(TARGET_DIR + 'upload-agreement-document-3.http', 'w') as self.app.file_obj:
            response = self.app.put('/agreements/{}/documents/{}?acc_token={}'.format(
                agreement_id, doc_id, agreement_token),
                upload_files=[('file', 'agreement_additional_docs.doc', 'extended additional info')])

        with open(TARGET_DIR + 'get-agreement-document-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}/documents/{}?acc_token={}'.format(
                agreement_id, doc_id, agreement_token))

        # Finalize agreement
        with open(TARGET_DIR + 'agreement-termination.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/agreements/{}?acc_token={}'.format(
                    agreement_id, agreement_token),
                {'data': {"status": "terminated"}})
            self.assertEqual(response.status, '200 OK')
