from copy import deepcopy

from openprocurement.tender.core.tests.utils import set_bid_items


def post_bid_multi_currency(self):
    """valueCurrencyEquality=False: the bid value isn't limited by the lot value and may be in another currency"""
    tender = self.mongodb.tenders.get(self.tender_id)
    lot = tender["lots"][0]

    bid_data = deepcopy(self.test_bids_data[0])
    value = bid_data.pop("value", None)
    value["amount"] = lot["value"]["amount"] * 2
    bid_data["lotValues"] = [{"value": value, "relatedLot": lot["id"]}]
    set_bid_items(self, bid_data, tender["items"])
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": bid_data}, status=201)
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], value["amount"])

    bid_data = deepcopy(self.test_bids_data[1])
    value = bid_data.pop("value", None)
    value["currency"] = "EUR"
    bid_data["lotValues"] = [{"value": value, "relatedLot": lot["id"]}]
    set_bid_items(self, bid_data, tender["items"])
    for item in bid_data["items"]:
        item["unit"]["value"]["currency"] = "EUR"
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": bid_data}, status=201)
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["currency"], "EUR")
