# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.contracting.api.tests.base import (
    test_contract_data,
    BaseWebTest,
    BaseContractWebTest,
    documents
)
from openprocurement.contracting.api.tests.contract_blanks import (
    # ContractTest
    simple_add_contract,
    # ContractResourceTest
    empty_listing,
    listing,
    listing_changes,
    get_contract,
    not_found,
    create_contract_invalid,
    create_contract_generated,
    create_contract,
    # ContractResource4BrokersTest
    contract_status_change,
    contract_items_change,
    patch_tender_contract,
    # ContractResource4AdministratorTest
    contract_administrator_change,
    # ContractCredentialsTest
    generate_credentials,
)


class ContractTest(BaseWebTest):
    initial_data = test_contract_data

    test_simple_add_contract = snitch(simple_add_contract)


class ContractResourceTest(BaseWebTest):
    """ contract resource test """
    initial_data = test_contract_data

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_get_contract = snitch(get_contract)
    test_not_found = snitch(not_found)
    test_create_contract_invalid = snitch(create_contract_invalid)
    test_create_contract_generated = snitch(create_contract_generated)
    test_create_contract = snitch(create_contract)


class ContractWDocumentsWithDSResourceTest(BaseWebTest):
    docservice = True

    def test_create_contract_w_documents(self):
        data = deepcopy(test_contract_data)
        data['documents'] = documents
        response = self.app.post_json('/contracts', {"data": data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        contract = response.json['data']
        self.assertEqual(contract['status'], 'active')
        for index, doc in enumerate(documents):
            self.assertEqual(response.json["data"]['documents'][index]['id'], documents[index]['id'])
            self.assertEqual(response.json["data"]['documents'][index]['datePublished'], documents[index]['datePublished'])
            self.assertEqual(response.json["data"]['documents'][index]['dateModified'], documents[index]['dateModified'])

        self.assertIn('Signature=', response.json["data"]['documents'][-1]["url"])
        self.assertIn('KeyID=', response.json["data"]['documents'][-1]["url"])
        self.assertNotIn('Expires=', response.json["data"]['documents'][-1]["url"])

        contract = self.db.get(contract['id'])
        self.assertIn('Prefix=ce536c5f46d543ec81ffa86ce4c77c8b%2F9c8b66120d4c415cb334bbad33f94ba9', contract['documents'][-1]["url"])
        self.assertIn('/da839a4c3d7a41d2852d17f90aa14f47?', contract['documents'][-1]["url"])
        self.assertIn('Signature=', contract['documents'][-1]["url"])
        self.assertIn('KeyID=', contract['documents'][-1]["url"])
        self.assertNotIn('Expires=', contract['documents'][-1]["url"])


class ContractResource4BrokersTest(BaseContractWebTest):
    """ contract resource test """
    initial_auth = ('Basic', ('broker', ''))

    test_contract_status_change = snitch(contract_status_change)
    test_contract_items_change = snitch(contract_items_change)
    test_patch_tender_contract = snitch(patch_tender_contract)


class ContractResource4AdministratorTest(BaseContractWebTest):
    """ contract resource test """
    initial_auth = ('Basic', ('administrator', ''))

    test_contract_administrator_change = snitch(contract_administrator_change)


class ContractCredentialsTest(BaseContractWebTest):
    """ Contract credentials tests """

    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_contract_data

    def test_get_credentials(self):
        response = self.app.get('/contracts/{0}/credentials?acc_token={1}'.format(self.contract_id,
                                                                                  self.initial_data['tender_token']), status=405)
        self.assertEqual(response.status, '405 Method Not Allowed')

    test_generate_credentials = snitch(generate_credentials)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractTest))
    suite.addTest(unittest.makeSuite(ContractResourceTest))
    suite.addTest(unittest.makeSuite(ContractCredentialsTest))
    suite.addTest(unittest.makeSuite(ContractResource4BrokersTest))
    suite.addTest(unittest.makeSuite(ContractResource4AdministratorTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
