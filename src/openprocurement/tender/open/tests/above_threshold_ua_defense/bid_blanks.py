from copy import deepcopy

from openprocurement.tender.core.tests.utils import set_bid_items


def bid_items_without_unit(self):
    tender = self.app.get(f"/tenders/{self.tender_id}").json["data"]
    item_id = tender["items"][0]["id"]
    self.assertIn("unit", tender["items"][0])

    bid_data = deepcopy(self.test_bids_data[0])
    set_bid_items(self, bid_data)

    # bid items are not required for defense, so unit is checked only by unit validation
    del bid_data["items"][0]["unit"]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids",
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": f"bid item.unit is required for item {item_id}",
            }
        ],
    )
