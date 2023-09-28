from datetime import datetime, timedelta
import os
import unittest
from copy import deepcopy

from mock import MagicMock, call, patch
from pyramid.exceptions import URLDecodeError
from schematics.types import StringType

from openprocurement.api.utils import get_now, parse_date
from openprocurement.framework.core.tests.base import BaseFrameworkTest, test_framework_data
from openprocurement.framework.core.tests.framework import Framework
from openprocurement.framework.core.utils import (
    obj_serialize,
    framework_from_data,
    extract_doc,
    register_framework_frameworkType,
    save_framework,
    apply_patch,
    generate_framework_pretty_id,
    calculate_framework_date,
)


class UtilsFrameworkTest(BaseFrameworkTest):
    relative_to = os.path.dirname(__file__)
    framework_data = deepcopy(test_framework_data)

    def test_obj_serialize(self):
        request = MagicMock()
        fields = []
        res = obj_serialize(request, self.framework_data, fields)
        self.assertEqual(res, {})

    def test_framework_from_data(self):
        request = MagicMock()
        request.registry.framework_frameworkTypes.get.side_effect = [None, None, Framework, Framework]

        with self.assertRaises(Exception) as e:
            framework_from_data(request, self.framework_data)
        self.assertEqual(request.errors.status, 415)
        request.errors.add.assert_called_once_with("body", "frameworkType", "Not implemented")

        model = framework_from_data(request, self.framework_data, raise_error=False)
        self.assertIs(model, None)

        model = framework_from_data(request, self.framework_data, create=False)
        self.assertIs(model, Framework)

        model = framework_from_data(request, self.framework_data)
        self.assertIsInstance(model, Framework)

    @patch("openprocurement.framework.core.utils.decode_path_info")
    def test_extract_doc(self, mocked_decode_path):
        mocked_decode_path.side_effect = [
            KeyError("Missing 'PATH_INFO'"),
            UnicodeDecodeError("UTF-8", b"obj", 1, 10, "Hm..."),
            "/",
            "/api/2.3/frameworks/{}".format(self.framework_data["id"]),
        ]
        framework_data = deepcopy(self.framework_data)
        framework_data["doc_type"] = "Framework"
        request = MagicMock()
        request.environ = {"PATH_INFO": "/"}
        request.registry.framework_frameworkTypes.get.return_value = Framework
        request.framework_from_data.return_value = framework_from_data(request, framework_data)
        get_mock = MagicMock()
        get_mock.get.return_value = None
        request.registry.databases = {"frameworks": get_mock}

        # Test with KeyError
        self.assertIs(extract_doc(request), None)

        # Test with UnicodeDecodeError
        with self.assertRaises(URLDecodeError) as e:
            extract_doc(request)
        self.assertEqual(e.exception.encoding, "UTF-8")
        self.assertEqual(e.exception.object, b"obj")
        self.assertEqual(e.exception.start, 1)
        self.assertEqual(e.exception.end, 10)
        self.assertEqual(e.exception.reason, "Hm...")
        self.assertIsInstance(e.exception, URLDecodeError)

        # Test with path '/'
        self.assertIs(extract_doc(request), None)

        mocked_decode_path.side_effect = ["/api/2.5/frameworks/{}".format(self.framework_data["id"])] * 3

        # Test with extract_doc_adapter return Framework object
        request.registry.mongodb.frameworks.get.return_value = framework_data
        framework = extract_doc(request)
        serialized_framework = framework.serialize("draft")
        self.assertIsInstance(framework, Framework)
        for k in framework_data:
            self.assertEqual(framework_data[k], serialized_framework[k])

    def test_register_framework_type(self):
        config = MagicMock()
        model = MagicMock()
        frameworkType = StringType(default="electronicCatalogue")
        model.frameworkType = frameworkType
        register_framework_frameworkType(config, model)

    def test_save_framework(self):
        request = MagicMock(authenticated_userid="user_uuid")
        framework = MagicMock()
        framework.mode = "test"
        framework.revisions = []
        framework.dateModified = datetime(2018, 8, 2, 12, 9, 2, 440566)
        framework.rev = "12341234"
        request.validated = {"framework": framework, "framework_src": "src_test"}
        res = save_framework(request)
        self.assertTrue(res)

    @patch("openprocurement.framework.core.utils.apply_data_patch")
    @patch("openprocurement.framework.core.utils.save_framework")
    def test_apply_patch(self, mocked_apply_data_patch, mocked_save_framework):
        request = MagicMock()
        data = deepcopy(test_framework_data)
        request.validated = {"data": data, "framework": data}
        mocked_save_framework.return_value = True

        request.context.serialize.return_value = data
        res = apply_patch(request, "framework")
        self.assertTrue(res)

        mocked_apply_data_patch.return_value = data
        res = apply_patch(request, "framework")
        self.assertEqual(res, data)

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
