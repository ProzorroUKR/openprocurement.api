# -*- coding: utf-8 -*-
import unittest
from datetime import timedelta, datetime
import mock
from pytz import timezone

from schematics.exceptions import ValidationError, ModelValidationError, ConversionError
from couchdb_schematics.document import SchematicsDocument

import openprocurement
from openprocurement.api.models import Item, IsoDateTimeType
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.models import BusinessOrganization, Address
from openprocurement.api.utils import get_now
from openprocurement.api.constants import COUNTRIES, UA_REGIONS, VALIDATE_ADDRESS_FROM, TZ


class ItemTestCase(BaseWebTest):
    def test_item_quantity(self):
        data = {"description": "", "quantity": 12.51}
        item = Item(data)
        item.validate()
        self.assertEqual(item.quantity, data["quantity"])

@mock.patch("openprocurement.api.models.Address.validate", mock.Mock())
class TestBusinessOrganizationScale(unittest.TestCase):
    organization_data = {
        "contactPoint": {"email": "john.doe@example.com", "name": "John Doe"},
        "identifier": {"scheme": "UA-EDR", "id": "00137256"},
        "name": "John Doe LTD",
        "address": {"countryName": "Ukraine"},
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
            e.exception.message, {"scale": [u"Value must be one of ['micro', 'sme', 'mid', 'large', 'not specified']."]}
        )

    def test_validate_required(self):
        organization = BusinessOrganization(self.organization_data)
        organization.__parent__ = SchematicsDocument()
        with self.assertRaises(ModelValidationError) as e:
            organization.validate()
        self.assertEqual(e.exception.message, {"scale": [u"This field is required."]})

    @mock.patch("openprocurement.api.models.ORGANIZATION_SCALE_FROM", get_now() + timedelta(days=1))
    def test_validate_not_required(self):
        organization = BusinessOrganization(self.organization_data)
        organization.__parent__ = SchematicsDocument()
        organization.validate()
        data = organization.serialize("embedded")
        self.assertNotIn("scale", data)


class TestAddress(unittest.TestCase):
    DATE_BEFORE = VALIDATE_ADDRESS_FROM - timedelta(days=1)
    DATE_AFTER = VALIDATE_ADDRESS_FROM

    @mock.patch("openprocurement.api.models.get_first_revision_date")
    @mock.patch("openprocurement.api.models.get_root")
    def test_validate(self, mock_get_root, mock_get_first_revision_date):

        address = Address()
        address.countryName = u"Украина"
        mock_get_root.return_value = None

        mock_get_first_revision_date.return_value = self.DATE_BEFORE
        address.validate()
        self.assertNotIn(address.countryName, COUNTRIES)

        mock_get_first_revision_date.return_value = self.DATE_AFTER
        with self.assertRaises(ModelValidationError) as e:
            address.validate()
        self.assertEqual(
            e.exception.message, {'countryName': [u"field address:countryName not exist in countries catalog"]}
        )

        address.countryName = u"Україна"
        address.validate()
        self.assertIn(address.countryName, COUNTRIES)

        # region
        address.countryName = u"Украина"
        address.region = u"Киевская область"
        mock_get_root.return_value = None

        mock_get_first_revision_date.return_value = self.DATE_BEFORE
        address.validate()
        self.assertNotIn(address.region, COUNTRIES)
        self.assertNotIn(address.region, UA_REGIONS)

        address.countryName = u"Україна"
        mock_get_first_revision_date.return_value = self.DATE_AFTER
        with self.assertRaises(ModelValidationError) as e:
            address.validate()
        self.assertEqual(
            e.exception.message, {"region": [u"field address:region not exist in ua_regions catalog"]}
        )

        address.region = u"Київська область"
        address.validate_region(address, address.region)
        self.assertIn(address.region, UA_REGIONS)


class TestIsoDateTimeType(unittest.TestCase):
    def test_to_native_string(self):
        dt_str = "2020-01-01T12:00:00+02:00"
        dt_result = IsoDateTimeType().to_native(dt_str)
        dt_expected = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_to_native_string_with_no_tz(self):
        dt_str = "2020-01-01T12:00:00"
        dt_result = IsoDateTimeType().to_native(dt_str)
        dt_expected = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_to_native_string_with_no_time_and_tz(self):
        dt_str = "2020-01-01"
        dt_result = IsoDateTimeType().to_native(dt_str)
        dt_expected = TZ.localize(datetime(2020, 1, 1))
        self.assertEqual(dt_result, dt_expected)

    def test_to_native_string_with_not_default_tz(self):
        dt_str = "2020-01-01T12:00:00-05:00"
        dt_result = IsoDateTimeType().to_native(dt_str)
        dt_expected = timezone('US/Eastern').localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_to_native_string_invalid_format(self):
        dt_str = "test"
        with self.assertRaises(ConversionError) as e:
            IsoDateTimeType().to_native(dt_str)
            self.assertEqual(
                e.exception.message,
                IsoDateTimeType.MESSAGES["parse"].format(dt_str)
            )

    def test_to_native_datetime(self):
        dt = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        dt_result = IsoDateTimeType().to_native(dt)
        self.assertEqual(dt_result, dt)

    def test_to_primitive_string(self):
        dt_str = "2020-01-01T12:00:00+02:00"
        dt_result = IsoDateTimeType().to_primitive(dt_str)
        self.assertEqual(dt_result, dt_str)

    def test_to_primitive_datetime(self):
        dt = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        dt_str_result = IsoDateTimeType().to_primitive(dt)
        dt_str_expected = "2020-01-01T12:00:00+02:00"
        self.assertEqual(dt_str_result, dt_str_expected)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ItemTestCase))
    suite.addTest(unittest.makeSuite(TestBusinessOrganizationScale))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
