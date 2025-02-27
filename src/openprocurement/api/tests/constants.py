import datetime
import unittest

from openprocurement.api.constants import COORDINATES_REG_EXP
from openprocurement.api.constants_utils import parse_date
from openprocurement.api.tests.base import BaseWebTest


class ConstantsTestCase(unittest.TestCase):
    def test_coordinates_reg_exp(self):
        self.assertEqual("1", COORDINATES_REG_EXP.match("1").group())
        self.assertEqual("1.1234567890", COORDINATES_REG_EXP.match("1.1234567890").group())
        self.assertEqual("12", COORDINATES_REG_EXP.match("12").group())
        self.assertEqual("12.1234567890", COORDINATES_REG_EXP.match("12.1234567890").group())
        self.assertEqual("123", COORDINATES_REG_EXP.match("123").group())
        self.assertEqual("123.1234567890", COORDINATES_REG_EXP.match("123.1234567890").group())
        self.assertEqual("0", COORDINATES_REG_EXP.match("0").group())
        self.assertEqual("0.1234567890", COORDINATES_REG_EXP.match("0.1234567890").group())
        self.assertEqual("-0.1234567890", COORDINATES_REG_EXP.match("-0.1234567890").group())
        self.assertEqual("-1", COORDINATES_REG_EXP.match("-1").group())
        self.assertEqual("-1.1234567890", COORDINATES_REG_EXP.match("-1.1234567890").group())
        self.assertEqual("-12", COORDINATES_REG_EXP.match("-12").group())
        self.assertEqual("-12.1234567890", COORDINATES_REG_EXP.match("-12.1234567890").group())
        self.assertEqual("-123", COORDINATES_REG_EXP.match("-123").group())
        self.assertEqual("-123.1234567890", COORDINATES_REG_EXP.match("-123.1234567890").group())
        self.assertNotEqual("1.", COORDINATES_REG_EXP.match("1.").group())
        self.assertEqual(None, COORDINATES_REG_EXP.match(".1"))
        self.assertNotEqual("1.1.", COORDINATES_REG_EXP.match("1.1.").group())
        self.assertNotEqual("1..1", COORDINATES_REG_EXP.match("1..1").group())
        self.assertNotEqual("1.1.1", COORDINATES_REG_EXP.match("1.1.1").group())
        self.assertEqual(None, COORDINATES_REG_EXP.match("$tr!ng"))
        self.assertEqual(None, COORDINATES_REG_EXP.match(""))


class HealthTestBase(BaseWebTest):
    def test_constants_view(self):
        response = self.app.get("/constants", status=200)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        date_example_contant_name = "DST_AWARE_PERIODS_FROM"
        bool_example_contant_name = "CRITICAL_HEADERS_LOG_ENABLED"

        self.assertEqual(type(response.json[bool_example_contant_name]), bool)
        self.assertEqual(type(response.json[date_example_contant_name]), str)
        self.assertEqual(type(parse_date(response.json[date_example_contant_name])), datetime.datetime)
