# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_bids,
    test_lots,
)
from openprocurement.tender.openeu.tests.qualification_blanks import (
    # Tender2LotQualificationComplaintDocumentResourceTest
    create_tender_2lot_qualification_complaint_document,
    put_tender_2lot_qualification_complaint_document,
    patch_tender_2lot_qualification_complaint_document,
    # TenderQualificationComplaintDocumentResourceTest
    complaint_not_found,
    create_tender_qualification_complaint_document,
    put_tender_qualification_complaint_document,
    patch_tender_qualification_complaint_document,
    # Tender2LotQualificationClaimResourceTest
    create_tender_qualification_claim,
    # Tender2LotQualificationComplaintResourceTest
    create_tender_2lot_qualification_complaint,
    patch_tender_2lot_qualification_complaint,
    change_status_to_standstill_with_complaint_cancel_lot,
    # TenderLotQualificationComplaintResourceTest
    create_tender_lot_qualification_complaint,
    patch_tender_lot_qualification_complaint,
    get_tender_lot_qualification_complaint,
    get_tender_lot_qualification_complaints,
    # TenderQualificationComplaintResourceTest
    create_tender_qualification_complaint_invalid,
    create_tender_qualification_complaint,
    patch_tender_qualification_complaint,
    review_tender_qualification_complaint,
    review_tender_award_claim,
    get_tender_qualification_complaint,
    get_tender_qualification_complaints,
    change_status_to_standstill_with_complaint,
    # TenderQualificationDocumentResourceTest
    not_found,
    create_qualification_document,
    put_qualification_document,
    patch_qualification_document,
    create_qualification_document_after_status_change,
    put_qualification_document_after_status_change,
    # Tender2LotQualificationResourceTest
    lot_patch_tender_qualifications,
    lot_get_tender_qualifications_collection,
    tender_qualification_cancelled,
    # TenderQualificationResourceTest
    post_tender_qualifications,
    get_tender_qualifications_collection,
    patch_tender_qualifications,
    get_tender_qualifications,
    patch_tender_qualifications_after_status_change
)


class TenderQualificationResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'  # 'active.pre-qualification' status sets in setUp
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderQualificationResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={'status': 'active.tendering'})

        # simulate chronograph tick
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')
        self.app.authorization = auth

    test_post_tender_qualifications = snitch(post_tender_qualifications)
    test_get_tender_qualifications_collection = snitch(get_tender_qualifications_collection)
    test_patch_tender_qualifications = snitch(patch_tender_qualifications)
    test_get_tender_qualifications = snitch(get_tender_qualifications)
    test_patch_tender_qualifications_after_status_change = snitch(patch_tender_qualifications_after_status_change)


class Tender2LotQualificationResourceTest(TenderQualificationResourceTest):
    initial_status = 'active.tendering'  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_lots = 2 * test_lots
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderQualificationResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={'status': 'active.tendering'})

        # simulate chronograph tick
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

    test_patch_tender_qualifications = snitch(lot_patch_tender_qualifications)
    test_get_tender_qualifications_collection = snitch(lot_get_tender_qualifications_collection)
    test_tender_qualification_cancelled = snitch(tender_qualification_cancelled)


class TenderQualificationDocumentResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderQualificationDocumentResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        # list qualifications
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.status, "200 OK")
        self.qualifications = response.json['data']
        self.assertEqual(len(self.qualifications), 2)

    test_not_found = snitch(not_found)
    test_create_qualification_document = snitch(create_qualification_document)
    test_put_qualification_document = snitch(put_qualification_document)
    test_patch_qualification_document = snitch(patch_qualification_document)
    test_create_qualification_document_after_status_change = snitch(create_qualification_document_after_status_change)
    test_put_qualification_document_after_status_change = snitch(put_qualification_document_after_status_change)


class TenderQualificationComplaintResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderQualificationComplaintResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={'status': 'active.tendering'})

        # simulate chronograph tick
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        self.qualification_id = qualifications[0]['id']

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, '200 OK')

    test_create_tender_qualification_complaint_invalid = snitch(create_tender_qualification_complaint_invalid)
    test_create_tender_qualification_complaint = snitch(create_tender_qualification_complaint)
    test_patch_tender_qualification_complaint = snitch(patch_tender_qualification_complaint)
    test_review_tender_qualification_complaint = snitch(review_tender_qualification_complaint)
    test_review_tender_award_claim = snitch(review_tender_award_claim)
    test_get_tender_qualification_complaint = snitch(get_tender_qualification_complaint)
    test_get_tender_qualification_complaints = snitch(get_tender_qualification_complaints)
    test_change_status_to_standstill_with_complaint = snitch(change_status_to_standstill_with_complaint)


class TenderLotQualificationComplaintResourceTest(TenderQualificationComplaintResourceTest):
    initial_lots = test_lots

    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_qualification_complaint = snitch(create_tender_lot_qualification_complaint)
    test_patch_tender_qualification_complaint = snitch(patch_tender_lot_qualification_complaint)
    test_get_tender_qualification_complaint = snitch(get_tender_lot_qualification_complaint)
    test_get_tender_qualification_complaints = snitch(get_tender_lot_qualification_complaints)


class Tender2LotQualificationComplaintResourceTest(TenderLotQualificationComplaintResourceTest):
    initial_lots = 2 * test_lots

    initial_auth = ('Basic', ('broker', ''))
    after_qualification_switch_to = "active.auction"

    test_create_tender_qualification_complaint = snitch(create_tender_2lot_qualification_complaint)
    test_patch_tender_qualification_complaint = snitch(patch_tender_2lot_qualification_complaint)
    test_change_status_to_standstill_with_complaint_cancel_lot = snitch(change_status_to_standstill_with_complaint_cancel_lot)


class Tender2LotQualificationClaimResourceTest(Tender2LotQualificationComplaintResourceTest):

    after_qualification_switch_to = "unsuccessful"

    def setUp(self):
        super(TenderQualificationComplaintResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={'status': 'active.tendering'})

        # simulate chronograph tick
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        self.qualification_id = qualifications[0]['id']

        for qualification in qualifications:
            if qualification['bidID'] == self.initial_bids[0]['id']:
                response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                               {"data": {"status": "active", "qualified": True, "eligible": True}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.json['data']['status'], 'active')
            else:
                response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                               {"data": {"status": "unsuccessful"}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.json['data']['status'], 'unsuccessful')
                self.unsuccessful_qualification_id = qualification['id']

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, '200 OK')

    test_create_tender_qualification_claim = snitch(create_tender_qualification_claim)

class TenderQualificationComplaintDocumentResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderQualificationComplaintDocumentResourceTest, self).setUp()

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={'status': 'active.tendering'})

        # simulate chronograph tick
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        self.qualification_id = qualifications[0]['id']

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')


        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, '200 OK')

        # Create complaint for qualification
        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': self.initial_bids[0]["tenderers"][0]
        }})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_not_found = snitch(complaint_not_found)
    test_create_tender_qualification_complaint_document = snitch(create_tender_qualification_complaint_document)
    test_put_tender_qualification_complaint_document = snitch(put_tender_qualification_complaint_document)
    test_patch_tender_qualification_complaint_document = snitch(patch_tender_qualification_complaint_document)


class Tender2LotQualificationComplaintDocumentResourceTest(TenderQualificationComplaintDocumentResourceTest):
    initial_lots = 2 * test_lots

    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_qualification_complaint_document = snitch(create_tender_2lot_qualification_complaint_document)
    test_put_tender_qualification_complaint_document = snitch(put_tender_2lot_qualification_complaint_document)
    test_patch_tender_qualification_complaint_document = snitch(patch_tender_2lot_qualification_complaint_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQualificationResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
