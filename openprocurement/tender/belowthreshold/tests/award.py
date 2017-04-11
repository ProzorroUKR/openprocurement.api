# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_bids,
    test_lots,
    test_organization
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    # TenderAwardResourceTest
    create_tender_award_invalid,
    create_tender_award,
    patch_tender_award,
    patch_tender_award_unsuccessful,
    get_tender_award,
    patch_tender_award_Administrator_change,
    # TenderLotAwardResourceTest
    create_tender_lot_award,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    # Tender2LotAwardResourceTest
    create_tender_lots_award,
    patch_tender_lots_award,
    # TenderAwardComplaintResourceTest
    create_tender_award_complaint_invalid,
    create_tender_award_complaint,
    patch_tender_award_complaint,
    review_tender_award_complaint,
    get_tender_award_complaint,
    get_tender_award_complaints,
    # TenderLotAwardComplaintResourceTest
    create_tender_lot_award_complaint,
    patch_tender_lot_award_complaint,
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    # Tender2LotAwardComplaintResourceTest
    create_tender_lots_award_complaint,
    patch_tender_lots_award_complaint,
    # TenderAwardComplaintDocumentResourceTest
    not_found,
    create_tender_award_complaint_document,
    put_tender_award_complaint_document,
    patch_tender_award_complaint_document,
    # Tender2LotAwardComplaintDocumentResourceTest
    create_tender_lots_award_complaint_document,
    put_tender_lots_award_complaint_document,
    patch_tender_lots_award_complaint_document,
    # TenderAwardDocumentResourceTest
    not_found_award_document,
    create_tender_award_document,
    put_tender_award_document,
    patch_tender_award_document,
    # Tender2LotAwardDocumentResourceTest
    create_tender_lots_award_document,
    put_tender_lots_award_document,
    patch_tender_lots_award_document,
)


class TenderAwardResourceTestMixin(object):
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_get_tender_award = snitch(get_tender_award)
    test_patch_tender_award_Administrator_change = snitch(patch_tender_award_Administrator_change)


class TenderAwardComplaintResourceTestMixin(object):
    test_create_tender_award_complaint_invalid = snitch(create_tender_award_complaint_invalid)
    test_get_tender_award_complaint = snitch(get_tender_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_award_complaints)


class TenderAwardDocumentResourceTestMixin(object):
    test_not_found_award_document = snitch(not_found_award_document)
    test_create_tender_award_document = snitch(create_tender_award_document)
    test_put_tender_award_document = snitch(put_tender_award_document)
    test_patch_tender_award_document = snitch(patch_tender_award_document)


class TenderAwardComplaintDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_tender_award_complaint_document = snitch(create_tender_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_award_complaint_document)


class Tender2LotAwardDocumentResourceTestMixin(object):
    test_create_tender_lots_award_document = snitch(create_tender_lots_award_document)
    test_put_tender_lots_award_document = snitch(put_tender_lots_award_document)
    test_patch_tender_lots_award_document = snitch(patch_tender_lots_award_document)


class TenderAwardResourceTest(TenderContentWebTest, TenderAwardResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_award_unsuccessful)


class TenderLotAwardResourceTest(TenderContentWebTest):
    initial_status = 'active.qualification'
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_tender_lot_award = snitch(create_tender_lot_award)
    test_patch_tender_lot_award = snitch(patch_tender_lot_award)
    test_patch_tender_lot_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)


class Tender2LotAwardResourceTest(TenderContentWebTest):
    initial_status = 'active.qualification'
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_create_tender_lots_award = snitch(create_tender_lots_award)
    test_patch_tender_lots_award = snitch(patch_tender_lots_award)


class TenderAwardComplaintResourceTest(TenderContentWebTest, TenderAwardComplaintResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardComplaintResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = auth

    test_create_tender_award_complaint = snitch(create_tender_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_award_complaint)
    test_review_tender_award_complaint = snitch(review_tender_award_complaint)


class TenderLotAwardComplaintResourceTest(TenderContentWebTest):
    initial_status = 'active.qualification'
    initial_lots = test_lots
    initial_bids = test_bids

    def setUp(self):
        super(TenderLotAwardComplaintResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        bid = self.initial_bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = auth

    test_create_tender_lot_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_lot_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_lot_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_lot_award_complaints = snitch(get_tender_lot_award_complaints)


class Tender2LotAwardComplaintResourceTest(TenderLotAwardComplaintResourceTest):
    initial_lots = 2 * test_lots

    test_create_tender_lots_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_lots_award_complaint = snitch(patch_tender_lots_award_complaint)


class TenderAwardComplaintDocumentResourceTest(TenderContentWebTest, TenderAwardComplaintDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = auth

        # Create complaint for award
        self.bid_token = self.initial_bids_tokens.values()[0]
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(TenderContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = auth
        # Create complaint for award
        bid_token = self.initial_bids_tokens.values()[0]
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, bid_token), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_create_tender_lots_award_complaint_document = snitch(create_tender_lots_award_complaint_document)
    test_put_tender_lots_award_complaint_document = snitch(put_tender_lots_award_complaint_document)
    test_patch_tender_lots_award_complaint_document = snitch(patch_tender_lots_award_complaint_document)


class TenderAwardDocumentResourceTest(TenderContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = auth


class TenderAwardDocumentWithDSResourceTest(TenderAwardDocumentResourceTest):
    docservice = True


class Tender2LotAwardDocumentResourceTest(TenderContentWebTest, Tender2LotAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        bid = self.initial_bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = auth


class Tender2LotAwardDocumentWithDSResourceTest(Tender2LotAwardDocumentResourceTest):
    docservice = True


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
