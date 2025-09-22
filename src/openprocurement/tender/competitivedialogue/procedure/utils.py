from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.utils import save_object
from openprocurement.api.utils import request_init_tender
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_DEFAULT_CONFIG,
    STAGE_2_EU_TYPE,
    STAGE_2_UA_DEFAULT_CONFIG,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.serializers.tender_credentials import (
    tender_token_serializer,
)
from openprocurement.tender.core.utils import calculate_tender_full_date

COPY_NAME_FIELDS = (
    "title_ru",
    "mode",
    "procurementMethodDetails",
    "title_en",
    "description",
    "description_en",
    "description_ru",
    "title",
    "minimalStep",
    "value",
    "procuringEntity",
    "submissionMethodDetails",
    "buyers",
    "contractTemplateName",
)


def prepare_shortlistedFirms(shortlistedFirms):
    """Make list with keys
    key = {identifier_id}_{identifier_scheme}_{lot_id}
    """
    all_keys = set()
    for firm in shortlistedFirms:
        key = "{firm_id}_{firm_scheme}".format(
            firm_id=firm["identifier"]["id"], firm_scheme=firm["identifier"]["scheme"]
        )
        if firm.get("lots"):
            keys = {"{key}_{lot_id}".format(key=key, lot_id=lot["id"]) for lot in firm.get("lots")}
        else:
            keys = {key}
        all_keys |= keys
    return all_keys


def prepare_author(obj):
    """Make key
    {author.identifier.id}_{author.identifier.scheme}
    or
    {author.identifier.id}_{author.identifier.scheme}_{id}
    if obj has relatedItem and questionOf != tender or obj has relatedLot than
    """
    base_key = "{id}_{scheme}".format(
        scheme=obj["author"]["identifier"]["scheme"],
        id=obj["author"]["identifier"]["id"],
    )
    related_id = None
    if obj.get("relatedLot"):
        related_id = obj.get("relatedLot")
    elif obj.get("relatedItem") and obj.get("questionOf") in ("lot", "item"):
        related_id = obj.get("relatedItem")
    if related_id:
        base_key = "{base_key}_{id}".format(
            base_key=base_key,
            id=related_id,
        )
    return base_key


def prepare_bid_identifier(bid):
    """Make list with keys
    key = {identifier_id}_{identifier_scheme}_{lot_id}
    """
    all_keys = set()
    for tenderer in bid["tenderers"]:
        key = "{id}_{scheme}".format(id=tenderer["identifier"]["id"], scheme=tenderer["identifier"]["scheme"])
        if bid.get("lotValues"):
            keys = {"{key}_{lot_id}".format(key=key, lot_id=lot["relatedLot"]) for lot in bid.get("lotValues")}
        else:
            keys = {key}
        all_keys |= keys
    return all_keys


def get_item_by_id(tender, item_id):
    for item in tender["items"]:
        if item["id"] == item_id:
            return item


# competitiveDialogue stage2 creation logic


def prepare_stage2_tender_data(tender: dict) -> dict:
    new_tender = {
        "id": uuid4().hex,
        "procurementMethod": "selective",
        "status": "draft.stage2",
        "dialogueID": tender["_id"],
        "tenderID": f"{tender['tenderID']}.2",
        "owner": tender["owner"],
        "dialogue_token": tender_token_serializer(tender["owner_token"]),
    }

    for field_name in COPY_NAME_FIELDS:
        if field_name in tender:
            new_tender[field_name] = tender[field_name]

    if tender["procurementMethodType"].endswith("EU"):
        new_tender["procurementMethodType"] = STAGE_2_EU_TYPE
        config = STAGE_2_EU_DEFAULT_CONFIG
    else:
        new_tender["procurementMethodType"] = STAGE_2_UA_TYPE
        config = STAGE_2_UA_DEFAULT_CONFIG

    new_tender["tenderPeriod"] = {
        "startDate": get_request_now().isoformat(),
        "endDate": calculate_tender_full_date(
            get_request_now(),
            timedelta(days=config["minTenderingDuration"]),
            tender=tender,
        ).isoformat(),
    }

    old_lots = process_qualifications(tender, new_tender)
    if "features" in tender:
        process_features(new_tender, tender["features"], old_lots)

    process_criteria(tender, new_tender)

    return new_tender


def get_bid_by_id(bids: list, bid_id: str) -> dict:
    for bid in bids:
        if bid["id"] == bid_id:
            return bid


def prepare_lot(orig_tender: dict, lot_id: str, items: list) -> dict:
    lot = None
    for tender_lot in orig_tender["lots"]:
        if tender_lot["id"] == lot_id:
            lot = tender_lot
            break
    if lot["status"] != "active":
        return {}

    for item in orig_tender["items"]:
        if item.get("relatedLot") == lot_id:
            items.append(item)
    return lot


def process_qualifications(tender: dict, new_tender: dict) -> dict:
    old_lots, items, short_listed_firms = {}, [], {}
    for qualification in tender["qualifications"]:
        if qualification["status"] == "active":
            bid = get_bid_by_id(tender["bids"], qualification["bidID"])
            if qualification.get("lotID"):
                if qualification["lotID"] not in old_lots:
                    lot = prepare_lot(tender, qualification["lotID"], items)
                    if not lot:
                        continue
                    old_lots[qualification["lotID"]] = lot
                for bid_tender in bid["tenderers"]:
                    if bid_tender["identifier"]["id"] not in short_listed_firms:
                        identifier = {
                            "name": bid_tender["name"],
                            "identifier": bid_tender["identifier"],
                            "lots": [{"id": old_lots[qualification["lotID"]]["id"]}],
                        }
                        short_listed_firms[bid_tender["identifier"]["id"]] = identifier
                    else:
                        short_listed_firms[bid_tender["identifier"]["id"]]["lots"].append(
                            {"id": old_lots[qualification["lotID"]]["id"]}
                        )
            else:
                new_tender["items"] = deepcopy(tender["items"])
                for bid_tender in bid["tenderers"]:
                    if bid_tender["identifier"]["id"] not in short_listed_firms:
                        identifier = {"name": bid_tender["name"], "identifier": bid_tender["identifier"], "lots": []}
                        short_listed_firms[bid_tender["identifier"]["id"]] = identifier
    new_tender["shortlistedFirms"] = list(short_listed_firms.values())
    new_tender["lots"] = list(old_lots.values())
    if items:
        new_tender["items"] = items
    return old_lots


def process_features(new_tender: dict, features: list, old_lots: dict) -> None:
    new_tender["features"] = []
    for feature in features:
        if feature["featureOf"] == "tenderer":
            new_tender["features"].append(feature)
        elif feature["featureOf"] == "item":
            if feature["relatedItem"] in (item["id"] for item in new_tender["items"]):
                new_tender["features"].append(feature)
        elif feature["featureOf"] == "lot":
            if feature["relatedItem"] in old_lots.keys():
                new_tender["features"].append(feature)


def process_criteria(tender: dict, new_tender: dict):
    new_tender["criteria"] = []
    for criterion in tender.get("criteria", []):
        if criterion.get("classification", {}).get("id", "") == "CRITERION.OTHER.CONTRACT.GUARANTEE":
            new_tender["criteria"].append(criterion)


def save_stage_2_tender(tender: dict) -> None:
    request = get_request()
    request_init_tender(request, tender, tender_src={})
    save_object(request, "tender", insert=True)
