from openprocurement.api.constants import (
    MASK_OBJECT_DATA,
    MASK_IDENTIFIER_IDS,
    MASK_OBJECT_DATA_SINGLE,
)
from hashlib import sha224

EXCLUDED_FIELDS = {
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

EXCLUDED_ROLES = (
    "chronograph",
    "auction",
    "bots",
    "contracting",
    "competitive_dialogue",
    "agreements",
    "agreement_selection",
    "Administrator",
)


def mask_simple_data(v):
    if isinstance(v, str):
        v = "0" * len(v)
    elif isinstance(v, bool):
        pass
    elif isinstance(v, int) or isinstance(v, float):
        v = 0
    return v


def ignore_mask(key):
    ignore_keys = EXCLUDED_FIELDS
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
    is_masked = data.get("is_masked", False)
    if is_masked is not True or not MASK_OBJECT_DATA_SINGLE:
        # Do not show is_masked field if it is False or masking is disabled
        data.pop("is_masked", None)

    identifier_id = data.get("procuringEntity", {}).get("identifier", {}).get("id")
    if (
        not (MASK_OBJECT_DATA and identifier_id and sha224(identifier_id.encode()).hexdigest() in MASK_IDENTIFIER_IDS)
        and
        not (MASK_OBJECT_DATA_SINGLE and is_masked is True)
    ):
        # Masking is disabled or object is not masked
        return

    if request.authenticated_role in EXCLUDED_ROLES:
        # Masking is not required for these roles
        return

    revisions = data.pop("revisions", [])
    # data["transfer_token"] = uuid4().hex
    # data["owner_token"] = uuid4().hex
    mask_process_compound(data)
    data["revisions"] = revisions
    if "title" in data:
        data["title"] = "Тимчасово замасковано, щоб русня не підглядала"
    if "title_en" in data:
        data["title_en"] = "It is temporarily disguised so that the rusnya does not spy"
