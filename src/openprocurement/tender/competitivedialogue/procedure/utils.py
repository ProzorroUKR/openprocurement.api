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
