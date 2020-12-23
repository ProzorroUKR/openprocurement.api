import os
import unittest
from copy import deepcopy

from openprocurement.framework.core.tests.base import BaseFrameworkTest, test_framework_data
from openprocurement.framework.core.tests.framework import Framework


class ModelFrameworkTest(BaseFrameworkTest):
    relative_to = os.path.dirname(__file__)

    def test_framework_model(self):
        data = deepcopy(test_framework_data)
        framework = Framework()
        data["title"] = "test_name"
        data["description"] = "test description"
        res = framework.import_data(data)
        self.assertTrue(res)
        roles = framework.__local_roles__()
        self.assertTrue(roles)
        acl = framework.__acl__()
        self.assertTrue(acl)
        repr = framework.__repr__()
        self.assertTrue(repr)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModelFrameworkTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
