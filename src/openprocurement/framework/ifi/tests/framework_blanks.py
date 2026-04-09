from copy import deepcopy
from datetime import timedelta

from ciso8601 import parse_datetime

from openprocurement.api.utils import get_now


def ifi_enquiry_period_calendar_days(self):
    """Verify IFI enquiryPeriod is calculated using calendar days, not working days."""
    data = deepcopy(self.initial_data)
    response = self.app.post_json(
        "/frameworks",
        {"data": data, "config": self.initial_config},
    )
    self.assertEqual(response.status, "201 Created")
    framework = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    enquiry_period = response.json["data"]["enquiryPeriod"]
    start = parse_datetime(enquiry_period["startDate"])
    end = parse_datetime(enquiry_period["endDate"])

    diff_days = (end - start).days
    # 10 calendar days with ceiling adjustment = 10-11 days
    # If working days were used (old behavior), it would be 14+ days
    # since 10 calendar days always spans at least one weekend
    self.assertGreaterEqual(diff_days, 10)
    self.assertLessEqual(
        diff_days,
        11,
        "enquiryPeriod should use calendar days (10-11 days), "
        "not working days (14+ days)",
    )


def ifi_period_calculation(self):
    """Verify IFI framework period calculations on activation."""
    data = deepcopy(self.initial_data)
    response = self.app.post_json(
        "/frameworks",
        {"data": data, "config": self.initial_config},
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

    # All start dates should align
    self.assertEqual(
        activated["enquiryPeriod"]["startDate"],
        activated["period"]["startDate"],
    )
    self.assertEqual(
        activated["qualificationPeriod"]["startDate"],
        activated["period"]["startDate"],
    )

    # period:endDate = qualificationPeriod:endDate - 30 calendar days
    period_end = parse_datetime(activated["period"]["endDate"])
    qual_end = parse_datetime(activated["qualificationPeriod"]["endDate"])
    diff = (qual_end - period_end).days
    self.assertGreaterEqual(diff, 29)
    self.assertLessEqual(diff, 31)

    # qualification period should be >= 40 days (IFI minimum)
    qual_start = parse_datetime(activated["qualificationPeriod"]["startDate"])
    qual_duration = (qual_end - qual_start).days
    self.assertGreaterEqual(qual_duration, 40)


def ifi_change_period_recalculation(self):
    """Verify /changes endpoint recalculates periods correctly with IFI settings."""
    data = deepcopy(self.initial_data)
    response = self.app.post_json(
        "/frameworks",
        {"data": data, "config": self.initial_config},
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

    # Extend qualificationPeriod via changes endpoint
    new_end_date = (get_now() + timedelta(days=100)).isoformat()
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

    # Verify periods were recalculated
    response = self.app.get("/frameworks/{}".format(framework["id"]))
    changed = response.json["data"]

    # qualificationPeriod:endDate should be updated
    self.assertEqual(changed["qualificationPeriod"]["endDate"], new_end_date)

    # period:endDate should be recalculated (different from original)
    self.assertNotEqual(changed["period"]["endDate"], original_period_end)

    # period:endDate should be ~30 days before new qualificationPeriod:endDate
    new_period_end = parse_datetime(changed["period"]["endDate"])
    new_qual_end = parse_datetime(changed["qualificationPeriod"]["endDate"])
    diff = (new_qual_end - new_period_end).days
    self.assertGreaterEqual(diff, 29)
    self.assertLessEqual(diff, 31)

    # enquiryPeriod should remain unchanged
    self.assertEqual(changed["enquiryPeriod"]["startDate"], original_enquiry_start)
    self.assertEqual(changed["enquiryPeriod"]["endDate"], original_enquiry_end)

    # Verify enquiryPeriod is still calendar-based (10-11 days)
    enquiry_start = parse_datetime(changed["enquiryPeriod"]["startDate"])
    enquiry_end = parse_datetime(changed["enquiryPeriod"]["endDate"])
    enquiry_diff = (enquiry_end - enquiry_start).days
    self.assertGreaterEqual(enquiry_diff, 10)
    self.assertLessEqual(enquiry_diff, 11)
