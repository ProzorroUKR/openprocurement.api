# -*- coding: utf-8 -*-
import os
import sys
import unittest
from datetime import datetime, timedelta

from isodate import duration_isoformat
from isodate.duration import Duration
from pytz import timezone
from schematics.exceptions import ConversionError
from schematics.types import BooleanType, StringType
from schematics.types.serializable import serializable

from openprocurement.api.constants import TZ
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, IsoDurationType
from openprocurement.api.tests.base import BaseWebTest


class TestModel(Model):
    test_field0 = BooleanType()
    test_field1 = StringType()
    test_field2 = StringType()

    @serializable(serialized_name="status")
    def serialize_status(self):
        return "test_status"


class IsoDurationTypeTest(BaseWebTest):
    def test_iso_duration_type(self):
        type_duration = IsoDurationType()
        period_str = "P3Y6M4DT12H30M5S"
        duration_period = Duration(years=3, months=6, days=4, hours=12, minutes=30, seconds=5)
        res_to_native = type_duration.to_native(period_str)

        self.assertEqual(res_to_native.years, 3)
        self.assertEqual(res_to_native.months, 6)
        self.assertEqual(res_to_native.days, 4)
        self.assertEqual(res_to_native.seconds, 45005)
        self.assertEqual(res_to_native, duration_period)
        self.assertEqual(duration_isoformat(res_to_native), period_str)

        res_to_primitive = type_duration.to_primitive(duration_period)
        self.assertEqual(res_to_primitive, period_str)
        # Parse with errors
        result = type_duration.to_native(duration_period)
        self.assertEqual(result, duration_period)
        with self.assertRaises(Exception) as context:
            result = type_duration.to_native("Ptest")
        self.assertEqual(
            context.exception.messages, ["ISO 8601 time designator 'T' missing. Unable to parse datetime string 'test'"]
        )
        with self.assertRaises(Exception) as context:
            result = type_duration.to_native("P3Y6MW4DT12H30M5S")
        self.assertEqual(context.exception.messages, ["Unrecognised ISO 8601 date format: '3Y6MW4D'"])
        with self.assertRaises(Exception) as context:
            result = type_duration.to_native(123123)
        self.assertEqual(context.exception.messages, ["Could not parse 123123. Should be ISO8601 Durations."])
        res_native1 = type_duration.to_native("P3Y6M4DT12H30M5S")
        res_native2 = type_duration.to_native("P2Y18M4DT12H30M5S")
        self.assertEqual(res_native1, res_native2)

        res_dur1 = type_duration.to_primitive(res_native1)
        res_dur2 = type_duration.to_primitive(res_native2)
        self.assertEqual("P3Y6M4DT12H30M5S", res_dur1)
        self.assertEqual("P2Y18M4DT12H30M5S", res_dur2)

    def test_iso_duration_type_from_timedelta(self):
        duration_instance = IsoDurationType()
        duration = timedelta(days=1)
        self.assertEqual(duration_instance(duration), duration)

    def test_iso_duration_type_from_Duration(self):
        duration_instance = IsoDurationType()
        duration = Duration(months=1, days=1)
        self.assertEqual(duration_instance(duration), duration)


class TestIsoDateTimeType(unittest.TestCase):
    def test_to_native_string(self):
        dt_str = "2020-01-01T12:00:00+02:00"
        dt_result = IsoDateTimeType().to_native(dt_str)
        dt_expected = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_to_native_string_with_no_tz(self):
        dt_str = "2020-01-01T12:00:00"
        dt_result = IsoDateTimeType().to_native(dt_str)
        dt_expected = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_to_native_string_with_no_time_and_tz(self):
        dt_str = "2020-01-01"
        dt_result = IsoDateTimeType().to_native(dt_str)
        dt_expected = TZ.localize(datetime(2020, 1, 1))
        self.assertEqual(dt_result, dt_expected)

    def test_to_native_string_with_not_default_tz(self):
        dt_str = "2020-01-01T12:00:00-05:00"
        dt_result = IsoDateTimeType().to_native(dt_str)
        dt_expected = timezone('US/Eastern').localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_to_native_string_invalid_format(self):
        dt_str = "test"
        with self.assertRaises(ConversionError) as e:
            IsoDateTimeType().to_native(dt_str)
            self.assertEqual(e.exception.message, IsoDateTimeType.MESSAGES["parse"].format(dt_str))

    def test_to_native_datetime(self):
        dt = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        dt_result = IsoDateTimeType().to_native(dt)
        self.assertEqual(dt_result, dt)

    def test_to_primitive_string(self):
        dt_str = "2020-01-01T12:00:00+02:00"
        dt_result = IsoDateTimeType().to_primitive(dt_str)
        self.assertEqual(dt_result, dt_str)

    def test_to_primitive_datetime(self):
        dt = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        dt_str_result = IsoDateTimeType().to_primitive(dt)
        dt_str_expected = "2020-01-01T12:00:00+02:00"
        self.assertEqual(dt_str_result, dt_str_expected)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IsoDurationTypeTest))
    suite.addTest(unittest.makeSuite(TestIsoDateTimeType))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
