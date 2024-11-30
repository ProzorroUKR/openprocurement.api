import unittest
from datetime import datetime, timedelta, timezone

from bson import Timestamp

from openprocurement.api.context import set_now
from openprocurement.tender.core.tests.base import BaseWebTest


class TenderEmptyResourceTest(BaseWebTest):
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

        response = self.app.get("/tenders?offset=last&descending=1&limit=10", status=404)
        self.assertEqual(
            response.json,
            {
                "status": "error",
                "errors": [
                    {"location": "querystring", "name": "offset", "description": "Invalid offset provided: last"}
                ],
            },
        )

        response = self.app.get("/tenders?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10")
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


class TenderResourceListingTest(BaseWebTest):

    def create_items_without_duplicates(self, now: datetime):
        before = now - timedelta(seconds=1)
        after = now + timedelta(seconds=1)
        now_seconds = int(now.timestamp())
        before_seconds = int(before.timestamp())
        after_seconds = int(after.timestamp())
        documents = [
            {
                "id": "11111111111111111111111111111111",
                "dateModified": before.isoformat(),
                "public_ts": Timestamp(before_seconds, 5),
            },
            {
                "id": "22222222222222222222222222222222",
                "dateModified": before.isoformat(),
                "public_ts": Timestamp(before_seconds, 7),
            },
            {
                "id": "33333333333333333333333333333333",
                "dateModified": now.isoformat(),
                "public_ts": Timestamp(now_seconds, 1),
            },
            {
                "id": "44444444444444444444444444444444",
                "dateModified": now.isoformat(),
                "public_ts": Timestamp(now_seconds, 2),
            },
            {
                "id": "55555555555555555555555555555555",
                "dateModified": after.isoformat(),
                "public_ts": Timestamp(after_seconds, 1),
            },
            {
                "id": "66666666666666666666666666666666",
                "dateModified": after.isoformat(),
                "public_ts": Timestamp(after_seconds, 2),
            },
        ]
        for doc in documents:
            self.mongodb.tenders.save(doc, insert=True, modified=False)

    def create_items_with_offset_duplicates(self, now: datetime):
        timestamp_seconds = int(now.timestamp())
        documents = [
            {
                "id": "11111111111111111111111111111111",
                "dateModified": now.isoformat(),
                "public_ts": Timestamp(timestamp_seconds, 1),
                "public_modified": float(f"{timestamp_seconds}.1"),
            },
            {
                "id": "22222222222222222222222222222222",
                "dateModified": now.isoformat(),
                "public_ts": Timestamp(timestamp_seconds, 2),
                "public_modified": float(f"{timestamp_seconds}.2"),
            },
            {
                "id": "33333333333333333333333333333333",
                "dateModified": now.isoformat(),
                "public_ts": Timestamp(timestamp_seconds, 3),  # duplicate
                "public_modified": float(f"{timestamp_seconds}.301"),
            },
            {
                "id": "44444444444444444444444444444444",
                "dateModified": now.isoformat(),
                "public_ts": Timestamp(timestamp_seconds, 3),  # duplicate
                "public_modified": float(f"{timestamp_seconds}.301"),
            },
            {
                "id": "55555555555555555555555555555555",
                "dateModified": now.isoformat(),
                "public_ts": Timestamp(timestamp_seconds, 3),  # duplicate
                "public_modified": float(f"{timestamp_seconds}.302"),  # not a duplicate by public_modified
            },
            {
                "id": "66666666666666666666666666666666",
                "dateModified": now.isoformat(),
                "public_ts": Timestamp(timestamp_seconds, 4),
                "public_modified": float(f"{timestamp_seconds}.4"),
            },
        ]
        for doc in documents:
            self.mongodb.tenders.save(doc, insert=True, modified=False)

    def test_duplicates_limit_six(self):
        now = datetime.now(tz=timezone.utc)
        set_now(now)
        timestamp_seconds = int(now.timestamp())

        self.create_items_with_offset_duplicates(now=now)

        # check there are 6 elements, the last offset is 4
        response = self.app.get("/tenders")
        result = response.json

        # {timestamp_seconds}.0000000004.1.08d53ef3e1e6b551a60fcd51e1e05f52
        assert result["next_page"]["offset"].startswith(f"{timestamp_seconds}.0000000004.1")
        assert len(result["data"]) == 6

    def test_duplicates_limit_3(self):
        now = datetime.now(tz=timezone.utc)
        set_now(now)
        timestamp_seconds = int(now.timestamp())

        self.create_items_with_offset_duplicates(now=now)

        limit = 3
        response = self.app.get(f"/tenders?limit={limit}")
        result = response.json
        offset = result["next_page"]["offset"]  # {timestamp_seconds}.0000000003.1.a30e23570cc3ba91f31c8e0caae48cb9
        assert offset.startswith(f"{timestamp_seconds}.0000000003.1")
        assert len(result["data"]) == 3
        expected_ids = {
            "11111111111111111111111111111111",
            "22222222222222222222222222222222",
            "33333333333333333333333333333333",  # can be 444.. or 555..  (they have the same public_ts)
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        response = self.app.get(f"/tenders?offset={offset}&limit={limit}")
        result = response.json
        offset = result["next_page"]["offset"]  # 1732457721.0000000004.1.08d53ef3e1e6b551a60fcd51e1e05f52
        assert len(result["data"]) == 4
        expected_ids = {
            "33333333333333333333333333333333",  # timestamp duplicate
            "44444444444444444444444444444444",  # timestamp duplicate
            "55555555555555555555555555555555",  # timestamp duplicate
            "66666666666666666666666666666666",
        }
        assert {i["id"] for i in result["data"]} == expected_ids
        assert offset.startswith(f"{timestamp_seconds}.0000000004.1")

    def test_duplicates_limit_2(self):
        limit = 2
        now = datetime.now(tz=timezone.utc)
        set_now(now)
        timestamp_seconds = int(now.timestamp())

        self.create_items_with_offset_duplicates(now=now)

        response = self.app.get(f"/tenders?limit={limit}")
        result = response.json
        offset = result["next_page"]["offset"]
        assert offset.startswith(f"{timestamp_seconds}.0000000002.1")
        assert len(result["data"]) == 2
        expected_ids = {
            "11111111111111111111111111111111",
            "22222222222222222222222222222222",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        response = self.app.get(f"/tenders?offset={offset}&limit={limit}")
        result = response.json
        offset = result["next_page"]["offset"]
        assert len(result["data"]) == 2, result
        expected_ids = {
            "33333333333333333333333333333333",  # timestamp duplicate
            "44444444444444444444444444444444",  # timestamp duplicate
        }
        assert {i["id"] for i in result["data"]} == expected_ids
        assert offset.startswith(f"{timestamp_seconds}.0000000003.2")

        response = self.app.get(f"/tenders?offset={offset}&limit={limit}")
        result = response.json
        offset = result["next_page"]["offset"]
        assert len(result["data"]) == 4, result
        expected_ids = {
            "33333333333333333333333333333333",  # timestamp duplicate
            "44444444444444444444444444444444",  # timestamp duplicate
            "55555555555555555555555555555555",  # timestamp duplicate
            "66666666666666666666666666666666",
        }
        assert {i["id"] for i in result["data"]} == expected_ids
        assert offset.startswith(f"{timestamp_seconds}.0000000004.1")

    def test_duplicates_limit_2_backwards(self):
        descending = 1
        limit = 2
        now = datetime.now(tz=timezone.utc)
        set_now(now)

        self.create_items_with_offset_duplicates(now=now)

        response = self.app.get(f"/tenders?limit={limit}&descending={descending}")
        result = response.json
        assert len(result["data"]) == 2
        assert result["data"][0]["id"] == "66666666666666666666666666666666"
        # first element can be any of the duplicates
        assert result["data"][1]["id"] in (
            "33333333333333333333333333333333",
            "44444444444444444444444444444444",
            "55555555555555555555555555555555",
        )

        offset = result["next_page"]["offset"]

        response = self.app.get(f"/tenders?offset={offset}&limit={limit}&descending={descending}")
        result = response.json
        assert len(result["data"]) == 3, result
        expected_ids = {
            "33333333333333333333333333333333",  # timestamp duplicate
            "44444444444444444444444444444444",  # timestamp duplicate
            "55555555555555555555555555555555",  # timestamp duplicate
        }
        assert {i["id"] for i in result["data"]} == expected_ids
        offset = result["next_page"]["offset"]

        response = self.app.get(f"/tenders?offset={offset}&limit={limit}&descending={descending}")
        result = response.json

        assert len(result["data"]) == 2, result
        expected_ids = {
            "22222222222222222222222222222222",
            "11111111111111111111111111111111",
        }
        assert {i["id"] for i in result["data"]} == expected_ids
        offset = result["next_page"]["offset"]

        response = self.app.get(f"/tenders?offset={offset}&limit={limit}&descending={descending}")
        result = response.json
        assert len(result["data"]) == 0, result
        assert offset == result["next_page"]["offset"]

    def test_duplicates_limit_4_items_offset_items_disappear(self):
        now = datetime.now(tz=timezone.utc)
        set_now(now)
        timestamp_seconds = int(now.timestamp())

        self.create_items_with_offset_duplicates(now=now)

        limit = 4
        response = self.app.get(f"/tenders?limit={limit}")
        result = response.json
        offset = result["next_page"]["offset"]
        assert offset.startswith(f"{timestamp_seconds}.0000000003.2")
        assert len(result["data"]) == 4
        expected_ids = {
            "11111111111111111111111111111111",
            "22222222222222222222222222222222",
            "33333333333333333333333333333333",
            "44444444444444444444444444444444",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        # update document 44444444444444444444444444444444
        tender = self.mongodb.tenders.get("44444444444444444444444444444444")
        tender["public_ts"] = Timestamp(timestamp_seconds, 6)
        self.mongodb.tenders.save(tender, modified=False)

        # get next page
        response = self.app.get(f"/tenders?offset={offset}&limit={limit}")
        result = response.json
        offset = result["next_page"]["offset"]
        assert len(result["data"]) == 4
        expected_ids = {
            "33333333333333333333333333333333",  # duplicate is shown
            "55555555555555555555555555555555",  # duplicate is shown
            "66666666666666666666666666666666",
            "44444444444444444444444444444444",  # now it in the end of the list
        }
        assert {i["id"] for i in result["data"]} == expected_ids
        assert offset.startswith(f"{timestamp_seconds}.0000000006.1")

    def test_duplicates_start_with_depr_offset_limit_3(self):
        now = datetime.now(tz=timezone.utc)
        set_now(now)
        timestamp_seconds = int(now.timestamp())

        self.create_items_with_offset_duplicates(now=now)

        limit = 3
        offset = f"{timestamp_seconds}.0000000002"
        response = self.app.get(f"/tenders?limit={limit}&offset={offset}")
        result = response.json

        assert len(result["data"]) == 3
        expected_ids = {
            "33333333333333333333333333333333",
            "44444444444444444444444444444444",
            "55555555555555555555555555555555",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        # get next page
        offset = result["next_page"]["offset"]
        response = self.app.get(f"/tenders?offset={offset}&limit={limit}")
        result = response.json

        offset = result["next_page"]["offset"]
        assert len(result["data"]) == 1
        expected_ids = {
            "66666666666666666666666666666666",
        }
        assert {i["id"] for i in result["data"]} == expected_ids
        assert offset.startswith(f"{timestamp_seconds}.0000000004.1")

    def test_duplicates_start_with_depr_offset_limit_2(self):
        now = datetime.now(tz=timezone.utc)
        set_now(now)
        timestamp_seconds = int(now.timestamp())

        self.create_items_with_offset_duplicates(now=now)

        limit = 2
        offset = f"{timestamp_seconds}.0000000002"
        response = self.app.get(f"/tenders?limit={limit}&offset={offset}")
        result = response.json

        assert len(result["data"]) == 2
        # all three have the same offset, so the order is not guaranteed
        expected_ids = {
            "33333333333333333333333333333333",
            "44444444444444444444444444444444",
            "55555555555555555555555555555555",
        }
        assert result["data"][0]["id"] in expected_ids
        assert result["data"][1]["id"] in expected_ids

        offset = result["next_page"]["offset"]
        assert offset.startswith(f"{timestamp_seconds}.0000000003.2")

        # get next page
        response = self.app.get(f"/tenders?offset={offset}&limit={limit}")
        result = response.json

        # the two duplicates that we've seen before + the last duplicate + the last one item
        assert len(result["data"]) == 4
        expected_ids = {
            "33333333333333333333333333333333",
            "44444444444444444444444444444444",
            "55555555555555555555555555555555",
            "66666666666666666666666666666666",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        offset = result["next_page"]["offset"]
        assert offset.startswith(f"{timestamp_seconds}.0000000004.1")

    def test_duplicates_float_offset_limit_2(self):
        now = datetime.now(tz=timezone.utc)
        set_now(now)
        timestamp_seconds = int(now.timestamp())

        self.create_items_with_offset_duplicates(now=now)

        limit = 2
        offset = f"{timestamp_seconds}.1"
        response = self.app.get(f"/tenders?limit={limit}&offset={offset}")
        result = response.json

        assert len(result["data"]) == 2
        # all three have the same offset, so the order is not guaranteed
        expected_ids = {
            "22222222222222222222222222222222",
            "33333333333333333333333333333333",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        offset = result["next_page"]["offset"]
        assert offset.startswith(f"{timestamp_seconds}.0000000003.1")

    def test_duplicates_float_offset_skip_duplicates(self):
        now = datetime.now(tz=timezone.utc)
        set_now(now)
        timestamp_seconds = int(now.timestamp())

        self.create_items_with_offset_duplicates(now=now)

        limit = 4
        offset = f"{timestamp_seconds}.301"
        response = self.app.get(f"/tenders?limit={limit}&offset={offset}")
        result = response.json

        assert len(result["data"]) == 2
        # all three have the same offset, so the order is not guaranteed
        expected_ids = {
            "55555555555555555555555555555555",
            "66666666666666666666666666666666",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        offset = result["next_page"]["offset"]
        assert offset.startswith(f"{timestamp_seconds}.0000000004.1")

    def test_without_duplicates_forward(self):
        now = datetime.now(tz=timezone.utc)
        set_now(now)
        self.create_items_without_duplicates(now=now)

        limit = 2
        response = self.app.get(f"/tenders?limit={limit}")
        result = response.json
        assert len(result["data"]) == 2
        expected_ids = {
            "11111111111111111111111111111111",
            "22222222222222222222222222222222",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        offset = result["next_page"]["offset"]
        response = self.app.get(f"/tenders?offset={offset}&limit={limit}")
        result = response.json
        assert len(result["data"]) == 2
        expected_ids = {
            "33333333333333333333333333333333",
            "44444444444444444444444444444444",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        offset = result["next_page"]["offset"]
        response = self.app.get(f"/tenders?offset={offset}&limit={limit}")
        result = response.json
        assert len(result["data"]) == 2
        expected_ids = {
            "55555555555555555555555555555555",
            "66666666666666666666666666666666",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        offset = result["next_page"]["offset"]
        response = self.app.get(f"/tenders?offset={offset}&limit={limit}")
        result = response.json
        assert len(result["data"]) == 0
        next_offset = result["next_page"]["offset"]
        assert next_offset == offset

    def test_without_duplicates_backward(self):
        now = datetime.now(tz=timezone.utc)
        set_now(now)
        self.create_items_without_duplicates(now=now)

        limit = 2
        descending = 1
        response = self.app.get(f"/tenders?limit={limit}&descending={descending}")
        result = response.json
        assert len(result["data"]) == 2
        expected_ids = {
            "55555555555555555555555555555555",
            "66666666666666666666666666666666",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        offset = result["next_page"]["offset"]
        response = self.app.get(f"/tenders?offset={offset}&limit={limit}&descending={descending}")
        result = response.json
        assert len(result["data"]) == 2
        expected_ids = {
            "33333333333333333333333333333333",
            "44444444444444444444444444444444",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        offset = result["next_page"]["offset"]
        response = self.app.get(f"/tenders?offset={offset}&limit={limit}&descending={descending}")
        result = response.json
        assert len(result["data"]) == 2
        expected_ids = {
            "11111111111111111111111111111111",
            "22222222222222222222222222222222",
        }
        assert {i["id"] for i in result["data"]} == expected_ids

        offset = result["next_page"]["offset"]
        response = self.app.get(f"/tenders?offset={offset}&limit={limit}&descending={descending}")
        result = response.json
        assert len(result["data"]) == 0
        next_offset = result["next_page"]["offset"]
        assert next_offset == offset


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEmptyResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderResourceListingTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
