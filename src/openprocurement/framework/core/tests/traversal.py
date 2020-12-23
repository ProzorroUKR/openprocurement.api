import os
import unittest
from copy import deepcopy

from mock import MagicMock, patch

from openprocurement.api.constants import VERSION
from openprocurement.framework.core.tests.base import test_framework_data, BaseFrameworkTest
from openprocurement.framework.core.traversal import framework_factory


class TraversalFrameworkTest(BaseFrameworkTest):
    relative_to = os.path.dirname(__file__)

    @patch("openprocurement.framework.core.traversal.get_item")
    def test_factory(self, mocked_get_item):
        data = deepcopy(test_framework_data)
        framework = MagicMock()
        framework.id = data["id"]
        framework.title = "test_factory"

        request = MagicMock()
        request.url = "http://localhost/api/" + VERSION + "/frameworks"
        request.matchdict = {"framework_id": data["id"], "document_id": "9a750db83cc64b34a879221513c13805"}
        request.framework = framework
        request.method = "POST"
        mocked_get_item.side_effect = ["test_item1", "test_item2"]
        res = framework_factory(request)
        self.assertEqual(res, "test_item1")
        self.assertEqual(mocked_get_item.called, True)
        request.matchdict = {"framework_id": data["id"]}
        res = framework_factory(request)
        self.assertEqual(res.id, data["id"])
        self.assertEqual(res.title, "test_factory")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TraversalFrameworkTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
