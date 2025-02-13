from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.contracting.core.procedure.models.change import RATIONALE_TYPES
from openprocurement.contracting.econtract.tests.data import test_signer_info
from openprocurement.contracting.econtract.tests.utils import create_contract


def not_found(self):
    response = self.app.get("/contracts/some_id/changes", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.get(f"/contracts/{self.contract['id']}/changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get(f"/contracts/{self.contract['id']}/changes/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "change_id"}])

    response = self.app.patch_json(f"/contracts/{self.contract['id']}/changes/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "change_id"}])


def get_change(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "Принцеси не какають.",
                "rationale_ru": "ff",
                "rationale_en": "asdf",
                "contractNumber": 12,
                "rationaleTypes": ["priceReduction"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertIn("date", change)

    response = self.app.get(f"/contracts/{self.contract['id']}/changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(f"/contracts/{self.contract['id']}/changes/{change['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    change_data = response.json["data"]
    self.assertEqual(change_data, change)

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertIn("changes", response.json["data"])
    self.assertEqual(len(response.json["data"]["changes"]), 1)
    self.assertEqual(
        set(response.json["data"]["changes"][0].keys()),
        {"id", "date", "status", "rationaleTypes", "rationale", "rationale_ru", "rationale_en", "contractNumber"},
    )

    self.app.authorization = None
    response = self.app.get(f"/contracts/{self.contract['id']}/changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        {"id", "date", "status", "rationaleTypes", "rationale", "rationale_ru", "rationale_en", "contractNumber"},
    )


def create_change_invalid(self):
    response = self.app.post(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}", "data", status=415
    )
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Content-Type header should be one of ['application/json']",
                "location": "header",
                "name": "Content-Type",
            }
        ],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}", {"data": {}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "rationale", "description": ["This field is required."]},
            {"location": "body", "name": "rationaleTypes", "description": ["This field is required."]},
        ],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {"data": {"rationale": "", "rationaleTypes": ["volumeCuts"]}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "rationale", "description": ["String value is too short."]}],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {"data": {"rationale_ua": ""}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "rationale_ua", "description": "Rogue field"}]
    )
    self.app.authorization = None
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {"data": {"rationale_ua": "aaa"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes", {"data": {"rationale_ua": "aaa"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"value": {**self.contract["value"], "amountNet": self.contract["value"]["amountNet"] - 1}}},
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"changes": [{"rationale": "penguin", "rationaleTypes": ["volumeCuts"]}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.json["errors"], [{"location": "body", "name": "changes", "description": "Rogue field"}])

    response = self.app.get(f"/contracts/{self.contract['id']}?acc_token={self.contract_token}")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("changes", response.json["data"])


def create_change(self):
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["qualityImprovement"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]
    self.assertEqual(change["status"], "pending")
    self.assertIn("date", change)

    response = self.app.get(f"/contracts/{self.contract['id']}/changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {"data": {"rationale": "трататата", "rationaleTypes": ["priceReduction"]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't create new contract change while any (pending) change exists",
            }
        ],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {"data": {"rationale": "трататата", "rationaleTypes": ["non-existing-rationale"]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "rationaleTypes",
                "description": [[f"Value must be one of {RATIONALE_TYPES}."]],
            }
        ],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {"data": {"rationale": "трататата", "rationaleTypes": ["priceReduction"]}},
    )
    self.assertEqual(response.status, "201 Created")
    change2 = response.json["data"]
    self.assertEqual(change2["status"], "pending")

    response = self.app.get(f"/contracts/{self.contract['id']}/changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)


def patch_change(self):
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
    creation_date = change["date"]

    now = get_now().isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.body, b"null")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"rationale_ru": "шота на руськом"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("rationale_ru", response.json["data"])
    first_patch_date = response.json["data"]["date"]
    self.assertEqual(first_patch_date, creation_date)

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"rationale_en": "another cause desctiption"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["rationale_en"], "another cause desctiption")
    second_patch_date = response.json["data"]["date"]
    self.assertEqual(first_patch_date, second_patch_date)

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"rationaleTypes": ["fiscalYearExtension", "priceReduction"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["rationaleTypes"], ["fiscalYearExtension", "priceReduction"])

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"rationaleTypes": ["fiscalYearExtension", "volumeCuts", "taxRate"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["rationaleTypes"], ["fiscalYearExtension", "volumeCuts", "taxRate"])

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"rationaleTypes": "fiscalYearExtension"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["rationaleTypes"], ["fiscalYearExtension"])

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"rationaleTypes": "fiscalYearExtension, volumeCuts"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "rationaleTypes",
                "description": [[f"Value must be one of {RATIONALE_TYPES}."]],
            }
        ],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"rationaleTypes": []}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "rationaleTypes", "description": ["Please provide at least 1 item."]}],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"id": "1234" * 8}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "id", "description": "Rogue field"}],
    )

    self.app.authorization = None
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"rationale_en": "la-la-la"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}",
        {"data": {"rationale_en": "la-la-la"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotEqual(response.json["data"]["date"], creation_date)
    self.assertNotEqual(response.json["data"]["date"], first_patch_date)
    self.assertNotEqual(response.json["data"]["date"], second_patch_date)

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")


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
        {"data": {"value": {**self.contract["value"], "amountNet": self.contract["value"]["amountNet"] - 1}}},
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


def change_date_signed_very_old_contracts_data(self):
    # prepare old contract data
    contract = self.mongodb.contracts.get(self.contract["id"])
    contract["dateSigned"] = None

    self.mongodb.contracts.save(contract)

    response = self.app.get(f"/contracts/{self.contract['id']}?acc_token={self.contract_token}")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("dateSigned", response.json["data"])

    self.app.authorization = ("Basic", ("broker", ""))
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

    one_day_in_past = (get_now() - timedelta(days=1)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active", "dateSigned": one_day_in_past}},
    )
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["dateSigned"], one_day_in_past)

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

    two_days_in_past = (get_now() - timedelta(days=2)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change2['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": two_days_in_past}},
        status=403,
    )
    self.assertEqual(
        f"Change dateSigned ({two_days_in_past}) can't "
        f"be earlier than last active change dateSigned ({one_day_in_past})",
        response.json["errors"][0]["description"],
    )

    valid_date = get_now().isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change2['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active", "dateSigned": valid_date}},
    )
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["dateSigned"], valid_date)

    # prepare old contract change data
    contract = self.mongodb.contracts.get(self.contract["id"])
    last_change = contract["changes"][-1]
    last_change["dateSigned"] = None
    self.mongodb.contracts.save(contract)

    response = self.app.get(
        f"/contracts/{self.contract['id']}/changes/{last_change['id']}?acc_token={self.contract_token}"
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("dateSigned", response.json["data"])

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

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change3['id']}?acc_token={self.contract_token}",
        {"data": {"dateSigned": two_days_in_past}},
        status=403,
    )
    self.assertEqual(
        f"Change dateSigned ({two_days_in_past}) can't "
        f"be earlier than last active change dateSigned ({last_change['date'].isoformat()})",
        response.json["errors"][0]["description"],
    )

    valid_date2 = get_now().isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change3['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active", "dateSigned": valid_date2}},
    )
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["dateSigned"], valid_date2)


