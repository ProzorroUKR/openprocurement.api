import unittest
from datetime import datetime
from openprocurement.tender.core.tests.base import BaseWebTest


class TenderResourceTest(BaseWebTest):
    def test_empty_listing(self):
        response = self.app.get("/tenders")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], [])
        self.assertNotIn('{\n    "', response.body.decode())
        self.assertNotIn("callback({", response.body.decode())
        self.assertEqual(response.json["next_page"]["offset"], "")
        self.assertNotIn("prev_page", response.json)

        response = self.app.get("/tenders?opt_jsonp=callback")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/javascript")
        self.assertNotIn('{\n    "', response.body.decode())
        self.assertIn("callback({", response.body.decode())

        response = self.app.get("/tenders?opt_pretty=1")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn('{\n    "', response.body.decode())
        self.assertNotIn("callback({", response.body.decode())

        response = self.app.get("/tenders?opt_jsonp=callback&opt_pretty=1")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/javascript")
        self.assertIn('{\n    "', response.body.decode())
        self.assertIn("callback({", response.body.decode())

        response = self.app.get(
            "/tenders?offset=last&descending=1&limit=10",
            status=404
        )
        self.assertEqual(
            response.json,
            {"status": "error", "errors": [
                {"location": "querystring",
                 "name": "offset",
                 "description": "Invalid offset provided: last"}]}
        )

        response = self.app.get(
            f"/tenders?offset=2015-01-01T00:00:00+02:00"
            "&descending=1&limit=10"
        )
        self.assertEqual(response.status, "200 OK")

        response = self.app.get(
            f"/tenders?offset={datetime.fromisoformat('2015-01-01T00:00:00+02:00').timestamp()}"
            "&descending=1&limit=10"
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], [])
        self.assertIn("descending=1", response.json["next_page"]["uri"])
        self.assertIn("limit=10", response.json["next_page"]["uri"])
        self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
        self.assertIn("limit=10", response.json["prev_page"]["uri"])

        response = self.app.get("/tenders?feed=changes")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], [])
        self.assertEqual(response.json["next_page"]["offset"], "")
        self.assertNotIn("prev_page", response.json)

        response = self.app.get("/tenders?feed=changes&descending=1&limit=10")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], [])
        self.assertIn("descending=1", response.json["next_page"]["uri"])
        self.assertIn("limit=10", response.json["next_page"]["uri"])
        self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
        self.assertIn("limit=10", response.json["prev_page"]["uri"])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
