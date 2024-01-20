from datetime import datetime, timedelta
import os
import unittest
from copy import deepcopy

from mock import MagicMock, call, patch
from pyramid.exceptions import URLDecodeError
from schematics.types import StringType

from openprocurement.api.utils import get_now
from openprocurement.api.procedure.utils import parse_date
from openprocurement.framework.core.tests.base import BaseFrameworkTest, test_framework_data
from openprocurement.framework.core.tests.framework import Framework
from openprocurement.framework.core.utils import (
    generate_framework_pretty_id,
    calculate_framework_date,
)


class UtilsFrameworkTest(BaseFrameworkTest):
    relative_to = os.path.dirname(__file__)
    framework_data = deepcopy(test_framework_data)

    def test_generate_framework_id(self):
        ctime = get_now()
        request = MagicMock()
        request.registry.mongodb.get_next_sequence_value.return_value = 103

        framework_id = generate_framework_pretty_id(request)
        tid = "UA-F-{:04}-{:02}-{:02}-{:06}".format(
            ctime.year, ctime.month, ctime.day, 103,
        )
        self.assertEqual(tid, framework_id)


class TestCalculateFrameworkDate(BaseFrameworkTest):
    def test_working_days(self):
        date_obj = parse_date("2020-11-07T12:00:00+02:00")
        delta_obj = timedelta(days=7)

        date = calculate_framework_date(date_obj, delta_obj, framework={}, working_days=True, ceil=True)
        self.assertEqual(date.isoformat(), "2020-11-18T00:00:00+02:00")

    def test_working_days_backwards(self):
        date_obj = parse_date("2020-11-19T12:00:00+02:00")
        delta_obj = -timedelta(days=7)

        date = calculate_framework_date(date_obj, delta_obj, framework={}, working_days=True)
        self.assertEqual(date.isoformat(), "2020-11-10T00:00:00+02:00")

    def test_calendar_days(self):
        date_obj = parse_date("2023-10-03T00:00:00+03:00")
        delta_obj = timedelta(days=30)

        date = calculate_framework_date(date_obj, delta_obj, framework={}, working_days=False, ceil=True)
        self.assertEqual(date.isoformat(), "2023-11-02T00:00:00+02:00")

    def test_calendar_days_backwards(self):
        date_obj = parse_date("2020-11-15T12:00:00+02:00")
        delta_obj = -timedelta(days=7)

        date = calculate_framework_date(date_obj, delta_obj, framework={}, working_days=False)
        self.assertEqual(date.isoformat(), "2020-11-08T00:00:00+02:00")

    def test_working_days_dst_transition(self):
        date_obj = parse_date("2021-03-10T12:00:00+02:00")
        delta_obj = timedelta(days=30)

        date = calculate_framework_date(date_obj, delta_obj, framework={}, working_days=True, ceil=True)
        self.assertEqual(date.isoformat(), "2021-04-22T00:00:00+03:00")

    def test_working_days_dst_transition_backwards(self):
        date_obj = parse_date("2021-04-21T12:00:00+03:00")
        delta_obj = -timedelta(days=30)

        date = calculate_framework_date(date_obj, delta_obj, framework={}, working_days=True)
        self.assertEqual(date.isoformat(), "2021-03-10T00:00:00+02:00")

    def test_calendar_dst_transition(self):
        date_obj = parse_date("2021-03-10T12:00:00+02:00")
        delta_obj = timedelta(days=30)

        date = calculate_framework_date(date_obj, delta_obj, framework={}, working_days=False, ceil=True)
        self.assertEqual(date.isoformat(), "2021-04-10T00:00:00+03:00")

    def test_calendar_dst_transition_backwards(self):
        date_obj = parse_date("2021-04-10T12:00:00+03:00")
        delta_obj = -timedelta(days=30)

        date = calculate_framework_date(date_obj, delta_obj, framework={}, working_days=False)
        self.assertEqual(date.isoformat(), "2021-03-11T00:00:00+02:00")

    def test_calendar_dst_transition_backwards_from_midnight(self):
        date_obj = parse_date("2021-04-10T00:00:00+03:00")
        delta_obj = -timedelta(days=30)

        date = calculate_framework_date(date_obj, delta_obj, framework={}, working_days=False)
        self.assertEqual(date.isoformat(), "2021-03-11T00:00:00+02:00")

    def test_with_accelerator(self):
        date_obj = datetime(2021, 10, 7)
        delta_obj = timedelta(days=7)

        # Test with accelerator = 1440
        context = {"frameworkDetails": "quick, accelerator=1440"}
        date = calculate_framework_date(date_obj, delta_obj, framework=context, working_days=True, ceil=True)
        self.assertEqual(date, datetime(2021, 10, 7, 0, 7))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilsFrameworkTest))
    suite.addTest(unittest.makeSuite(TestCalculateFrameworkDate))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
