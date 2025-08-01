from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.tests.base import BaseContractWebTest
from openprocurement.contracting.core.tests.utils import create_contract
from openprocurement.contracting.econtract.tests.data import test_econtract_data


class BaseEContractWebTest(BaseContractWebTest):
    def create_contract(self):
        for tender_contract in self.tender_document.get("contracts", ""):
            contract = self.initial_data
            contract.update(tender_contract)
            contract.update(
                {
                    "tender_id": self.tender_id,
                    "access": [
                        {"owner": "broker", "role": AccessRole.SUPPLIER},
                        {
                            "owner": self.tender_document["owner"],
                            "role": AccessRole.BUYER,
                        },
                    ],
                }
            )
            self.contract_id = contract["id"]
            self.contract = create_contract(self, contract)


class BaseEContractContentWebTest(BaseEContractWebTest):
    initial_data = test_econtract_data

    def activate_contract(self):
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
        # add signature for supplier
        self.app.post_json(
            f"/contracts/{self.contract_id}/documents?acc_token={self.bid_token}",
            {"data": contract_sign_data},
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
        self.set_status(self.initial_status)
