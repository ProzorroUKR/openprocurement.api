from uuid import uuid4

from copy import deepcopy


def set_tender_lots(tender, lots):
    tender["lots"] = []
    for lot in lots:
        lot = deepcopy(lot)
        lot["id"] = uuid4().hex
        tender["lots"].append(lot)
    for i, item in enumerate(tender["items"]):
        item["relatedLot"] = tender["lots"][i % len(tender["lots"])]["id"]
    return tender


def set_tender_criteria(criteria, lots, items):
    for i, criterion in enumerate(criteria):
        if lots and criterion["relatesTo"] == "lot":
            criterion["relatedItem"] = lots[i % len(lots)]["id"]
        elif items and criterion["relatesTo"] == "item":
            criterion["relatedItem"] = items[i % len(lots)]["id"]
    return criteria


def set_bid_responses(criteria):
    rrs = []
    for criterion in criteria:
        for req in criterion["requirementGroups"][0]["requirements"]:
            if criterion["source"] == "tenderer":
                rrs.append(
                    {
                        "title": "Requirement response",
                        "description": "some description",
                        "requirement": {
                            "id": req["id"],
                            "title": req["title"],
                        },
                        "value": True,
                    },
                )
    return rrs


def set_bid_lotvalues(bid, lots):
    try:
        value = bid.pop("value", None) or bid["lotValues"][0]["value"]
    except KeyError:
        bid["lotValues"] = [{"relatedLot": lot["id"]} for lot in lots]
    else:
        bid["lotValues"] = [{"value": value, "relatedLot": lot["id"]} for lot in lots]
    return bid


def set_tender_multi_buyers(_test_tender_data, _test_item, _test_organization):
    _tender_data = deepcopy(_test_tender_data)

    # create 3 items
    test_item1 = deepcopy(_test_item)
    test_item1["description"] = "телевізори"

    test_item2 = deepcopy(_test_item)
    test_item2["description"] = "портфелі"
    test_item2.pop("id", None)

    test_item3 = deepcopy(_test_item)
    test_item3["description"] = "столи"
    test_item3.pop("id", None)

    _tender_data["items"] = [test_item1, test_item2, test_item2]

    # create 2 buyers
    buyer1_id = uuid4().hex
    buyer2_id = uuid4().hex

    _test_organization_1 = deepcopy(_test_organization)
    _test_organization_2 = deepcopy(_test_organization)
    _test_organization_2["identifier"]["id"] = "00037254"

    _tender_data["buyers"] = [
        {
            "id": buyer1_id,
            "name": _test_organization_1["name"],
            "identifier": _test_organization_1["identifier"]
        },
        {
            "id": buyer2_id,
            "name": _test_organization_2["name"],
            "identifier": _test_organization_2["identifier"]
        },
    ]
    # assign items to buyers
    _tender_data["items"][0]["relatedBuyer"] = buyer1_id
    _tender_data["items"][1]["relatedBuyer"] = buyer2_id
    _tender_data["items"][2]["relatedBuyer"] = buyer2_id

    return _tender_data
