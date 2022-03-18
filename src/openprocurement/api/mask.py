from openprocurement.api.constants import MASK_OBJECT_DATA


def mask_simple_data(v):
    if isinstance(v, str):
        v = "0" * len(v)
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


def mask_object_data(data):
    if data is not None and MASK_OBJECT_DATA and data["procuringEntity"]["kind"] == "defense":
        revisions = data.pop("revisions", [])
        # data["transfer_token"] = uuid4().hex
        # data["owner_token"] = uuid4().hex
        mask_process_compound(data)
        data["revisions"] = revisions
        if "title" in data:
            data["title"] = "Тимчасово замасковано, щоб русня не підглядала"
        if "title_en" in data:
            data["title_en"] = "It is temporarily disguised so that the rusnya does not spy"
