import os
from copy import deepcopy
from uuid import uuid4

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.contracting.core.tests.data import (
    test_tender_token as test_contract_tender_token,
)
from openprocurement.contracting.econtract.tests.data import (
    test_contract_data,
    test_signer_info,
)
from openprocurement.contracting.econtract.tests.utils import create_contract
from openprocurement.tender.core.tests.utils import change_auth


class BaseContractOwnershipChangeTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_contract_data
    tender_token = test_contract_tender_token
    first_owner = "brokerx"
    initial_auth = ("Basic", (first_owner, ""))

    def setUp(self):
        super().setUp()
        self.create_contract()

    def create_contract(self):
        data = deepcopy(self.initial_data)
        data['id'] = uuid4().hex
        data['owner'] = self.first_owner
        data['bid_owner'] = self.first_owner
        self.bid_token = uuid4().hex
        data['bid_token'] = self.bid_token
        self.contract = create_contract(self, data)
        self.contract_id = self.contract["id"]
        response = self.app.patch_json(
            f"/contracts/{self.contract_id}/credentials?acc_token={self.tender_token}", {"data": ""}
        )
        self.assertEqual(response.status, "200 OK")
        self.contract_token = response.json["access"]["token"]
        self.contract_transfer = response.json["access"]["transfer"]

        # TODO: Test pending contract

        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{self.contract_id}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{self.contract_id}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        response = self.app.patch_json(
            "/contracts/{}?acc_token={}".format(self.contract_id, self.contract_token),
            {
                "data": {
                    "status": "active",
                    "period": {
                        "startDate": "2014-01-01T00:00:00+02:00",
                        "endDate": "2015-01-01T00:00:00+02:00",
                    },
                    "contractNumber": 1,
                }
            },
        )
        self.assertEqual(response.status, "200 OK")


class ContractOwnershipChangeTest(BaseContractOwnershipChangeTest):
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"

    def test_transfer_required(self):
        response = self.app.post_json(
            "/contracts/{}/ownership".format(self.contract_id), {"data": {"id": 12}}, status=422
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [{"description": "This field is required.", "location": "body", "name": "transfer"}],
        )

    def test_change_ownership(self):
        # check first contract created
        response = self.app.get("/contracts/{}".format(self.contract_id))
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

        # change contract ownership
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/contracts/{}/ownership".format(self.contract_id),
                {"data": {"id": transfer["id"], "transfer": self.contract_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertEqual(self.second_owner, response.json["data"]["owner"])

        # contract location is stored in Transfer
        response = self.app.get("/transfers/{}".format(transfer["id"]))
        transfer = response.json["data"]
        transfer_modification_date = transfer["date"]
        self.assertEqual(transfer["usedFor"], "/contracts/" + self.contract_id)
        self.assertNotEqual(transfer_creation_date, transfer_modification_date)

        # try to use already applied transfer
        data = deepcopy(self.initial_data)
        data["owner"] = self.first_owner
        data["id"] = uuid4().hex
        data["tender_token"] = self.tender_token
        contract = create_contract(self, data)
        response = self.app.patch_json(
            "/contracts/{}/credentials?acc_token={}".format(contract["id"], self.tender_token), {"data": ""}
        )
        self.assertEqual(response.status, "200 OK")
        access = response.json["access"]

        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/contracts/{}/ownership".format(contract["id"]),
                {"data": {"id": transfer["id"], "transfer": access["transfer"]}},
                status=403,
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{"description": "Transfer already used", "location": "body", "name": "transfer"}],
        )

        # simulate half-applied transfer activation process (i.e. transfer
        # is successfully applied to a contract and relation is saved in transfer,
        # but contract is not stored with new credentials)
        transfer_doc = self.mongodb.transfers.get(transfer["id"])
        transfer_doc["usedFor"] = "/contracts/" + contract["id"]
        self.mongodb.transfers.save(transfer_doc)
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/contracts/{}/ownership".format(contract["id"]),
                {"data": {"id": transfer["id"], "transfer": access["transfer"]}},
                status=200,
            )
        self.assertEqual(self.second_owner, response.json["data"]["owner"])

        # broker2 can change the contract (first contract which created in test setup)
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.patch_json(
                "/contracts/{}?acc_token={}".format(self.contract_id, new_access_token),
                {"data": {"terminationDetails": "broker2 now can change the contract"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertIn("owner", response.json["data"])
        self.assertEqual(response.json["data"]["terminationDetails"], "broker2 now can change the contract")
        self.assertEqual(response.json["data"]["owner"], self.second_owner)

        # old owner now can`t change contract
        response = self.app.patch_json(
            "/contracts/{}?acc_token={}".format(self.contract_id, new_access_token),
            {"data": {"description": "yummy donut"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")

    def test_transfer_invalid(self):
        response = self.app.post_json(
            "/contracts/{}/ownership".format(self.contract_id),
            {"data": {"id": "fake id", "transfer": "fake transfer"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"], [{"description": "Invalid transfer", "location": "body", "name": "transfer"}]
        )

        response = self.app.post_json(
            "/contracts/{}/ownership".format(self.contract_id),
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
                "/contracts/{}/ownership".format(self.contract_id),
                {"data": {"id": transfer["id"], "transfer": self.contract_transfer}},
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
        # test level permits to change ownership for 'test' contracts
        # first try on non-test contract
        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        transfer_tokens = response.json["access"]

        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json(
                "/contracts/{}/ownership".format(self.contract_id),
                {"data": {"id": transfer["id"], "transfer": self.contract_transfer}},
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
            response = self.app.patch_json("/contracts/{}".format(self.contract_id), {"data": {"mode": "test"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["mode"], "test")

        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json(
                "/contracts/{}/ownership".format(self.contract_id),
                {"data": {"id": transfer["id"], "transfer": self.contract_transfer}},
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
                "/contracts/{}/ownership".format(self.contract_id),
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
        # terminated contract is also protected
        response = self.app.patch_json(
            "/contracts/{}?acc_token={}".format(self.contract_id, self.contract_token),
            {"data": {"status": "terminated", "amountPaid": {"amount": 200, "amountNet": 190}}},
        )
        self.assertEqual(response.status, "200 OK")

        response = self.app.post_json(
            "/contracts/{}/ownership".format(self.contract_id),
            {"data": {"id": "test_id", "transfer": "test_transfer"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": "Can't update credentials in current (terminated) contract status",
                    "location": "body",
                    "name": "data",
                }
            ],
        )


class ContractOwnerOwnershipChangeTest(BaseContractOwnershipChangeTest):
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
                "/contracts/{}/ownership".format(self.contract_id),
                {"data": {"id": transfer["id"], "transfer": self.contract_transfer}},
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

        contract_doc = self.mongodb.contracts.get(self.contract_id)
        contract_doc["owner"] = "deleted_broker"
        self.mongodb.contracts.save(contract_doc)

        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/contracts/{}/ownership".format(self.contract_id),
                {"data": {"id": transfer["id"], "transfer": self.contract_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertEqual(self.second_owner, response.json["data"]["owner"])
