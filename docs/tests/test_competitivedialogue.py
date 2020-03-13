# -*- coding: utf-8 -*-
import os
from datetime import timedelta
from hashlib import sha512
from copy import deepcopy

from openprocurement.api.models import get_now
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUWebTest,
    BaseCompetitiveDialogUAStage2WebTest
)

from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.base.constants import DOCS_URL, AUCTIONS_URL
from tests.base.data import (
    bid_draft, bid2, bid3, bid4, bad_participant, question, complaint, qualified,
    bid_document, bid_document2, lots, subcontracting,
    bid_document3_eligibility, bid_document4_financialy,
    bid_document5_qualification, tender_stage1, tender_stage2_multiple_lots,
    tender_stage2EU, tender_stage2UA,
    bad_author)

test_tender_data_stage1 = deepcopy(tender_stage1)
test_tender_data_stage2_multiple_lots = deepcopy(tender_stage2_multiple_lots)
test_tender_data_stage2EU = deepcopy(tender_stage2EU)
test_tender_data_stage2UA = deepcopy(tender_stage2UA)
test_lots = deepcopy(lots)
bid_stage2 = deepcopy(bid_draft)
bid = deepcopy(bid_draft)
bid_with_bad_participant = deepcopy(bid_draft)
bid2 = deepcopy(bid2)
bid3 = deepcopy(bid3)
bid4 = deepcopy(bid4)
bid2_with_docs = deepcopy(bid2)
bid4_with_docs = deepcopy(bid4)
bid_document2 = deepcopy(bid_document2)

bid_stage2.update(subcontracting)
bid_stage2.update(qualified)
bid.update(subcontracting)
bid.update(qualified)
bid_with_bad_participant.update(subcontracting)
bid_with_bad_participant.update(qualified)
bid2.update(qualified)
bid3.update(qualified)
bid4.update(qualified)
bid2_with_docs.update(qualified)
bid4_with_docs.update(qualified)

del bid['value']
bid_with_bad_participant['tenderers'] = [bad_participant]
test_lots[0]['value'] = test_tender_data_stage1['value']
test_lots[0]['minimalStep'] = test_tender_data_stage1['minimalStep']
test_lots[1]['value'] = test_tender_data_stage1['value']
test_lots[1]['minimalStep'] = test_tender_data_stage1['minimalStep']

TARGET_DIR = 'docs/source/tendering/competitivedialogue/tutorial/'
TARGET_DIR_MULTIPLE = 'docs/source/tendering/competitivedialogue/multiple_lots_tutorial/'


