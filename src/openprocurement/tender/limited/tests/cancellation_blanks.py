# -*- coding: utf-8 -*-
from mock import patch
from datetime import timedelta
from copy import deepcopy
from openprocurement.tender.core.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_cancellation,
)


def create_tender_cancellation_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/cancellations", {"data": test_tender_below_cancellation}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

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


def create_tender_cancellation(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_tender_below_cancellation},
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
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_tender_below_cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    first_cancellation = response.json["data"]
    self.assertEqual(first_cancellation["reason"], "cancellation reason")

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_tender_below_cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    second_cancellation = response.json["data"]
    self.assertEqual(second_cancellation["reason"], "cancellation reason")

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(
                self.tender_id, second_cancellation["id"], self.tender_token
            ),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "active")
    else:
        activate_cancellation_after_2020_04_19(self, second_cancellation["id"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
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


def create_tender_cancellation_with_post(self):
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_tender_below_cancellation},
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
    self.assertEqual(response.json["data"]["status"], "active")

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    if get_now() < RELEASE_2020_04_19:
        self.assertEqual(cancellation["status"], "active")
        self.assertIn("id", cancellation)
        self.assertIn(cancellation["id"], response.headers["Location"])
    else:
        self.assertEqual(cancellation["status"], "draft")
        activate_cancellation_after_2020_04_19(self, cancellation["id"])

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def create_cancellation_on_lot(self):
    """ Try create cancellation with cancellationOf = lot while tender hasn't lots """
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": "1" * 32
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "relatedLot",
                "description": ["relatedLot should be one of lots"],
            }
        ],
    )


# TenderNegotiationCancellationResourceTest


def negotiation_create_cancellation_on_lot(self):
    """ Try create cancellation with cancellationOf = lot while tender hasn't lots """
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": "1" * 32
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["relatedLot should be one of lots"], "location": "body", "name": "relatedLot"}],
    )


# TenderNegotiationLotsCancellationResourceTest


def create_tender_lots_cancellation(self):
    lot_id = self.initial_lots[0]["id"]
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": lot_id
    })
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
    self.assertEqual(response.json["data"]["status"], "active")

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": lot_id,
        "status": "active"
    })
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

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
        "relatedLot": lot_id,
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can perform cancellation only in active lot status")

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[1]["id"],
    })
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


def cancelled_lot_without_relatedLot(self):
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "cancellationOf": "lot",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["cancellationOf"], "tender")


def delete_first_lot_second_cancel(self):
    """ One lot we delete another cancel and check tender status """
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = self.initial_lots[1]["id"]

    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": items}},
    )

    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, self.initial_lots[0]["id"], self.tender_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 1)

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[1]["id"],
    })
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


    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def cancel_tender(self):
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "tender",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    if get_now() < RELEASE_2020_04_19:
        self.assertEqual(cancellation["status"], "active")
        self.assertIn("id", cancellation)
        self.assertIn(cancellation["id"], response.headers["Location"])
    else:
        activate_cancellation_after_2020_04_19(self, cancellation["id"])

    # Check tender
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # Check lots
    response = self.app.get("/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0]["status"], "active")
    self.assertEqual(response.json["data"][1]["status"], "active")


def create_cancellation_on_tender_with_one_complete_lot(self):
    lot = self.initial_lots[0]

    # Create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "qualified": True,
                "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
                "lotID": lot["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "pending")

    # Activate award
    award = response.json["data"]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    # Sign contract
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract["value"]["valueAddedTaxIncluded"] = False
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(
            self.tender_id, contract["id"], self.tender_token
        ),
        {"data": {"status": "active", "value": contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    # Try to create cancellation on tender
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "tender",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't perform cancellation, if there is at least one complete lot"
    )


def cancellation_on_not_active_lot(self):
    lot = self.initial_lots[0]

    # Create cancellation on lot with status cancelled
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": lot["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    # check lot status
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # Try to create cancellation on lot with status cancelled
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": lot["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can perform cancellation only in active lot status")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def create_tender_cancellation_2020_04_19(self):
    reasonType_choices = self.valid_reasonType_choices
    request_path = "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token)

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        request_path,
        {"data": cancellation}
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

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[1]})
    response = self.app.post_json(
        request_path,
        {"data": cancellation}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn("date", cancellation)
    self.assertEqual(cancellation["reasonType"], reasonType_choices[1])
    self.assertEqual(cancellation["status"], "draft")
    self.assertIn(cancellation_id, response.headers["Location"])

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content")],
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    request_path = "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token)
    response = self.app.patch_json(
        request_path,
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["status"], "pending")


@patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
@patch("openprocurement.tender.core.views.cancellation.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def patch_tender_cancellation_2020_04_19(self):
    reasonType_choices = self.valid_reasonType_choices

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[0]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation}
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

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Fields reason, cancellationOf and documents must be filled for switch cancellation to pending status",
            "location": "body",
            "name": "data",
        }]
    )

    for reasonType_choice in self.valid_reasonType_choices:
        if reasonType_choice != cancellation["reasonType"]:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation['id'], self.tender_token),
                {"data": {"reasonType": reasonType_choice}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["reasonType"], reasonType_choice)

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "active"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Cancellation can't be updated from draft to active status",
            "location": "body",
            "name": "data",
        }]
    )

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content")],
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    request_path = "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id,
                                                                      self.tender_token)
    response = self.app.patch_json(
        request_path,
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "draft"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Cancellation can't be updated from pending to draft status",
            "location": "body",
            "name": "data",
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "active"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Cancellation can't be updated from pending to active status",
            "location": "body",
            "name": "data",
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": None}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Cancellation can't be updated from unsuccessful to pending status",
            "location": "body",
            "name": "data",
        }]
    )

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({"reasonType": reasonType_choices[1]})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    cancellation_id = cancellation["id"]
    self.assertEqual(cancellation["reason"], "cancellation reason")
    self.assertIn("id", cancellation)
    self.assertIn("date", cancellation)
    self.assertEqual(cancellation["reasonType"], reasonType_choices[1])
    self.assertEqual(cancellation["status"], "draft")
    self.assertIn(cancellation_id, response.headers["Location"])

    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content")],
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    cancellation = response.json["data"]
    self.assertEqual(cancellation["status"], "pending")

    with patch(
            "openprocurement.tender.core.validation.get_now",
            return_value=get_now() + timedelta(days=20)) as mock_date:
        response = self.app.patch_json(
            "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
            {"data": {"status": "active"}},
        )

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Can't perform cancellation in current (cancelled) tender status",
            "location": "body",
            "name": "data",
        }]
    )
