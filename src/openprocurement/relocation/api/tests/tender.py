import uuid

import os
from copy import deepcopy
from mock import patch
from datetime import timedelta
from openprocurement.relocation.api.models import Transfer
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.openeu.models import TENDERING_DURATION
from openprocurement.api.models import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest,
    test_tender_below_data,
    test_tender_below_config,
)
from openprocurement.tender.openua.tests.base import (
    test_tender_openua_data,
    test_tender_openua_config,
)
from openprocurement.tender.openuadefense.tests.base import (
    test_tender_openuadefense_data,
    test_tender_openuadefense_config,
)
from openprocurement.tender.simpledefense.tests.base import (
    test_tender_simpledefense_data,
    test_tender_simpledefense_config,
)
from openprocurement.tender.openeu.tests.base import (
    test_tender_openeu_data,
    test_tender_openeu_config,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_cdeu_data,
    test_tender_cdua_data,
    test_tender_cdeu_stage2_data,
    test_tender_cdua_stage2_data,
    test_tender_cd_access_token,
    test_tender_cdua_config,
    test_tender_cdeu_config,
    test_tender_cdua_stage2_config,
    test_tender_cdeu_stage2_config,
)
from openprocurement.tender.limited.tests.base import (
    test_tender_reporting_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
    test_tender_reporting_config,
    test_tender_negotiation_config,
    test_tender_negotiation_quick_config,
)


class BaseTenderOwnershipChangeTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_below_data
    initial_config = test_tender_below_config
    first_owner = "brokerx"
    initial_auth = ("Basic", (first_owner, ""))

    def setUp(self):
        super(BaseTenderOwnershipChangeTest, self).setUp()
        self.create_tender()

    def create_tender(self):
        data = deepcopy(self.initial_data)
        config = deepcopy(self.initial_config)
        response = self.app.post_json("/tenders", {"data": data, "config": config})
        tender = response.json["data"]
        self.tender_token = response.json["access"]["token"]
        self.tender_transfer = response.json["access"]["transfer"]
        self.tender_id = tender["id"]


