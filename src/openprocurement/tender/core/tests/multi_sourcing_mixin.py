from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.constants import (
    TENDER_CO_CONFIG_JSONSCHEMAS,
    TENDER_CONFIG_JSONSCHEMAS,
)
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier


def _patch_schema(schema_dict, key):
    original = deepcopy(schema_dict[key])
    patched = deepcopy(original)
    patched["properties"]["hasMultiSourcing"]["enum"] = [True, False]
    if patched["properties"]["hasAuction"].get("enum") == [True]:
        patched["properties"]["hasAuction"]["enum"] = [True, False]
    schema_dict[key] = patched
    return original


class MultiSourcingTestMixin:
    multi_sourcing_pmt: str = None
    multi_sourcing_co_keys: list = ()
    initial_config = {}
    award_activation_data: dict = {"status": "active", "qualified": True, "eligible": True}

    @classmethod
    def setUpClass(cls):
        cls._original_ms_schema = _patch_schema(TENDER_CONFIG_JSONSCHEMAS, cls.multi_sourcing_pmt)
        cls._original_co_schemas = {}
        for key in cls.multi_sourcing_co_keys:
            cls._original_co_schemas[key] = _patch_schema(TENDER_CO_CONFIG_JSONSCHEMAS, key)
        cls.initial_config = deepcopy(cls.initial_config)
        cls.initial_config["hasMultiSourcing"] = True
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        TENDER_CONFIG_JSONSCHEMAS[cls.multi_sourcing_pmt] = cls._original_ms_schema
        for key, original in cls._original_co_schemas.items():
            TENDER_CO_CONFIG_JSONSCHEMAS[key] = original
        super().tearDownClass()

    def _seed_one_lot_two_bids_one_pending_award(self):
        tender = self.mongodb.tenders.get(self.tender_id)
        tender["status"] = "active.qualification"
        lot_id = "1" * 32
        tender["lots"] = [
            {
                "id": lot_id,
                "title": "lot1",
                "description": "lot1",
                "value": tender["value"],
                "status": "active",
            }
        ]
        tender["items"][0]["relatedLot"] = lot_id
        tender["bids"] = [
            {
                "id": "b" * 32,
                "owner": "broker",
                "owner_token": "b" * 32,
                "tenderers": [deepcopy(test_tender_below_supplier)],
                "status": "active",
                "submissionDate": tender["dateModified"],
                "lotValues": [
                    {
                        "relatedLot": lot_id,
                        "value": tender["value"],
                        "date": tender["dateModified"],
                        "status": "active",
                    }
                ],
            },
            {
                "id": "d" * 32,
                "owner": "broker",
                "owner_token": "d" * 32,
                "tenderers": [deepcopy(test_tender_below_supplier)],
                "status": "active",
                "submissionDate": tender["dateModified"],
                "lotValues": [
                    {
                        "relatedLot": lot_id,
                        "value": tender["value"],
                        "date": tender["dateModified"],
                        "status": "active",
                    }
                ],
            },
        ]
        tender["awards"] = [
            {
                "id": "a" * 32,
                "bid_id": "b" * 32,
                "status": "pending",
                "lotID": lot_id,
                "suppliers": [deepcopy(test_tender_below_supplier)],
                "items": [deepcopy(tender["items"][0])],
                "value": tender["value"],
                "date": tender["dateModified"],
            }
        ]
        self.mongodb.tenders.save(tender)
        return "a" * 32, "d" * 32

    def _seed_two_pending_awards(self):
        tender = self.mongodb.tenders.get(self.tender_id)
        tender["status"] = "active.qualification"
        lot_id = "1" * 32
        tender["lots"] = [
            {
                "id": lot_id,
                "title": "lot1",
                "description": "lot1",
                "value": tender["value"],
                "status": "active",
            }
        ]
        tender["items"][0]["relatedLot"] = lot_id
        tender["bids"] = [
            {
                "id": "b" * 32,
                "owner": "broker",
                "owner_token": "b" * 32,
                "tenderers": [deepcopy(test_tender_below_supplier)],
                "status": "active",
                "submissionDate": tender["dateModified"],
                "lotValues": [
                    {
                        "relatedLot": lot_id,
                        "value": tender["value"],
                        "date": tender["dateModified"],
                        "status": "active",
                    }
                ],
            },
            {
                "id": "d" * 32,
                "owner": "broker",
                "owner_token": "d" * 32,
                "tenderers": [deepcopy(test_tender_below_supplier)],
                "status": "active",
                "submissionDate": tender["dateModified"],
                "lotValues": [
                    {
                        "relatedLot": lot_id,
                        "value": tender["value"],
                        "date": tender["dateModified"],
                        "status": "active",
                    }
                ],
            },
        ]
        tender["awards"] = [
            {
                "id": "a" * 32,
                "bid_id": "b" * 32,
                "status": "pending",
                "lotID": lot_id,
                "suppliers": [deepcopy(test_tender_below_supplier)],
                "items": [deepcopy(tender["items"][0])],
                "value": tender["value"],
                "date": tender["dateModified"],
            },
            {
                "id": "c" * 32,
                "bid_id": "d" * 32,
                "status": "pending",
                "lotID": lot_id,
                "suppliers": [deepcopy(test_tender_below_supplier)],
                "items": [deepcopy(tender["items"][0])],
                "value": tender["value"],
                "date": tender["dateModified"],
            },
        ]
        self.mongodb.tenders.save(tender)
        return "a" * 32, "c" * 32

    def test_create_tender_with_multi_sourcing(self):
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.assertEqual(response.status, "200 OK")
        config = response.json.get("config", {})
        self.assertIs(config.get("hasMultiSourcing"), True)

    def test_create_tender_accepts_auction_and_multi_sourcing(self):
        config = deepcopy(self.initial_config)
        config["hasAuction"] = True
        response = self.app.post_json(
            "/tenders",
            {"data": deepcopy(self.initial_data), "config": config},
            status=201,
        )
        self.assertIs(response.json["config"].get("hasMultiSourcing"), True)
        self.assertIs(response.json["config"].get("hasAuction"), True)

    def test_next_pending_generated_after_award_activation(self):
        award_id, next_bid_id = self._seed_one_lot_two_bids_one_pending_award()
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
            {"data": deepcopy(self.award_activation_data)},
        )
        self.assertEqual(response.status, "200 OK")

        tender_after = self.mongodb.tenders.get(self.tender_id)
        awards = tender_after.get("awards", [])
        self.assertEqual(
            len(awards),
            2,
            f"Expected second pending award after activation; got {len(awards)}",
        )
        active = [a for a in awards if a["status"] == "active"]
        pending = [a for a in awards if a["status"] == "pending"]
        self.assertEqual(len(active), 1)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["bid_id"], next_bid_id)

    def test_tender_stays_in_qualification_while_pending_awards_remain(self):
        award_id, _ = self._seed_one_lot_two_bids_one_pending_award()
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id}?acc_token={self.tender_token}",
            {"data": deepcopy(self.award_activation_data)},
        )
        self.assertEqual(response.status, "200 OK")

        tender_after = self.mongodb.tenders.get(self.tender_id)
        self.assertEqual(
            tender_after["status"],
            "active.qualification",
            "Tender must stay in active.qualification while pending awards exist",
        )
        self.assertNotIn(
            "endDate",
            tender_after.get("awardPeriod", {}),
            "awardPeriod.endDate must not be set while awards are still pending",
        )

    def test_tender_transitions_to_awarded_when_no_pending(self):
        award_id_1, award_id_2 = self._seed_two_pending_awards()
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id_1}/documents")
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id_2}/documents")

        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id_1}?acc_token={self.tender_token}",
            {"data": deepcopy(self.award_activation_data)},
        )
        rejection = {"status": "unsuccessful", "qualified": False}
        if "eligible" in self.award_activation_data:
            rejection["eligible"] = False
        self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{award_id_2}?acc_token={self.tender_token}",
            {"data": rejection},
        )

        tender_after = self.mongodb.tenders.get(self.tender_id)
        self.assertEqual(tender_after["status"], "active.awarded")
        self.assertIn("endDate", tender_after.get("awardPeriod", {}))

        contracts = tender_after.get("contracts", [])
        contracts_for_award_1 = [c for c in contracts if c.get("awardID") == award_id_1]
        contracts_for_award_2 = [c for c in contracts if c.get("awardID") == award_id_2]
        self.assertEqual(
            len(contracts_for_award_1),
            1,
            f"Expected 1 contract for active award_1; got {len(contracts_for_award_1)}",
        )
        self.assertEqual(contracts_for_award_1[0]["status"], "pending")
        self.assertEqual(
            len(contracts_for_award_2),
            0,
            "Unsuccessful award_2 should not produce a contract",
        )

    def test_invalid_to_pending_triggers_quantity_validation(self):
        tender = self.mongodb.tenders.get(self.tender_id)
        tender["status"] = "active.tendering"
        tender["tenderPeriod"] = {
            "startDate": (get_now() - timedelta(days=5)).isoformat(),
            "endDate": (get_now() + timedelta(days=10)).isoformat(),
        }
        lot_id = "1" * 32
        tender["lots"] = [
            {
                "id": lot_id,
                "title": "lot1",
                "description": "lot1",
                "value": tender["value"],
                "status": "active",
            }
        ]
        tender_item = tender["items"][0]
        tender_item["relatedLot"] = lot_id
        tender_qty = tender_item["quantity"]
        bad_qty = tender_qty + 5

        bid_id = "1" * 32
        bid_token = "2" * 32
        tender["bids"] = [
            {
                "id": bid_id,
                "owner": "broker",
                "owner_token": bid_token,
                "tenderers": [deepcopy(test_tender_below_supplier)],
                "status": "invalid",
                "submissionDate": tender["dateModified"],
                "date": tender["dateModified"],
                "lotValues": [
                    {
                        "relatedLot": lot_id,
                        "value": tender["value"],
                        "date": tender["dateModified"],
                        "status": "active",
                    }
                ],
                "items": [
                    {
                        "id": tender_item["id"],
                        "description": tender_item.get("description", "test"),
                        "quantity": bad_qty,
                        "unit": tender_item.get("unit", {"name": "штук", "code": "H87"}),
                    }
                ],
            }
        ]
        self.mongodb.tenders.save(tender)

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/bids/{bid_id}?acc_token={bid_token}",
            {"data": {"status": "pending"}},
            status=422,
        )
        descriptions = " ".join(str(e.get("description", "")) for e in response.json.get("errors", []))
        self.assertIn(
            "should be less than or equal to",
            descriptions,
            f"Expected quantity validation error, got: {descriptions}",
        )