class TenderResourceTest(BaseCompetitiveDialogEUWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data_stage1
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL


    def setUp(self):
        super(TenderResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderResourceTest, self).tearDown()

    def test_stage1(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules

        # Write empty listing
        with open(TARGET_DIR + 'tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        # Try send bad data
        with open(TARGET_DIR + 'tender-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post(request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        #### Creating tender

        test_tender_data_stage1["tenderPeriod"] = {"endDate": (get_now() + timedelta(days=31)).isoformat()}

        # Create tender
        with open(TARGET_DIR + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data_stage1})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        # Check tender
        with open(TARGET_DIR + 'blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        # Get tender without auth
        with open(TARGET_DIR + 'tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender

        # Update endDate
        tenderPeriod_endDate = get_now() + timedelta(days=30, seconds=10)
        with open(TARGET_DIR + 'patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {"tenderPeriod": {"endDate": tenderPeriod_endDate.isoformat()}}})

        # Show listing after tender patch
        with open(TARGET_DIR + 'tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        # Setting Bid guarantee

        # Set bit guarantee
        with open(TARGET_DIR + 'set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'guarantee': {'amount': 8, 'currency': 'USD'}}})
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        #### Uploading documentation

        with open(TARGET_DIR + 'upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                upload_files=[('file', u'AwardCriteria.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        #### Enquiries

        with open(TARGET_DIR + 'ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': question}, status=201)
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/questions/{}?acc_token={}'.format(
                    self.tender_id, question_id, owner_token),
                {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}}, status=200)
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'list-question.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions/{}'.format(
                self.tender_id, question_id))
            self.assertEqual(response.status, '200 OK')

        self.time_shift('enquiryPeriod_ends')
        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(tender['id'], owner_token))
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {'value': {'amount': 501.0}}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': question}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'update-tender-after-enqiery-with-update-periods.http', 'w') as self.app.file_obj:
            tenderPeriod_endDate = get_now() + timedelta(days=8)
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {
                    'value': {
                        'amount': 501,
                        'currency': u'UAH'
                    },
                    'tenderPeriod': {'endDate': tenderPeriod_endDate.isoformat()}
                }})
            self.assertEqual(response.status, '200 OK')

        #### Registering bid

        bids_access = {}
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
                {'data': {'status': 'pending'}})
            self.assertEqual(response.status, '200 OK')

        #### Proposal Uploading

        with open(TARGET_DIR + 'upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'upload-bid-descriptive-decision-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'DescriptiveProposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        priv_doc_id1 = response.json['data']['id']

        # set confidentiality properties
        with open(TARGET_DIR + 'mark-bid-doc-decision-proposal.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, priv_doc_id1, bids_access[bid1_id]),
                {'data': {'isDescriptionDecision': True}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-bid-private-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal_top_secrets.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')
            priv_doc_id = response.json['data']['id']

        # set confidentiality properties
        with open(TARGET_DIR + 'mark-bid-doc-private.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, priv_doc_id, bids_access[bid1_id]),
                {'data': {
                    'confidentiality': 'buyerOnly',
                    'confidentialityRationale': 'Only our company sells badgers with pink hair.'}
                })
            self.assertEqual(response.status, '200 OK')

        # set confidentiality properties
        with open(TARGET_DIR + 'mark-bid-doc-decision-private.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, priv_doc_id1, bids_access[bid1_id]),
                {'data': {'confidentiality': 'buyerOnly'}})
            self.assertEqual(response.status, '200 OK')

        # set confidentiality properties
        with open(TARGET_DIR + 'bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
            {'data': {"value": {'amount': 501.0}}})
        self.assertEqual(response.status, '200 OK')

        #### Bid invalidation

        with open(TARGET_DIR + 'bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        #### Bid confirmation

        with open(TARGET_DIR + 'bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {'status': 'pending'}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'register-2nd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid2})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'register-3rd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid3})
            bid3_id = response.json['data']['id']
            bids_access[bid3_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        bid_document2.update({
            'confidentiality': 'buyerOnly',
            'confidentialityRationale': 'Only our company sells badgers with pink hair.'
        })
        bid4_with_docs["documents"] = [bid_document, bid_document2]
        for document in bid4_with_docs['documents']:
            document['url'] = self.generate_docservice_url()

        with open(TARGET_DIR + 'register-4rd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid4_with_docs})
            bid4_id = response.json['data']['id']
            bids_access[bid4_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        # Pre-qualification

        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json(
            '/tenders/{}'.format(self.tender_id),
            {'data': {'id': self.tender_id}})
        self.app.authorization = auth

        with open(TARGET_DIR + 'qualifications-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
            qualifications = response.json['data']
            self.assertEqual(len(qualifications), 4)
            self.assertEqual(qualifications[0]['bidID'], bid1_id)
            self.assertEqual(qualifications[1]['bidID'], bid2_id)
            self.assertEqual(qualifications[2]['bidID'], bid3_id)
            self.assertEqual(qualifications[3]['bidID'], bid4_id)

        with open(TARGET_DIR + 'approve-qualification1.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[0]['id'], owner_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')
        with open(TARGET_DIR + 'approve-qualification2.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[1]['id'], owner_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'reject-qualification3.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[2]['id'], owner_token),
                {'data': {'status': 'unsuccessful'}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'approve-qualification4.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[3]['id'], owner_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualificated-bids-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'rejected-bid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid3_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        # active.pre-qualification.stand-still
        with open(TARGET_DIR + 'pre-qualification-confirmation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'status': 'active.pre-qualification.stand-still'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        ###### Pending

        self.set_status(
            'active.stage2.pending',
            {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json(
            '/tenders/{}'.format(self.tender_id),
            {'data': {'id': self.tender_id}})
        self.app.authorization = auth

        with open(TARGET_DIR + 'stage2-pending.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.stage2.pending')

        with open(TARGET_DIR + 'stage2-waiting.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'status': 'active.stage2.waiting'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.stage2.waiting')

        auth = self.app.authorization
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        test_tender_data_stage2EU['dialogue_token'] = sha512(owner_token).hexdigest()
        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data_stage2EU})
        self.assertEqual(response.status, '201 Created')
        new_tender_id = response.json['data']['id']
        self.new_tender_token = response.json['access']['token']

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(new_tender_id, self.new_tender_token),
            {'data': {'status': 'draft.stage2'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'draft.stage2')

        self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
            {'data': {
                'stage2TenderID': new_tender_id,
                'status': 'complete'
            }})

        self.app.authorization = auth

        with open(TARGET_DIR + 'tender_stage1_complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'complete')
            self.assertEqual(response.json['data']['stage2TenderID'], new_tender_id)

        with open(TARGET_DIR + 'tender_stage2_get_token.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/credentials?acc_token={}'.format(new_tender_id, owner_token), {})
            self.assertEqual(response.status, '200 OK')
            self.new_tender_token = response.json['access']['token']

        with open(TARGET_DIR + 'tender_stage2_modify_status.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(new_tender_id, self.new_tender_token),
                {'data': {'status': 'active.tendering'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.tendering')

    def test_stage2_EU(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender

        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        test_tender_data_stage2EU['dialogue_token'] = sha512("super_secret_token").hexdigest()
        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data_stage2EU})
        self.assertEqual(response.status, '201 Created')
        self.tender_id = response.json['data']['id']
        tender = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
            {'data': {'status': 'draft.stage2'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'draft.stage2')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender

        tenderPeriod_endDate = get_now() + timedelta(days=30, seconds=10)
        with open(TARGET_DIR + 'stage2/EU/patch-tender-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'tenderPeriod': {'endDate': tenderPeriod_endDate.isoformat()}}})

        with open(TARGET_DIR + 'stage2/EU/tender-activate.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'status': 'active.tendering'}})

        response = self.app.get('/tenders')
        with open(TARGET_DIR + 'stage2/EU/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Uploading documentation

        with open(TARGET_DIR + 'stage2/EU/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'stage2/EU/tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                upload_files=[('file', u'AwardCriteria.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'stage2/EU/tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put(
                '/tenders/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, doc_id, owner_token),
                upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        #### Enquiries

        with open(TARGET_DIR + 'stage2/EU/ask-question-bad-participant.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': {
                    "author": bad_author,
                    "description": "Просимо додати таблицю потрібної калорійності харчування",
                    "title": "Калорійність"
                }}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'stage2/EU/ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': question}, status=201)
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'stage2/EU/answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/questions/{}?acc_token={}'.format(
                    self.tender_id, question_id, owner_token),
                {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}}, status=200)
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/list-question.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question_id))
            self.assertEqual(response.status, '200 OK')

        self.time_shift('enquiryPeriod_ends', {'items': [{"deliveryDate": {
            "startDate": (get_now() + timedelta(days=20)).isoformat(),
            "endDate": (get_now() + timedelta(days=50)).isoformat()
        }}]})
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}?acc_token={}'.format(tender['id'], owner_token))
        endDate = (get_now() + timedelta(days=30, seconds=10)).isoformat()

        with open(TARGET_DIR + 'stage2/EU/update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {'items': [{'deliveryDate': {"endDate": endDate}}]}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'stage2/EU/ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': question}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'stage2/EU/update-tender-after-enqiery-with-update-periods.http',
                  'w') as self.app.file_obj:
            tenderPeriod_endDate = get_now() + timedelta(days=8)
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {
                    'items': [{'deliveryDate': {'endDate': endDate}}],
                    'tenderPeriod': {'endDate': tenderPeriod_endDate.isoformat()}
                }})
            self.assertEqual(response.status, '200 OK')

        #### Registering bid

        bids_access = {}

        with open(TARGET_DIR + 'stage2/EU/try-register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid_with_bad_participant}, status=403)

        with open(TARGET_DIR + 'stage2/EU/register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid_stage2})
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'stage2/EU/activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        #### Proposal Uploading

        with open(TARGET_DIR + 'stage2/EU/upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'stage2/EU/upload-bid-private-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal_top_secrets.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')
            priv_doc_id = response.json['data']['id']

        # set confidentiality properties
        with open(TARGET_DIR + 'stage2/EU/mark-bid-doc-private.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, priv_doc_id, bids_access[bid1_id]),
                {'data': {'confidentiality': 'buyerOnly',
                          'confidentialityRationale': 'Only our company sells badgers with pink hair.'}})
            self.assertEqual(response.status, '200 OK')

        # set confidentiality properties
        with open(TARGET_DIR + 'stage2/EU/bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/upload-bid-financial-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'financial_doc.pdf', '1000$')])
            self.assertEqual(response.status, '201 Created')
            financial_doc_id = response.json['data']['id']

        response = self.app.post('/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
            self.tender_id, bid1_id, bids_access[bid1_id]),
            upload_files=[('file', 'financial_doc2.pdf', '1000$')])
        self.assertEqual(response.status, '201 Created')
        financial_doc_id = response.json['data']['id']

        with open(TARGET_DIR + 'stage2/EU/bidder-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/upload-bid-qualification-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/qualification_documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'qualification_document.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'stage2/EU/bidder-view-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
            {'data': {"value": {'amount': 501.0}}})
        self.assertEqual(response.status, '200 OK')

        #### Bid invalidation

        with open(TARGET_DIR + 'stage2/EU/bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        #### Bid confirmation

        with open(TARGET_DIR + 'stage2/EU/bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/register-2nd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid2})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')


        bid_document2.update({
            'confidentiality': 'buyerOnly',
            'confidentialityRationale': 'Only our company sells badgers with pink hair.'
        })
        bid4_with_docs["documents"] = [bid_document, bid_document2]
        bid4_with_docs["eligibilityDocuments"] = [bid_document3_eligibility]
        bid4_with_docs["financialDocuments"] = [bid_document4_financialy]
        bid4_with_docs["qualificationDocuments"] = [bid_document5_qualification]
        for document in bid4_with_docs['documents']:
            document['url'] = self.generate_docservice_url()
        for document in bid4_with_docs['eligibilityDocuments']:
            document['url'] = self.generate_docservice_url()
        for document in bid4_with_docs['financialDocuments']:
            document['url'] = self.generate_docservice_url()
        for document in bid4_with_docs['qualificationDocuments']:
            document['url'] = self.generate_docservice_url()

        with open(TARGET_DIR + 'stage2/EU/register-3rd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid4_with_docs})
            bid3_id = response.json['data']['id']
            bids_access[bid3_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        # Pre-qualification

        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json(
            '/tenders/{}'.format(self.tender_id),
            {'data': {'id': self.tender_id}})
        self.app.authorization = auth

        with open(TARGET_DIR + 'stage2/EU/qualifications-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
            qualifications = response.json['data']['qualifications']
            self.assertEqual(len(qualifications), 3)
            self.assertEqual(qualifications[0]['bidID'], bid1_id)
            self.assertEqual(qualifications[1]['bidID'], bid2_id)
            self.assertEqual(qualifications[2]['bidID'], bid3_id)

        with open(TARGET_DIR + 'stage2/EU/approve-qualification1.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[0]['id'], owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, "200 OK")
        with open(TARGET_DIR + 'stage2/EU/approve-qualification2.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[1]['id'], owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'stage2/EU/reject-qualification3.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[2]['id'], owner_token),
                {'data': {"status": "unsuccessful"}})
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'stage2/EU/qualificated-bids-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open(TARGET_DIR + 'stage2/EU/rejected-bid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid3_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        # active.pre-qualification.stand-still
        with open(TARGET_DIR + 'stage2/EU/pre-qualification-confirmation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'status': 'active.pre-qualification.stand-still'}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        #### Auction

        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction_url = u'{}/tenders/{}'.format(self.auctions_url, self.tender_id)
        patch_data = {
            'auctionUrl': auction_url,
            'bids': [{
                "id": bid1_id,
                "participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid1_id)
            }, {
                "id": bid2_id,
                "participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid2_id)
            }, {
                "id": bid3_id
            }]
        }
        response = self.app.patch_json(
            '/tenders/{}/auction?acc_token={}'.format(self.tender_id, owner_token),
            {'data': patch_data})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'stage2/EU/auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid2_id, bids_access[bid2_id]))
            self.assertEqual(response.status, '200 OK')

        #### Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json(
            '/tenders/{}/auction'.format(self.tender_id),
            {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open(TARGET_DIR + 'stage2/EU/confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {"data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open(TARGET_DIR + 'stage2/EU/tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'contractNumber': 'contract#1', 'value': {'amount': 238, 'amountNet': 230}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        #### Setting contract signature date

        self.tick()

        with open(TARGET_DIR + 'stage2/EU/tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'dateSigned': get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {'period': {'startDate': (get_now()).isoformat(),
                                   'endDate': (get_now() + timedelta(days=365)).isoformat()}}
        with open(TARGET_DIR + 'stage2/EU/tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'period': period_dates['period']}})
        self.assertEqual(response.status, '200 OK')

        #### Uploading contract documentation

        with open(TARGET_DIR + 'stage2/EU/tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                upload_files=[('file', 'contract_first_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'stage2/EU/tender-contract-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(
                self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/tender-contract-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                upload_files=[('file', 'contract_second_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open(TARGET_DIR + 'stage2/EU/tender-contract-patch-document.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, self.document_id, owner_token),
                {'data': {
                    'language': 'en',
                    'title_en': 'Title of Document',
                    'description_en': 'Description of Document'
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/tender-contract-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(
                self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/tender-contract-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request

        with open(TARGET_DIR + 'stage2/EU/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}})
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'stage2/EU/update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {"data": {'reasonType': 'unFixable'}})
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'stage2/EU/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
                upload_files=[('file', u'Notice.pdf', 'content')])
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'stage2/EU/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                {'data': {"description": 'Changed description'}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/EU/update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        with open(TARGET_DIR + 'pending-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        self.tick(delta=timedelta(days=11))
        self.check_chronograph()

        with open(TARGET_DIR + 'stage2/EU/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token))
            self.assertEqual(response.status, '200 OK')

    def test_cancel_tender(self):
        self.app.authorization = ('Basic', ('broker', ''))

        #### Creating tender

        test_tender_data_stage1["tenderPeriod"] = {"endDate": (get_now() + timedelta(days=31)).isoformat()}

        # Create tender
        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data_stage1})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # Check tender
        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')

        # Get tender without auth
        self.app.authorization = None
        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Preparing the cancellation request

        with open(TARGET_DIR + 'prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}})
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {'reasonType': 'unFixable'}})
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
                upload_files=[('file', u'Notice.pdf', 'content')])
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                {'data': {"description": 'Changed description'}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        with open(TARGET_DIR + 'pending-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        self.tick(delta=timedelta(days=11))

        with open(TARGET_DIR + 'active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

    def test_multiple_lots(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules

        with open(TARGET_DIR_MULTIPLE + 'tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        #### Creating tender

        test_tender_data_stage1["tenderPeriod"] = {"endDate": (get_now() + timedelta(days=31)).isoformat()}

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR_MULTIPLE + 'tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data_stage1})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # add lots
        with open(TARGET_DIR_MULTIPLE + 'tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
            {'data': test_lots[1]})
        self.assertEqual(response.status, '201 Created')
        lot_id2 = response.json['data']['id']

        # add relatedLot for item
        with open(TARGET_DIR_MULTIPLE + 'tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {'data': {'items': [{'relatedLot': lot_id1}, {'relatedLot': lot_id2}]}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR_MULTIPLE + 'bid-lot1.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(tender_id),
                {'data': {
                    'selfEligible': True,
                    'selfQualified': True,
                    'tenderers': bid["tenderers"],
                    'lotValues': [{
                        'subcontractingDetails': 'ДКП «Орфей», Україна',
                        'relatedLot': lot_id1
                    }]
                }})
            self.assertEqual(response.status, '201 Created')
            bid1_token = response.json['access']['token']
            bid1_id = response.json['data']['id']

        with open(TARGET_DIR_MULTIPLE + 'bid-lot2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(tender_id),
                {'data': {
                    'selfEligible': True,
                    'selfQualified': True,
                    'tenderers': bid2['tenderers'],
                    'lotValues': [{
                        'relatedLot': lot_id1
                    }, {
                        'subcontractingDetails': 'ДКП «Укр Прінт», Україна',
                        'relatedLot': lot_id2
                    }]
                }})
            self.assertEqual(response.status, '201 Created')
            bid2_id = response.json['data']['id']
            bid2_token = response.json['access']['token']

        with open(TARGET_DIR_MULTIPLE + 'bid-lot2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(tender_id),
                {'data': {
                    'selfEligible': True,
                    'selfQualified': True,
                    'tenderers': bid3['tenderers'],
                    'lotValues': [{
                        'relatedLot': lot_id1
                    }, {
                        'subcontractingDetails': 'ДКП «Укр Прінт», Україна',
                        'relatedLot': lot_id2
                    }]
                }})
            self.assertEqual(response.status, '201 Created')
            bid3_id = response.json['data']['id']
            bid3_token = response.json['access']['token']

        with open(TARGET_DIR_MULTIPLE + 'tender-invalid-all-bids.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/lots/{}?acc_token={}'.format(tender_id, lot_id2, owner_token),
                {'data': {'value': {'amount': 400}}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'bid-lot1-invalid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'bid-lot1-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token),
                {'data': {
                    'lotValues': [{
                        'subcontractingDetails': 'ДКП «Орфей»',
                        'relatedLot': lot_id1
                    }],
                    'status': 'pending'
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'bid-lot2-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid2_id, bid2_token),
                {'data': {
                    'lotValues': [{'relatedLot': lot_id1}],
                    'status': 'pending'
                }})

        with open(TARGET_DIR_MULTIPLE + 'bid-lot3-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid3_id, bid3_token),
                {'data': {
                    'lotValues': [{'relatedLot': lot_id1}],
                    'status': 'pending'
                }})

            self.assertEqual(response.status, '200 OK')
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        with open(TARGET_DIR_MULTIPLE + 'tender-view-pre-qualification.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR_MULTIPLE + 'qualifications-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.content_type, 'application/json')
            qualifications = response.json['data']

        with open(TARGET_DIR_MULTIPLE + 'tender-activate-qualifications.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/qualifications/{}?acc_token={}'.format(
                    self.tender_id, qualifications[0]['id'], owner_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualifications[1]['id'], owner_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualifications[2]['id'], owner_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        with open(TARGET_DIR_MULTIPLE + 'tender-view-pre-qualification-stand-still.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {'data': {'status': 'active.pre-qualification.stand-still'}})
            self.assertEqual(response.status, "200 OK")

        ###### Pending

        self.set_status(
            'active.stage2.pending',
            {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json(
            '/tenders/{}'.format(self.tender_id),
            {'data': {'id': self.tender_id}})
        self.app.authorization = auth

        with open(TARGET_DIR_MULTIPLE + 'stage2-pending.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.stage2.pending')

        with open(TARGET_DIR_MULTIPLE + 'stage2-waiting.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'status': 'active.stage2.waiting'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.stage2.waiting')

        auth = self.app.authorization
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
        # Update firms after adding lots
        test_tender_data_stage2_multiple_lots['lots'] = response.json['data']['lots']
        test_tender_data_stage2_multiple_lots['items'] = response.json['data']['items']
        test_tender_data_stage2_multiple_lots['shortlistedFirms'][0]['lots'] = [{'id': lot_id1}]
        test_tender_data_stage2_multiple_lots['shortlistedFirms'][1]['lots'] = [{'id': lot_id1}, {'id': lot_id2}]
        test_tender_data_stage2_multiple_lots['shortlistedFirms'][2]['lots'] = [{'id': lot_id1}, {'id': lot_id2}]

        test_tender_data_stage2EU['dialogue_token'] = sha512(owner_token).hexdigest()
        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data_stage2_multiple_lots})
        self.assertEqual(response.status, '201 Created')
        new_tender_id = response.json['data']['id']
        self.new_tender_token = response.json['access']['token']

        self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
            {'data': {
                'stage2TenderID': new_tender_id,
                'status': 'complete'
            }})

        self.app.authorization = auth

        with open(TARGET_DIR_MULTIPLE + 'tender_stage1_complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'complete')
            self.assertEqual(response.json['data']['stage2TenderID'], new_tender_id)

        with open(TARGET_DIR_MULTIPLE + 'tender_stage2_modify_status.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(new_tender_id, self.new_tender_token),
                {'data': {'status': 'active.tendering'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.tendering')

        with open(TARGET_DIR_MULTIPLE + 'show_stage2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(new_tender_id, self.new_tender_token))

            self.assertEqual(response.status, '200 OK')

        # user which wasn't allowed on first stage can't create bid on second
        with open(TARGET_DIR_MULTIPLE + 'register_bad_bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(new_tender_id),
                {'data': {
                    'selfEligible': True,
                    'selfQualified': True,
                    'tenderers': bid_with_bad_participant['tenderers'],
                    'lotValues': [{
                        'subcontractingDetails': 'ДКП «Орфей», Україна',
                        'value': {'amount': 500},
                        'relatedLot': lot_id1
                    }]
                }}, status=403)

        # user can create bid
        with open(TARGET_DIR_MULTIPLE + 'register_ok_bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(new_tender_id),
                {'data': {
                    'selfEligible': True,
                    'selfQualified': True,
                    'tenderers': bid['tenderers'],
                    'lotValues': [{
                        'subcontractingDetails': 'ДКП «Орфей», Україна',
                        'value': {'amount': 500},
                        'relatedLot': lot_id1
                    }]
                }}, status=201)

        # user can't create bid on lot which he wasn't allowed
        with open(TARGET_DIR_MULTIPLE + 'register_bad_not_allowed_lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(new_tender_id),
                {'data': {
                    'selfEligible': True,
                    'selfQualified': True,
                    'tenderers': bid['tenderers'],
                    'lotValues': [{
                        'subcontractingDetails': 'ДКП «Орфей», Україна',
                        'value': {'amount': 300},
                        'relatedLot': lot_id2
                    }]
                }},
                status=403)


class TenderResourceTestStage2UA(BaseCompetitiveDialogUAStage2WebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data_stage1
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL


    def setUp(self):
        super(TenderResourceTestStage2UA, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderResourceTestStage2UA, self).tearDown()

    def test_stage2_UA(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules

        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        test_tender_data_stage2UA['dialogue_token'] = sha512("super_secret_token").hexdigest()
        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data_stage2UA})
        self.assertEqual(response.status, '201 Created')
        self.tender_id = response.json['data']['id']
        tender = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
            {'data': {'status': 'draft.stage2'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'draft.stage2')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender

        tenderPeriod_endDate = get_now() + timedelta(days=30, seconds=10)
        with open(TARGET_DIR + 'stage2/UA/patch-tender-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'tenderPeriod': {'endDate': tenderPeriod_endDate.isoformat()}}})

        with open(TARGET_DIR + 'stage2/UA/tender-activate.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                {'data': {'status': 'active.tendering'}})

        with open(TARGET_DIR + 'stage2/UA/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Uploading documentation

        with open(TARGET_DIR + 'stage2/UA/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open(TARGET_DIR + 'stage2/UA/tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}?acc_token={}'.format(
                self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/UA/upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                upload_files=[('file', u'AwardCriteria.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'stage2/UA/tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/UA/update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put(
                '/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/UA/tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        #### Enquiries

        with open(TARGET_DIR + 'stage2/UA/ask-question-bad-participant.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': {
                    "author": bad_author,
                    "description": "Просимо додати таблицю потрібної калорійності харчування",
                    "title": "Калорійність"
                }}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'stage2/UA/ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': question}, status=201)
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'stage2/UA/answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/questions/{}?acc_token={}'.format(
                    self.tender_id, question_id, owner_token),
                {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}}, status=200)
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/UA/list-question.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/UA/get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question_id))
            self.assertEqual(response.status, '200 OK')

        self.set_enquiry_period_end()
        self.app.authorization = ('Basic', ('broker', ''))
        endDate = (get_now() + timedelta(days=30, seconds=10)).isoformat()
        with open(TARGET_DIR + 'stage2/UA/update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {'items': [{'deliveryDate': {'endDate': endDate}}]}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'stage2/UA/ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/questions'.format(self.tender_id),
                {'data': question}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open(TARGET_DIR + 'stage2/UA/update-tender-after-enqiery-with-update-periods.http',
                  'w') as self.app.file_obj:
            tenderPeriod_endDate = get_now() + timedelta(days=8)
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data': {
                    'items': [{'deliveryDate': {'endDate': endDate}}],
                    'tenderPeriod': {'endDate': tenderPeriod_endDate.isoformat()}
                }})
            self.assertEqual(response.status, '200 OK')

        #### Registering bid

        bids_access = {}

        with open(TARGET_DIR + 'stage2/UA/try-register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid_with_bad_participant}, status=403)

        with open(TARGET_DIR + 'stage2/UA/register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid_stage2})
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'stage2/UA/activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        #### Proposal Uploading

        with open(TARGET_DIR + 'stage2/UA/upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'stage2/UA/bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')
        # make bids invalid
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
            {'data': {"value": {'amount': 501.0}}})
        self.assertEqual(response.status, '200 OK')

        #### Bid invalidation

        with open(TARGET_DIR + 'stage2/UA/bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        #### Bid confirmation

        with open(TARGET_DIR + 'stage2/UA/bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        bid2_with_docs["documents"] = [bid_document]
        for document in bid2_with_docs['documents']:
            document['url'] = self.generate_docservice_url()
        with open(TARGET_DIR + 'stage2/UA/register-2nd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid2_with_docs})
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        #### Auction
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        auction_url = u'{}/tenders/{}'.format(self.auctions_url, self.tender_id)
        patch_data = {
            'auctionUrl': auction_url,
            'bids': [{
                "id": bid1_id,
                "participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid1_id)
            }, {
                "id": bid2_id,
                "participationUrl": u'{}?key_for_bid={}'.format(auction_url, bid2_id)
            }]
        }
        response = self.app.patch_json(
            '/tenders/{}/auction?acc_token={}'.format(self.tender_id, owner_token),
            {'data': patch_data})
        self.assertEqual(response.status, '200 OK')

        self.tick()

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'stage2/UA/auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/UA/bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/UA/bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id]))
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}'.format(self.tender_id))

        #### Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json(
            '/tenders/{}/auction'.format(self.tender_id),
            {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open(TARGET_DIR + 'stage2/UA/confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open(TARGET_DIR + 'stage2/UA/tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'value': {'amount': 238, 'amountNet': 230}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        #### Setting contract signature date

        self.tick()

        with open(TARGET_DIR + 'stage2/UA/tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {"dateSigned": get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {"period": {
            "startDate": (get_now()).isoformat(),
            "endDate": (get_now() + timedelta(days=365)).isoformat()
        }}
        with open(TARGET_DIR + 'stage2/UA/tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'period': period_dates["period"]}})
        self.assertEqual(response.status, '200 OK')

        #### Uploading contract documentation

        with open(TARGET_DIR + 'stage2/UA/tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                upload_files=[('file', 'contract_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open(TARGET_DIR + 'stage2/UA/tender-contract-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request

        with open(TARGET_DIR + 'stage2/UA/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}})
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'stage2/UA/update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {'reasonType': 'unFixable'}})
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation

        with open(TARGET_DIR + 'stage2/UA/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
                upload_files=[('file', u'Notice.pdf', 'content')])
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'stage2/UA/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                {'data': {"description": 'Changed description'}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'stage2/UA/update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        with open(TARGET_DIR + 'pending-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        self.tick(delta=timedelta(days=11))

        self.check_chronograph()

        with open(TARGET_DIR + 'active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token))
            self.assertEqual(response.status, '200 OK')