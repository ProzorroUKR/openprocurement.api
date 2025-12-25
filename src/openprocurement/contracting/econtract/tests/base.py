from unittest.mock import patch

from openprocurement.contracting.core.tests.base import BaseContractWebTest
from openprocurement.contracting.econtract.tests.data import (
    test_tender_pq_e_bids,
    test_tender_pq_e_data,
    test_tender_pq_e_supplier,
)


class BaseEContractWebTest(BaseContractWebTest):
    initial_data = test_tender_pq_e_data
    initial_bids = test_tender_pq_e_bids

    def create_award(self):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards",
            {
                "data": {
                    "suppliers": [test_tender_pq_e_supplier],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "value": {"currency": "UAH", "amount": 450.0, "valueAddedTaxIncluded": True},
                }
            },
        )
        self.app.authorization = auth
        self.award = response.json["data"]
        self.award_id = self.award["id"]

    def activate_award(self):
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        with patch(
            "openprocurement.tender.core.procedure.contracting.upload_contract_pdf_document"
        ) as mock_upload_contract_pdf:
            response = self.app.patch_json(
                f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
                {"data": {"status": "active", "qualified": True}},
            )

        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contract_id = response.json["data"]["contracts"][0]["id"]
        response = self.app.get(f"/contracts/{self.contract_id}")
        self.contract = response.json["data"]
        self.bid_token = self.initial_bids_tokens[self.award["bid_id"]]

        contract_doc = self.mongodb.contracts.get(self.contract["id"])
        contract_doc["value"]["amountNet"] = 440
        self.mongodb.contracts.save(contract_doc)


class BaseEContractContentWebTest(BaseEContractWebTest):

    def activate_contract(self):
        # validate signatory without contractSignature document
        response = self.app.post_json(
            f"/contracts/{self.contract_id}/signatories?acc_token={self.contract_token}",
            {"data": {}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "documents",
                    "description": "Not enough contractSignature documents by buyer were uploaded.",
                },
            ],
        )

        # add signature for buyer
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
        # add signatory for buyer
        self.app.post_json(
            f"/contracts/{self.contract_id}/signatories?acc_token={self.contract_token}",
            {"data": {}},
        )
        # validate signatory already provided by supplier
        response = self.app.post_json(
            f"/contracts/{self.contract_id}/signatories?acc_token={self.contract_token}",
            {"data": {}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [{"location": "body", "name": "signatories", "description": "Signatory by buyer was already created."}],
        )

        # validate upload signature after signatory confirmation
        response = self.app.post_json(
            f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
            {"data": contract_sign_data},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Signatory was already confirmed."
                }
            ],
        )

        # validate signatory without contractSignature document
        response = self.app.post_json(
            f"/contracts/{self.contract_id}/signatories?acc_token={self.bid_token}",
            {"data": {}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "documents",
                    "description": "Not enough contractSignature documents by supplier were uploaded.",
                },
            ],
        )
        # add signature for supplier
        self.app.post_json(
            f"/contracts/{self.contract_id}/documents?acc_token={self.bid_token}",
            {"data": contract_sign_data},
        )
        # add signatory for supplier
        self.app.post_json(
            f"/contracts/{self.contract_id}/signatories?acc_token={self.bid_token}",
            {"data": {}},
        )
        # validate contract already activated
        response = self.app.post_json(
            f"/contracts/{self.contract_id}/signatories?acc_token={self.bid_token}",
            {"data": {}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{"location": "body", "name": "data", "description": "Operation forbidden in current (active) status"}],
        )

        # check contract status
        response = self.app.get(f"/contracts/{self.contract_id}?acc_token={self.supplier_token}")
        self.assertEqual(response.json["data"]["status"], "active")
        self.assertIn("signerInfo", response.json["data"]["buyer"])
        self.assertIn("signerInfo", response.json["data"]["suppliers"][0])

        response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract_id}?acc_token={self.tender_token}")
        self.assertEqual(response.json["data"]["status"], "active")

    def set_contract_token(self, contract_id, identifier_data):
        response = self.app.post_json(
            f"/contracts/{contract_id}/access",
            {
                "data": {
                    "identifier": identifier_data,
                }
            },
        )
        contract_token = response.json["access"]["token"]
        return contract_token

    def setUp(self):
        super().setUp()
        self.contract_token = self.set_contract_token(self.contract_id, self.contract["buyer"]["identifier"])
        self.bid_token = self.set_contract_token(self.contract_id, self.contract["suppliers"][0]["identifier"])
        self.supplier_token = self.bid_token
        self.set_contract_status(self.initial_contract_status)