def date_signed_on_change_creation_for_very_old_contracts_data(self):
    # prepare old contract data
    contract = self.mongodb.contracts.get(self.contract["id"])
    contract["dateSigned"] = None
    self.mongodb.contracts.save(contract)

    response = self.app.get(f"/contracts/{self.contract['id']}?acc_token={self.contract_token}")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("dateSigned", response.json["data"])

    self.app.authorization = ("Basic", ("broker", ""))
    one_day_in_past = (get_now() - timedelta(days=1)).isoformat()
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
                "contractNumber": "№ 146",
                "dateSigned": one_day_in_past,
            }
        },
    )
    self.assertEqual(response.json["data"]["dateSigned"], one_day_in_past)
    change = response.json["data"]
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.json["data"]["status"], "active")

    # prepare old contract change data
    contract = self.mongodb.contracts.get(self.contract["id"])
    last_change = contract["changes"][-1]
    last_change["dateSigned"] = None
    self.mongodb.contracts.save(contract)

    response = self.app.get(
        f"/contracts/{self.contract['id']}/changes/{last_change['id']}?acc_token={self.contract_token}"
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("dateSigned", response.json["data"])

    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "третя причина зміни укр",
                "rationale_en": "third change cause en",
                "rationaleTypes": ["priceReduction"],
                "contractNumber": "№ 148",
                "dateSigned": one_day_in_past,
            }
        },
        status=403,
    )
    self.assertEqual(
        f"Change dateSigned ({one_day_in_past}) can't "
        f"be earlier than last active change dateSigned ({last_change['date'].isoformat()})",
        response.json["errors"][0]["description"],
    )

    valid_date = get_now().isoformat()
    response = self.app.post_json(
        f"/contracts/{self.contract['id']}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "третя причина зміни укр",
                "rationale_en": "third change cause en",
                "rationaleTypes": ["priceReduction"],
                "contractNumber": "№ 148",
                "dateSigned": valid_date,
            }
        },
    )
    self.assertEqual(response.json["data"]["dateSigned"], valid_date)


def patch_change_after_contract_is_already_terminated(self):
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

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"status": "terminated", "amountPaid": {"amount": 15, "amountNet": 14}}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update contract in current (terminated) status",
    )
