from openprocurement.contracting.core.tests.base import BaseContractWebTest


class BaseContractContentWebTest(BaseContractWebTest):
    def activate_contract(self):
        self.prepare_contract_for_signing()
        response = self.app.patch_json(
            f"/contracts/{self.contract_id}?acc_token={self.tender_token}", {"data": {"status": "active"}}
        )
        self.assertEqual(response.status, "200 OK")
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
        response = self.app.patch_json(
            "/contracts/{}/credentials?acc_token={}".format(self.contract_id, self.initial_data["access"][-1]["token"]),
            {"data": {}},
        )
        self.contract_token = response.json["access"]["token"]
        self.bid_token = self.initial_bids_tokens[0]
        self.set_status(self.initial_status)
