from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
)
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)


def create_tender_cancellation_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/cancellations", {"data": test_tender_below_cancellation}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    request_path = "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token)

    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Content-Type header should be one of ['application/json']",
                "location": "header",
                "name": "Content-Type",
            }
        ],
    )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Expecting value: line 1 column 1 (char 0)", "location": "body", "name": "data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "reason"}],
    )

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["cancellationOf"], "tender", "Because relatedLot is not provided")

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": "0" * 32,
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["relatedLot should be one of lots"], "location": "body", "name": "relatedLot"}],
    )


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def create_tender_cancellation(self):
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.pop("reasonType", None)

    request_path = "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token)
    response = self.app.post_json(request_path, {"data": cancellation})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn("date", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    cancellation.update({"status": "active"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertEqual(cancellation["status"], "active")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertNotIn("bids", response.json["data"])

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"reason": "cancellation reason"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (cancelled) tender status"
    )


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def create_tender_cancellation_before_19_04_2020(self):
    request_path = "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token)
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": "noDemand"})
    response = self.app.post_json(
        request_path,
        {"data": cancellation},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ['Rogue field'],
                "location": "body",
                "name": "reasonType",
            }
        ],
    )


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def patch_tender_cancellation(self):
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.pop("reasonType", None)

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertNotIn("bids", response.json["data"])

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (cancelled) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/some_id".format(self.tender_id), {"data": {"status": "active"}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "cancellation_id"}]
    )

    response = self.app.patch_json("/tenders/some_id/cancellations/some_id", {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["reason"], "cancellation reason")


def get_tender_cancellation(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_tender_below_cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], cancellation)

    response = self.app.get("/tenders/{}/cancellations/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "cancellation_id"}]
    )

    response = self.app.get("/tenders/some_id/cancellations/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


def get_tender_cancellation_data_for_sign(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_tender_below_cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]

    response = self.app.get("/tenders/{}/cancellations/{}?opt_context=1".format(self.tender_id, cancellation_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(["data", "context"], list(response.json.keys()))
    self.assertEqual(response.json["data"]["reason"], "cancellation reason")
    self.assertIn("tender", response.json["context"])
    self.assertEqual(response.json["context"]["tender"]["status"], "active.tendering")


def get_tender_cancellations(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_tender_below_cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]

    response = self.app.get("/tenders/{}/cancellations".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], cancellation)

    response = self.app.get("/tenders/some_id/cancellations", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


# TenderLotCancellationResourceTest


def create_tender_lot_cancellation(self):
    lot_id = self.initial_lots[0]["id"]
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": lot_id,
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(cancellation["status"], "pending")
    else:
        self.assertEqual(cancellation["status"], "draft")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "active")
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"cancellationOf": "lot", "relatedLot": lot_id, "status": "active"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(cancellation["status"], "active")
    else:
        self.assertNotEqual(cancellation["status"], "active")
        activate_cancellation_after_2020_04_19(self, cancellation["id"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "cancelled")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_tender_below_cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (cancelled) tender status"
    )


def patch_tender_lot_cancellation(self):
    lot_id = self.initial_lots[0]["id"]
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": lot_id,
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]

    if RELEASE_2020_04_19 > get_now():
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "active")
    else:
        activate_cancellation_after_2020_04_19(self, cancellation["id"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "cancelled")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (cancelled) tender status"
    )

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["reason"], "cancellation reason")


# TenderLotsCancellationResourceTest


