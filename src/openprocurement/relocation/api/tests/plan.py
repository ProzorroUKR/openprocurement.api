import os
from copy import deepcopy
from openprocurement.relocation.api.models import Transfer
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.planning.api.tests.base import test_plan_data
from openprocurement.tender.core.tests.utils import change_auth


class BasePlanOwnershipChangeTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_plan_data
    first_owner = "brokerx"
    initial_auth = ("Basic", (first_owner, ""))

    def setUp(self):
        super(BasePlanOwnershipChangeTest, self).setUp()
        self.create_plan()

    def create_plan(self):
        data = deepcopy(self.initial_data)
        response = self.app.post_json("/plans", {"data": data})
        self.plan = response.json["data"]
        self.plan_token = response.json["access"]["token"]
        self.plan_transfer = response.json["access"]["transfer"]
        self.plan_id = self.plan["id"]


class PlanOwnershipChangeTest(BasePlanOwnershipChangeTest):
    second_owner = "broker1"
    test_owner = "broker1t"
    invalid_owner = "broker4"

    def test_transfer_required(self):
        response = self.app.post_json("/plans/{}/ownership".format(self.plan_id), {"data": {"id": 12}}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [{"description": "This field is required.", "location": "body", "name": "transfer"}],
        )

    def test_change_ownership(self):
        # check first plan created
        response = self.app.get("/plans/{}".format(self.plan_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["owner"], self.first_owner)

        # create Transfer with second owner
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        self.assertIn("date", transfer)
        transfer_creation_date = transfer["date"]
        new_access_token = response.json["access"]["token"]
        new_transfer_token = response.json["access"]["transfer"]

        # change plan ownership
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/plans/{}/ownership".format(self.plan_id),
                {"data": {"id": transfer["id"], "transfer": self.plan_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertEqual(self.second_owner, response.json["data"]["owner"])

        # plan location is stored in Transfer
        response = self.app.get("/transfers/{}".format(transfer["id"]))
        transfer = response.json["data"]
        transfer_modification_date = transfer["date"]
        self.assertEqual(transfer["usedFor"], "/plans/" + self.plan_id)
        self.assertNotEqual(transfer_creation_date, transfer_modification_date)

        # try to use already applied transfer
        response = self.app.post_json("/plans", {"data": self.initial_data})
        plan = response.json["data"]
        access = response.json["access"]
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/plans/{}/ownership".format(plan["id"]),
                {"data": {"id": transfer["id"], "transfer": access["transfer"]}},
                status=403,
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{"description": "Transfer already used", "location": "body", "name": "transfer"}],
        )
        # simulate half-applied transfer activation process (i.e. transfer
        # is successfully applied to a plan and relation is saved in transfer,
        # but plan is not stored with new credentials)
        transfer_doc = self.mongodb.transfers.get(transfer["id"])
        transfer_doc["usedFor"] = "/plans/" + plan["id"]
        self.mongodb.transfers.save(Transfer(transfer_doc))
        response = self.app.post_json(
            "/plans/{}/ownership".format(plan["id"]),
            {"data": {"id": transfer["id"], "transfer": access["transfer"]}},
            status=200,
        )
        self.assertEqual(self.second_owner, response.json["data"]["owner"])

        # broker2 can change the plan (first plan which created in test setup)
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.patch_json(
                "/plans/{}?acc_token={}".format(self.plan_id, new_access_token),
                {"data": {"budget": {"description": "broker2 now can change the plan"}}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertIn("owner", response.json["data"])
        self.assertEqual(response.json["data"]["budget"]["description"], "broker2 now can change the plan")
        self.assertEqual(response.json["data"]["owner"], self.second_owner)

        # old owner now can`t change plan
        response = self.app.patch_json(
            "/plans/{}?acc_token={}".format(self.plan_id, new_access_token),
            {"data": {"description": "yummy donut"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")

    def test_transfer_invalid(self):
        response = self.app.post_json(
            "/plans/{}/ownership".format(self.plan_id),
            {"data": {"id": "fake id", "transfer": "fake transfer"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"], [{"description": "Invalid transfer", "location": "body", "name": "transfer"}]
        )

        response = self.app.post_json(
            "/plans/{}/ownership".format(self.plan_id),
            {"data": {"id": "fake id", "transfer": "трансфер з кирилицею"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"], [{"description": "Invalid transfer", "location": "body", "name": "transfer"}]
        )

    def test_accreditation_level(self):
        # try to use transfer by broker without appropriate accreditation level
        with change_auth(self.app, ("Basic", (self.invalid_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        transfer_tokens = response.json["access"]
        with change_auth(self.app, ("Basic", (self.invalid_owner, ""))):
            response = self.app.post_json(
                "/plans/{}/ownership".format(self.plan_id),
                {"data": {"id": transfer["id"], "transfer": self.plan_transfer}},
                status=403,
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": "Broker Accreditation level does not permit ownership change",
                    "location": "url",
                    "name": "accreditation",
                }
            ],
        )

    def test_accreditation_level_mode_test(self):
        # test level permits to change ownership for 'test' plans
        # first try on non-test plan
        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        transfer_tokens = response.json["access"]

        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json(
                "/plans/{}/ownership".format(self.plan_id),
                {"data": {"id": transfer["id"], "transfer": self.plan_transfer}},
                status=403,
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": "Broker Accreditation level does not permit ownership change",
                    "location": "url",
                    "name": "mode",
                }
            ],
        )

        # set test mode and try to change ownership
        with change_auth(self.app, ("Basic", ("administrator", ""))):
            response = self.app.patch_json("/plans/{}".format(self.plan_id), {"data": {"mode": "test"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["mode"], "test")

        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json(
                "/plans/{}/ownership".format(self.plan_id),
                {"data": {"id": transfer["id"], "transfer": self.plan_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertIn("owner", response.json["data"])
        self.assertEqual(response.json["data"]["owner"], self.test_owner)

        # test accreditation levels are also separated
        with change_auth(self.app, ("Basic", (self.invalid_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]

        new_transfer_token = transfer_tokens["transfer"]
        with change_auth(self.app, ("Basic", (self.invalid_owner, ""))):
            response = self.app.post_json(
                "/plans/{}/ownership".format(self.plan_id),
                {"data": {"id": transfer["id"], "transfer": new_transfer_token}},
                status=403,
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": "Broker Accreditation level does not permit ownership change",
                    "location": "url",
                    "name": "accreditation",
                }
            ],
        )

    def test_validate_status(self):
        self.app.patch_json(
            "/plans/{}?acc_token={}".format(self.plan_id, self.plan_token),
            {"data": {"status": "complete"}}
        )

        response = self.app.post_json(
            "/plans/{}/ownership".format(self.plan_id),
            {"data": {"id": "test_id", "transfer": "test_transfer"}},
            status=403
        )

        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": "Can't update credentials in current (complete) plan status",
                    "location": "body",
                    "name": "data",
                }
            ],
        )


class PlanOwnerOwnershipChangeTest(BasePlanOwnershipChangeTest):
    first_owner = "broker"
    second_owner = "broker1"
    initial_auth = ("Basic", (first_owner, ""))

    def test_owner_accreditation_level(self):
        # try to use transfer with owner without appropriate accreditation level
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        transfer_tokens = response.json["access"]
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/plans/{}/ownership".format(self.plan_id),
                {"data": {"id": transfer["id"], "transfer": self.plan_transfer}},
                status=403,
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": "Owner Accreditation level does not permit ownership change",
                    "location": "url",
                    "name": "accreditation",
                }
            ],
        )

    def test_owner_deleted(self):
        # try to use transfer with owner without appropriate accreditation level
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        transfer_tokens = response.json["access"]

        plan_doc = self.mongodb.plans.get(self.plan_id)
        plan_doc["owner"] = "deleted_broker"
        self.mongodb.save_data(self.mongodb.plans.collection, plan_doc)

        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/plans/{}/ownership".format(self.plan_id),
                {"data": {"id": transfer["id"], "transfer": self.plan_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertEqual(self.second_owner, response.json["data"]["owner"])
