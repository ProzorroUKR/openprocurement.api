# -*- coding: utf-8 -*-
import os
from copy import deepcopy

from openprocurement.tender.core.tests.base import change_auth
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.openeu.models import TENDERING_DURATION
from openprocurement.api.models import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_data, test_criteria, BaseTenderWebTest
from openprocurement.tender.openua.tests.base import test_tender_data as test_ua_tender_data
from openprocurement.tender.openuadefense.tests.base import test_tender_data as test_uadefense_tender_data
from openprocurement.tender.openeu.tests.base import test_tender_data as test_eu_tender_data
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_data_eu as test_tender_data_competitive_eu,
    test_tender_data_ua as test_tender_data_competitive_ua,
    test_tender_stage2_data_eu,
    test_tender_stage2_data_ua,
    test_access_token_stage1,
)
from openprocurement.tender.limited.tests.base import (
    test_tender_data as test_tender_reporting_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
)


class BaseTenderOwnershipChangeTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    first_owner = "brokerx"
    initial_auth = ("Basic", (first_owner, ""))

    def setUp(self):
        super(BaseTenderOwnershipChangeTest, self).setUp()
        self.create_tender()

    def create_tender(self):
        data = deepcopy(self.initial_data)
        response = self.app.post_json("/tenders", {"data": data})
        tender = response.json["data"]
        self.tender_token = response.json["access"]["token"]
        self.tender_transfer = response.json["access"]["transfer"]
        self.tender_id = tender["id"]


class TenderOwnershipChangeTest(BaseTenderOwnershipChangeTest):
    second_owner = "broker1"
    test_owner = "broker1t"
    invalid_owner = "broker3"
    central_owner = "broker5"
    initial_criteria = test_criteria

    def setUp(self):
        super(TenderOwnershipChangeTest, self).setUp()
        self.create_tender()

    def create_tender(self):
        response = self.app.post_json("/tenders", {"data": self.initial_data})
        tender = response.json["data"]
        self.tender_token = response.json["access"]["token"]
        self.tender_transfer = response.json["access"]["transfer"]
        self.tender_id = tender["id"]

    def test_transfer_required(self):
        response = self.app.post_json("/tenders/{}/ownership".format(self.tender_id), {"data": {"id": 12}}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [{u"description": u"This field is required.", u"location": u"body", u"name": u"transfer"}],
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
        response = self.app.post_json("/tenders", {"data": self.initial_data})
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
            [{u"description": u"Transfer already used", u"location": u"body", u"name": u"transfer"}],
        )
        # simulate half-applied transfer activation process (i.e. transfer
        # is successfully applied to a tender and relation is saved in transfer,
        # but tender is not stored with new credentials)
        transfer_doc = self.db.get(transfer["id"])
        transfer_doc["usedFor"] = "/tenders/" + tender["id"]
        self.db.save(transfer_doc)
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
            response.json["errors"], [{u"description": u"Invalid transfer", u"location": u"body", u"name": u"transfer"}]
        )

        response = self.app.post_json(
            "/tenders/{}/ownership".format(self.tender_id),
            {"data": {"id": "fake id", "transfer": "трансфер з кирилицею"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"], [{u"description": u"Invalid transfer", u"location": u"body", u"name": u"transfer"}]
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
                    u"description": u"Broker Accreditation level does not permit ownership change",
                    u"location": u"ownership",
                    u"name": u"accreditation",
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
                    u"description": u"Broker Accreditation level does not permit ownership change",
                    u"location": u"ownership",
                    u"name": u"mode",
                }
            ],
        )

        # set test mode and try to change ownership
        with change_auth(self.app, ("Basic", ("administrator", ""))):
            response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"mode": "test"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["mode"], "test")

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
                    u"description": u"Broker Accreditation level does not permit ownership change",
                    u"location": u"ownership",
                    u"name": u"accreditation",
                }
            ],
        )

    def test_accreditation_level_central(self):
        # test level permits to change ownership for 'central' kind tenders
        # first try on non 5th level broker
        tender = self.db.get(self.tender_id)
        tender["procuringEntity"]["kind"] = "central"
        tender["buyers"]= [{
            "name": tender["procuringEntity"]["name"],
            "identifier": tender["procuringEntity"]["identifier"]
        }]
        self.db.save(tender)

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
                    u"description": u"Broker Accreditation level does not permit ownership change",
                    u"location": u"ownership",
                    u"name": u"accreditation",
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
                    u"description": u"Can't update credentials in current (cancelled) tender status",
                    u"location": u"body",
                    u"name": u"data",
                }
            ],
        )


class OpenUATenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_ua_tender_data
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class OpenUADefenseTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_uadefense_tender_data
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class OpenUACompetitiveTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_data_competitive_ua
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class OpenEUCompetitiveTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_data_competitive_eu
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class OpenUACompetitiveDialogueStage2TenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_stage2_data_ua
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"

    def create_tender(self):
        data = deepcopy(self.initial_data)
        data["owner"] = self.first_owner
        with change_auth(self.app, ("Basic", ("competitive_dialogue", ""))):
            response = self.app.post_json("/tenders", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("transfer", response.json["access"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.tender_id = response.json["data"]["id"]
        self.set_status("draft.stage2")

        response = self.app.patch_json(
            "/tenders/{}/credentials?acc_token={}".format(self.tender_id, test_access_token_stage1), {"data": ""}
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

        # second owner can change the tender
        end_date = calculate_tender_business_date(
            get_now(), TENDERING_DURATION
        )
        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(self.tender_id, new_access_token),
                {"data": {"tenderPeriod": {"endDate": end_date.isoformat()}}},
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
        with change_auth(self.app, ("Basic", ("competitive_dialogue", ""))):
            response = self.app.post_json("/tenders", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("transfer", response.json["access"])
        self.assertNotIn("transfer_token", response.json["data"])
        tender = response.json["data"]
        self.tender_id = tender["id"]
        self.set_status("draft.stage2")

        response = self.app.patch_json(
            "/tenders/{}/credentials?acc_token={}".format(tender["id"], test_access_token_stage1), {"data": ""}
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
            [{u"description": u"Transfer already used", u"location": u"body", u"name": u"transfer"}],
        )

        # simulate half-applied transfer activation process (i.e. transfer
        # is successfully applied to a tender and relation is saved in transfer,
        # but tender is not stored with new credentials)
        transfer_doc = self.db.get(transfer["id"])
        transfer_doc["usedFor"] = "/tenders/" + tender["id"]
        self.db.save(transfer_doc)
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
    initial_data = test_tender_stage2_data_eu
    second_owner = "broker3"
    invalid_owner = "broker1"
    test_owner = "broker3t"


class OpenEUTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_eu_tender_data
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class ReportingTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_reporting_data
    second_owner = "broker1"
    test_owner = "broker1t"
    invalid_owner = "broker4"


class NegotiationTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_negotiation_data
    second_owner = "broker3"
    test_owner = "broker3t"
    invalid_owner = "broker1"


class NegotiationQuickTenderOwnershipChangeTest(TenderOwnershipChangeTest):
    initial_data = test_tender_negotiation_quick_data
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
                    u"description": u"Owner Accreditation level does not permit ownership change",
                    u"location": u"ownership",
                    u"name": u"accreditation",
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

        tender_doc = self.db.get(self.tender_id)
        tender_doc["owner"] = "deleted_broker"
        self.db.save(tender_doc)

        with change_auth(self.app, ("Basic", (self.second_owner, ""))):
            response = self.app.post_json(
                "/tenders/{}/ownership".format(self.tender_id),
                {"data": {"id": transfer["id"], "transfer": self.tender_transfer}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("transfer", response.json["data"])
        self.assertNotIn("transfer_token", response.json["data"])
        self.assertEqual(self.second_owner, response.json["data"]["owner"])
