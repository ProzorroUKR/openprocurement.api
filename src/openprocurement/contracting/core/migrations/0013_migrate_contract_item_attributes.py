import json
import logging
from collections import defaultdict
from unittest.mock import ANY, MagicMock, call, patch

from pymongo import DESCENDING

from openprocurement.api.migrations.base import (
    PymongoCollectionMigration,
    ReadonlyCollectionWrapper,
    migrate_collection,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

MARKET_FIELDS = ("product", "category")


class Migration(PymongoCollectionMigration):
    description = (
        "Migrating dataSchema from tender criteria to contract item attributes and market fields to contract items"
    )

    collection_name = "contracts"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def process_data(self, cursor):
        cursor.sort([("public_modified", DESCENDING)])
        return super().process_data(cursor)

    def get_filter(self) -> dict:
        return {"items": {"$exists": True}}

    def get_projection(self):
        return {"items": 1, "tender_id": 1, "awardID": 1}

    def _get_tenders_collection(self):
        return ReadonlyCollectionWrapper(self.db_store.tenders.collection)

    @property
    def _tenders_collection(self):
        return self._get_tenders_collection()

    def _get_tender(self, tender_id):
        return self._tenders_collection.find_one(
            {"_id": tender_id},
            {"criteria": 1, "items": 1, "bids": 1, "awards": 1},
        )

    @staticmethod
    def _get_award(tender, award_id):
        for award in tender.get("awards", []):
            if award["id"] == award_id:
                return award

        return None

    @staticmethod
    def _get_winning_bid(tender, award):
        if not award or not (bid_id := award.get("bid_id")):
            return None

        for bid in tender.get("bids", []):
            if bid["id"] == bid_id:
                return bid

        return None

    @staticmethod
    def _get_data_schemas(tender):
        data_schemas = {}
        for criterion in tender.get("criteria", []):
            if criterion.get("relatesTo") != "item":
                continue

            for group in criterion.get("requirementGroups", []):
                for requirement in group.get("requirements", []):
                    if requirement.get("status", "active") != "active":
                        continue

                    if requirement.get("dataSchema"):
                        data_schemas[requirement["title"]] = requirement["dataSchema"]

        return data_schemas

    @staticmethod
    def _item_key(item):
        return json.dumps(
            {
                "classification": item.get("classification") or {},
                "relatedLot": item.get("relatedLot") or "",
                "relatedBuyer": item.get("relatedBuyer") or "",
                "additionalClassifications": sorted(
                    item.get("additionalClassifications") or [],
                    key=lambda a: a.get("id", ""),
                ),
            },
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )

    def _resolve_tender_items(self, tender, items, contract_id):
        tender_items = tender.get("items") or []
        tender_items_by_id = {i["id"]: i for i in tender_items}

        tender_items_by_key = defaultdict(list)
        for tender_item in tender_items:
            tender_items_by_key[self._item_key(tender_item)].append(tender_item)

        resolved = {}
        for item in items:
            if tender_item := tender_items_by_id.get(item["id"]):
                resolved[item["id"]] = tender_item
                continue

            candidates = tender_items_by_key.get(self._item_key(item)) or []
            if len(candidates) == 1:
                resolved[item["id"]] = candidates[0]
            else:
                logger.warning(
                    f"Can't resolve tender item of split item {item['id']} "
                    f"of contract {contract_id}: {len(candidates)} candidates"
                )

        return resolved

    @staticmethod
    def _get_market_fields(tender, bid):
        market_fields = {}
        bid_items = {i["id"]: i for i in (bid or {}).get("items", [])}

        for tender_item in tender.get("items", []):
            merged = {**tender_item, **bid_items.get(tender_item["id"], {})}
            values = {field: merged[field] for field in MARKET_FIELDS if merged.get(field)}
            if values:
                market_fields[tender_item["id"]] = values

        return market_fields

    def update_document(self, doc, context=None):
        tender = self._get_tender(doc["tender_id"])
        if not tender:
            logger.warning(f"Tender {doc['tender_id']} of contract {doc['_id']} not found")
            return

        items = doc.get("items") or []
        award = self._get_award(tender, doc.get("awardID"))
        bid = self._get_winning_bid(tender, award)
        tender_items = self._resolve_tender_items(tender, items, doc["_id"])

        is_updated = False

        market_fields = self._get_market_fields(tender, bid)
        for item in items:
            tender_item = tender_items.get(item["id"])
            if not tender_item:
                continue

            for field, value in market_fields.get(tender_item["id"], {}).items():
                if field not in item:
                    item[field] = value
                    is_updated = True

        data_schemas = self._get_data_schemas(tender)

        for item in items:
            for attribute in item.get("attributes") or []:
                if data_schema := data_schemas.get(attribute.get("name")):
                    attribute["dataSchema"] = data_schema
                    is_updated = True

        if is_updated:
            return doc

        return

    def generate_base_pipeline_stages(self, doc: dict) -> list:
        return [{"$set": {"items": doc["items"], "revisions": doc["revisions"]}}]

    def run_test(self):
        gpa_title = (
            "Товар походить з однієї з країн, що підписала Угоду про державні закупівлі "
            "Світової Організації торгівлі (GPA) або іншої країни з якою Україна має "
            "міжнародні договори про державні закупівлі"
        )
        data_schema = "ISO 3166-1 alpha-2"
        classification = {
            "scheme": "LAW922",
            "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES",
        }
        product_id = "655360-30230000-889652-40000777"
        category_id = "655360-30230000-889652"

        tender_1_id = "e42f8b4d0e2e4b0a9c6a9a9c1a7c5a11"
        item_1_id = "1c1a5d0b6f9f4d3ba1f8f0e5c7a1b201"
        contract_1_id = "0d7f3f8a6a3a4a0f8e1c2b3d4e5f6a01"

        tender_2_id = "e42f8b4d0e2e4b0a9c6a9a9c1a7c5a22"
        item_2_id = "1c1a5d0b6f9f4d3ba1f8f0e5c7a1b202"
        contract_2_id = "0d7f3f8a6a3a4a0f8e1c2b3d4e5f6a02"

        tender_3_id = "e42f8b4d0e2e4b0a9c6a9a9c1a7c5a33"
        item_3_id = "1c1a5d0b6f9f4d3ba1f8f0e5c7a1b203"
        contract_3_id = "0d7f3f8a6a3a4a0f8e1c2b3d4e5f6a03"

        tender_4_id = "e42f8b4d0e2e4b0a9c6a9a9c1a7c5a44"
        item_4_id = "1c1a5d0b6f9f4d3ba1f8f0e5c7a1b204"
        contract_4_id = "0d7f3f8a6a3a4a0f8e1c2b3d4e5f6a04"

        tender_5_id = "e42f8b4d0e2e4b0a9c6a9a9c1a7c5a55"
        item_5_id = "1c1a5d0b6f9f4d3ba1f8f0e5c7a1b205"
        split_item_5_id = "1c1a5d0b6f9f4d3ba1f8f0e5c7a1b295"
        contract_5_id = "0d7f3f8a6a3a4a0f8e1c2b3d4e5f6a05"
        item_classification = {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"}

        award_id = "a1a1a1a1a1a1a1a1a1a1a1a1a1a1a101"
        bid_id = "b1b1b1b1b1b1b1b1b1b1b1b1b1b1b101"
        requirement_id = "r1r1r1r1r1r1r1r1r1r1r1r1r1r1r101"
        award_requirement_id = "r2r2r2r2r2r2r2r2r2r2r2r2r2r2r202"

        def build_contract(contract_id, tender_id, item_id, attributes=None):
            item = {"id": item_id}
            if attributes is not None:
                item["attributes"] = attributes
            return {
                "_id": contract_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "tender_id": tender_id,
                "awardID": award_id,
                "items": [item],
            }

        def build_tender(
            tender_id,
            item_id,
            requirements,
            relates_to="item",
            tender_item=None,
            bids=None,
            awards=None,
        ):
            return {
                "_id": tender_id,
                "criteria": [
                    {
                        "relatesTo": relates_to,
                        "relatedItem": item_id,
                        "classification": classification,
                        "requirementGroups": [{"requirements": requirements}],
                    }
                ],
                "items": [tender_item if tender_item is not None else {"id": item_id}],
                "bids": bids if bids is not None else [],
                "awards": awards if awards is not None else [],
            }

        contracts = [
            build_contract(
                contract_1_id,
                tender_1_id,
                item_1_id,
                [
                    {"name": gpa_title, "values": ["UA"]},
                    {"name": "Гарантія", "value": 36},
                ],
            ),
            build_contract(contract_2_id, tender_2_id, item_2_id),
            build_contract(contract_3_id, tender_3_id, item_3_id),
            build_contract(contract_4_id, tender_4_id, item_4_id),
            {
                "_id": contract_5_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "tender_id": tender_5_id,
                "awardID": award_id,
                "items": [
                    {"id": item_5_id, "classification": item_classification},
                    {"id": split_item_5_id, "classification": item_classification},
                ],
            },
        ]

        tender_find_one_results = [
            build_tender(
                tender_1_id,
                item_1_id,
                [
                    {"id": requirement_id, "title": gpa_title, "dataSchema": data_schema},
                    {"id": "other", "title": "Гарантія"},
                ],
                tender_item={"id": item_1_id, "category": category_id},
                bids=[{"id": bid_id, "items": [{"id": item_1_id, "product": product_id}]}],
                awards=[{"id": award_id, "bid_id": bid_id, "status": "active"}],
            ),
            build_tender(
                tender_2_id,
                item_2_id,
                [
                    {"id": requirement_id, "title": gpa_title, "dataSchema": data_schema},
                    {"id": award_requirement_id, "title": "Гарантія"},
                ],
                bids=[
                    {
                        "id": bid_id,
                        "requirementResponses": [
                            {"requirement": {"id": requirement_id}, "values": ["UA"]},
                        ],
                    }
                ],
                awards=[
                    {
                        "id": award_id,
                        "bid_id": bid_id,
                        "status": "active",
                        "requirementResponses": [
                            {"requirement": {"id": award_requirement_id}, "value": 36},
                        ],
                    }
                ],
            ),
            build_tender(
                tender_3_id,
                item_3_id,
                [{"id": requirement_id, "title": "Гарантія", "unit": {"name": "місяць", "code": "MON"}}],
                awards=[
                    {
                        "id": award_id,
                        "status": "active",
                        "requirementResponses": [
                            {"requirement": {"id": requirement_id}, "value": 36},
                        ],
                    }
                ],
            ),
            build_tender(
                tender_4_id,
                item_4_id,
                [{"id": requirement_id, "title": gpa_title, "dataSchema": data_schema}],
                relates_to="tenderer",
                bids=[
                    {
                        "id": bid_id,
                        "requirementResponses": [
                            {"requirement": {"id": requirement_id}, "values": ["UA"]},
                        ],
                    }
                ],
                awards=[{"id": award_id, "bid_id": bid_id, "status": "active"}],
            ),
            build_tender(
                tender_5_id,
                item_5_id,
                [{"id": requirement_id, "title": "Колір"}],
                tender_item={
                    "id": item_5_id,
                    "classification": item_classification,
                    "category": category_id,
                },
                bids=[
                    {
                        "id": bid_id,
                        "items": [{"id": item_5_id, "product": product_id}],
                        "requirementResponses": [
                            {"requirement": {"id": requirement_id}, "values": ["червоний"]},
                        ],
                    }
                ],
                awards=[{"id": award_id, "bid_id": bid_id, "status": "active"}],
            ),
        ]

        mock_tenders_collection = MagicMock(find_one=MagicMock(side_effect=tender_find_one_results))

        with patch.object(self, "_get_tenders_collection", return_value=mock_tenders_collection):
            mock_collection = self.run_test_data(contracts)

        tender_projection = {"criteria": 1, "items": 1, "bids": 1, "awards": 1}
        assert mock_tenders_collection.find_one.call_args_list == [
            call({"_id": tender_1_id}, tender_projection),
            call({"_id": tender_2_id}, tender_projection),
            call({"_id": tender_3_id}, tender_projection),
            call({"_id": tender_4_id}, tender_projection),
            call({"_id": tender_5_id}, tender_projection),
        ]

        def unpack(operation):
            set_stage, rev_stage = operation._doc
            revisions = set_stage["$set"]["revisions"]
            assert revisions[0]["author"] == "broker"
            assert revisions[-1]["author"] == "migration"
            assert rev_stage == {"$set": {"_rev": ANY}}
            return (
                operation._filter,
                set_stage["$set"]["items"],
                sorted((change["op"], change["path"]) for change in revisions[-1]["changes"]),
            )

        mock_collection.bulk_write.assert_called_once()
        (operations,), _ = mock_collection.bulk_write.call_args

        contract_rev = {"_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"}

        assert [unpack(operation) for operation in operations] == [
            (
                {"_id": contract_1_id, **contract_rev},
                [
                    {
                        "id": item_1_id,
                        "attributes": [
                            {"name": gpa_title, "values": ["UA"], "dataSchema": data_schema},
                            {"name": "Гарантія", "value": 36},
                        ],
                        "product": product_id,
                        "category": category_id,
                    }
                ],
                [
                    ("remove", "/items/0/attributes/0/dataSchema"),
                    ("remove", "/items/0/category"),
                    ("remove", "/items/0/product"),
                ],
            ),
            (
                {"_id": contract_5_id, **contract_rev},
                [
                    {
                        "id": item_5_id,
                        "classification": item_classification,
                        "product": product_id,
                        "category": category_id,
                    },
                    {
                        "id": split_item_5_id,
                        "classification": item_classification,
                        "product": product_id,
                        "category": category_id,
                    },
                ],
                [
                    ("remove", "/items/0/category"),
                    ("remove", "/items/0/product"),
                    ("remove", "/items/1/category"),
                    ("remove", "/items/1/product"),
                ],
            ),
        ]


if __name__ == "__main__":
    migrate_collection(Migration)
