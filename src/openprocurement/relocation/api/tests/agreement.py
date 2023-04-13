import os
from copy import deepcopy

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.relocation.api.models import Transfer
from openprocurement.framework.cfaua.models.agreement import Agreement
from openprocurement.framework.cfaua.tests.data import test_tender_token as test_agreement_tender_token, \
    test_agreement_data


class BaseAgreementOwnershipChangeTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_agreement_data
    tender_token = test_agreement_tender_token
    first_owner = "brokerx"
    initial_auth = ("Basic", (first_owner, ""))

    def setUp(self):
        super(BaseAgreementOwnershipChangeTest, self).setUp()
        self.create_agreement()

    def create_agreement(self):
        data = deepcopy(self.initial_data)
        data["owner"] = self.first_owner
        with change_auth(self.app, ("Basic", ("agreements", ""))):
            response = self.app.post_json("/agreements", {"data": data})
        self.agreement = response.json["data"]
        self.agreement_id = self.agreement["id"]
        response = self.app.patch_json(
            "/agreements/{}/credentials?acc_token={}".format(self.agreement_id, self.tender_token), {"data": ""}
        )
        self.assertEqual(response.status, "200 OK")
        self.agreement_token = response.json["access"]["token"]
        self.agreement_transfer = response.json["access"]["transfer"]


class AgreementOwnershipChangeTest(BaseAgreementOwnershipChangeTest):
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"

    def test_transfer_required(self):
        response = self.app.post_json(
            "/agreements/{}/ownership".format(self.agreement_id), {"data": {"id": 12}}, status=422
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [{"description": "This field is required.", "location": "body", "name": "transfer"}],
        )

    def test_change_ownership(self):
        # check first agreement created
        response = self.app.get("/agreements/{}".format(self.agreement_id))
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

        # change agreement ownership
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/agreements/{}/ownership".format(self.agreement_id),
                {"data": {"id": transfer["id"], "transfer": self.agreement_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertEqual(self.second_owner, response.json["data"]["owner"])

        # agreement location is stored in Transfer
        response = self.app.get("/transfers/{}".format(transfer["id"]))
        transfer = response.json["data"]
        transfer_modification_date = transfer["date"]
        self.assertEqual(transfer["usedFor"], "/agreements/" + self.agreement_id)
        self.assertNotEqual(transfer_creation_date, transfer_modification_date)

        # try to use already applied transfer
        data = deepcopy(self.initial_data)
        data["owner"] = self.first_owner
        data.pop("id")
        with change_auth(self.app, ("Basic", ("agreements", ""))):
            response = self.app.post_json("/agreements", {"data": data})
        agreement = response.json["data"]

        response = self.app.patch_json(
            "/agreements/{}/credentials?acc_token={}".format(agreement["id"], self.tender_token), {"data": ""}
        )
        self.assertEqual(response.status, "200 OK")
        access = response.json["access"]

        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/agreements/{}/ownership".format(agreement["id"]),
                {"data": {"id": transfer["id"], "transfer": access["transfer"]}},
                status=403,
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{"description": "Transfer already used", "location": "body", "name": "transfer"}],
        )

        # simulate half-applied transfer activation process (i.e. transfer
        # is successfully applied to a agreement and relation is saved in transfer,
        # but agreement is not stored with new credentials)
        transfer_doc = self.mongodb.transfers.get(transfer["id"])
        transfer_doc["usedFor"] = "/agreements/" + agreement["id"]
        self.mongodb.transfers.save(Transfer(transfer_doc))
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/agreements/{}/ownership".format(agreement["id"]),
                {"data": {"id": transfer["id"], "transfer": access["transfer"]}},
                status=200,
            )
        self.assertEqual(self.second_owner, response.json["data"]["owner"])

        # broker2 can change the agreement (first agreement which created in test setup)
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.patch_json(
                "/agreements/{}?acc_token={}".format(self.agreement_id, new_access_token),
                {"data": {"terminationDetails": "broker2 now can change the agreement"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertIn("owner", response.json["data"])
        self.assertEqual(response.json["data"]["terminationDetails"], "broker2 now can change the agreement")
        self.assertEqual(response.json["data"]["owner"], self.second_owner)

        # old owner now can`t change agreement
        response = self.app.patch_json(
            "/agreements/{}?acc_token={}".format(self.agreement_id, new_access_token),
            {"data": {"description": "yummy donut"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")

    def test_transfer_invalid(self):
        response = self.app.post_json(
            "/agreements/{}/ownership".format(self.agreement_id),
            {"data": {"id": "fake id", "transfer": "fake transfer"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"], [{"description": "Invalid transfer", "location": "body", "name": "transfer"}]
        )
        response = self.app.post_json(
            "/agreements/{}/ownership".format(self.agreement_id),
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
                "/agreements/{}/ownership".format(self.agreement_id),
                {"data": {"id": transfer["id"], "transfer": self.agreement_transfer}},
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
        # test level permits to change ownership for 'test' agreements
        # first try on non-test agreement
        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        transfer_tokens = response.json["access"]

        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json(
                "/agreements/{}/ownership".format(self.agreement_id),
                {"data": {"id": transfer["id"], "transfer": self.agreement_transfer}},
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
            response = self.app.patch_json("/agreements/{}".format(self.agreement_id), {"data": {"mode": "test"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["mode"], "test")

        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json(
                "/agreements/{}/ownership".format(self.agreement_id),
                {"data": {"id": transfer["id"], "transfer": self.agreement_transfer}},
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
                "/agreements/{}/ownership".format(self.agreement_id),
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
        # terminated agreement is also protected
        response = self.app.patch_json(
            "/agreements/{}?acc_token={}".format(self.agreement_id, self.agreement_token),
            {"data": {"status": "terminated"}},
        )
        self.assertEqual(response.status, "200 OK")

        response = self.app.post_json(
            "/agreements/{}/ownership".format(self.agreement_id),
            {"data": {"id": "test_id", "transfer": "test_transfer"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": "Can't update credentials in current (terminated) agreement status",
                    "location": "body",
                    "name": "data",
                }
            ],
        )


class AgreementOwnerOwnershipChangeTest(BaseAgreementOwnershipChangeTest):
    first_owner = "broker"
    second_owner = "broker3"
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
                "/agreements/{}/ownership".format(self.agreement_id),
                {"data": {"id": transfer["id"], "transfer": self.agreement_transfer}},
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

        agreement_doc = self.mongodb.agreements.get(self.agreement_id)
        agreement_doc["owner"] = "deleted_broker"
        self.mongodb.agreements.save(Agreement(agreement_doc))

        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/agreements/{}/ownership".format(self.agreement_id),
                {"data": {"id": transfer["id"], "transfer": self.agreement_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertEqual(self.second_owner, response.json["data"]["owner"])
