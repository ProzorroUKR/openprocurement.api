import os.path
from copy import deepcopy

from jsonpatch import apply_patch
from jsonpointer import resolve_pointer

from openprocurement.historical.core.constants import HASH
from openprocurement.historical.core.constants import PREVIOUS_HASH as PHASH
from openprocurement.historical.core.constants import VERSION
from openprocurement.historical.core.tests.tests import mock_doc
from openprocurement.historical.core.utils import parse_hash
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest,
    test_tender_below_config,
    test_tender_below_data,
    test_tender_below_lots,
    test_tender_below_organization,
)

test_data_with_revisions = deepcopy(mock_doc)
test_data_with_revisions["doc_type"] = "Tender"
test_data_with_revisions["config"] = test_tender_below_config


class HistoricalTenderTestCase(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super().setUp()
        self.app.authorization = ("Basic", ("brokerh", ""))
        self.create_tender()

    def _update_doc(self):
        data = test_data_with_revisions.copy()
        tender = self.mongodb.tenders.get(self.tender_id)
        data["_id"] = self.tender_id
        data["id"] = self.tender_id
        data["_rev"] = tender["_rev"]
        self.mongodb.tenders.save(data)

    def test_get_tender(self):
        response = self.app.get("/tenders")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(len(response.json["data"]), 1)

        response = self.app.post_json("/tenders", {"data": test_tender_below_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        tender = response.json["data"]
        response = self.app.get("/tenders/{}/historical".format(tender["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        result = response.json["data"]
        self.assertEqual(result, tender)

        response = self.app.get("/tenders/{}/historical?opt_jsonp=callback".format(tender["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/javascript")
        self.assertIn('callback({"data": {"', response.body.decode())
        response = self.app.get("/tenders/{}/historical?" "opt_pretty=1".format(tender["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn('{\n    "data": {\n        "', response.body.decode())
        self.assertIn(VERSION, response.headers)
        self.assertEqual(response.headers[VERSION], "1")

        # test administrator view
        self.app.authorization = ("Basic", ("administrator", ""))
        response = self.app.get("/tenders/{}/historical".format(tender["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        result = response.json["data"]
        self.assertEqual(result, tender)

        # test forbidden
        self.app.authorization = ("Basic", ("", ""))
        response = self.app.get("/tenders/{}".format(tender["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        result = response.json["data"]
        self.assertEqual(result, tender)

        response = self.app.get("/tenders/{}/historical".format(tender["id"]), status=403)
        self.assertEqual(response.status, "403 Forbidden")

    def test_get_tender_invalid_header(self):
        for header in ["invalid", "1.5", "-1", "10000", "0"]:
            response = self.app.get(
                "/tenders/{}/historical".format(self.tender_id), headers={VERSION: header}, status=404
            )
            self.assertEqual(response.status, "404 Not Found")
            self.assertEqual(response.json["status"], "error")
            self.assertEqual(
                response.json["errors"], [{"description": "Not Found", "location": "header", "name": "version"}]
            )

    def test_get_tender_versioned(self):
        response = self.app.get("/tenders")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(len(response.json["data"]), 1)

        response = self.app.post_json("/tenders", {"data": test_tender_below_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        tender = response.json["data"]
        self.tender_id = tender["id"]
        self._update_doc()
        doc = test_data_with_revisions.copy()
        revisions = doc.pop("revisions")
        for i, rev in list(enumerate(revisions))[1:]:
            path = "/tenders/{}/historical".format(self.tender_id)
            response = self.app.get(path, headers={VERSION: str(i)})
            tender = response.json["data"]
            headers = response.headers
            self.assertEqual(headers[HASH], parse_hash(rev["rev"]))
            self.assertEqual(headers[VERSION], str(i))
            self.assertEqual(headers[PHASH], parse_hash(revisions[i - 1].get("rev", "")))
            for ch in list(rev["changes"]):
                val = ch["value"] if ch["op"] != "remove" else "missing"
                if not all(p for p in ["next_check", "shouldStartAfter"] if ch["path"] in p):
                    self.assertEqual(resolve_pointer(tender, ch["path"], "missing"), val)
                if rev["author"] != "chronograph":
                    if any("bids" in c["path"] for c in rev["changes"]):
                        self.assertNotEqual(tender["dateModified"], rev["date"])

    def test_doc_type_mismatch(self):
        doc = self.mongodb.tenders.get(self.tender_id)
        doc["doc_type"] = "invalid"
        self.mongodb.tenders.save(doc)
        response = self.app.get("/tenders/{}/historical".format(self.tender_id))
        self.assertEqual(response.status, "200 OK")

    def test_get_doc_invalid_hash(self):
        self._update_doc()
        response = self.app.get("/tenders/{}/historical".format(self.tender_id), headers={VERSION: str(3)})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        response = self.app.get(
            "/tenders/{}/historical".format(self.tender_id), headers={VERSION: str(3), HASH: "invalid"}, status=404
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "header", "name": "hash"}])

    def test_get_tender_equal_with_api(self):
        data = test_data_with_revisions.copy()
        revisions = data.pop("revisions")
        tenders = []
        for p in reversed(revisions):
            data = apply_patch(data, p["changes"])
            tenders.append(data.copy())

        for tender in reversed(tenders[:-1]):
            db_tender = self.mongodb.tenders.get(self.tender_id)
            tender["id"] = tender["_id"] = db_tender["_id"]
            tender["_rev"] = db_tender["_rev"]

            self.mongodb.tenders.save(tender)
            response = self.app.get("/tenders/{}/historical".format(self.tender_id))
            historical_tender = response.json["data"]
            response = self.app.get("/tenders/{}".format(self.tender_id))
            tender = response.json["data"]
            self.assertEqual(historical_tender, tender)

    # def test_route_not_find(self):
    #     routelist = [r for r in self.app.app.routes_mapper.routelist if r.name != "belowThreshold:Tender"]
    #     with patch.object(self.app.app.routes_mapper, "routelist", routelist):
    #         response = self.app.get("/tenders/{}/historical".format(self.tender_id), status=404)
    #         self.assertEqual(response.status, "404 Not Found")
    #         self.assertEqual(
    #             response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    #         )

    def test_json_patch_error(self):
        self._update_doc()
        db_tender = self.mongodb.tenders.get(self.tender_id)
        for rev in db_tender["revisions"]:
            rev["changes"] = [{"path": "/skjddkfjsdkjfdsjk", "op": "remove"}]
        self.mongodb.tenders.save(db_tender)

        resp = self.app.get("/tenders/{}/historical".format(self.tender_id), headers={VERSION: "11"}, status=501)
        self.assertEqual(resp.status, "501 Not Implemented")
        self.assertEqual(resp.json["status"], "error")
        self.assertEqual(
            resp.json["errors"], [{"description": "Not Implemented", "location": "body", "name": "revision"}]
        )


class TestGetHistoricalData(BaseTenderWebTest):
    initial_data = test_tender_below_data
    initial_lots = test_tender_below_lots
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super().setUp()
        self.app.authorization = ("Basic", ("brokerh", ""))
        self.create_tender()

    def test_get_historical_data(self):
        response = self.app.get("/tenders")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(len(response.json["data"]), 1)

        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

        tender = response.json["data"]

        enquiries_historical = self.app.get("/tenders/{}/historical".format(tender["id"]))
        self.assertEqual(enquiries_historical.status, "200 OK")
        self.assertEqual(enquiries_historical.content_type, "application/json")
        enquiries = self.app.get("/tenders/{}".format(tender["id"]))
        self.assertEqual(enquiries.status, "200 OK")
        self.assertEqual(enquiries.content_type, "application/json")
        enquiries_historical = enquiries_historical.json["data"]
        enquiries = enquiries.json["data"]
        self.assertEqual(enquiries_historical, enquiries)

        self.app.authorization = ("Basic", ("administrator", ""))
        response = self.set_status("active.tendering")

        tender = response.json["data"]

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token), {"data": {"title": "hello"}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.app.authorization = ("Basic", ("brokerh", ""))

        tendering_historical = self.app.get("/tenders/{}/historical".format(tender["id"]))
        self.assertEqual(tendering_historical.status, "200 OK")
        self.assertEqual(tendering_historical.content_type, "application/json")
        tendering = self.app.get("/tenders/{}".format(tender["id"]))
        self.assertEqual(tendering.status, "200 OK")
        self.assertEqual(tendering.content_type, "application/json")
        tendering_historical = tendering_historical.json["data"]
        tendering = tendering.json["data"]
        self.assertEqual(tendering_historical, tendering)

        response = self.app.post_json(
            "/tenders/{}/bids".format(tender["id"]),
            {
                "data": {
                    "lotValues": [{"value": {"amount": 499}, "relatedLot": self.initial_lots[0]["id"]}],
                    "tenderers": [test_tender_below_organization],
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

        tendering_historical = self.app.get("/tenders/{}/historical".format(tender["id"]))
        self.assertEqual(tendering_historical.status, "200 OK")
        self.assertEqual(tendering_historical.content_type, "application/json")
        tendering = self.app.get("/tenders/{}".format(tender["id"]))
        self.assertEqual(tendering.status, "200 OK")
        self.assertEqual(tendering.content_type, "application/json")
        tendering_historical = tendering_historical.json["data"]
        tendering = tendering.json["data"]
        self.assertEqual(tendering_historical, tendering)

        self.app.authorization = ("Basic", ("administrator", ""))
        response = self.set_status("active.auction")

        tender = response.json["data"]

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token), {"data": {"title": "hello again"}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.app.authorization = ("Basic", ("brokerh", ""))

        auction_historical = self.app.get("/tenders/{}/historical".format(tender["id"]))
        self.assertEqual(auction_historical.status, "200 OK")
        self.assertEqual(auction_historical.content_type, "application/json")

        auction = self.app.get("/tenders/{}".format(tender["id"]))
        self.assertEqual(auction.status, "200 OK")
        self.assertEqual(auction.content_type, "application/json")
        auction_historical = auction_historical.json["data"]
        auction = auction.json["data"]
        self.assertEqual(auction_historical, auction)

        self.app.authorization = ("Basic", ("administrator", ""))
        response = self.set_status("active.qualification")

        tender = response.json["data"]

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token), {"data": {"title": "hello third"}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.app.authorization = ("Basic", ("brokerh", ""))

        qualification_historical = self.app.get("/tenders/{}/historical".format(tender["id"]))
        self.assertEqual(qualification_historical.status, "200 OK")
        self.assertEqual(qualification_historical.content_type, "application/json")

        qualification = self.app.get("/tenders/{}".format(tender["id"]))
        self.assertEqual(qualification.status, "200 OK")
        self.assertEqual(qualification.content_type, "application/json")
        self.assertEqual(qualification_historical.json["data"]["bids"], qualification.json["data"]["bids"])
        qualification_historical = qualification_historical.json["data"]
        qualification = qualification.json["data"]

        self.assertEqual(qualification_historical, qualification)

        self.app.authorization = ("Basic", ("administrator", ""))
        response = self.set_status("active.awarded")

        tender = response.json["data"]

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token), {"data": {"title": "hello, I said"}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.app.authorization = ("Basic", ("brokerh", ""))

        awarded_historical = self.app.get("/tenders/{}/historical".format(tender["id"]))
        self.assertEqual(awarded_historical.status, "200 OK")
        self.assertEqual(awarded_historical.content_type, "application/json")

        awarded = self.app.get("/tenders/{}".format(tender["id"]))
        self.assertEqual(awarded.status, "200 OK")
        self.assertEqual(awarded.content_type, "application/json")
        self.assertEqual(awarded_historical.json["data"]["bids"], awarded.json["data"]["bids"])
        awarded_historical = awarded_historical.json["data"]
        awarded = awarded.json["data"]

        self.assertEqual(awarded_historical, awarded)

        self.app.authorization = ("Basic", ("administrator", ""))
        response = self.set_status("complete")

        tender = response.json["data"]

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token),
            {"data": {"title": "I dunno what this test is about I just change thing and it works"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.app.authorization = ("Basic", ("brokerh", ""))

        complete_historical = self.app.get("/tenders/{}/historical".format(tender["id"]))
        self.assertEqual(complete_historical.status, "200 OK")
        self.assertEqual(complete_historical.content_type, "application/json")

        complete = self.app.get("/tenders/{}".format(tender["id"]))
        self.assertEqual(complete.status, "200 OK")
        self.assertEqual(complete.content_type, "application/json")
        complete_historical_bids = complete_historical.json["data"]["bids"]
        self.assertEqual(complete_historical_bids, complete.json["data"]["bids"])
        complete_historical = complete_historical.json["data"]
        complete = complete.json["data"]

        self.assertEqual(complete_historical, complete)

        response = self.app.get("/tenders/{}/historical".format(tender["id"]), headers={VERSION: "7"})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(complete_historical_bids, response.json["data"]["bids"])
        data = response.json["data"]
        self.assertEqual(complete_historical, data)

        response = self.app.get("/tenders/{}/historical".format(tender["id"]), headers={VERSION: "100"}, status=404)
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "header", "name": "version"}]
        )
