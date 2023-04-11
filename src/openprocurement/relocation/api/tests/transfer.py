import os
from uuid import uuid4
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_data,
    test_tender_below_config,
)


class TransferResourceTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    initial_auth = ("Basic", ("broker", ""))

    def test_get_transfer(self):
        response = self.app.get("/transfers", status=405)
        self.assertEqual(response.status, "405 Method Not Allowed")

        response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        self.assertIn("id", transfer)

        response = self.app.get("/transfers/{}".format(transfer["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], transfer)

        response = self.app.get("/transfers/{}?opt_jsonp=callback".format(transfer["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/javascript")
        self.assertIn('callback({"data": {"', response.body.decode())

        response = self.app.get("/transfers/{}?opt_pretty=1".format(transfer["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn('{\n    "data": {\n        "', response.body.decode())

    def test_not_found(self):
        response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]

        response = self.app.get("/transfers/{}".format("1234" * 8), status=404)
        self.assertEqual(response.status, "404 Not Found")

        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker1", ""))
        response = self.app.post_json("/tenders", {"data": test_tender_below_data, "config": test_tender_below_config})
        self.assertEqual(response.status, "201 Created")
        tender = response.json["data"]
        self.app.authorization = orig_auth

        response = self.app.get("/transfers/{}".format(tender["id"]), status=404)
        self.assertEqual(response.status, "404 Not Found")

        data = {"id": uuid4().hex}
        response = self.app.post_json("/transfers", {"data": data})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        self.assertNotEqual(transfer["id"], data["id"])

        response = self.app.get("/transfers/{}".format(data["id"]), status=404)
        self.assertEqual(response.status, "404 Not Found")

        response = self.app.get("/transfers/some_id", status=404)
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "url", "name": "transfer_id"}]
        )

        response = self.app.patch_json("/transfers/some_id", {"data": {}}, status=404)
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "url", "name": "transfer_id"}]
        )

    def test_create_transfer(self):
        response = self.app.post_json("/transfers", status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [{"description": "Expecting value: line 1 column 1 (char 0)", "location": "body", "name": "data"}],
        )

        response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        transfer = response.json["data"]
        self.assertNotIn("usedFor", transfer)
        self.assertIn("token", response.json["access"])
        self.assertIn("transfer", response.json["access"])

        response = self.app.get("/transfers/{}".format(transfer["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(set(response.json["data"]), set(transfer))
        self.assertEqual(response.json["data"], transfer)

        response = self.app.post_json("/transfers?opt_jsonp=callback", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/javascript")
        self.assertIn('callback({"', response.body.decode())

        response = self.app.post_json("/transfers?opt_pretty=1", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn('{\n    "', response.body.decode())

        response = self.app.post_json("/transfers", {"data": {}, "options": {"pretty": True}})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn('{\n    "', response.body.decode())
