# -*- coding: utf-8 -*-
import unittest
from datetime import timedelta

import mock
from openprocurement.api.models import BusinessOrganization
from schematics.exceptions import ModelValidationError

from op_robot_tests.tests_files.local_time import get_now


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
        organization.validate()
        data = organization.serialize("embedded")
        self.assertIn("scale", data)
        self.assertIn(data["scale"], "micro")

    def test_validate_not_valid(self):
        organization = BusinessOrganization(dict(scale="giant", **self.organization_data))
        with self.assertRaises(ModelValidationError) as e:
            organization.validate()
        self.assertEqual(
            e.exception.message,
            {'scale': [u"Value must be one of ['micro', 'sme', 'mid', 'large']."]}
        )

    def test_validate_required(self):
        organization = BusinessOrganization(self.organization_data)
        with self.assertRaises(ModelValidationError) as e:
            organization.validate()
        self.assertEqual(
            e.exception.message,
            {'scale': [u'This field is required.']}
        )

    @mock.patch('openprocurement.api.models.ORGANIZATION_SCALE_FROM', get_now() + timedelta(days=1))
    def test_validate_rogue(self):
        organization = BusinessOrganization(dict(scale="micro", **self.organization_data))
        with self.assertRaises(ModelValidationError) as e:
            organization.validate()
        self.assertEqual(
            e.exception.message,
            {'scale': [u'Rogue field']}
        )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBusinessOrganizationScale))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
