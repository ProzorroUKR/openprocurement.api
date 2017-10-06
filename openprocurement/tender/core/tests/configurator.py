import unittest
from openprocurement.api.tests.base import snitch
from openprocurement.tender.core.adapters import TenderConfigurator
from configurator_blanks import (reverse_awarding_criteria_check,
                                 test_awarding_criteria_key,
                                 test_model)


class ConfiguratorTestMixin(object):
    test_reverse_awarding_criteria = snitch(reverse_awarding_criteria_check)
    test_test_awarding_criteria_key = snitch(test_awarding_criteria_key)
    test_model = snitch(test_model)


class ConfiguratorTest(unittest.TestCase, ConfiguratorTestMixin):
    configurator_class = TenderConfigurator
    reverse_awarding_criteria = False
    awarding_criteria_key = 'not yet implemented'
    configurator_model = None


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ConfiguratorTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
