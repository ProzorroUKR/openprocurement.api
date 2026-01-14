from copy import deepcopy

from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
    test_tender_below_complaint,
)
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)


def create_tender_co_lot_cancellation_complaint(self):
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

    self.add_sign_doc(
        self.tender_id,
        self.tender_token,
        docs_url=f"/cancellations/{cancellation_id}/documents",
        document_type="cancellationReport",
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.json["data"]["status"], "active")  # as we don't have complaintPeriod
    self.assertNotIn("complaintPeriod", response.json["data"])

    response = self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations/{cancellation_id}/complaints?acc_token={self.tender_token}",
        {"data": test_tender_below_complaint},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint as it is forbidden by configuration"
    )

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def patch_tender_co_lot_cancellation(self):
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
