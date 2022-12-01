import configparser
import unittest

from os.path import dirname, join

from openprocurement.api.constants import COORDINATES_REG_EXP
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.constants import parse_date

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

        file_path = join(dirname(dirname(__file__))) + '/constants.ini'
        config = configparser.ConfigParser()
        config.read(file_path)
        result = {k.upper(): v for k, v in config["DEFAULT"].items()}

        # Only dates
        for key in list(result.keys()):
            try:
                parse_date(result[key])
            except ValueError:
                result.pop(key)

        self.assertEqual(response.json, result)
