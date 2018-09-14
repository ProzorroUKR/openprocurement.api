# -*- coding: utf-8 -*-
from openprocurement.api.models import Item
from openprocurement.api.tests.base import BaseWebTest
import unittest


class ItemTestCase(BaseWebTest):

    def test_item_quantity(self):
        data = {
            "description": "",
            "quantity": 12.51,
        }
        item = Item(data)
        item.validate()
        self.assertEqual(item.quantity, data["quantity"])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ItemTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