def create_tender_lots_cancellation(self):
    lot_id = self.initial_lots[0]["id"]
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": lot_id,
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "active")
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": lot_id,
            "status": "active",
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(cancellation["status"], "active")
    else:
        activate_cancellation_after_2020_04_19(self, cancellation["id"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "cancelled")
    self.assertNotEqual(response.json["data"]["status"], "cancelled")

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"cancellationOf": "lot", "relatedLot": lot_id, "status": "active"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can perform cancellation only in active lot status")

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": self.initial_lots[1]["id"],
            "status": "active",
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn(cancellation["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(cancellation["status"], "active")
    else:
        activate_cancellation_after_2020_04_19(self, cancellation["id"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "cancelled")
    self.assertEqual(response.json["data"]["lots"][1]["status"], "cancelled")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def patch_tender_lots_cancellation(self):
    lot_id = self.initial_lots[0]["id"]
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": lot_id,
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]

    if RELEASE_2020_04_19 > get_now():
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "active")
    else:
        activate_cancellation_after_2020_04_19(self, cancellation["id"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lots"][0]["status"], "cancelled")
    self.assertNotEqual(response.json["data"]["status"], "cancelled")

    if RELEASE_2020_04_19 > get_now():
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation["id"], self.tender_token),
            {"data": {"status": "pending"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can perform cancellation only in active lot status"
        )

    response = self.app.get("/tenders/{}/cancellations/{}".format(self.tender_id, cancellation["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["reason"], "cancellation reason")


# TenderCancellationDocumentResourceTest


def not_found(self):
    response = self.app.post_json(
        "/tenders/some_id/cancellations/some_id/documents",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.post_json(
        "/tenders/{}/cancellations/some_id/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "cancellation_id"}]
    )

    response = self.app.get("/tenders/some_id/cancellations/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/{}/cancellations/some_id/documents".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "cancellation_id"}]
    )

    response = self.app.get("/tenders/some_id/cancellations/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/{}/cancellations/some_id/documents/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "cancellation_id"}]
    )

    response = self.app.get(
        "/tenders/{}/cancellations/{}/documents/some_id".format(self.tender_id, self.cancellation_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])

    response = self.app.put_json(
        "/tenders/some_id/cancellations/some_id/documents/some_id",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.put_json(
        "/tenders/{}/cancellations/some_id/documents/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "cancellation_id"}]
    )


def create_tender_cancellation_document(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    key = self.get_doc_id_from_url(response.json["data"]["url"])
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.get(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/cancellations/{}/documents?all=true".format(self.tender_id, self.cancellation_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/cancellations/{}/documents/{}?download=some_id".format(
            self.tender_id, self.cancellation_id, doc_id
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}])

    response = self.app.get(
        "/tenders/{}/cancellations/{}/documents/{}?download={}".format(
            self.tender_id, self.cancellation_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    response = self.app.get(
        "/tenders/{}/cancellations/{}/documents/{}".format(self.tender_id, self.cancellation_id, doc_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (complete) tender status"
    )


def put_tender_cancellation_document(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put_json(
        "/tenders/{}/cancellations/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/cancellations/{}/documents/{}?download={}".format(
            self.tender_id, self.cancellation_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    response = self.app.get(
        "/tenders/{}/cancellations/{}/documents/{}".format(self.tender_id, self.cancellation_id, doc_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put_json(
        "/tenders/{}/cancellations/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/cancellations/{}/documents/{}?download={}".format(
            self.tender_id, self.cancellation_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    self.set_status("complete")

    response = self.app.put_json(
        "/tenders/{}/cancellations/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (complete) tender status"
    )


def patch_tender_cancellation_document(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, self.cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/tenders/{}/cancellations/{}/documents/{}".format(self.tender_id, self.cancellation_id, doc_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (complete) tender status"
    )


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def patch_tender_cancellation_2020_04_19(self):
    reasonType_choices = self.valid_reasonType_choices

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn("date", cancellation)
    self.assertEqual(cancellation["status"], "draft")
    self.assertEqual(cancellation["reasonType"], reasonType_choices[0])
    self.assertIn(cancellation_id, response.headers["Location"])

    for reasonType_choice in self.valid_reasonType_choices:
        if reasonType_choice != cancellation["reasonType"]:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(
                    self.tender_id, cancellation['id'], self.tender_token
                ),
                {"data": {"reasonType": reasonType_choice}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["reasonType"], reasonType_choice)

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Fields reason, cancellationOf and documents must be filled for switch cancellation to active status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "active"}},
        status=422,
    )

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update cancellation in current (unsuccessful) status"
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "draft"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update cancellation in current (unsuccessful) status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn("date", cancellation)
    self.assertEqual(cancellation["reasonType"], reasonType_choices[0])
    self.assertEqual(cancellation["status"], "draft")
    self.assertIn(cancellation_id, response.headers["Location"])

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "draft"}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't perform cancellation in current (cancelled) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )


@patch("openprocurement.tender.core.procedure.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def permission_cancellation_pending(self):
    reasonType_choices = self.valid_reasonType_choices

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_1 = response.json["data"]
    cancellation_1_id = cancellation_1["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation_1)
    self.assertIn("date", cancellation_1)
    self.assertEqual(cancellation_1["status"], "draft")
    self.assertEqual(cancellation_1["reasonType"], reasonType_choices[0])
    self.assertIn(cancellation_1_id, response.headers["Location"])

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_2 = response.json["data"]
    cancellation_2_id = cancellation_2["id"]
    self.assertEqual(cancellation_2["reason"], "cancellation reason")
    self.assertEqual(cancellation_2["status"], "draft")

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_1_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_1_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (cancelled) tender status"
    )

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_2_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (cancelled) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_2_id, self.tender_token),
        {"data": {"reasonType": reasonType_choices[1]}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation in current (cancelled) tender status"
    )


def tender_lot_cancellation_universal_logic(self):
    cancellation_data = deepcopy(test_tender_below_cancellation)
    cancellation_data["reasonType"] = "noDemand"

    cancellation_lot_data = deepcopy(cancellation_data)
    lot = self.initial_lots[0]

    cancellation_lot_data["relatedLot"] = lot["id"]
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation_lot_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]

    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.json["data"]["status"], "active")  # as we don't have complaintPeriod
    self.assertNotIn("complaintPeriod", response.json["data"])

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")
