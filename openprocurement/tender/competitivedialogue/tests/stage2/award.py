# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import (
    snitch
)

from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardComplaintResourceTestMixin,
    TenderAwardComplaintDocumentResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
    Tender2LotAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    # TenderLotAwardComplaintResourceTest
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    # Tender2LotAwardComplaintDocumentResourceTest
    create_tender_lots_award_complaint_document,
)

from openprocurement.tender.openua.tests.award import (
    TenderUaAwardComplaintResourceTestMixin,
    TenderAwardResourceTestMixin
)

from openprocurement.tender.openua.tests.award_blanks import (
    # TenderAwardResourceTest
    create_tender_award,
    patch_tender_award,
    patch_tender_award_active,
    patch_tender_award_unsuccessful,
    # TenderAwardComplaintDocumentResourceTest
    patch_tender_award_complaint_document as patch_tender_award_complaint_document_from_ua,
    # TenderLotAwardResourceTest
    create_tender_lot_award,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    # Tender2LotAwardComplaintResourceTest
    create_tender_lots_award,
    patch_tender_lots_award,
    # TenderLotAwardComplaintResourceTest
    create_tender_lot_award_complaint,
    patch_tender_lot_award_complaint,
    # Tender2LotAwardComplaintResourceTest
    create_tender_lots_award_complaint,
    patch_tender_lots_award_complaint,
    # Tender2LotAwardComplaintDocumentResourceTest
    put_tender_lots_award_complaint_document,
    patch_tender_lots_award_complaint_document,
)

from openprocurement.tender.openeu.tests.award import (
    TenderAwardResourceTestMixin,
    TenderLotAwardResourceTestMixin,
    Tender2LotAwardResourceTestMixin, 
    TenderLotAwardComplaintResourceTestMixin,
    Tender2LotAwardComplaintResourceTestMixin,
)

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_bids,
    test_lots,
    author
)
from openprocurement.tender.competitivedialogue.tests.stage2.award_blanks import (
    # TenderAwardCompaintDocument EU
    create_tender_award_complaint_document,
    put_tender_award_complaint_document,
    patch_tender_award_complaint_document,
    # TenderAwardResourseTest UA 
    create_tender_award_invalid,
    get_tender_award,
    patch_tender_award_Administrator_change,
    # TenderAwardComplaintDocumentResourceTest
    patch_tender_award_complaint_document,
)

test_tender_bids = deepcopy(test_bids[:2])
for test_bid in test_tender_bids:
    test_bid['tenderers'] = [author]


class TenderStage2EUAwardResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest,
                                      TenderAwardResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_tender_bids
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        """ Create tender with lots add 2 bids, play auction and get award """
        super(TenderStage2EUAwardResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction time
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        # switch to auction role
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')

        # get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))


class TenderStage2EULotAwardResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest,
                                         TenderLotAwardResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_tender_bids
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2EULotAwardResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token),
            {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))


class TenderStage2EU2LotAwardResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest,
                                          Tender2LotAwardResourceTestMixin):
    initial_status = 'active.tendering'
    initial_lots = deepcopy(2 * test_lots)
    initial_bids = test_tender_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2EU2LotAwardResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.app.authorization = ('Basic', ('broker', ''))


class TenderStage2EUAwardComplaintResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest,
                                               TenderAwardComplaintResourceTestMixin,
                                               TenderUaAwardComplaintResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_lots)
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2EUAwardComplaintResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))


class TenderStage2EULotAwardComplaintResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest,
                                                  TenderLotAwardComplaintResourceTestMixin):
    initial_status = 'active.tendering'
    initial_lots = deepcopy(test_lots)
    initial_bids = test_tender_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2EULotAwardComplaintResourceTest, self).setUp()

        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')

        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        bid = self.bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': bid['id'],
                                                'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))


class TenderStage2EU2LotAwardComplaintResourceTest(TenderStage2EULotAwardComplaintResourceTest,
                                                   Tender2LotAwardComplaintResourceTestMixin):
    initial_lots = deepcopy(2 * test_lots)


class TenderStage2EUAwardComplaintDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest,
                                                       TenderAwardComplaintDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2EUAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document_from_ua)


class TenderStage2EU2LotAwardComplaintDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_lots)

    def setUp(self):
        super(TenderStage2EU2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.bids[0]
        self.app.authorization = ('Basic', ('token', ''))
        self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                           {'data': {'suppliers': [author], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][1]['relatedLot']}})
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_create_tender_award_complaint_document = snitch(create_tender_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class TenderStage2EUAwardDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest,
                                              TenderAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2EUAwardDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']


class TenderStage2EU2LotAwardDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest,
                                                  Tender2LotAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_lots)

    def setUp(self):
        super(TenderStage2EU2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        bid = self.bids[0]
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']


# UA


class TenderStage2UAAwardResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_active = snitch(patch_tender_award_active)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_get_tender_award = snitch(get_tender_award)
    test_patch_tender_award_Administrator_change = snitch(patch_tender_award_Administrator_change)


class TenderStage2UALotAwardResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_lots = deepcopy(test_lots)
    initial_bids = test_tender_bids

    test_create_lot_award = snitch(create_tender_lot_award)
    test_patch_tender_lot_award = snitch(patch_tender_lot_award)
    test_patch_tender_lot_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)


class TenderStage2UA2LotAwardResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_lots = deepcopy(2 * test_lots)
    initial_bids = test_tender_bids

    test_create_tender_lots_award = snitch(create_tender_lots_award)
    test_patch_tender_lots_award = snitch(patch_tender_lots_award)


class TenderStage2UAAwardComplaintResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest,
                                               TenderAwardComplaintResourceTestMixin,
                                               TenderUaAwardComplaintResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2UAAwardComplaintResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.app.authorization = auth
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]


class TenderStage2UALotAwardComplaintResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_lots = deepcopy(test_lots)
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2UALotAwardComplaintResourceTest, self).setUp()
        # Create award
        bid = self.bids[0]
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        self.app.authorization = auth

    test_create_tender_lot_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_lot_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_lot_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_lot_award_complaints = snitch(get_tender_lot_award_complaints)


class Tender2LotAwardComplaintResourceTest(TenderStage2UALotAwardComplaintResourceTest):
    initial_lots = deepcopy(2 * test_lots)

    test_create_tender_lots_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_lots_award_complaint = snitch(patch_tender_lots_award_complaint)


class TenderStage2UAAwardComplaintDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest,
                                                       TenderAwardComplaintDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2UAAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.app.authorization = auth

        # Create complaint for award
        bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class TenderStage2UA2LotAwardComplaintDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_lots)

    def setUp(self):
        super(TenderStage2UA2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.bids[0]
        bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.app.authorization = auth
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_create_tender_lots_award_document = snitch(create_tender_lots_award_complaint_document)
    test_put_tender_lots_award_complaint_document = snitch(put_tender_lots_award_complaint_document)
    test_patch_tender_lots_award_complaint_document = snitch(patch_tender_lots_award_complaint_document)


class TenderStage2UAAwardDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest,
                                              TenderAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2UAAwardDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = auth


class TenderStage2UA2LotAwardDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest,
                                                  Tender2LotAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_lots)

    def setUp(self):
        super(TenderStage2UA2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        bid = self.bids[0]
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [author], 'status': 'pending',
                                       'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = auth


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotAwardResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