class TenderOwnershipChangeTest(BaseTenderOwnershipChangeTest):
    second_owner = "broker1"
    test_owner = "broker1t"
    invalid_owner = "broker3"
    central_owner = "broker5"
    initial_criteria = test_exclusion_criteria

    def setUp(self):
        super(TenderOwnershipChangeTest, self).setUp()
        self.create_tender()

    def create_tender(self):
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        tender = response.json["data"]
        self.tender_token = response.json["access"]["token"]
        self.tender_transfer = response.json["access"]["transfer"]
        self.tender_id = tender["id"]

    def test_transfer_required(self):
        response = self.app.post_json("/tenders/{}/ownership".format(self.tender_id), {"data": {"id": 12}}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [{"description": "This field is required.", "location": "body", "name": "transfer"}],
        )

    def test_change_ownership(self):
        # check first tender created
        response = self.app.get("/tenders/{}".format(self.tender_id))
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

        # change tender ownership
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(self.tender_id),
                {"data": {"id": transfer["id"], "transfer": self.tender_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertEqual(self.second_owner, response.json["data"]["owner"])

        # tender location is stored in Transfer
        response = self.app.get("/transfers/{}".format(transfer["id"]))
        transfer = response.json["data"]
        transfer_modification_date = transfer["date"]
        self.assertEqual(transfer["usedFor"], "/tenders/" + self.tender_id)
        self.assertNotEqual(transfer_creation_date, transfer_modification_date)

        # try to use already applied transfer
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        tender = response.json["data"]
        access = response.json["access"]
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(tender["id"]),
                {"data": {"id": transfer["id"], "transfer": access["transfer"]}},
                status=403,
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{"description": "Transfer already used", "location": "body", "name": "transfer"}],
        )
        # simulate half-applied transfer activation process (i.e. transfer
        # is successfully applied to a tender and relation is saved in transfer,
        # but tender is not stored with new credentials)
        transfer_doc = self.mongodb.transfers.get(transfer["id"])
        transfer_doc["usedFor"] = "/tenders/" + tender["id"]
        self.mongodb.transfers.save(Transfer(transfer_doc))
        response = self.app.post_json(
            "/tenders/{}/ownership".format(tender["id"]),
            {"data": {"id": transfer["id"], "transfer": access["transfer"]}},
            status=200,
        )
        self.assertEqual(self.second_owner, response.json["data"]["owner"])

        # broker2 can change the tender (first tender which created in test setup)
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, new_access_token),
                {"data": {"description": "broker2 now can change the tender"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertIn("owner", response.json["data"])
        self.assertEqual(response.json["data"]["description"], "broker2 now can change the tender")
        self.assertEqual(response.json["data"]["owner"], self.second_owner)

        # old owner now can`t change tender
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, new_access_token),
            {"data": {"description": "yummy donut"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")

    def test_transfer_invalid(self):
        response = self.app.post_json(
            "/tenders/{}/ownership".format(self.tender_id),
            {"data": {"id": "fake id", "transfer": "fake transfer"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"], [{"description": "Invalid transfer", "location": "body", "name": "transfer"}]
        )

        response = self.app.post_json(
            "/tenders/{}/ownership".format(self.tender_id),
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
                "/tenders/{}/ownership".format(self.tender_id),
                {"data": {"id": transfer["id"], "transfer": self.tender_transfer}},
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
        # test level permits to change ownership for 'test' tenders
        # first try on non-test tender
        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        transfer_tokens = response.json["access"]

        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(self.tender_id),
                {"data": {"id": transfer["id"], "transfer": self.tender_transfer}},
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
        tender = self.mongodb.tenders.get(self.tender_id)
        tender["mode"] = "test"
        self.mongodb.tenders.save(tender)

        with change_auth(self.app, ("Basic", (self.test_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(self.tender_id),
                {"data": {"id": transfer["id"], "transfer": self.tender_transfer}},
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
                "/tenders/{}/ownership".format(self.tender_id),
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

    def test_accreditation_level_central(self):
        # test level permits to change ownership for 'central' kind tenders
        # first try on non 5th level broker
        tender = self.mongodb.tenders.get(self.tender_id)
        tender["procuringEntity"]["kind"] = "central"
        tender["buyers"] = [{
            "id": uuid.uuid4().hex,
            "name": tender["procuringEntity"]["name"],
            "identifier": tender["procuringEntity"]["identifier"]
        }]
        for item in tender["items"]:
            item["relatedBuyer"] = tender["buyers"][0]["id"]
        self.mongodb.tenders.save(tender)

        # create Transfer with second owner
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        transfer_tokens = response.json["access"]

        # try to change ownership
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(self.tender_id),
                {"data": {"id": transfer["id"], "transfer": self.tender_transfer}},
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

        # create Transfer with central owner
        with change_auth(self.app, ("Basic", (self.central_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        transfer_tokens = response.json["access"]

        # try to change ownership with 5th level
        with change_auth(self.app, ("Basic", (self.central_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(self.tender_id),
                {"data": {"id": transfer["id"], "transfer": self.tender_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertIn("owner", response.json["data"])
        self.assertEqual(response.json["data"]["owner"], self.central_owner)


    def test_validate_status(self):
        # terminated contract is also protected
        self.set_status("cancelled")

        response = self.app.post_json(
            "/tenders/{}/ownership".format(self.tender_id),
            {"data": {"id": "test_id", "transfer": "test_transfer"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": "Can't update credentials in current (cancelled) tender status",
                    "location": "body",
                    "name": "data",
                }
            ],
        )


class OpenUATenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_openua_data
    initial_config = test_tender_openua_config
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class OpenUADefenseTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_openuadefense_data
    initial_config = test_tender_openuadefense_config
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"

    def setUp(self):
        self.pathcer_release_date = patch("openprocurement.tender.core.validation.RELEASE_SIMPLE_DEFENSE_FROM",
                                          get_now() + timedelta(days=1))
        self.pathcer_release_date.start()
        super(OpenUADefenseTenderOwnershipChangeTest, self).setUp()

    def tearDown(self):
        super(OpenUADefenseTenderOwnershipChangeTest, self).tearDown()
        self.pathcer_release_date.stop()


class SimpleDefenseTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_simpledefense_data
    initial_config = test_tender_simpledefense_config
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"

    def setUp(self):
        self.pathcer_release_date = patch("openprocurement.tender.core.validation.RELEASE_SIMPLE_DEFENSE_FROM",
                                          get_now() - timedelta(days=1))
        self.pathcer_release_date.start()
        super(SimpleDefenseTenderOwnershipChangeTest, self).setUp()

    def tearDown(self):
        super(SimpleDefenseTenderOwnershipChangeTest, self).tearDown()
        self.pathcer_release_date.stop()


class OpenUACompetitiveTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_cdua_data
    initial_config = test_tender_cdua_config
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class OpenEUCompetitiveTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_cdeu_data
    initial_config = test_tender_cdeu_config
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class OpenUACompetitiveDialogueStage2TenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_cdua_stage2_data
    initial_config = test_tender_cdua_stage2_config
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"

    def create_tender(self):
        data = deepcopy(self.initial_data)
        data["owner"] = self.first_owner
        config = self.initial_config
        with change_auth(self.app, ("Basic", ("competitive_dialogue", ""))):
            response = self.app.post_json("/tenders", {"data": data, "config": config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("transfer", response.json["access"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.tender_id = response.json["data"]["id"]
        self.set_status("draft.stage2")

        response = self.app.patch_json(
            "/tenders/{}/credentials?acc_token={}".format(self.tender_id, test_tender_cd_access_token), {"data": ""}
        )
        self.tender_transfer = response.json["access"]["transfer"]
        tender_access_token = response.json["access"]["token"]

        add_criteria(self, tender_token=tender_access_token)

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, tender_access_token),
            {"data": {"status": "active.tendering"}},
        )

    def test_change_ownership(self):
        # check first tender created
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        tender = response.json["data"]
        self.assertEqual(tender["owner"], self.first_owner)

        # create Transfer with second owner
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json("/transfers", {"data": {}})
        self.assertEqual(response.status, "201 Created")
        transfer = response.json["data"]
        self.assertIn("date", transfer)
        transfer_creation_date = transfer["date"]
        new_access_token = response.json["access"]["token"]
        new_transfer_token = response.json["access"]["transfer"]

        # change tender ownership
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(self.tender_id),
                {"data": {"id": transfer["id"], "transfer": self.tender_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertEqual(self.second_owner, response.json["data"]["owner"])

        # tender location is stored in Transfer
        response = self.app.get("/transfers/{}".format(transfer["id"]))
        transfer = response.json["data"]
        transfer_modification_date = transfer["date"]
        self.assertEqual(transfer["usedFor"], "/tenders/" + self.tender_id)
        self.assertNotEqual(transfer_creation_date, transfer_modification_date)

        # second owner can change the tender
        end_date = calculate_tender_business_date(
            get_now(), TENDERING_DURATION
        )
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, new_access_token),
                {"data": {"tenderPeriod": {
                    "startDate": tender["tenderPeriod"]["startDate"],
                    "endDate": end_date.isoformat(),
                }}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertIn("owner", response.json["data"])
        self.assertEqual(response.json["data"]["owner"], self.second_owner)
        self.assertEqual(response.json["data"]["tenderPeriod"]["endDate"], end_date.isoformat())

        # first owner now can`t change tender
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, new_access_token),
            {"data": {"tenderPeriod": {"endDate": end_date.isoformat()}}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")

        # try to use already applied transfer on new tender created by bridge
        data = deepcopy(self.initial_data)
        data["owner"] = self.first_owner
        config = self.initial_config
        with change_auth(self.app, ("Basic", ("competitive_dialogue", ""))):
            response = self.app.post_json("/tenders", {"data": data, "config": config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("transfer", response.json["access"])
        self.assertNotIn("transfer_token", response.json["data"])
        tender = response.json["data"]
        self.tender_id = tender["id"]
        self.set_status("draft.stage2")

        response = self.app.patch_json(
            "/tenders/{}/credentials?acc_token={}".format(tender["id"], test_tender_cd_access_token), {"data": ""}
        )
        access = response.json["access"]
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(tender["id"]),
                {"data": {"id": transfer["id"], "transfer": access["transfer"]}},
                status=403,
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{"description": "Transfer already used", "location": "body", "name": "transfer"}],
        )

        # simulate half-applied transfer activation process (i.e. transfer
        # is successfully applied to a tender and relation is saved in transfer,
        # but tender is not stored with new credentials)
        transfer_doc = self.mongodb.transfers.get(transfer["id"])
        transfer_doc["usedFor"] = "/tenders/" + tender["id"]
        self.mongodb.transfers.save(Transfer(transfer_doc))
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(tender["id"]),
                {"data": {"id": transfer["id"], "transfer": access["transfer"]}},
                status=200,
            )
        self.assertEqual(self.second_owner, response.json["data"]["owner"])


class OpenEUCompetitiveDialogueStage2TenderOwnershipChangeTest(
    OpenUACompetitiveDialogueStage2TenderOwnershipChangeTest
):
    initial_data = test_tender_cdeu_stage2_data
    initial_config = test_tender_cdeu_stage2_config
    second_owner = "broker3"
    invalid_owner = "broker1"
    test_owner = "broker3t"


class OpenEUTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_openeu_data
    initial_config = test_tender_openeu_config
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class ReportingTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_reporting_data
    initial_config = test_tender_reporting_config
    second_owner = "broker1"
    test_owner = "broker1t"
    invalid_owner = "broker4"


class NegotiationTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class NegotiationQuickTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class TenderOwnerOwnershipChangeTest(BaseTenderOwnershipChangeTest):
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
                "/tenders/{}/ownership".format(self.tender_id),
                {"data": {"id": transfer["id"], "transfer": self.tender_transfer}},
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

        tender_doc = self.mongodb.tenders.get(self.tender_id)
        tender_doc["owner"] = "deleted_broker"
        self.mongodb.tenders.save(tender_doc)

        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(self.tender_id),
                {"data": {"id": transfer["id"], "transfer": self.tender_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertEqual(self.second_owner, response.json["data"]["owner"])
