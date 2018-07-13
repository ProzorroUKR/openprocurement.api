# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_organization

from openprocurement.frameworkagreement.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_data,
    test_bids
)
from openprocurement.frameworkagreement.cfaua.tests.agreement_blanks import (
    # TenderAgreementResourceTest
    agreement_termination,
    create_tender_agreement,
    create_tender_agreement_invalid,
    create_tender_agreement_document,
    get_tender_agreement,
    get_tender_agreements,
    not_found,
    patch_tender_agreement,
    patch_tender_agreement_datesigned,
    patch_tender_agreement_document,
    put_tender_agreement_document,
)


class TenderAgreementResourceTestMixin(object):
    test_create_tender_agreement_invalid = snitch(create_tender_agreement_invalid)
    test_get_tender_agreement = snitch(get_tender_agreement)
    test_get_tender_agreements = snitch(get_tender_agreements)


class TenderAgreementDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_tender_agreement_document = snitch(create_tender_agreement_document)
    test_put_tender_agreement_document = snitch(put_tender_agreement_document)
    test_patch_tender_agreement_document = snitch(patch_tender_agreement_document)


class TenderAgreementResourceTest(BaseTenderContentWebTest, TenderAgreementResourceTestMixin):
    # initial_data = tender_data
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderAgreementResourceTest, self).setUp()
        # Create award
        self.supplier_info = deepcopy(test_organization)
        self.app.authorization = ('Basic', ('token', ''))
        data = {
            'data': {
                'suppliers': [self.supplier_info],
                'status': 'pending',
                'bid_id': self.initial_bids[0]['id'],
                'value': {
                    "amount": 500,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": True
                },
                'items': test_tender_data["items"]
            }
        }
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id), data)
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}}
        )

    test_agreement_termination = snitch(agreement_termination)
    test_create_tender_agreement = snitch(create_tender_agreement)
    test_patch_tender_agreement_datesigned = snitch(patch_tender_agreement_datesigned)
    test_patch_tender_agreement = snitch(patch_tender_agreement)


class TenderAgreementDocumentResourceTest(BaseTenderContentWebTest, TenderAgreementDocumentResourceTestMixin):
    # initial_data = tender_data
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderAgreementDocumentResourceTest, self).setUp()
        # Create award
        supplier_info = deepcopy(test_organization)
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json(
            '/tenders/{}/awards'.format(self.tender_id),
            {'data': {'suppliers': [supplier_info], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}}
        )
        award = response.json['data']
        self.award_id = award['id']
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id),
                                       {"data": {"status": "active", "qualified": True, "eligible": True}})
        # Create agreement for award
        response = self.app.post_json(
            '/tenders/{}/agreements'.format(self.tender_id),
            {'data': {'title': 'agreement title', 'description': 'agreement description', 'awardID': self.award_id}}
        )
        agreement = response.json['data']
        self.agreement_id = agreement['id']
        self.app.authorization = ('Basic', ('broker', ''))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAgreementResourceTest))
    suite.addTest(unittest.makeSuite(TenderAgreementDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
