import datetime
from copy import deepcopy
from datetime import timedelta

from ciso8601 import parse_datetime
from freezegun import freeze_time

from openprocurement.api.mask import MASK_STRING
from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import get_now
from openprocurement.framework.core.procedure.models.milestone import (
    CONTRACT_BAN_DURATION,
)
from openprocurement.framework.core.utils import MILESTONE_CONTRACT_STATUSES
from openprocurement.framework.dps.tests.base import (
    ban_milestone_data,
    ban_milestone_data_with_documents,
)


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
    self.assertEqual(agreement_data.get("frameworkDetails"), framework_data.get("frameworkDetails"))
    self.assertEqual(agreement_data["status"], "active")
    self.assertAlmostEqual(
        parse_datetime(agreement_data["period"]["startDate"]),
        parse_datetime(qualification_data["date"]),
        delta=datetime.timedelta(60),
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
    self.assertEqual(contract_data["submissionID"], submission_data["id"])

    self.assertIsNotNone(contract_data.get("milestones"))
    self.assertEqual(len(contract_data["milestones"]), 1)
    self.assertEqual(contract_data["milestones"][0]["type"], "activation")


def create_agreement_config_test(self):
    # Create framework
    config = deepcopy(self.initial_config)
    config["test"] = True
    self.create_framework(config=config)
    response = self.activate_framework()

    framework = response.json["data"]
    self.assertNotIn("config", framework)
    self.assertEqual(framework["mode"], "test")
    self.assertTrue(response.json["config"]["test"])

    # Create and activate submission
    self.create_submission()
    response = self.activate_submission()

    qualification_id = response.json["data"]["qualificationID"]

    # Activate qualification
    response = self.activate_qualification()

    # Check framework was updated
    response = self.app.get(f"/frameworks/{self.framework_id}")
    self.assertEqual(response.status, "200 OK")
    framework_data = response.json["data"]
    self.assertIsNotNone(framework_data["agreementID"])

    agreement_id = self.agreement_id = framework_data["agreementID"]

    # Check agreement
    expected_config = {
        "test": True,
        "restricted": False,
    }

    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(agreement_id, self.framework_token),
        {"data": {"status": "terminated"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    agreement = response.json["data"]
    self.assertNotIn("config", agreement)
    self.assertEqual(agreement["mode"], "test")
    self.assertEqual(response.json["config"], expected_config)

    response = self.app.get("/agreements/{}".format(agreement_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    agreement = response.json["data"]
    self.assertNotIn("config", agreement)
    self.assertEqual(agreement["mode"], "test")
    self.assertEqual(response.json["config"], expected_config)


def create_agreement_config_restricted(self):
    # Create framework
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        data = deepcopy(self.initial_data)
        data["procuringEntity"]["kind"] = "defense"
        config = deepcopy(self.initial_config)
        config["restrictedDerivatives"] = True
        self.create_framework(data=data, config=config)
        response = self.activate_framework()

        framework = response.json["data"]

        self.assertEqual(framework["procuringEntity"]["kind"], "defense")

    # Create and activate submission
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        config = deepcopy(self.initial_submission_config)
        config["restricted"] = True

        response = self.create_submission(config=config)
        response = self.activate_submission()

        submission = response.json["data"]
        qualification_id = submission["qualificationID"]

    # Activate qualification
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        expected_config = {
            "restricted": True,
        }

        response = self.activate_qualification()

        # Check framework was updated
        response = self.app.get(f"/frameworks/{self.framework_id}")
        self.assertEqual(response.status, "200 OK")
        framework_data = response.json["data"]
        self.assertIsNotNone(framework_data["agreementID"])

        agreement_id = self.agreement_id = framework_data["agreementID"]

        # Check agreement
        expected_config = {
            "restricted": True,
        }

        response = self.app.patch_json(
            "/agreements/{}?acc_token={}".format(agreement_id, self.framework_token),
            {"data": {"status": "terminated"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        agreement = response.json["data"]
        self.assertEqual(response.json["config"], expected_config)

        response = self.app.get("/agreements/{}".format(agreement_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        agreement = response.json["data"]
        self.assertEqual(response.json["config"], expected_config)

    # Check access
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        # Check object
        response = self.app.get("/agreements/{}".format(agreement_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertNotEqual(
            response.json["data"]["contracts"][0]["suppliers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )

        # Check listing
        response = self.app.get("/agreements?opt_fields=status")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        submissions = response.json["data"]
        self.assertEqual(len(submissions), 1)
        self.assertEqual(
            set(submissions[0].keys()),
            {
                "id",
                "dateModified",
                "status",
            },
        )

    # Check access (no accreditation for restricted)
    with change_auth(self.app, ("Basic", ("broker", ""))):

        # Check object
        response = self.app.get("/agreements/{}".format(agreement_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"]["contracts"][0]["suppliers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )

    # Check access (anonymous)
    with change_auth(self.app, ("Basic", ("", ""))):

        # Check object
        response = self.app.get("/agreements/{}".format(agreement_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"]["contracts"][0]["suppliers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )

        # Check listing
        response = self.app.get("/agreements?opt_fields=status")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        submissions = response.json["data"]
        self.assertEqual(len(submissions), 1)
        self.assertEqual(
            set(submissions[0].keys()),
            {
                "id",
                "dateModified",
                "status",
            },
        )

        # Check object contracts
        response = self.app.get("/agreements/{}/contracts".format(agreement_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"][0]["suppliers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )

        # Check object contract
        response = self.app.get(
            "/agreements/{}/contracts/{}".format(
                agreement_id,
                agreement["contracts"][0]["id"],
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"]["suppliers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )


def change_agreement(self):
    new_endDate = (parse_datetime(self.initial_data["qualificationPeriod"]["endDate"]) - timedelta(days=1)).isoformat()

    response = self.app.patch_json(
        f"/frameworks/{self.framework_id}?acc_token={self.framework_token}",
        {"data": {"qualificationPeriod": {"endDate": new_endDate}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["qualificationPeriod"]["endDate"], new_endDate)

    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["period"]["endDate"], new_endDate)

    new_procuringEntity = deepcopy(self.initial_data["procuringEntity"])
    new_procuringEntity["contactPoint"]["telephone"] = "+380440000000"
    response = self.app.patch_json(
        f"/frameworks/{self.framework_id}?acc_token={self.framework_token}",
        {"data": {"procuringEntity": {"contactPoint": new_procuringEntity["contactPoint"]}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procuringEntity"], new_procuringEntity)

    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procuringEntity"], new_procuringEntity)


def patch_contract_suppliers(self):
    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}?acc_token={'0' * 32}",
        {"data": {}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"], [{"location": "url", "name": "permission", "description": "Forbidden"}])

    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.patch_json(
            f"/agreements/{self.agreement_id}/contracts/{self.contract_id}?acc_token={self.framework_token}",
            {"data": {}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"], [{"location": "url", "name": "permission", "description": "Forbidden"}]
        )

    supplier = deepcopy(self.initial_submission_data["tenderers"][0])
    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}?acc_token={self.framework_token}",
        {"data": {"suppliers": [supplier, supplier]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "suppliers", "description": ["Contract must have only one supplier"]}],
    )

    contract_invalid_patch_fields = {
        "milestones": [{"type": "ban"}],
        "qualificationID": "",
        "submissionID": "",
    }
    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}?acc_token={self.framework_token}",
        {"data": contract_invalid_patch_fields},
        status=422,
    )
    error_fields = [field["name"] for field in response.json["errors"]]
    self.assertListEqual(sorted(error_fields), list(contract_invalid_patch_fields.keys()))

    supplier = deepcopy(self.initial_submission_data["tenderers"][0])
    supplier.update(
        {
            "address": {
                "countryName": "Україна",
                "postalCode": "01221",
                "region": "Київська область",
                "locality": "Київська область",
                "streetAddress": "вул. Банкова, 11, корпус 2",
            },
            "contactPoint": {
                "name": "Найновіше державне управління справами",
                "name_en": "New state administration",
                "telephone": "+0440000001",
                "email": "aa@aa.com",
            },
        }
    )

    contract_patch_fields = {"suppliers": [supplier]}
    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}?acc_token={self.framework_token}",
        {"data": contract_patch_fields},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertTrue(len(response.json["data"]["suppliers"]), 1)
    for field in contract_patch_fields["suppliers"][0]:
        self.assertEqual(
            response.json["data"]["suppliers"][0].get(field), contract_patch_fields["suppliers"][0].get(field)
        )


def post_submission_with_active_contract(self):
    response = self.app.get(f"/agreements/{self.agreement_id}")
    agreement = response.json["data"]
    self.assertEqual(agreement["contracts"][0]["status"], "active")

    response = self.app.post_json(
        "/submissions",
        {
            "data": self.initial_submission_data,
            "config": self.initial_submission_config,
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add submission when contract in agreement with same identifier.id in active status",
    )


def patch_agreement_terminated_status(self):
    end_date = get_now() + timedelta(days=CONTRACT_BAN_DURATION - 1)
    response = self.app.patch_json(
        f"/frameworks/{self.framework_id}?acc_token={self.framework_token}",
        {"data": {"qualificationPeriod": {"endDate": end_date.isoformat()}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")
    next_check = response.json["data"]["next_check"]

    with freeze_time((parse_datetime(next_check) + timedelta(hours=1)).isoformat()):
        self.check_chronograph()

    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")
    self.assertIsNone(response.json["data"].get("next_check"))


def patch_contract_active_status(self):
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={self.framework_token}",
        {"data": {"type": "ban"}},
    )
    self.assertEqual(response.status, "201 Created")
    response = self.app.get(f"/agreements/{self.agreement_id}/contracts/{self.contract_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "suspended")

    response = self.app.patch_json(
        f"/frameworks/{self.framework_id}?acc_token={self.framework_token}",
        {
            "data": {
                "qualificationPeriod": {"endDate": (get_now() + timedelta(days=CONTRACT_BAN_DURATION + 2)).isoformat()}
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")
    next_check = response.json["data"]["next_check"]
    self.assertEqual(response.json["data"]["contracts"][0]["status"], "suspended")

    with freeze_time((parse_datetime(next_check) + timedelta(hours=1)).isoformat()):
        self.check_chronograph()
    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["contracts"][0]["status"], "active")

    submission = self.mongodb.submissions.get(self.submission_id)
    submission["status"] = "draft"
    self.mongodb.submissions.save(submission)

    response = self.app.patch_json(
        f"/submissions/{self.submission_id}?acc_token={self.submission_token}",
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Tenderer can't activate submission with active/suspended contract "
                f'in agreement for framework {self.framework_id}',
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    # this contract is terminated but another user contract is active
    agreement = self.mongodb.agreements.get(self.agreement_id)
    contract = dict(agreement["contracts"][0])
    agreement["contracts"].append(contract)
    agreement["contracts"][0]["status"] = "terminated"
    agreement["contracts"][1]["suppliers"][0]["identifier"]["id"] = "1111222"
    self.mongodb.agreements.save(agreement)

    # should be fine
    response = self.app.patch_json(
        f"/submissions/{self.submission_id}?acc_token={self.submission_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")


def patch_several_contracts_active_status(self):
    response = self.app.patch_json(
        f"/frameworks/{self.framework_id}?acc_token={self.framework_token}",
        {
            "data": {
                "qualificationPeriod": {"endDate": (get_now() + timedelta(days=CONTRACT_BAN_DURATION + 3)).isoformat()}
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")

    base_identifier_id = self.initial_submission_data["tenderers"][0]["identifier"]["id"]
    for shift, milestone_type, identifier_id in [
        (0, "ban", "00037257"),
        (48, "ban", "00037260"),
    ]:
        self.initial_submission_data["tenderers"][0]["identifier"]["id"] = identifier_id
        self.create_submission()

        response = self.app.patch_json(
            f"/submissions/{self.submission_id}?acc_token={self.submission_token}", {"data": {"status": "active"}}
        )
        self.assertEqual(response.status, "200 OK")
        qualification_id = response.json["data"]["qualificationID"]
        response = self.app.patch_json(
            f"/qualifications/{qualification_id}?acc_token={self.framework_token}", {"data": {"status": "active"}}
        )
        self.assertEqual(response.status, "200 OK")
        response = self.app.get(f"/agreements/{self.agreement_id}")
        self.assertEqual(response.status, "200 OK")
        contract_id = response.json["data"]["contracts"][-1]["id"]
        with freeze_time((get_now() + timedelta(hours=shift)).isoformat()):
            response = self.app.post_json(
                f"/agreements/{self.agreement_id}/contracts/{contract_id}/milestones?acc_token={self.framework_token}",
                {"data": {"type": milestone_type}},
            )
    self.initial_submission_data["tenderers"][0]["identifier"]["id"] = base_identifier_id
    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")
    contract_statuses = [contract["status"] for contract in response.json["data"]["contracts"]]
    self.assertEqual(contract_statuses, ["active", "suspended", "suspended"])

    next_check = parse_datetime(response.json["data"]["next_check"])
    with freeze_time((next_check + timedelta(hours=2)).isoformat()):
        self.check_chronograph()
        response = self.app.get(f"/agreements/{self.agreement_id}")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
        contract_statuses = [contract["status"] for contract in response.json["data"]["contracts"]]
        self.assertEqual(contract_statuses, ["active", "active", "suspended"])

    with freeze_time((next_check + timedelta(hours=38)).isoformat()):
        self.check_chronograph()
        response = self.app.get(f"/agreements/{self.agreement_id}")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
        contract_statuses = [contract["status"] for contract in response.json["data"]["contracts"]]
        self.assertEqual(contract_statuses, ["active", "active", "suspended"])

    with freeze_time((next_check + timedelta(hours=72, minutes=1)).isoformat()):  # after agreement period.endDate
        self.check_chronograph()
        response = self.app.get(f"/agreements/{self.agreement_id}")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "terminated")
        contract_statuses = [contract["status"] for contract in response.json["data"]["contracts"]]
        self.assertEqual(contract_statuses, ["terminated", "terminated", "suspended"])


def agreement_chronograph_milestones(self):
    response = self.app.get(f"/agreements/{self.agreement_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["next_check"], response.json["data"]["period"]["endDate"])

    milestone_data = deepcopy(ban_milestone_data)
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={self.framework_token}",
        {"data": milestone_data},
    )
    self.assertEqual(response.status, "201 Created")
    milestone = response.json["data"]
    self.assertEqual(milestone["status"], "scheduled")

    response = self.app.get(f"/agreements/{self.agreement_id}")
    agreement = response.json["data"]
    next_check = agreement["next_check"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(next_check, milestone["dueDate"])
    with freeze_time((parse_datetime(next_check) + timedelta(hours=1)).isoformat()):
        response = self.check_chronograph()

        agreement = response.json["data"]
        milestone = agreement["contracts"][0]["milestones"][1]
        self.assertEqual(milestone["status"], "met")

        response = self.app.post_json(
            f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={self.framework_token}",
            {"data": milestone_data},
        )
    self.assertEqual(response.status, "201 Created")
    milestone = response.json["data"]
    self.assertEqual(milestone["status"], "scheduled")

    response = self.app.get(f"/agreements/{self.agreement_id}")
    agreement = response.json["data"]
    next_check = agreement["next_check"]
    self.assertEqual(next_check, agreement["period"]["endDate"])
    self.assertNotEqual(next_check, milestone["dueDate"])

    with freeze_time((parse_datetime(next_check) + timedelta(hours=1)).isoformat()):
        response = self.check_chronograph()
        agreement = response.json["data"]

    milestone_statuses = [i["status"] for i in agreement["contracts"][0]["milestones"]]
    self.assertEqual(milestone_statuses, ["met", "met", "notMet"])
    self.assertNotIn("next_check", agreement)


def post_milestone_invalid(self):
    milestone_data = deepcopy(ban_milestone_data)
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={'0' * 32}",
        {"data": milestone_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"], [{"location": "url", "name": "permission", "description": "Forbidden"}])

    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post_json(
            f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={self.framework_token}",
            {"data": milestone_data},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"], [{"location": "url", "name": "permission", "description": "Forbidden"}]
        )

    milestone_data = {"type": "other_type"}
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={self.framework_token}",
        {"data": milestone_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "type", "description": ["Value must be one of ['activation', 'ban']."]}],
    )
    milestone_data = {"type": "activation"}
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={self.framework_token}",
        {"data": milestone_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't add object for 'activation' milestone"}],
    )


def post_ban_milestone(self):
    milestone_data = deepcopy(ban_milestone_data)
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={self.framework_token}",
        {"data": milestone_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    milestone = response.json["data"]
    self.assertEqual(milestone["type"], milestone_data["type"])
    self.assertIsNotNone(milestone["dateModified"])
    self.assertTrue(parse_datetime(milestone["dueDate"]) - get_now() >= timedelta(days=CONTRACT_BAN_DURATION))

    contract = self.app.get(f"/agreements/{self.agreement_id}/contracts/{self.contract_id}").json["data"]
    self.assertEqual(contract["status"], MILESTONE_CONTRACT_STATUSES[milestone["type"]])

    milestone_data = deepcopy(ban_milestone_data)
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={self.framework_token}",
        {"data": milestone_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "name": "data",
                "location": "body",
                "description": "Can't add ban milestone for contract in suspended status",
            }
        ],
    )


def post_ban_milestone_with_documents(self):
    milestone_data = deepcopy(ban_milestone_data_with_documents)
    milestone_data["documents"][0]["url"] = self.generate_docservice_url()
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={self.framework_token}",
        {"data": milestone_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    milestone = response.json["data"]
    self.assertEqual(milestone["type"], milestone_data["type"])
    self.assertIsNotNone(milestone["dateModified"])
    self.assertEqual(milestone["documents"][0]["dateModified"], milestone["documents"][0]["datePublished"])
    self.assertEqual(len(milestone["documents"]), len(milestone_data["documents"]))
    self.assertTrue(parse_datetime(milestone["dueDate"]) - get_now() >= timedelta(days=CONTRACT_BAN_DURATION))

    contract = self.app.get(f"/agreements/{self.agreement_id}/contracts/{self.contract_id}").json["data"]
    self.assertEqual(contract["status"], MILESTONE_CONTRACT_STATUSES[milestone["type"]])


def get_documents_list(self):
    response = self.app.get(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}/documents"
    )
    documents = response.json["data"]
    self.assertEqual(len(documents), len(self.initial_milestone_data["documents"]))


def get_document_by_id(self):
    documents = (
        self.app.get(f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}")
        .json["data"]
        .get("documents")
    )
    for doc in documents:
        response = self.app.get(
            f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
            f"/documents/{doc['id']}"
        )
        document = response.json["data"]
        self.assertEqual(doc["id"], document["id"])
        self.assertEqual(doc["title"], document["title"])
        self.assertEqual(doc["format"], document["format"])
        self.assertEqual(doc["datePublished"], document["datePublished"])


def create_milestone_document_forbidden(self):
    # without acc_token
    response = self.app.post(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}/documents",
        upload_files=[("file", "укр.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Forbidden", "location": "url", "name": "permission"}],
    )

    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post(
            f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
            f"/documents?acc_token={self.framework_token}",
            upload_files=[("file", "укр.doc", b"content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{"description": "Forbidden", "location": "url", "name": "permission"}],
        )


def create_milestone_documents(self):
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"/documents?acc_token={self.framework_token}",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def create_milestone_document_json_bulk(self):
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"/documents?acc_token={self.framework_token}",
        {
            "data": [
                {
                    "title": "name1.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                },
                {
                    "title": "name2.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                },
            ]
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]

    def assert_document(document, title):
        self.assertEqual(title, document["title"])
        self.assertIn("Signature=", document["url"])
        self.assertIn("KeyID=", document["url"])
        self.assertNotIn("Expires=", document["url"])

    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")

    milestone = self.app.get(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
    ).json["data"]
    doc_1 = milestone["documents"][1]
    doc_2 = milestone["documents"][2]
    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")

    response = self.app.get(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}/documents"
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][1]
    doc_2 = response.json["data"][2]
    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")


def put_milestone_document(self):
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"/documents?acc_token={self.framework_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])
    with freeze_time((get_now() + timedelta(days=1)).isoformat()):
        response = self.app.put_json(
            f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
            f"/documents/{doc_id}?acc_token={self.framework_token}",
            {
                "data": {
                    "title": "name name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])

    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    milestone = self.app.get(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
    ).json["data"]
    self.assertIn(key, milestone["documents"][-1]["url"])
    self.assertIn("Signature=", milestone["documents"][-1]["url"])
    self.assertIn("KeyID=", milestone["documents"][-1]["url"])
    self.assertNotIn("Expires=", milestone["documents"][-1]["url"])
    response = self.app.get(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"/documents/{doc_id}",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name name.doc", response.json["data"]["title"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])

    response = self.app.get(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"/documents?all=true",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][2]["dateModified"])

    with freeze_time((get_now() + timedelta(days=2)).isoformat()):
        response = self.app.post_json(
            f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
            f"/documents?acc_token={self.framework_token}",
            {
                "data": {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.get(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}/documents",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][2]["dateModified"])
    response = self.app.put_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"/documents/{doc_id}?acc_token={self.framework_token}",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    milestone = self.app.get(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
    ).json["data"]
    self.assertIn(key, milestone["documents"][-1]["url"])
    self.assertIn("Signature=", milestone["documents"][-1]["url"])
    self.assertIn("KeyID=", milestone["documents"][-1]["url"])
    self.assertNotIn("Expires=", milestone["documents"][-1]["url"])

    response = self.app.get(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"/documents/{doc_id}?download={key}"
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}/documents"
    )
    self.assertEqual(response.status, "200 OK")
    doc_id = response.json["data"][0]["id"]

    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"/documents/{doc_id}?acc_token={self.framework_token}",
        {"data": {"documentType": None}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.set_contract_status("terminated")
    response = self.app.put_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"/documents/{doc_id}?acc_token={self.framework_token}",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        content_type="application/msword",
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update document in current (terminated) contract status",
                "location": "body",
                "name": "data",
            }
        ],
    )
    #  document in current (complete) contract status
    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"/documents/{doc_id}?acc_token={self.framework_token}",
        {"data": {"documentType": None}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update document in current (terminated) contract status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def patch_activation_milestone(self):
    response = self.app.get(f"/agreements/{self.agreement_id}/contracts/{self.contract_id}")
    self.assertEqual(response.status, "200 OK")

    milestones = response.json["data"]["milestones"]
    activation_milestone_id = milestones[0]["id"]

    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{activation_milestone_id}"
        f"?acc_token={self.framework_token}",
        {"data": {"status": "notMet"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't switch milestone status from `scheduled` to `notMet`"
    )

    # empty patch
    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{activation_milestone_id}"
        f"?acc_token={self.framework_token}",
        {"data": {}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{activation_milestone_id}"
        f"?acc_token={self.framework_token}",
        {"data": {"status": "met"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "met")

    response = self.app.get(f"/agreements/{self.agreement_id}/contracts/{self.contract_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "terminated")

    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{activation_milestone_id}"
        f"?acc_token={self.framework_token}",
        {"data": {"status": "notMet"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update object in current (terminated) contract status"
    )


def patch_ban_milestone(self):
    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones/{self.milestone_id}"
        f"?acc_token={self.framework_token}",
        {"data": {"status": "met"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add ban milestone for contract in suspended status"
    )


def search_by_classification(self):
    response = self.app.get(f"/agreements/{self.agreement_id}")
    classification_id = response.json["data"]["classification"]["id"]

    self.assertEqual(len(classification_id), 10)

    response = self.app.get(f"/agreements_by_classification/{classification_id}")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(f"/agreements_by_classification/{classification_id[:8]}")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(f"/agreements_by_classification/{classification_id[:2]}")
    self.assertEqual(len(response.json["data"]), 1)
