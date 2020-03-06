from openprocurement.api.constants import COORDINATES_REG_EXP
import unittest


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
