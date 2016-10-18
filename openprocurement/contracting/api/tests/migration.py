# -*- coding: utf-8 -*-
import os
import json
import unittest

from copy import deepcopy
from openprocurement.api.models import Tender
from openprocurement.contracting.api.models import Contract
from openprocurement.contracting.api.migration import migrate_data, get_db_schema_version, set_db_schema_version, SCHEMA_VERSION
from openprocurement.contracting.api.tests.base import test_contract_data, BaseWebTest


class MigrateTest(BaseWebTest):

    def setUp(self):
        super(MigrateTest, self).setUp()
        migrate_data(self.app.app.registry)

    def test_migrate(self):
        self.assertEqual(get_db_schema_version(self.db), SCHEMA_VERSION)
        migrate_data(self.app.app.registry, 1)
        self.assertEqual(get_db_schema_version(self.db), SCHEMA_VERSION)

    def test_migrate_from0to1(self):
        set_db_schema_version(self.db, 0)

        with open(os.path.join(os.path.dirname(__file__), 'data/tender-contract-complete.json'), 'r') as df:
            data = json.loads(df.read())

        t = Tender(data)
        t.store(self.db)
        tender = self.db.get(t.id)

        self.assertEqual(tender['awards'][0]['value'], data['awards'][0]['value'])
        self.assertEqual(tender['awards'][0]['suppliers'], data['awards'][0]['suppliers'])

        contract_data = deepcopy(tender['contracts'][0])
        del contract_data['value']
        del contract_data['suppliers']
        contract_data['tender_id'] = tender['_id']
        contract_data['tender_token'] = 'xxx'
        contract_data['procuringEntity'] = tender['procuringEntity']

        contract = Contract(contract_data)
        contract.store(self.db)
        contract_data = self.db.get(contract.id)
        self.assertNotIn("value", contract_data)
        self.assertNotIn("suppliers", contract_data)

        migrate_data(self.app.app.registry, 1)
        migrated_item = self.db.get(contract.id)

        self.assertIn("value", migrated_item)
        self.assertEqual(migrated_item['value'], tender['awards'][0]['value'])
        self.assertIn("suppliers", migrated_item)
        self.assertEqual(migrated_item['suppliers'], tender['awards'][0]['suppliers'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MigrateTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
