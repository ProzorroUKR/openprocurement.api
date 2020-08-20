# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta
from time import sleep
from uuid import uuid4

from openprocurement.api.models import get_now
from openprocurement.tender.cfaselectionua.constants import BOT_NAME
from openprocurement.tender.cfaselectionua.tests.base import (
    BaseTenderWebTest, test_tender_data, test_bids, test_agreement
)

from tests.base.constants import DOCS_URL, AUCTIONS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.base.data import (
    parameters, lot_bid, lot_bid2_with_docs, features,
    tender_cfaselectionua_maximum, lots,
)

bid = deepcopy(lot_bid)
bid2 = deepcopy(lot_bid2_with_docs)
test_features = deepcopy(features)
test_agreement = deepcopy(test_agreement)
test_agreement['contracts'][0]['suppliers'][0]['scale'] = "large"
test_lots = deepcopy(lots)
test_tender_maximum_data = deepcopy(tender_cfaselectionua_maximum)

TARGET_DIR = 'docs/source/tendering/cfaselectionua/tutorial/'


class TenderResourceTest(BaseTenderWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_bids = test_bids
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super(TenderResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderResourceTest, self).tearDown()

    def test_docs_tutorial(self):
        request_path = '/tenders?opt_pretty=1'

        # Exploring basic rules

        with open(TARGET_DIR + 'tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        with open(TARGET_DIR + 'tender-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post(request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        # Creating tender

        agreement_id = uuid4().hex
        agreements = {'agreements': [{'id': agreement_id}]}

        test_features[0]['relatedItem'] = test_agreement['items'][0]['id']
        test_agreement['features'] = test_features
        for contract in test_agreement['contracts']:
            contract['parameters'] = parameters

        lot = deepcopy(test_lots[0])
        lot['id'] = uuid4().hex

        test_tender_data.update(agreements)
        test_tender_data['lots'] = [lot]
        for item in test_tender_data['items']:
            item['relatedLot'] = lot['id']
            item['deliveryDate'] = {
                "startDate": (get_now() + timedelta(days=2)).isoformat(),
                "endDate": (get_now() + timedelta(days=5)).isoformat()
            }

        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        test_tender_maximum_data.update(agreements)
        test_tender_maximum_data['lots'] = [lot]
        test_tender_maximum_data['items'][0]['id'] = uuid4().hex
        test_tender_maximum_data['items'][0]['relatedLot'] = lot['id']

        with open(TARGET_DIR + 'create-tender-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_maximum_data})
            self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tender-switch-draft-pending.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {'status': 'draft.pending'}})
            data = response.json['data']
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'draft.pending')

        self.app.authorization = ('Basic', (BOT_NAME, ''))

        agreement = deepcopy(test_agreement)
        agreement['features'] = test_features

        response = self.app.patch_json(
            '/tenders/{}/agreements/{}'.format(tender['id'], agreement_id),
            {'data': agreement})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}'.format(tender['id']),
            {'data': {'status': 'active.enquiries'}})
        self.assertEqual(response.json['data']['status'], 'active.enquiries')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tender-in-active-enquiries.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.json['data']['status'], 'active.enquiries')
            tender = response.json['data']

        # start couchdb index views
        response = self.app.get('/tenders')

        # wait until couchdb index views complete
        sleep(8)

        with open(TARGET_DIR + 'initial-tender-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders',
            {'data': data})
        self.assertEqual((response.status, response.content_type), ('201 Created', 'application/json'))
        self.tender_id = response.json['data']['id']
        self.tender_token = owner_token = response.json['access']['token']

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(
                self.tender_id, self.tender_token),
            {'data': {'agreements': [test_agreement]}})
        self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(
                self.tender_id, self.tender_token),
            {'data': {'status': 'draft.pending'}})

        self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
        self.assertEqual(response.json['data']['status'], 'draft.pending')

        self.app.authorization = ('Basic', (BOT_NAME, ''))
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(
                self.tender_id, self.tender_token),
            {'data': {'agreements': [test_agreement]}})
        self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(
                self.tender_id, self.tender_token),
            {'data': {'status': 'active.enquiries'}})
        tender = response.json['data']
        self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
        self.assertEqual(response.json['data']['status'], 'active.enquiries')

        self.app.authorization = ('Basic', ('broker', ''))

        # Modifying tender

        tender_period_end_date = get_now() + timedelta(days=15, seconds=10)
        with open(TARGET_DIR + 'patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {
                    "tenderPeriod": {"endDate": tender_period_end_date.isoformat()},
                    "items": [{"quantity": 6}]
                }})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')

        with open(TARGET_DIR + 'tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        # Setting Bid guarantee

        with open(TARGET_DIR + 'set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], owner_token),
                {"data": {"guarantee": {"amount": 8, "currency": "USD"}}})
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        # Uploading documentation

        with open(TARGET_DIR + 'upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {
                    'title': u'Notice.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}'.format(
                self.tender_id, doc_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-document-add-documentType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token),
                {'data': {"documentType": "technicalSpecifications"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-document-edit-docType-desc.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token),
                {'data': {"description": "document description modified"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {
                    'title': u'AwardCriteria.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                {'data': {
                    'title': u'AwardCriteria-2.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # Switch tender to active.tendering

        self.set_status('active.enquiries', start_end='end')
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json(
            '/tenders/{}'.format(tender['id']),
            {'data': {}})
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        # Registering bid

        self.app.authorization = ('Basic', ('broker', ''))
        bids_access = {}

        bid['parameters'] = parameters
        bid['lotValues'][0]['relatedLot'] = lot['id']
        with open(TARGET_DIR + 'register-bidder-invalid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        bid['tenderers'] = tender['agreements'][0]['contracts'][0]['suppliers']
        with open(TARGET_DIR + 'register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid})
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

        # Proposal Uploading

        with open(TARGET_DIR + 'upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {
                    'title': u'Proposal.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        # Second bid registration with documents

        bid2['parameters'] = parameters
        bid2['lotValues'][0]['relatedLot'] = lot['id']
        bid2['tenderers'] = tender['agreements'][0]['contracts'][1]['suppliers']
        with open(TARGET_DIR + 'register-2nd-bidder.http', 'w') as self.app.file_obj:
            for document in bid2['documents']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid2})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        bid3 = deepcopy(bid2)
        bid3['tenderers'] = tender['agreements'][0]['contracts'][3]['suppliers']
        for document in bid3['documents']:
            document['url'] = self.generate_docservice_url()
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid3})
        bid3_id = response.json['data']['id']
        bids_access[bid3_id] = response.json['access']['token']
        self.assertEqual(response.status, '201 Created')

        # Auction

        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction_url = u'{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot['id'])
        patch_data = {
            'lots': [{
                'auctionUrl': auction_url,
            }],
            'bids': [{
                "id": bid1_id,
                "lotValues": [{"participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid1_id)}]
            }, {
                "id": bid2_id,
                "lotValues": [{"participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid2_id)}]
            }, {
                "id": bid3_id,
                "lotValues": [{"participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid3_id)}]
            }]
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot['id'], owner_token),
            {'data': patch_data})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id]))
            self.assertEqual(response.status, '200 OK')

        # Confirming qualification

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot['id']),
            {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'awards-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open(TARGET_DIR + 'award-qualification-unsuccessful.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful"}}, status=403)

        with open(TARGET_DIR + 'award-qualification-active.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active"}})

        with open(TARGET_DIR + 'award-qualification-cancelled.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "cancelled"}})

        # get new pending award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open(TARGET_DIR + 'award-qualification-unsuccessful1.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "unsuccessful"}})

        # post document for unsuccessful award
        with open(TARGET_DIR + 'award-qualification-unsuccessful1_document.http', 'w') as self.app.file_obj:
            self.app.post_json(
                '/tenders/{}/awards/{}/documents?acc_token={}'.format(
                    self.tender_id, award_id, owner_token),
                {"data": {
                    "title": u"explanation.pdf",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                }})

        # get new pending award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open(TARGET_DIR + 'confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.contract_id = [c for c in response.json['data'] if c['status'] == 'pending'][0]['id']

        #  Set contract value

        with open(TARGET_DIR + 'tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {"data": {
                    "contractNumber": "contract #13111",
                    "value": {"amount": 238, "amountNet": 230}
                }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        # Setting contract signature date

        with open(TARGET_DIR + 'tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {'data': {"dateSigned": get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

        # Setting contract period

        period_dates = {
            "period": {
                "startDate": get_now().isoformat(),
                "endDate": (get_now() + timedelta(days=365)).isoformat()
            }
        }
        with open(TARGET_DIR + 'tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {'data': {'period': period_dates["period"]}})
        self.assertEqual(response.status, '200 OK')

        # Uploading contract documentation

        with open(TARGET_DIR + 'tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {'data': {
                    'title': u'contract_first_document.doc',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword',
                }})
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tender-contract-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-contract-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/contracts/{}/documents?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {'data': {
                    'title': u'contract_second_document.doc',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/msword',
                }})
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tender-contract-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        # Setting contract signature date

        with open(TARGET_DIR + 'tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, self.contract_id, owner_token),
                {'data': {"dateSigned": get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

        # Contract signing

        with open(TARGET_DIR + 'tender-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        # Preparing the cancellation request

        self.set_status('active.awarded')
        with open(TARGET_DIR + 'prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token),
                {'data': {
                    'reason': 'cancellation reason',
                    'reasonType': 'noDemand',
                }})
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        # Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {
                    'title': u'Notice.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                {'data': {"description": 'Changed description'}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                {'data': {
                    'title': u'Notice-2.pdf',
                    'url': self.generate_docservice_url(),
                    'hash': 'md5:' + '0' * 32,
                    'format': 'application/pdf',
                }})
            self.assertEqual(response.status, '200 OK')

        # Activating the request and cancelling tender

        with open(TARGET_DIR + 'active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "active"}})
            self.assertEqual(response.status, '200 OK')
