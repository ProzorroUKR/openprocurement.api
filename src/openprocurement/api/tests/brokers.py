from openprocurement.api.tests.base import BaseWebTest


class BrokersTestBase(BaseWebTest):
    def test_brokers_view(self):
        response = self.app.get("/brokers", status=200)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.assertEqual(len(response.json["data"]), 15)

        response = self.app.get("/brokers?levels=6", status=200)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.assertEqual(len(response.json["data"]), 1)
        self.assertIn(6, response.json["data"][0]["levels"])
