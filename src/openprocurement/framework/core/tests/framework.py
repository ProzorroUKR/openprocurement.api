import os
import unittest
from copy import deepcopy
from datetime import datetime
from mock import MagicMock, patch
from schematics.transforms import wholelist
from schematics.types import StringType
from schematics.types.serializable import serializable

from openprocurement.framework.core.models import Framework as BaseFramework
from openprocurement.framework.core.tests.base import BaseFrameworkTest, test_framework_data
from openprocurement.framework.core.utils import isFramework
from openprocurement.framework.core.views.framework import FrameworkResource


class Framework(BaseFramework):
    class Options:
        roles = {"draft": wholelist()}

    frameworkType = StringType(
        choices=["electronicCatalogue"], default="electronicCatalogue"
    )

    @serializable(serialized_name="date")
    def old_date(self):
        pass


class FrameworksResourceTest(BaseFrameworkTest):
    relative_to = os.path.dirname(__file__)

    def test_empty_listing(self):
        response = self.app.get("/frameworks")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], [])
        self.assertNotIn('{\n    "', response.body.decode())
        self.assertNotIn("callback({", response.body.decode())
        self.assertEqual(response.json["next_page"]["offset"], "")
        self.assertNotIn("prev_page", response.json)

        response = self.app.get("/frameworks?opt_jsonp=callback")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/javascript")
        self.assertNotIn('{\n    "', response.body.decode())
        self.assertIn("callback({", response.body.decode())

        response = self.app.get("/frameworks?opt_pretty=1")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn('{\n    "', response.body.decode())
        self.assertNotIn("callback({", response.body.decode())

        response = self.app.get("/frameworks?opt_jsonp=callback&opt_pretty=1")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/javascript")
        self.assertIn('{\n    "', response.body.decode())
        self.assertIn("callback({", response.body.decode())

        offset = datetime.fromisoformat("2015-01-01T00:00:00+02:00").timestamp()
        response = self.app.get(f"/frameworks?offset={offset}&descending=1&limit=10")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], [])
        self.assertIn("descending=1", response.json["next_page"]["uri"])
        self.assertIn("limit=10", response.json["next_page"]["uri"])
        self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
        self.assertIn("limit=10", response.json["prev_page"]["uri"])

        response = self.app.get("/frameworks?offset=latest", status=404)
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{"description": "Invalid offset provided: latest",
              "location": "querystring", "name": "offset"}],
        )

        response = self.app.get("/frameworks?descending=1&limit=10")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], [])
        self.assertIn("descending=1", response.json["next_page"]["uri"])
        self.assertIn("limit=10", response.json["next_page"]["uri"])
        self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
        self.assertIn("limit=10", response.json["prev_page"]["uri"])


class ViewsFrameworkTest(BaseFrameworkTest):
    relative_to = os.path.dirname(__file__)

    @patch("openprocurement.framework.core.views.framework.save_framework")
    def test_view(self, mocked_save_framework):
        request = MagicMock()
        context = MagicMock()
        data = deepcopy(test_framework_data)
        framework = MagicMock()
        framework.id = data["id"]
        framework.frameworkType = "electronicCatalogue"
        framework.serialize.side_effect = [data]
        request.validated = {"framework": framework, "framework_config": {}}
        mocked_save_framework.side_effect = [True]
        view = FrameworkResource(request=request, context=context)
        res = view.post()
        self.assertTrue(res["access"]["token"])
        self.assertEqual(res["data"], data)


class ResourcesFrameworkTest(BaseFrameworkTest):
    relative_to = os.path.dirname(__file__)

    def test_isFramework(self):
        config = MagicMock()
        request = MagicMock()
        context = MagicMock()
        obj = isFramework(val="electronicCatalogue_test", config=config)
        framework_type = obj.text()
        self.assertEqual(framework_type, "frameworkType = electronicCatalogue_test")
        res_call = obj.__call__(context=context, request=request)
        self.assertFalse(res_call)
        request.framework = None
        res_call = obj.__call__(context=context, request=request)
        self.assertFalse(res_call)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FrameworksResourceTest))
    suite.addTest(unittest.makeSuite(ViewsFrameworkTest))
    suite.addTest(unittest.makeSuite(ResourcesFrameworkTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
