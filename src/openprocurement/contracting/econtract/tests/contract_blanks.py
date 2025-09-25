from copy import deepcopy
from uuid import uuid4

import mock

from openprocurement.contracting.core.tests.data import test_signer_info
from openprocurement.tender.core.tests.utils import change_auth


def contract_activate(self):
    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "signerInfo field for buyer and suppliers is required for contract in `active` status",
            }
        ],
    )

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/buyer/signer_info?acc_token={self.contract_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/suppliers/signer_info?acc_token={self.bid_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "period is required for contract in `active` status",
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {
            "data": {
                "status": "active",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "contractNumber is required for contract in `active` status",
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {
            "data": {
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    # try to activate contract
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "contractSignature document type for all participants is required for contract in `active` status",
            }
        ],
    )

    # add signature only for buyer
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {"data": contract_sign_data},
    )

    # try to activate again
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "contractSignature document type for all participants is required f"
                "or contract in `active` status",
            }
        ],
    )

    # add signature for supplier
    self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.bid_token}",
        {"data": contract_sign_data},
    )

    # it is automatically activated after second signature
    response = self.app.get(f"/contracts/{self.contract['id']}?acc_token={self.contract_token}")
    self.assertEqual(response.json["data"]["status"], "active")


def update_pending_contract_forbidden(self):
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {"data": {"title": "new contract"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update contract in current (pending) status",
            }
        ],
    )


def post_new_version_of_contract(self):
    with change_auth(self.app, ("Basic", ("brokerx", ""))):
        response = self.app.post_json(
            "/contracts",
            {"data": self.initial_data},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "url",
                    "name": "accreditation",
                    "description": "Broker Accreditation level does not permit contract creation",
                }
            ],
        )

    contract_data = deepcopy(self.initial_data)
    # invalid tender id
    contract_data["tender_id"] = uuid4().hex
    response = self.app.post_json(
        "/contracts",
        {"data": contract_data},
        status=404,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "url", "name": "tender_id", "description": "Not Found"}],
    )

    contract_data["tender_id"] = self.tender_id
    response = self.app.post_json(
        "/contracts",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Previous version of pending contract with cancellations not found",
            }
        ],
    )

    # add cancellation by supplier
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.supplier_token}",
        {"data": {"reasonType": "requiresChanges", "reason": "want to change info"}},
    )
    self.assertEqual(response.status, "201 Created")

    # try to create contract without token
    response = self.app.post_json(
        "/contracts",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Role isn't found, check auth and token"}],
    )

    # try to change forbidden field
    contract_data["title_ru"] = "New contract"
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Updated could be only ('items', 'value', 'period', 'title', 'title_en', 'description', 'description_en', 'dateSigned', 'suppliers') in contract, title_ru change forbidden",
            }
        ],
    )

    del contract_data["title_ru"]
    contract_data["items"][0]["deliveryDate"] = {
        "startDate": "2022-01-01",
    }
    contract_data.update(
        {
            "period": {
                "startDate": "2022-01-01",
                "endDate": "2026-01-01",
            },
        }
    )
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Updated could be only ('unit', 'quantity') in item, deliveryDate change forbidden",
            }
        ],
    )

    contract_data["items"][0]["deliveryDate"] = self.initial_data["items"][0]["deliveryDate"]
    contract_data["value"]["currency"] = "USD"
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "value", "description": "Can't update currency for contract value"}],
    )

    contract_data["value"]["currency"] = "UAH"
    contract_data["value"]["amount"] = 100
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "value",
                "description": "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
            }
        ],
    )

    contract_data["value"] = deepcopy(self.initial_data["value"])
    del contract_data["value"]["amountNet"]
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "value", "description": {"amountNet": "This field is required."}}],
    )

    contract_data["value"]["amountNet"] = contract_data["value"]["amount"]
    contract_data["suppliers"][0]["name"] = "new name"
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Updated could be only signerInfo in suppliers, name change forbidden",
            }
        ],
    )

    contract_data["suppliers"] = deepcopy(self.initial_data["suppliers"])
    contract_data["suppliers"][0]["signerInfo"].update(
        {
            "email": "new@gmail.com",
            "name": "New supplier",
        }
    )

    pdf_data = {
        "url": self.generate_docservice_url(),
        "format": "application/pdf",
        "hash": "md5:" + "0" * 32,
        "title": "contract.pdf",
    }

    with mock.patch(
        "openprocurement.tender.core.procedure.contracting.upload_contract_pdf"
    ) as mock_upload_contract_pdf:
        mock_upload_contract_pdf.return_value = {"data": pdf_data}
        response = self.app.post_json(
            f"/contracts?acc_token={self.supplier_token}",
            {"data": contract_data},
        )
        mock_upload_contract_pdf.assert_called_once()

    new_contract = response.json["data"]
    self.assertEqual(new_contract["status"], "pending")
    self.assertEqual(new_contract["author"], "supplier")
    self.assertEqual(new_contract["suppliers"][0]["signerInfo"]["email"], "new@gmail.com")

    self.assertIn("documents", new_contract)
    self.assertEqual(new_contract["documents"][0]["documentType"], "contractNotice")
    self.assertEqual(new_contract["documents"][0]["format"], pdf_data["format"])
    self.assertEqual(new_contract["documents"][0]["hash"], pdf_data["hash"])
    self.assertEqual(new_contract["documents"][0]["title"], pdf_data["title"])
    self.assertIn("url", new_contract["documents"][0])
    self.assertIn("datePublished", new_contract["documents"][0])
    self.assertIn("dateModified", new_contract["documents"][0])

    response = self.app.get(
        f"/tenders/{self.tender_id}/contracts",
    )
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0]["status"], "cancelled")
    self.assertEqual(response.json["data"][1]["status"], "pending")

    response = self.app.get(
        f"/contracts?acc_token={self.supplier_token}",
    )
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(
        f"/contracts/{self.contract_id}",
    )
    prev_contract = response.json["data"]
    self.assertEqual(prev_contract["status"], "cancelled")
    self.assertEqual(prev_contract["cancellations"][0]["status"], "active")

    response = self.app.get(
        f"/contracts/{new_contract['id']}",
    )
    new_contract = response.json["data"]
    self.assertEqual(new_contract["status"], "pending")
    self.assertNotEqual(prev_contract["contractID"], new_contract["contractID"])
    self.assertNotEqual(prev_contract["dateCreated"], new_contract["dateCreated"])
