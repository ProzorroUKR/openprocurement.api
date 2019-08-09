# -*- coding: utf-8 -*-
import unittest
from datetime import timedelta
import mock

from schematics.exceptions import ModelValidationError
from couchdb_schematics.document import SchematicsDocument

from openprocurement.api.models import Item
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.models import BusinessOrganization
from openprocurement.api.utils import get_now


class ItemTestCase(BaseWebTest):

    def test_item_quantity(self):
        data = {
            "description": "",
            "quantity": 12.51,
        }
        item = Item(data)
        item.validate()
        self.assertEqual(item.quantity, data["quantity"])


class TestBusinessOrganizationScale(unittest.TestCase):
    organization_data = {
        "contactPoint": {
            "email": "john.doe@example.com",
            "name": "John Doe"
        },
        "identifier": {
            "scheme": "UA-EDR",
            "id": "00137256",
        },
        "name": "John Doe LTD",
        "address": {
            "countryName": "Ukraine",
        }
    }

    def test_validate_valid(self):
        organization = BusinessOrganization(dict(scale="micro", **self.organization_data))
        organization.__parent__ = SchematicsDocument()
        organization.validate()
        data = organization.serialize("embedded")
        self.assertIn("scale", data)
        self.assertIn(data["scale"], "micro")

    def test_validate_not_valid(self):
        organization = BusinessOrganization(dict(scale="giant", **self.organization_data))
        organization.__parent__ = SchematicsDocument()
        with self.assertRaises(ModelValidationError) as e:
            organization.validate()
        self.assertEqual(
            e.exception.message,
            {'scale': [u"Value must be one of ['micro', 'sme', 'mid', 'large', 'not specified']."]}
        )

    def test_validate_required(self):
        organization = BusinessOrganization(self.organization_data)
        organization.__parent__ = SchematicsDocument()
        with self.assertRaises(ModelValidationError) as e:
            organization.validate()
        self.assertEqual(
            e.exception.message,
            {'scale': [u'This field is required.']}
        )

    @mock.patch('openprocurement.api.models.ORGANIZATION_SCALE_FROM', get_now() + timedelta(days=1))
    def test_validate_not_required(self):
        organization = BusinessOrganization(self.organization_data)
        organization.__parent__ = SchematicsDocument()
        organization.validate()
        data = organization.serialize("embedded")
        self.assertNotIn("scale", data)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ItemTestCase))
    suite.addTest(unittest.makeSuite(TestBusinessOrganizationScale))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
