# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.tender.limited.tests.tender import BaseTenderWebTest

from tests.base.test import DumpsWebTestApp, MockWebTestMixin
from tests.base.constants import DOCS_URL, AUCTIONS_URL
from tests.base.data import complaint, award, tender_limited, lots

test_tender_data = deepcopy(tender_limited)
test_lots = deepcopy(lots)
award_negotiation = deepcopy(award)
test_tender_negotiation_data = deepcopy(test_tender_data)
test_tender_negotiation_quick_data = deepcopy(test_tender_data)

award_negotiation['value']['valueAddedTaxIncluded'] = False
test_tender_negotiation_data['procurementMethodType'] = "negotiation"
test_tender_negotiation_data['cause'] = "twiceUnsuccessful"
test_tender_negotiation_data['causeDescription'] = "оригінальний тендер не вдався двічі"
test_tender_negotiation_data['causeDescription_en'] = "original tender has failed twice"
test_tender_negotiation_data['causeDescription_ru'] = "оригинальный тендер не получился дважды"
test_tender_negotiation_data['value']['valueAddedTaxIncluded'] = False
test_tender_negotiation_quick_data['cause'] = "twiceUnsuccessful"
test_tender_negotiation_quick_data['procurementMethodType'] = "negotiation.quick"
test_tender_negotiation_quick_data['causeDescription'] = "оригінальний тендер не вдався двічі"
test_tender_negotiation_quick_data['causeDescription_en'] = "original tender has failed twice"
test_tender_negotiation_quick_data['causeDescription_ru'] = "оригинальный тендер не получился дважды"
test_lots[0]['value'] = test_tender_negotiation_data['value']

TARGET_DIR = 'docs/source/tendering/limited/http/'


