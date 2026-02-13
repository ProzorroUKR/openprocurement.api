from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.contracting.core.tests.data import test_signer_info

# TenderContractResourceTest


def patch_tender_contract(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]

    items = contract["items"]
    items[0]["description"] = "New Description"

    value = contract["value"]
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"items": items}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Updated could be only ('unit', 'quantity') in item, description change forbidden",
    )

    old_currency = value["currency"]
    value["currency"] = "USD"
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    value["currency"] = old_currency
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    self.set_status("complete", {"status": "active.awarded"})

    one_hour_in_future = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"dateSigned": one_hour_in_future}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Contract signature date can't be in the future"],
                "location": "body",
                "name": "dateSigned",
            }
        ],
    )

    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"dateSigned": custom_signature_date}},
    )
    self.assertEqual(response.status, "200 OK")

    # set signerInfo for buyer
    response = self.app.put_json(
        f"/contracts/{contract['id']}/buyer/signer_info?acc_token={self.tender_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    # set signerInfo for suppliers
    response = self.app.put_json(
        f"/contracts/{contract['id']}/suppliers/signer_info?acc_token={self.bid_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
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
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")


def patch_tender_contract_datesigned(self):
    response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    contract = response.json["data"][0]

    self.set_status("complete", {"status": "active.awarded"})

    value = contract["value"]
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contract['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contract['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
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
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertIn("dateSigned", response.json["data"].keys())
