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
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    # TenderLotAwardComplaintResourceTest
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
)

from openprocurement.tender.openua.tests.award import TenderUaAwardComplaintResourceTestMixin
from openprocurement.tender.openua.tests.award_blanks import (
    # Tender2LotAwardComplaintResourceTest
    create_tender_lots_award_complaint,
    patch_tender_lots_award_complaint,
    # TenderLotAwardComplaintResourceTest
    create_tender_lot_award_complaint,
    patch_tender_lot_award_complaint,
)

from openprocurement.tender.openeu.tests.award_blanks import (
    # Tender2LotAwardComplaintDocumentResourceTest
    patch_tender_award_complaint_document,
    # TenderAwardComplaintDocumentResourceTest
    create_tender_2lot_award_complaint_document,
    put_tender_2lot_award_complaint_document,
    patch_tender_2lot_award_complaint_document,
    # Tender2LotAwardResourceTest
    create_tender_2lot_award,
    patch_tender_2lot_award,
    # TenderLotAwardResourceTest
    create_tender_lot_award,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    # TenderAwardResourceTest
    create_tender_award_invalid,
    create_tender_award,
    get_tender_award,
    patch_tender_award,
    patch_tender_award_active,
    patch_tender_award_unsuccessful,
    patch_tender_award_Administrator_change,
)
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_bids,
    test_lots
)


class TenderAwardResourceTestMixin(object):

    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_active = snitch(patch_tender_award_active)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)
    test_get_tender_award = snitch(get_tender_award)
    test_patch_tender_award_Administrator_change = snitch(patch_tender_award_Administrator_change)


class TenderAwardResourceTest(BaseTenderContentWebTest,
                              TenderAwardResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_bids
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderAwardResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
            self.tender_id, qualification['id'], self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.auction")

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.initial_lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),{'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], "active.qualification")

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))


class TenderLotAwardResourceTestMixin(object):
    
    test_create_tender_award = snitch(create_tender_lot_award)
    test_patch_tender_award= snitch(patch_tender_lot_award)
    test_patch_tender_award_unsuccessful= snitch(patch_tender_lot_award_unsuccessful)    


class TenderLotAwardResourceTest(BaseTenderContentWebTest,
                                 TenderLotAwardResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_bids
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderLotAwardResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
            self.tender_id, qualification['id'], self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.auction")

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.initial_lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),{'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], "active.qualification")

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))


class Tender2LotAwardResourceTestMixin(object):

    test_create_tender_award = snitch(create_tender_2lot_award)
    test_patch_tender_award = snitch(patch_tender_2lot_award)


class Tender2LotAwardResourceTest(BaseTenderContentWebTest,
                                  Tender2LotAwardResourceTestMixin):
    initial_status = 'active.tendering'
    initial_lots = 2 * test_lots
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(Tender2LotAwardResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
            self.tender_id, qualification['id'], self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.auction")

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.initial_lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),{'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], "active.qualification")

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.app.authorization = ('Basic', ('broker', ''))


class TenderAwardComplaintResourceTest(BaseTenderContentWebTest,
                                       TenderAwardComplaintResourceTestMixin,
                                       TenderUaAwardComplaintResourceTestMixin):
    #initial_data = tender_data
    initial_status = 'active.tendering'
    initial_bids = test_bids
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderAwardComplaintResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
            self.tender_id, qualification['id'], self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.auction")

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.initial_lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),{'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], "active.qualification")

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]['id']]


class TenderLotAwardComplaintResourceTestMixin(object):

    test_create_tender_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_lot_award_complaints)


class TenderLotAwardComplaintResourceTest(BaseTenderContentWebTest,
                                          TenderLotAwardComplaintResourceTestMixin):
    #initial_data = tender_data
    initial_status = 'active.tendering'
    initial_lots = test_lots
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderLotAwardComplaintResourceTest, self).setUp()

        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
            self.tender_id, qualification['id'], self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.auction")

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.initial_lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),{'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], "active.qualification")

        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        bid = self.initial_bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]['id']]


class Tender2LotAwardComplaintResourceTestMixin(object):

    test_create_tender_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lots_award_complaint)


class Tender2LotAwardComplaintResourceTest(TenderLotAwardComplaintResourceTest,
                                           Tender2LotAwardComplaintResourceTestMixin):
    initial_lots = 2 * test_lots


class TenderAwardComplaintDocumentResourceTest(BaseTenderContentWebTest,
                                               TenderAwardComplaintDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_create_tender_award_complaint_document = snitch(create_tender_2lot_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_2lot_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_2lot_award_complaint_document)


class TenderAwardDocumentResourceTest(BaseTenderContentWebTest,
                                      TenderAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardDocumentResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']


class Tender2LotAwardDocumentResourceTest(BaseTenderContentWebTest,
                                          Tender2LotAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tender2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