class TenderLimitedResourceTest(BaseTenderWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    def setUp(self):
        super(TenderLimitedResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderLimitedResourceTest, self).tearDown()

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tutorial/create-tender-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'tutorial/tender-listing-after-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders?opt_pretty=1')
            self.assertEqual(response.status, '200 OK')

        #### Modifying tender

        with open(TARGET_DIR + 'tutorial/patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                {'data':
                    {"items": [
                        {
                            "quantity": 9,
                            "unit": {
                                "code": "MON",
                                "name": "month"
                            }
                        }]
                    }
                })

        with open(TARGET_DIR + 'tutorial/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        #### Uploading documentation

        with open(TARGET_DIR + 'tutorial/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(
                self.tender_id, owner_token),
                upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open(TARGET_DIR + 'tutorial/update-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(
                self.tender_id, doc_id, owner_token),
                upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Adding supplier information

        with open(TARGET_DIR + 'tutorial/tender-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
                {'data': award})
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Uploading Award documentation

        with open(TARGET_DIR + 'tutorial/tender-award-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
                self.tender_id, self.award_id, owner_token),
                upload_files=[('file', 'award_first_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/tender-award-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards/{}/documents?acc_token={}'.format(
                self.tender_id, self.award_id, owner_token))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-award-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
                self.tender_id, self.award_id, owner_token),
                upload_files=[('file', 'award_second_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/tender-award-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/awards/{}/documents?acc_token={}'.format(
                self.tender_id, self.award_id, owner_token))
        self.assertEqual(response.status, '200 OK')

        #### Award confirmation

        with open(TARGET_DIR + 'tutorial/tender-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token),
                {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        #### Contracts

        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(
            self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        with open(TARGET_DIR + 'tutorial/tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {"data": {"value": {"amount": 238, "amountNet": 230}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        #### Set contact.item.unit value
        with open(TARGET_DIR + 'tutorial/tender-contract-set-contract_items_unit-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {"data": {"items": [{'unit': {'value': {'amount': 12}}}]}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['items'][0]['unit']['value']['amount'], 12)

        #### Setting contract signature date

        with open(TARGET_DIR + 'tutorial/tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {"dateSigned": get_now().isoformat()}})
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {"period": {
            "startDate": get_now().isoformat(),
            "endDate": (get_now() + timedelta(days=365)).isoformat()
        }}
        with open(TARGET_DIR + 'tutorial/tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'period': period_dates["period"]}})
        self.assertEqual(response.status, '200 OK')

        #### Uploading Contract documentation

        with open(TARGET_DIR + 'tutorial/tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                upload_files=[('file', 'contract_first_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/tender-contract-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/tender-contract-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                upload_files=[('file', 'contract_second_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/tender-contract-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token))
        self.assertEqual(response.status, '200 OK')

        #### Contract signing

        self.tick()

        with open(TARGET_DIR + 'tutorial/tender-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')


class TenderNegotiationLimitedResourceTest(TenderLimitedResourceTest):
    initial_data = test_tender_negotiation_data

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tutorial/create-tender-negotiation-procuringEntity.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': self.initial_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        #### Adding supplier information

        with open(TARGET_DIR + 'tutorial/tender-negotiation-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
                {'data': award_negotiation})
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation

        with open(TARGET_DIR + 'tutorial/tender-negotiation-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token),
                {'data': {'status': 'active',
                          'qualified': True}})
            self.assertEqual(response.status, '200 OK')

        # get contract
        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(
            self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        with open(TARGET_DIR + 'tutorial/negotiation-prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token),
                {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}})
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open(TARGET_DIR + 'tutorial/negotiation-update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                {'data': {'reasonType': 'dateViolation'}})
            self.assertEqual(response.status, '200 OK')

        #### Contract signing

        self.tick()

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open(TARGET_DIR + 'tutorial/tender-negotiation-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

            #### Preparing the cancellation request

            self.set_status('active')

            with open(TARGET_DIR + 'tutorial/prepare-cancellation.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/tenders/{}/cancellations?acc_token={}'.format(
                        self.tender_id, owner_token),
                    {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}})
                self.assertEqual(response.status, '201 Created')

            cancellation_id = response.json['data']['id']

            with open(TARGET_DIR + 'tutorial/update-cancellation-reasonType.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/tenders/{}/cancellations/{}?acc_token={}'.format(
                        self.tender_id, cancellation_id, owner_token),
                    {'data': {'reasonType': 'unFixable'}})
                self.assertEqual(response.status, '200 OK')

            #### Filling cancellation with protocol and supplementary documentation

            with open(TARGET_DIR + 'tutorial/upload-cancellation-doc.http', 'w') as self.app.file_obj:
                response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token),
                    upload_files=[('file', u'Notice.pdf', 'content')])
                cancellation_doc_id = response.json['data']['id']
                self.assertEqual(response.status, '201 Created')

            with open(TARGET_DIR + 'tutorial/patch-cancellation.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                        self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                    {'data': {"description": 'Changed description'}})
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'tutorial/update-cancellation-doc.http', 'w') as self.app.file_obj:
                response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                    upload_files=[('file', 'Notice-2.pdf', 'content2')])
                self.assertEqual(response.status, '200 OK')

            #### Activating the request and cancelling tender
            with open(TARGET_DIR + 'tutorial/pending-cancellation.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/tenders/{}/cancellations/{}?acc_token={}'.format(
                        self.tender_id, cancellation_id, owner_token),
                    {'data': {"status": "pending"}})
                self.assertEqual(response.status, '200 OK')

            self.tick(delta=timedelta(days=11))

            with open(TARGET_DIR + 'tutorial/active-cancellation.http', 'w') as self.app.file_obj:
                response = self.app.get(
                    '/tenders/{}/cancellations/{}?acc_token={}'.format(
                        self.tender_id, cancellation_id, owner_token))
                self.assertEqual(response.status, '200 OK')

    def test_multiple_lots(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules

        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        #### Creating tender
        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': self.initial_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # add lots
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']

        # add relatedLot for item
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {'data': {'items': [{'relatedLot': lot_id1}]}})
            self.assertEqual(response.status, '200 OK')

        while True:
            with open(TARGET_DIR + 'multiple_lots_tutorial/tender-listing-no-auth.http', 'w') as self.app.file_obj:
                self.app.authorization = None
                response = self.app.get(request_path)
                self.assertEqual(response.status, '200 OK')
                if len(response.json['data']):
                    break

        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        #### Adding supplier information
        self.app.authorization = ('Basic', ('broker', ''))
        suspplier_loc = deepcopy({'data': award})
        suspplier_loc['data']['lotID'] = lot_id1
        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token),
                suspplier_loc)
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation

        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token),
                {'data': {'status': 'active',
                          'qualified': True}})
            self.assertEqual(response.status, '200 OK')

        # get contract
        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-contract-set-contract-value.http',
                  'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {"data": {"value": {"amount": 238, "amountNet": 230}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        #### Contract signing

        self.tick()

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open(TARGET_DIR + 'multiple_lots_tutorial/tender-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')


class TenderNegotiationQuickLimitedResourceTest(TenderNegotiationLimitedResourceTest):
    initial_data = test_tender_negotiation_quick_data

    def test_docs(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender for negotiation/reporting procedure

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tutorial/create-tender-negotiation-quick-procuringEntity.http',
                  'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': self.initial_data})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        #### Adding supplier information

        with open(TARGET_DIR + 'tutorial/tender-negotiation-quick-award.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(
                    self.tender_id, owner_token),
                {'data': award_negotiation})
            self.assertEqual(response.status, '201 Created')
        self.award_id = response.json['data']['id']

        #### Award confirmation

        with open(TARGET_DIR + 'tutorial/tender-negotiation-quick-award-approve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(
                    self.tender_id, self.award_id, owner_token),
                {'data': {'status': 'active', 'qualified': True}})
            self.assertEqual(response.status, '200 OK')

        # get contract
        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(
            self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        #### Contract signing

        self.tick()

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open(TARGET_DIR + 'tutorial/tender-negotiation-quick-contract-sign.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/contracts/{}?acc_token={}'.format(
                    self.tender_id, self.contract_id, owner_token),
                {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

    def test_award_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        response = self.app.post_json(
            '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
            {'data': award})
        self.assertEqual(response.status, '201 Created')
        award_id = response.json['data']['id']

        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
            {"data": {"status": "active", "qualified": True}})

        with open(TARGET_DIR + 'tutorial/award-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        self.tick()

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open(TARGET_DIR + 'tutorial/award-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
                    self.tender_id, award_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/award-complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint1_id, complaint1_token),
                {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        complaint_data = {'data': complaint.copy()}
        complaint_data['data']['status'] = 'pending'
        with open(TARGET_DIR + 'tutorial/award-complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id),
                complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint2_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id),
            complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint3_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id),
            complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint4_token = response.json['access']['token']
        complaint4_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id),
            complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_id = response.json['data']['id']

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'tutorial/award-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint2_id),
                {'data': {
                    "status": "invalid"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/award-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id),
                {'data': {
                    "status": "accepted"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint3_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint4_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint5_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/award-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/awards/{}/complaints/{}/documents'.format(self.tender_id, award_id, complaint1_id),
                upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/award-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id),
                {'data': {
                    "status": "satisfied"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/award-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint3_id),
                {'data': {
                    "status": "declined"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/award-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint5_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/award-complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/award-complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tutorial/award-complaint-satisfied-resolving.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                {'data': {
                    "status": "cancelled"}})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/award-complaint-newaward.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
                {'data': award})
            self.assertEqual(response.status, '201 Created')
            new_award_id = response.json['data']['id']

        with open(TARGET_DIR + 'tutorial/award-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint1_id, owner_token),
                {'data': {
                    "tendererAction": "Умови виправлено, вибір переможня буде розгянуто повторно",
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/award-complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, complaint4_id, complaint4_token),
                {'data': {
                    "cancellationReason": "Тендер скасовується замовником",
                    "status": "stopping"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'tutorial/award-complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint4_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        award_id = new_award_id

        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
            {"data": {
                "status": "active", "qualified": True
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tutorial/award-complaint-submit.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id),
                complaint_data)
            self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id),
            {'data': complaint})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'tutorial/award-complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, award_id, response.json['data']['id'], response.json['access']['token']),
                {'data': {
                    "cancellationReason": "Умови виправлено",
                    "status": "cancelled"
                }})
            self.assertEqual(response.status, '200 OK')

    def test_cancellation_complaints(self):
        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_negotiation_data})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        # Cancellation turn to complaint_period
        response = self.app.post_json(
            '/tenders/{}/cancellations?acc_token={}'.format(
                self.tender_id, owner_token),
            {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}})
        cancellation_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.post(
            '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
            upload_files=[('file', u'Notice.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
            {'data': {"status": "pending"}})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/complaints'.format(
                    self.tender_id, cancellation_id),
                {'data': complaint})
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open(TARGET_DIR + 'cancellation-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/cancellations/{}/complaints/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        complaint_data = {'data': complaint.copy()}
        complaint_data['data']['status'] = 'pending'
        with open(TARGET_DIR + 'cancellation-complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/cancellations/{}/complaints'.format(
                    self.tender_id, cancellation_id), complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint3_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/complaints'.format(
                self.tender_id, cancellation_id), complaint_data)
        self.assertEqual(response.status, '201 Created')

        complaint4_id = response.json['data']['id']
        complaint4_token = response.json['access']['token']

        with open(TARGET_DIR + 'cancellation-complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, complaint1_id, complaint1_token),
                {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')


        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/complaints'.format(
                self.tender_id, cancellation_id), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_id = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/complaints'.format(
                self.tender_id, cancellation_id), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint6_id = response.json['data']['id']
        complaint6_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'cancellation-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint4_id),
                {'data': {
                    "status": "invalid"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint1_id),
                {'data': {
                    "status": "accepted"
                }})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint3_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint5_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint6_id),
            {'data': {
                "status": "accepted"
            }})
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/tenders/{}/cancellations/{}/complaints/{}/documents'.format
                (self.tender_id, cancellation_id, complaint1_id),
                upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'cancellation-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint1_id),
                {'data': {
                    "status": "satisfied"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint3_id),
                {'data': {
                    "status": "declined"
                }})
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint5_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
            {'data': {'status': 'unsuccessful'}}
        )
        self.assertEqual(response.status_code, 200)

        with open(TARGET_DIR + 'cancellation-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, complaint1_id, owner_token),
                {'data': {
                    "tendererAction": "Умови виправлено",
                    "status": "resolved"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open(TARGET_DIR + 'cancellation-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}/complaints/{}'.format(
                    self.tender_id, cancellation_id, complaint6_id),
                {'data': {
                    "decision": "Тендер скасовується замовником",
                    "status": "stopped"
                }})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        # Create new cancellations
        response = self.app.post_json(
            '/tenders/{}/cancellations?acc_token={}'.format(
                self.tender_id, owner_token),
            {'data': {'reason': 'cancellation reason', 'reasonType': 'unFixable'}})
        cancellation2_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.post(
            '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                self.tender_id, cancellation2_id, owner_token),
            upload_files=[('file', u'Notice.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/cancellations/{}?acc_token={}'.format(
                self.tender_id, cancellation2_id, owner_token),
            {'data': {"status": "pending"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/complaints'.format(self.tender_id, cancellation2_id),
            {'data': complaint})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'cancellation-complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/cancellations/{}/complaints'.format(
                self.tender_id, cancellation_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'cancellation-complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/cancellations/{}/complaints/{}'.format(
                self.tender_id, cancellation_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')
