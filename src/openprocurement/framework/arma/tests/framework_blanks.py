from copy import deepcopy
from datetime import timedelta
from unittest import mock

from ciso8601 import parse_datetime
from freezegun import freeze_time

from openprocurement.api.procedure.models.organization import PROCURING_ENTITY_KIND_CHOICES
from openprocurement.api.utils import calculate_date, get_now
from openprocurement.framework.arma.procedure.models.framework import Framework
from openprocurement.framework.core.tests.base import get_framework_unsuccessful_status_check_date
from openprocurement.framework.core.utils import calculate_framework_full_date


def arma_period_calculation(self):
    response = self.app.post_json(
        "/frameworks",
        {"data": self.initial_data, "config": self.initial_config},
    )
    self.assertEqual(response.status, "201 Created")
    framework = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    activated = response.json["data"]

    # all the periods start at the same moment
    self.assertEqual(activated["enquiryPeriod"]["startDate"], activated["period"]["startDate"])
    self.assertEqual(activated["qualificationPeriod"]["startDate"], activated["period"]["startDate"])

    # enquiryPeriod:endDate == period:endDate
    self.assertEqual(activated["enquiryPeriod"]["endDate"], activated["period"]["endDate"])

    # period:endDate = qualificationPeriod:endDate - 30 calendar days
    period_end = parse_datetime(activated["period"]["endDate"])
    qual_end = parse_datetime(activated["qualificationPeriod"]["endDate"])
    self.assertGreaterEqual((qual_end - period_end).days, 29)
    self.assertLessEqual((qual_end - period_end).days, 31)

    # clarificationsUntil is still counted from the end of the enquiry period
    clarification_until_duration = response.json["config"]["clarificationUntilDuration"]
    self.assertEqual(
        parse_datetime(activated["enquiryPeriod"]["clarificationsUntil"]),
        calculate_framework_full_date(
            parse_datetime(activated["enquiryPeriod"]["endDate"]),
            timedelta(days=clarification_until_duration),
            framework=activated,
            working_days=True,
        ),
    )


def arma_change_period_recalculation(self):
    response = self.app.post_json(
        "/frameworks",
        {"data": self.initial_data, "config": self.initial_config},
    )
    self.assertEqual(response.status, "201 Created")
    framework = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    framework = response.json["data"]

    original_period_end = framework["period"]["endDate"]
    original_enquiry_start = framework["enquiryPeriod"]["startDate"]
    original_enquiry_end = framework["enquiryPeriod"]["endDate"]

    new_end_date = calculate_date(get_now(), timedelta(days=400)).isoformat()
    response = self.app.post_json(
        "/frameworks/{}/changes?acc_token={}".format(framework["id"], token),
        {
            "data": {
                "modifications": {"qualificationPeriod": {"endDate": new_end_date}},
                "rationale": "Потрібно більше часу",
                "rationaleType": "other",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.get("/frameworks/{}".format(framework["id"]))
    changed = response.json["data"]

    self.assertEqual(changed["qualificationPeriod"]["endDate"], new_end_date)
    self.assertNotEqual(changed["period"]["endDate"], original_period_end)

    new_period_end = parse_datetime(changed["period"]["endDate"])
    new_qual_end = parse_datetime(changed["qualificationPeriod"]["endDate"])
    self.assertGreaterEqual((new_qual_end - new_period_end).days, 29)
    self.assertLessEqual((new_qual_end - new_period_end).days, 31)

    self.assertEqual(changed["enquiryPeriod"]["startDate"], original_enquiry_start)
    self.assertNotEqual(changed["enquiryPeriod"]["endDate"], original_enquiry_end)
    self.assertEqual(changed["enquiryPeriod"]["endDate"], changed["period"]["endDate"])


def arma_successful_status_without_submissions(self):
    response = self.app.post_json(
        "/frameworks",
        {"data": self.initial_data, "config": self.initial_config},
    )
    self.assertEqual(response.status, "201 Created")
    self.framework_id = response.json["data"]["id"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(self.framework_id, token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")

    framework = Framework(response.json["data"])
    date = get_framework_unsuccessful_status_check_date(
        framework,
        self.min_submissions_number_days,
        self.min_submissions_number_working_days,
    )
    self.assertFalse(self.mongodb.frameworks.get(self.framework_id)["successful"])

    with freeze_time((date + timedelta(hours=1)).isoformat()):
        with mock.patch(
            "openprocurement.framework.core.procedure.state.chronograph.get_framework_number_of_submissions",
            lambda x, y: 0,
        ):
            self.check_chronograph()

    response = self.app.get("/frameworks/{}".format(self.framework_id))
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertTrue(self.mongodb.frameworks.get(self.framework_id)["successful"])

    qualification_end = parse_datetime(response.json["data"]["qualificationPeriod"]["endDate"])
    with freeze_time((qualification_end + timedelta(hours=1)).isoformat()):
        with mock.patch(
            "openprocurement.framework.core.procedure.state.chronograph.get_framework_number_of_submissions",
            lambda x, y: 0,
        ):
            self.check_chronograph()

    response = self.app.get("/frameworks/{}".format(self.framework_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def arma_validate_procurement_entity_kind(self):
    self.app.authorization = ("Basic", ("token", ""))
    data = deepcopy(self.initial_data)
    config = deepcopy(self.initial_config)

    with mock.patch(
        "openprocurement.framework.core.procedure.state.framework.PROCUREMENT_ENTITY_KIND_VALIDATION_FROM",
        get_now() - timedelta(days=1),
    ):
        for kind in PROCURING_ENTITY_KIND_CHOICES:
            resp_status = 201 if kind in self.allowed_proc_entity_kinds else 422
            data["procuringEntity"]["kind"] = kind

            response = self.app.post_json("/frameworks", {"data": data, "config": config}, status=resp_status)
            if resp_status == 201:
                self.assertEqual(response.status, "201 Created")
            else:
                self.assertRegex(
                    response.json["errors"][0]["description"],
                    rf"^Framework publishing with type (.+) is not allowed for procuringEntity.kind {kind}$",
                )
