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
from openprocurement.tender.competitivedialogue.tests.stage2.contract_blanks import (
    # TenderStage2EUContractResourceTest
    contract_termination_eu,
    create_tender_contract_invalid_eu,
    create_tender_contract_eu,
    patch_tender_contract_datesigned_eu,
    patch_tender_contract_eu,
    get_tender_contract_eu,
    get_tender_contracts_eu,
    # TenderStage2EUContractDocumentResourceTest
    not_found_eu,
    create_tender_contract_document_eu,
    put_tender_contract_document_eu,
    patch_tender_contract_document_eu,
    # TenderStage2UAContractResourceTest
    create_tender_contract_invalid_ua,
    create_tender_contract_ua,
    patch_tender_contract_datesigned_ua,
    patch_tender_contract_ua,
    get_tender_contract_ua,
    get_tender_contracts_ua,
    # TenderStage2UAContractDocumentResourceTest
    not_found_ua,
    create_tender_contract_document_ua,
    put_tender_contract_document_ua,
    patch_tender_contract_document_ua,    
)

test_tender_bids = deepcopy(test_bids[:2])
for test_bid in test_tender_bids:
    test_bid['tenderers'] = [author]


class TenderStage2EUContractResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

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
        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        print(response.json['data']['tenderPeriod'], response.json['data']['awardPeriod'])
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})

    test_contract_termination = snitch(contract_termination_eu)

    test_create_tender_contract_invalid = snitch(create_tender_contract_invalid_eu)

    test_create_tender_contract = snitch(create_tender_contract_eu)

    test_patch_tender_contract_datesigned = snitch(patch_tender_contract_datesigned_eu)

    test_patch_tender_contract = snitch(patch_tender_contract_eu)

    test_get_tender_contract = snitch(get_tender_contract_eu)

    test_get_tender_contracts = snitch(get_tender_contracts_eu)


class TenderStage2EUContractDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
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

    test_not_found = snitch(not_found_eu)

    test_create_tender_contract_document = snitch(create_tender_contract_document_eu)

    test_put_tender_contract_document = snitch(put_tender_contract_document_eu)

    test_patch_tender_contract_document = snitch(patch_tender_contract_document_eu)


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
        self.app.authorization = authorization
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})

    test_create_tender_contract_invalid = snitch(create_tender_contract_invalid_ua)

    test_create_tender_contract = snitch(create_tender_contract_ua)

    test_patch_tender_contract_datesigned = snitch(patch_tender_contract_datesigned_ua)

    test_patch_tender_contract = snitch(patch_tender_contract_ua)

    test_get_tender_contract = snitch(get_tender_contract_ua)

    test_get_tender_contracts = snitch(get_tender_contracts_ua)


class TenderStage2UAContractDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
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

    test_not_found = snitch(not_found_ua)

    test_create_tender_contract_document = snitch(create_tender_contract_document_ua)

    test_put_tender_contract_document = snitch(put_tender_contract_document_ua)

    test_patch_tender_contract_document = snitch(patch_tender_contract_document_ua)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUContractDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAContractDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
