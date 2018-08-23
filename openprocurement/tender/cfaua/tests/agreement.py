# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_organization

from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_data,
    test_bids
)
from openprocurement.tender.cfaua.tests.agreement_blanks import (
    # TenderAgreementResourceTest
    agreement_cancellation,
    agreement_termination,
    create_tender_agreement_document,
    get_tender_agreement,
    get_tender_agreements,
    get_tender_agreement_contract,
    get_tender_agreement_contracts,
    not_found,
    patch_tender_agreement,
    patch_tender_agreement_contract,
    patch_tender_agreement_datesigned,
    patch_tender_agreement_document,
    put_tender_agreement_document,
    patch_no_lot_agreement_contract_unit_prices,
    patch_lots_agreement_contract_unit_prices,
)


class TenderAgreementResourceTestMixin(object):
    test_get_tender_agreement = snitch(get_tender_agreement)
    test_get_tender_agreements = snitch(get_tender_agreements)
    test_get_tender_agreement_contract = snitch(get_tender_agreement_contract)
    test_get_tender_agreement_contracts = snitch(get_tender_agreement_contracts)


class TenderAgreementDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_tender_agreement_document = snitch(create_tender_agreement_document)
    test_put_tender_agreement_document = snitch(put_tender_agreement_document)
    test_patch_tender_agreement_document = snitch(patch_tender_agreement_document)


# @unittest.skipIf(True, 'Update setUp ( qualify all awards)')
class TenderAgreementResourceTest(BaseTenderContentWebTest, TenderAgreementResourceTestMixin):
    # initial_data = tender_data
    initial_status = 'active.awarded'
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderAgreementResourceTest, self).setUp()
        self.tender = self.app.get('/tenders/{}'.format(self.tender_id)).json['data']
        self.agreement_id = self.tender['agreements'][0]['id']
        self.contract_id = self.tender['agreements'][0]['contracts'][0]['id']

    test_agreement_termination = snitch(agreement_termination)
    test_agreement_cancellation = snitch(agreement_cancellation)
    test_patch_tender_agreement_contract = snitch(patch_tender_agreement_contract)
    test_patch_tender_agreement_datesigned = snitch(patch_tender_agreement_datesigned)
    test_patch_tender_agreement = snitch(patch_tender_agreement)
    test_patch_no_lot_agreement_contract_unit_prices = snitch(patch_no_lot_agreement_contract_unit_prices)
    test_patch_lots_agreement_contract_unit_prices = snitch(patch_lots_agreement_contract_unit_prices)


class TenderAgreementDocumentResourceTest(BaseTenderContentWebTest, TenderAgreementDocumentResourceTestMixin):
    # initial_data = tender_data
    initial_status = 'active.awarded'
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderAgreementDocumentResourceTest, self).setUp()
        self.tender = self.app.get('/tenders/{}'.format(self.tender_id)).json['data']
        self.agreement_id = self.tender['agreements'][0]['id']
        self.contract_id = self.tender['agreements'][0]['contracts'][0]['id']
        self.app.authorization = ('Basic', ('broker', ''))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAgreementResourceTest))
    suite.addTest(unittest.makeSuite(TenderAgreementDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
