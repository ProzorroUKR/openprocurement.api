import datetime
from copy import deepcopy
from datetime import timedelta

from ciso8601 import parse_datetime

from openprocurement.framework.electroniccatalogue.tests.base import test_electronicCatalogue_data


def create_agreement(self):
    response = self.app.patch_json(
        f"/qualifications/{self.qualification_id}?acc_token={self.framework_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    qualification_data = response.json["data"]

    # Check framework was updated
    response = self.app.get(f"/frameworks/{self.framework_id}")
    self.assertEqual(response.status, "200 OK")
    framework_data = response.json["data"]
    self.assertIsNotNone(framework_data["agreementID"])

    # Check agreement was created with correct data
    agreementID = self.agreement_id = framework_data["agreementID"]
    response = self.app.get(f"/agreements/{agreementID}")
    self.assertEqual(response.status, "200 OK")
    agreement_data = response.json["data"]
    self.assertEqual(agreement_data["frameworkID"], framework_data["id"])
    self.assertEqual(agreement_data["agreementType"], framework_data["frameworkType"])
    self.assertEqual(agreement_data["classification"], framework_data["classification"])
    self.assertEqual(agreement_data["additionalClassifications"], framework_data["additionalClassifications"])
    self.assertEqual(agreement_data["procuringEntity"], framework_data["procuringEntity"])
    self.assertEqual(agreement_data["period"]["endDate"], framework_data["qualificationPeriod"]["endDate"])
    self.assertEqual(agreement_data["status"], "active")
    self.assertAlmostEqual(
        parse_datetime(agreement_data["period"]["startDate"]),
        parse_datetime(qualification_data["date"]),
        delta=datetime.timedelta(60)
    )

    # Check contract was created and created with correct data
    response = self.app.get(f"/submissions/{self.submission_id}")
    submission_data = response.json["data"]

    self.assertIsNotNone(agreement_data.get("contracts"))
    self.assertEqual(len(agreement_data["contracts"]), 1)

    contract_data = agreement_data["contracts"][0]
    self.assertEqual(contract_data["status"], "active")
    self.assertEqual(contract_data["suppliers"], submission_data["tenderers"])
    self.assertEqual(contract_data["qualificationID"], self.qualification_id)

    self.assertIsNotNone(contract_data.get("milestones"))
    self.assertEqual(len(contract_data["milestones"]), 1)
    self.assertEqual(contract_data["milestones"][0]["type"], "activation")
    self.assertEqual(contract_data["milestones"][0]["documents"], qualification_data["documents"])
    self.assertIsNone(contract_data["milestones"][0].get("dueDate"))


def change_agreement(self):
    new_endDate = (
            parse_datetime(test_electronicCatalogue_data["qualificationPeriod"]["endDate"]) - timedelta(days=1)
    ).isoformat()

    response = self.app.patch_json(
        f"/frameworks/{self.framework_id}?acc_token={self.framework_token}",
        {"data": {"qualificationPeriod": {"endDate": new_endDate}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["qualificationPeriod"]["endDate"], new_endDate)

    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["period"]["endDate"], new_endDate)

    new_procuringEntity = deepcopy(test_electronicCatalogue_data["procuringEntity"])
    new_procuringEntity["contactPoint"]["telephone"] = "+380440000000"
    response = self.app.patch_json(
        f"/frameworks/{self.framework_id}?acc_token={self.framework_token}",
        {"data": {"procuringEntity": new_procuringEntity}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procuringEntity"], new_procuringEntity)

    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procuringEntity"], new_procuringEntity)
