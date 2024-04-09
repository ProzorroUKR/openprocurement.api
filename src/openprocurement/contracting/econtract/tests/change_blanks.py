from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.contracting.econtract.tests.data import test_signer_info
from openprocurement.contracting.econtract.tests.utils import create_contract


def no_items_contract_change(self):
    data = deepcopy(self.initial_data)
    del data["items"]

    contract = create_contract(self, data)
    self.assertEqual(contract["status"], "pending")
    self.assertNotIn("items", contract)
    token = data["tender_token"]
    supplier_token = data["bid_token"]

    # activate contract

    response = self.app.put_json(
        f"/contracts/{contract['id']}/buyer/signer_info?acc_token={token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{contract['id']}/suppliers/signer_info?acc_token={supplier_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={token}",
        {
            "data": {
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        f"/contracts/{contract['id']}/changes?acc_token={token}",
        {"data": {"rationale": "причина зміни укр", "rationaleTypes": ["qualityImprovement"]}},
    )
    self.assertEqual(response.status, "201 Created")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}/changes/{change['id']}?acc_token={token}",
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={token}",
        {"data": {"value": {**contract["value"], "amountNet": contract["value"]["amount"] - 1}}},
    )

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={token}",
        {
            "data": {
                "status": "terminated",
                "amountPaid": {"amount": 100, "amountNet": 90, "valueAddedTaxIncluded": True, "currency": "UAH"},
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")

    response = self.app.get(f"/contracts/{contract['id']}")
    self.assertNotIn("items", response.json["data"])


def change_date_signed(self):
    self.set_status("active")

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "contractNumber": "№ 146",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertEqual(change["contractNumber"], "№ 146")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update contract change status. 'dateSigned' is required.",
            }
        ],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": "12-14-11"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "dateSigned", "description": ["Could not parse 12-14-11. Should be ISO8601."]}],
    )

    valid_date1_raw = get_now()
    valid_date1 = valid_date1_raw.isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": valid_date1}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["dateSigned"], valid_date1)

    one_day_in_past = (get_now() - timedelta(days=1)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": one_day_in_past}},
        status=403,
    )
    self.assertIn("can't be earlier than contract dateSigned", response.json["errors"][0]["description"])

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": get_now().isoformat()}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update contract change in current (active) status",
            }
        ],
    )

    response = self.app.get(f"/contracts/{self.contract['id']}/changes/{change['id']}")
    change1 = response.json["data"]
    self.assertEqual(change1["dateSigned"], valid_date1)

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "iнша причина зміни укр",
                "rationale_en": "another change cause en",
                "rationaleTypes": ["priceReduction"],
                "contractNumber": "№ 147",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change2 = response.json["data"]
    self.assertEqual(change["status"], "pending")

    one_day_in_future = (get_now() + timedelta(days=1)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change2['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": one_day_in_future}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "dateSigned",
                "description": ["Contract signature date can't be in the future"],
            }
        ],
    )

    smaller_than_last_change = (valid_date1_raw - timedelta(seconds=1)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change2['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": smaller_than_last_change}},
        status=403,
    )
    self.assertEqual(
        f"Change dateSigned ({smaller_than_last_change}) can't "
        f"be earlier than last active change dateSigned ({valid_date1})",
        response.json["errors"][0]["description"],
    )

    date = get_now().isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change2['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": date}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["dateSigned"], date)

    # date update request
    valid_date2_raw = get_now()
    valid_date2 = valid_date2_raw.isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change2['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": valid_date2}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["dateSigned"], valid_date2)

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change2['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["dateSigned"], valid_date2)

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "третя причина зміни укр",
                "rationale_en": "third change cause en",
                "rationaleTypes": ["priceReduction"],
                "contractNumber": "№ 148",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    change3 = response.json["data"]
    self.assertEqual(change["status"], "pending")

    smaller_than_last_change = (valid_date2_raw - timedelta(seconds=1)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change3['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": smaller_than_last_change}},
        status=403,
    )
    self.assertEqual(
        f"Change dateSigned ({smaller_than_last_change}) can't "
        f"be earlier than last active change dateSigned ({valid_date2})",
        response.json["errors"][0]["description"],
    )

    date = get_now().isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change3['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": date}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["dateSigned"], date)

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change3['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"value": {**self.contract["value"], "amountNet": self.contract["value"]["amount"] - 1}}},
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"status": "terminated", "amountPaid": {"amount": 15, "amountNet": 14}}},
    )
    self.assertEqual(response.status, "200 OK")


def date_signed_on_change_creation(self):
    # test create change with date signed
    self.set_status("active")

    now = get_now()
    one_day_in_past = (now - timedelta(days=1)).isoformat()

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "dateSigned": one_day_in_past,
                "rationaleTypes": ["priceReduction"],
                "contractNumber": "№ 146",
            }
        },
        status=403,
    )
    self.assertIn("can't be earlier than contract dateSigned", response.json["errors"][0]["description"])

    one_day_in_future = (now + timedelta(days=1)).isoformat()
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "dateSigned": one_day_in_future,
                "rationaleTypes": ["priceReduction"],
                "contractNumber": "№ 146",
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "dateSigned",
                "description": ["Contract signature date can't be in the future"],
            }
        ],
    )

    date = get_now().isoformat()
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "dateSigned": date,
                "rationaleTypes": ["priceReduction"],
                "contractNumber": "№ 146",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["dateSigned"], date)

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
