import unittest

from openprocurement.framework.cfaua.tests.base import BaseAgreementContentWebTest
from openprocurement.framework.cfaua.tests.data import TEST_AGREEMENT


class AgreementContractsResourceTest(BaseAgreementContentWebTest):
    initial_data = TEST_AGREEMENT

    def test_get_agreement_contracts(self):
        resp = self.app.get("/agreements/{}/contracts".format(self.agreement_id))
        self.assertEqual(resp.status, "200 OK")
        resp = self.app.get("/agreements/{}/contracts".format("some_id"), status=404)
        self.assertEqual(resp.status, "404 Not Found")

    def test_get_agreement_contracts_by_id(self):
        response = self.app.get("/agreements/{}/contracts/{}".format(self.agreement_id, "some_id"), status=404)
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
        )

        while True:
            resp = self.app.get("/agreements")
            if len(resp.json["data"]) >= 1:
                break
        agr_id = resp.json["data"][0]["id"]
        response = self.app.get("/agreements/{}/contracts".format(agr_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        contract_id = self.initial_data["contracts"][0]["id"]
        response = self.app.get("/agreements/{}/contracts/{}".format(agr_id, contract_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"], self.initial_data["contracts"][0])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AgreementContractsResourceTest))
    return suite
