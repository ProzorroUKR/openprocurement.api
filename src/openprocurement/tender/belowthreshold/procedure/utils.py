def prepare_tender_item_for_contract(item):
    prepated_item = dict(item)
    if prepated_item.get("profile", None):
        prepated_item.pop("profile")
    return prepated_item
