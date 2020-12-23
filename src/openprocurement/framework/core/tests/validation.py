import os
import unittest
from copy import deepcopy

from mock import patch, MagicMock

from openprocurement.framework.core.tests.base import BaseFrameworkTest, test_framework_data
from openprocurement.framework.core.validation import validate_framework_data


class ValidationFrameworkTest(BaseFrameworkTest):
    relative_to = os.path.dirname(__file__)

    @patch("openprocurement.framework.core.validation.validate_json_data")
    def test_validate_framework_data(self, mocked_validation_json_data):
        request = MagicMock()
        data = deepcopy(test_framework_data)
        model = MagicMock()
        request.check_accreditations.side_effect = [False, True]
        mocked_validation_json_data.side_effect = [data, data]
        request.framework_from_data.side_effect = [model, model]
        with self.assertRaises(Exception) as e:
            res = validate_framework_data(request)
        res = validate_framework_data(request)
        self.assertTrue(res)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ValidationFrameworkTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
