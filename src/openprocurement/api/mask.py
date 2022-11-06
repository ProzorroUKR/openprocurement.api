from openprocurement.api.constants import MASK_OBJECT_DATA, MASK_IDENTIFIER_IDS
from hashlib import sha224


def mask_simple_data(v):
    if isinstance(v, str):
        v = "0" * len(v)
    elif isinstance(v, bool):
        pass
    elif isinstance(v, int) or isinstance(v, float):
        v = 0
    return v


def ignore_mask(key):
    ignore_keys = {
        "mode",
        "submissionMethod",
        "submissionMethodDetails",
        "awardCriteria",
        "owner",
        "scheme",
        "currency",
        "qualified",
        "eligible",

        "_id",
        "id",
        "tender_id",
        "bid_id",
        "bidID",
        "lotID",
        "complaintID",
        "awardID",
        "planID",
        "hash",

        "relatesTo",
        "relatedLot",
        "documentOf",
        "contractID",
        "relatedItem",
        "rationaleType",
        "type",

        "transfer_token",
        "owner_token",

        "agreementDuration",
        "clarificationsUntil",
        "shouldStartAfter",
        "status",
        "tenderID",
        "procurementMethod",
        "procurementMethodType",
        "next_check",
    }
    if key in ignore_keys:
        return True
    elif key.startswith("date") or key.endswith("Date"):
        return True


def mask_process_compound(data):
    if isinstance(data, list):
        data = [mask_process_compound(e) for e in data]
    elif isinstance(data, dict):
        for i, j in data.items():
            if not ignore_mask(i):
                j = mask_process_compound(j)
                if i == "identifier":  # identifier.id
                    j["id"] = mask_simple_data(j["id"])
            data[i] = j
    else:
        data = mask_simple_data(data)
    return data


def mask_object_data(request, data):
    if not MASK_OBJECT_DATA:
        # Masking is disabled
        return

    if data is None:
        # Nothing to mask
        return

    if request.authenticated_role in (
        "chronograph",
        "auction",
        "bots",
        "contracting",
        "competitive_dialogue",
        "agreements",
        "agreement_selection",
        "Administrator",
    ):
        # Masking is not required for these roles
        return

    identifier_id = data.get("procuringEntity", {}).get("identifier", {}).get("id")
    is_masked = data.get("is_masked", False)
    if (
        (identifier_id and sha224(identifier_id.encode()).hexdigest() in MASK_IDENTIFIER_IDS)
        or is_masked is True
    ):
        revisions = data.pop("revisions", [])
        # data["transfer_token"] = uuid4().hex
        # data["owner_token"] = uuid4().hex
        mask_process_compound(data)
        data["revisions"] = revisions
        if "title" in data:
            data["title"] = "Тимчасово замасковано, щоб русня не підглядала"
        if "title_en" in data:
            data["title_en"] = "It is temporarily disguised so that the rusnya does not spy"
