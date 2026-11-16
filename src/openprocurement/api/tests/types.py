import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Annotated

import pytest
from isodate.duration import Duration
from pytz import timezone

from openprocurement.api.constants import TZ
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.errors import DataValidationError
from openprocurement.api.procedure.types import (
    DecimalOf,
    IsoDateTime,
    IsoDuration,
)
from openprocurement.api.tests.base import BaseWebTest


class ListTypeTest(BaseWebTest):
    def test_list_type(self):
        class ChildObjModel(Model):
            test_field: str | None = None

        class ObjModel(Model):
            test_list: list[ChildObjModel] | None = None

        data = ObjModel.validate_data({"test_list": [{"test_field": "test1"}, {"test_field": "test2"}]})
        self.assertEqual(data, {"test_list": [{"test_field": "test1"}, {"test_field": "test2"}]})

    def test_list_type_from_dict(self):
        class ChildObjModel(Model):
            test_field: str | None = None

        class ObjModel(Model):
            test_list: list[ChildObjModel] | None = None

        with self.assertRaises(DataValidationError) as e:
            ObjModel.validate_data({"test_list": {"0": {"test_field": "test1"}, "1": {"test_field": "test2"}}})
        self.assertEqual(e.exception.messages, {"test_list": ["Input should be a valid list"]})

    def test_list_type_not_list(self):
        class ChildObjModel(Model):
            test_field: str | None = None

        class ObjModel(Model):
            test_list: list[ChildObjModel] | None = None

        with self.assertRaises(DataValidationError) as e:
            ObjModel.validate_data({"test_list": {"test_field": "test1"}})
        self.assertEqual(e.exception.messages, {"test_list": ["Input should be a valid list"]})


class IsoDurationTypeTest(BaseWebTest):
    def test_iso_duration_type(self):
        class ObjModel(Model):
            duration: IsoDuration

        period_str = "P3Y6M4DT12H30M5S"
        duration_period = Duration(years=3, months=6, days=4, hours=12, minutes=30, seconds=5)
        result = ObjModel.model_validate({"duration": period_str}).duration

        self.assertEqual(result.years, 3)
        self.assertEqual(result.months, 6)
        self.assertEqual(result.days, 4)
        self.assertEqual(result.seconds, 45005)
        self.assertEqual(result, duration_period)
        self.assertEqual(ObjModel.validate_data({"duration": period_str}), {"duration": period_str})
        self.assertEqual(ObjModel.validate_data({"duration": duration_period}), {"duration": period_str})

        # Parse with errors
        with self.assertRaises(DataValidationError) as context:
            ObjModel.validate_data({"duration": "Ptest"})
        self.assertEqual(
            context.exception.messages,
            {"duration": ["ISO 8601 time designator 'T' missing. Unable to parse datetime string 'test'"]},
        )
        with self.assertRaises(DataValidationError) as context:
            ObjModel.validate_data({"duration": "P3Y6MW4DT12H30M5S"})
        self.assertEqual(context.exception.messages, {"duration": ["Unrecognised ISO 8601 date format: '3Y6MW4D'"]})
        with self.assertRaises(DataValidationError) as context:
            ObjModel.validate_data({"duration": 123123})
        self.assertEqual(
            context.exception.messages, {"duration": ["Could not parse 123123. Should be ISO8601 Durations."]}
        )

        result1 = ObjModel.model_validate({"duration": "P3Y6M4DT12H30M5S"})
        result2 = ObjModel.model_validate({"duration": "P2Y18M4DT12H30M5S"})
        self.assertEqual(result1.duration, result2.duration)
        self.assertEqual(result1.serialize(), {"duration": "P3Y6M4DT12H30M5S"})
        self.assertEqual(result2.serialize(), {"duration": "P2Y18M4DT12H30M5S"})

    def test_iso_duration_type_from_timedelta(self):
        class ObjModel(Model):
            duration: IsoDuration

        duration = timedelta(days=1)
        self.assertEqual(ObjModel.model_validate({"duration": duration}).duration, duration)

    def test_iso_duration_type_from_Duration(self):
        class ObjModel(Model):
            duration: IsoDuration

        duration = Duration(months=1, days=1)
        self.assertEqual(ObjModel.model_validate({"duration": duration}).duration, duration)


class TestIsoDateTimeType(unittest.TestCase):
    class ObjModel(Model):
        date: IsoDateTime

    def test_parse_string(self):
        dt_result = self.ObjModel.model_validate({"date": "2020-01-01T12:00:00+02:00"}).date
        dt_expected = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_parse_string_with_no_tz(self):
        dt_result = self.ObjModel.model_validate({"date": "2020-01-01T12:00:00"}).date
        dt_expected = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_parse_string_with_no_time_and_tz(self):
        dt_result = self.ObjModel.model_validate({"date": "2020-01-01"}).date
        dt_expected = TZ.localize(datetime(2020, 1, 1))
        self.assertEqual(dt_result, dt_expected)

    def test_parse_string_with_not_default_tz(self):
        dt_result = self.ObjModel.model_validate({"date": "2020-01-01T12:00:00-05:00"}).date
        dt_expected = timezone("US/Eastern").localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_parse_string_invalid_format(self):
        with self.assertRaises(DataValidationError) as e:
            self.ObjModel.validate_data({"date": "test"})
        self.assertEqual(e.exception.messages, {"date": ["Could not parse test. Should be ISO8601."]})

    def test_parse_datetime(self):
        dt = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(self.ObjModel.model_validate({"date": dt}).date, dt)

    def test_to_primitive_string(self):
        dt_str = "2020-01-01T12:00:00+02:00"
        self.assertEqual(self.ObjModel.validate_data({"date": dt_str}), {"date": dt_str})

    def test_to_primitive_datetime(self):
        dt = TZ.localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(self.ObjModel.validate_data({"date": dt}), {"date": "2020-01-01T12:00:00+02:00"})


@pytest.mark.parametrize(
    "raw_input, expected_conversion_error",
    [
        ("300", False),
        ("Infinity", True),
        ("-Infinity", True),
        ("NaN", True),
    ],
)
def test_decimal_type_conversion(raw_input, expected_conversion_error):
    class Poket(Model):
        money: Annotated[Decimal, DecimalOf()]

    try:
        Poket.validate_data({"money": raw_input})
    except DataValidationError as e:
        assert expected_conversion_error is True
        assert e.messages == {"money": [f"Number '{raw_input}' failed to convert to a decimal."]}
    else:
        assert expected_conversion_error is False


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(IsoDurationTypeTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestIsoDateTimeType))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
