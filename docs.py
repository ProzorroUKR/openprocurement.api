# -*- coding: utf-8 -*-
import json
import os

from copy import deepcopy
from webtest import TestApp
from uuid import uuid4

from openprocurement.api.models import get_now
from openprocurement.api.tests.base import PrefixedRequestClass

from openprocurement.tender.cfaua.tests.base import \
    BaseTenderWebTest, test_tender_data, test_lots
import openprocurement.agreement.cfaua.tests.base as base_test


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
                    self.file_obj.write(
                        json.dumps(json.loads(resp.testbody), indent=2, ensure_ascii=False).encode('utf8'))
                except:
                    pass
            self.file_obj.write("\n\n")
        return resp


class TenderResourceTest(BaseTenderWebTest):

    def setUp(self):
        self.app = DumpsTestAppwebtest(
            "config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        self.setUpDS()
        self.app.app.registry.docservice_url = 'http://public.docs-sandbox.openprocurement.org'

    def generate_docservice_url(self):
        return super(TenderResourceTest, self).generate_docservice_url().replace(
            '/localhost/', '/public.docs-sandbox.openprocurement.org/'
        )

    def tearDown(self):
        self.couchdb_server.delete(self.db.name)

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

        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']

        # switch to complete - dirty hack
        response = self.set_status('complete')

        # check status
        with open('docs/source/tutorial/example_tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender_id))
            self.assertEqual(response.json['data']['status'], 'complete')
            tender = response.json['data']

        with open('docs/source/tutorial/example_agreement.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/agreements/{}'.format(
                tender_id, response.json['data']['agreements'][0]['id']))
        test_agreement_data = response.json['data']

        # # empty agreements listing
        request_path = '/agreements'
        #### Exploring basic rules
        with open('docs/source/tutorial/agreements-listing-0.http', 'w') as self.app.file_obj:
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
        response = self.app.post_json(request_path, {"data": test_agreement_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.json['data']['status'], 'active')
        self.app.get(request_path)  # need to start couchdb indexing views, so next request gives results

        # Getting agreement
        self.app.authorization = None

        with open('docs/source/tutorial/agreement-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}'.format(test_agreement_data['id']))
            self.assertEqual(response.status, '200 OK')
            agreement = response.json['data']

        # Getting access
        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/agreement-credentials.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/agreements/{}/credentials?acc_token={}'.format(
                test_agreement_data['id'], owner_token))
            self.assertEqual(response.status, '200 OK')
        agreement_token = response.json['access']['token']
        agreement_id = test_agreement_data['id']

        with open('docs/source/tutorial/agreements-listing-1.http', 'w') as self.app.file_obj:
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 1)

        # Modifying agreement

        # Submitting agreement change
        with open('docs/source/tutorial/add-agreement-change.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/agreements/{}/changes?acc_token={}'.format(
                agreement_id, agreement_token), {'data': {'rationale': u'Опис причини змін егріменту',
                                                          'rationale_en': 'Agreement change cause',
                                                          'rationaleType': 'taxRate'}})
            self.assertEqual(response.status, '201 Created')
            change = response.json['data']

        with open('docs/source/tutorial/view-agreement-change.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}/changes/{}'.format(agreement_id, change['id']))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['id'], change['id'])

        with open('docs/source/tutorial/patch-agreement-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/agreements/{}/changes/{}?acc_token={}'.format(
                agreement_id, change['id'], agreement_token),
                {'data': {'rationale': u'Друга і третя поставка має бути розфасована'}})
            self.assertEqual(response.status, '200 OK')
            change = response.json['data']

        # add agreement change document
        with open('docs/source/tutorial/add-agreement-change-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/agreements/{}/documents?acc_token={}'.format(
                agreement_id, agreement_token), upload_files=[('file', u'agreement_changes.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            doc_id = response.json["data"]['id']

        with open('docs/source/tutorial/set-document-of-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/agreements/{}/documents/{}?acc_token={}'.format(
                agreement_id, doc_id, agreement_token),
                {"data": {"documentOf": "change",
                          "relatedItem": change['id'],
                          }})
            self.assertEqual(response.status, '200 OK')
        # patching change with modification
        with open('docs/source/tutorial/add-agreement-change-modification.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/agreements/{}/changes/{}?acc_token={}'.format(
                agreement_id, change['id'], agreement_token),
                {'data': {
                    'modifications': [
                        {'itemId': agreement['items'][0]['id'],
                         'factor': 0.1605}
                    ]}})
            self.assertEqual(response.status, '200 OK')
            change = response.json['data']

        # preview agreement
        with open('docs/source/tutorial/agreement_preview.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}/preview?acc_token={}'.format(agreement_id, agreement_token))
            self.assertEqual(response.status, '200 OK')

        # apply agreement change
        with open('docs/source/tutorial/apply-agreement-change.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/agreements/{}/changes/{}?acc_token={}'.format(
                agreement_id, change['id'], agreement_token),
                {'data': {'status': 'active', 'dateSigned': get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/view-all-agreement-changes.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}/changes'.format(agreement_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 1)

        with open('docs/source/tutorial/view-agreement.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}'.format(agreement_id))
            self.assertEqual(response.status, '200 OK')
            self.assertIn('changes', response.json['data'])

        # Uploading documentation
        with open('docs/source/tutorial/upload-agreement-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/agreements/{}/documents?acc_token={}'.format(
                agreement_id, agreement_token), upload_files=[('file', u'agreement.doc', 'content')])

        with open('docs/source/tutorial/agreement-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}/documents?acc_token={}'.format(
                agreement_id, agreement_token))

        with open('docs/source/tutorial/upload-agreement-document-2.http', 'w') as self.app.file_obj:
            response = self.app.post('/agreements/{}/documents?acc_token={}'.format(
                agreement_id, agreement_token),
                upload_files=[('file', u'agreement_additional_docs.doc', 'additional info')])

        doc_id = response.json['data']['id']

        with open('docs/source/tutorial/upload-agreement-document-3.http', 'w') as self.app.file_obj:
            response = self.app.put('/agreements/{}/documents/{}?acc_token={}'.format(
                agreement_id, doc_id, agreement_token),
                upload_files=[('file', 'agreement_additional_docs.doc', 'extended additional info')])

        with open('docs/source/tutorial/get-agreement-document-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/agreements/{}/documents/{}?acc_token={}'.format(
                agreement_id, doc_id, agreement_token))

        # Finalize agreement
        with open('docs/source/tutorial/agreement-termination.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/agreements/{}?acc_token={}'.format(
                agreement_id, agreement_token), {"data": {"status": "terminated"}})
            self.assertEqual(response.status, '200 OK')
