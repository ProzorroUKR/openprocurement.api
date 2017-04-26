# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_bids,
    author,
    test_tender_stage2_data_eu
)
from openprocurement.tender.belowthreshold.tests.contract import (
    TenderContractResourceTestMixin,
    TenderContractDocumentResourceTestMixin
)
from openprocurement.tender.belowthreshold.tests.contract_blanks import (
    # TenderStage2EU(UA)ContractResourceTest
    create_tender_contract,
)
from openprocurement.tender.openua.tests.contract_blanks import (
    # TenderStage2EU(UA)ContractResourceTest
    patch_tender_contract_datesigned,
    # TenderStage2UAContractResourceTest,
    patch_tender_contract,
)
from openprocurement.tender.openeu.tests.contract_blanks import (
    # TenderStage2EUContractResourceTest
    contract_termination,
    patch_tender_contract as patch_tender_contract_eu,
)

test_tender_bids = deepcopy(test_bids[:2])
for test_bid in test_tender_bids:
    test_bid['tenderers'] = [author]


class TenderStage2EUContractResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderContractResourceTestMixin):

    initial_status = 'active.qualification'
    initial_bids = test_tender_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2EUContractResourceTest, self).setUp()
        # Create award
        self.supplier_info = deepcopy(author)
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [self.supplier_info],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id'],
                                                'value': {'amount': 500,
                                                          'currency': 'UAH', 'valueAddedTaxIncluded': True},
                                                'items': test_tender_stage2_data_eu['items']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authotization = ('Basic', ('broker', ''))
        self.award_value = award['value']
        self.award_suppliers = award['suppliers']
        self.award_items = award['items']
        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})

    test_contract_termination = snitch(contract_termination)
    test_create_tender_contract = snitch(create_tender_contract)
    test_patch_tender_contract_datesigned = snitch(patch_tender_contract_datesigned)
    test_patch_tender_contract = snitch(patch_tender_contract_eu)


class TenderStage2EUContractDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderContractDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2EUContractDocumentResourceTest, self).setUp()
        # Create award
        supplier_info = deepcopy(author)
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [supplier_info],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        # Create contract for award
        response = self.app.post_json('/tenders/{}/contracts'.format(self.tender_id),
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award_id}})
        contract = response.json['data']
        self.contract_id = contract['id']
        self.app.authorization = ('Basic', ('broker', ''))


class TenderStage2UAContractResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2UAContractResourceTest, self).setUp()
        # Create award
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': self.bids[0]['id'], 'value': self.bids[0]['value']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authotization = ('Basic', ('broker', ''))
        self.award_value = award['value']
        self.award_suppliers = award['suppliers']
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})

    test_create_tender_contract = snitch(create_tender_contract)
    test_patch_tender_contract_datesigned = snitch(patch_tender_contract_datesigned)
    test_patch_tender_contract = snitch(patch_tender_contract)


class TenderStage2UAContractDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderContractDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2UAContractDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        # Create contract for award
        response = self.app.post_json('/tenders/{}/contracts'.format(self.tender_id),
                                      {'data': {'title': 'contract title',
                                                'description': 'contract description',
                                                'awardID': self.award_id}})
        contract = response.json['data']
        self.contract_id = contract['id']
        self.app.authorization = auth


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUContractDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAContractDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
