from openprocurement.api.constants import COORDINATES_REG_EXP
from openprocurement.api.tests.base import BaseWebTest
import configparser
from os.path import dirname, join
import unittest
from os import environ
from openprocurement.api.constants import parse_constant_date

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
        result.pop("MASK_OBJECT_DATA")
        result.pop("FAST_CATALOGUE_FLOW")
        if "DEFAULT_RELEASE_2020_04_19" in environ:
            date = environ['DEFAULT_RELEASE_2020_04_19']
            result["RELEASE_2020_04_19"] = parse_constant_date(date).isoformat()
        elif "DEFAULT_RELEASE_ECRITERIA_ARTICLE_17" in environ:
            date = environ['DEFAULT_RELEASE_ECRITERIA_ARTICLE_17']
            result["RELEASE_ECRITERIA_ARTICLE_17"] = parse_constant_date(date).isoformat()

        self.assertEqual(response.json, result)
