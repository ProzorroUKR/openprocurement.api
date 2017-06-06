# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_organization
from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardComplaintResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
    TenderAwardComplaintDocumentResourceTestMixin,
    Tender2LotAwardDocumentResourceTestMixin
)

from openprocurement.tender.openua.tests.award import TenderUaAwardComplaintResourceTestMixin

from openprocurement.tender.openeu.tests.award import (
    TenderAwardResourceTestMixin,
    TenderLotAwardResourceTestMixin,
    Tender2LotAwardResourceTestMixin,
    TenderLotAwardComplaintResourceTestMixin,
    Tender2LotAwardComplaintResourceTestMixin,
)
from openprocurement.tender.openeu.tests.award_blanks import (
    # Tender2LotAwardComplaintDocumentResourceTest
    patch_tender_award_complaint_document,
    # TenderAwardComplaintDocumentResourceTest
    create_tender_2lot_award_complaint_document,
    put_tender_2lot_award_complaint_document,
    patch_tender_2lot_award_complaint_document,
)

from openprocurement.tender.esco.utils import calculate_npv

from openprocurement.tender.esco.tests.base import (
    BaseESCOEUContentWebTest,
    test_bids,
    test_lots,
    NBU_DISCOUNT_RATE
)

award_amount = calculate_npv(NBU_DISCOUNT_RATE,
                             test_bids[0]['value']['annualCostsReduction'],
                             test_bids[0]['value']['yearlyPayments'],
                             test_bids[0]['value']['contractDuration'])


class TenderAwardResourceTest(BaseESCOEUContentWebTest,
                              TenderAwardResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_bids
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    expected_award_amount = award_amount

    def setUp(self):
        super(TenderAwardResourceTest, self).setUp()
        # switch to active.pre-qualification

        self.prepare_award()

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))


class TenderLotAwardResourceTest(BaseESCOEUContentWebTest,
                                 TenderLotAwardResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_bids
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    expected_award_amount = award_amount

    def setUp(self):
        super(TenderLotAwardResourceTest, self).setUp()

        self.prepare_award()
        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))


class Tender2LotAwardResourceTest(BaseESCOEUContentWebTest,
                                  Tender2LotAwardResourceTestMixin):
    initial_status = 'active.tendering'
    initial_lots = 2 * test_lots
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(Tender2LotAwardResourceTest, self).setUp()

        self.prepare_award()

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.app.authorization = ('Basic', ('broker', ''))


class TenderAwardComplaintResourceTest(BaseESCOEUContentWebTest,
                                       TenderAwardComplaintResourceTestMixin,
                                       TenderUaAwardComplaintResourceTestMixin):
    # initial_data = tender_data
    initial_status = 'active.tendering'
    initial_bids = test_bids
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderAwardComplaintResourceTest, self).setUp()

        self.prepare_award()

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]['id']]


class TenderLotAwardComplaintResourceTest(BaseESCOEUContentWebTest,
                                          TenderLotAwardComplaintResourceTestMixin):
    # initial_data = tender_data
    initial_status = 'active.tendering'
    initial_lots = test_lots
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderLotAwardComplaintResourceTest, self).setUp()

        self.prepare_award()

        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        bid = self.initial_bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid['id'],
                                       'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]['id']]


class Tender2LotAwardComplaintResourceTest(TenderLotAwardComplaintResourceTest,
                                           Tender2LotAwardComplaintResourceTestMixin):
    initial_lots = 2 * test_lots


class TenderAwardComplaintDocumentResourceTest(BaseESCOEUContentWebTest,
                                               TenderAwardComplaintDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id),
            {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'active', "qualified": True, "eligible": True}})
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(BaseESCOEUContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        bid = self.initial_bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid['id'],
                                       'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'active', "qualified": True, "eligible": True}})
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_create_tender_award_complaint_document = snitch(create_tender_2lot_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_2lot_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_2lot_award_complaint_document)


class TenderAwardDocumentResourceTest(BaseESCOEUContentWebTest,
                                      TenderAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id),
            {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']


class Tender2LotAwardDocumentResourceTest(BaseESCOEUContentWebTest,
                                          Tender2LotAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        bid = self.initial_bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid['id'],
                                       'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
