# -*- coding: utf-8 -*-
import unittest
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta

from mock import MagicMock, call, patch
from pyramid.exceptions import URLDecodeError

from openprocurement.api.constants import TZ
from openprocurement.api.procedure.utils import parse_date
from openprocurement.tender.core.procedure.utils import (
    extract_tender_doc,
    extract_tender_id,
    generate_tender_id,
)
from openprocurement.tender.core.utils import calculate_tender_business_date


class TestUtilsBase(unittest.TestCase):
    def setUp(self):
        self.tender_data = {
            "id": "ae50ea25bb1349898600ab380ee74e57",
            "dateModified": "2016-04-18T11:26:10.320970+03:00",
            "status": "draft",
            "tenderID": "UA-2016-04-18-000003",
        }
        self.lots = [
            {
                "id": "11111111111111111111111111111111",
                "title": "Earth",
                "value": {"amount": 500000},
                "minimalStep": {"amount": 1000},
            },
            {
                "id": "22222222222222222222222222222222",
                "title": "Mars",
                "value": {"amount": 600000},
                "minimalStep": {"amount": 2000},
            },
        ]
        self.items = [{"description": "Some item", "relatedLot": "11111111111111111111111111111111"}]


class TestUtils(TestUtilsBase):
    def setUp(self):
        self.tender_data = {
            "id": "ae50ea25bb1349898600ab380ee74e57",
            "dateModified": "2016-04-18T11:26:10.320970+03:00",
            "status": "draft",
            "tenderID": "UA-2016-04-18-000003",
        }
        self.lots = [
            {
                "id": "11111111111111111111111111111111",
                "title": "Earth",
                "value": {"amount": 500000},
                "minimalStep": {"amount": 1000},
            },
            {
                "id": "22222222222222222222222222222222",
                "title": "Mars",
                "value": {"amount": 600000},
                "minimalStep": {"amount": 2000},
            },
        ]
        self.items = [{"description": "Some item", "relatedLot": "11111111111111111111111111111111"}]

    def test_generate_tender_id(self):
        ctime = datetime.now(TZ)
        request = MagicMock()
        request.registry.mongodb.get_next_sequence_value.return_value = 99

        tender_id = generate_tender_id(request)
        tid = "UA-{:04}-{:02}-{:02}-{:06}-a".format(ctime.year, ctime.month, ctime.day, 99)
        self.assertEqual(tid, tender_id)

    @patch("openprocurement.tender.core.procedure.utils.decode_path_info")
    @patch("openprocurement.tender.core.procedure.utils.error_handler")
    def test_extract_tender_id(self, mocked_error_handler, mocked_decode_path):
        mocked_error_handler.return_value = Exception("Oops.")
        mocked_decode_path.side_effect = [
            KeyError("Missing 'PATH_INFO'"),
            UnicodeDecodeError("UTF-8", b"obj", 1, 10, "Hm..."),
            "/",
            "/api/2.3/tenders/{}".format(self.tender_data["id"]),
        ]
        request = MagicMock()
        request.environ = {"PATH_INFO": "/"}

        # Test with KeyError
        self.assertIs(extract_tender_id(request), None)

        # Test with UnicodeDecodeError
        with self.assertRaises(URLDecodeError) as e:
            extract_tender_id(request)
        self.assertEqual(e.exception.encoding, "UTF-8")
        self.assertEqual(e.exception.object, b"obj")
        self.assertEqual(e.exception.start, 1)
        self.assertEqual(e.exception.end, 10)
        self.assertEqual(e.exception.reason, "Hm...")
        self.assertIsInstance(e.exception, URLDecodeError)

        # Test with path '/'
        self.assertIs(extract_tender_id(request), None)

    @patch("openprocurement.tender.core.procedure.utils.extract_tender_id")
    def test_extract_tender_doc(self, mocked_extract_tender_id):
        tender_data = deepcopy(self.tender_data)
        mocked_extract_tender_id.return_value = tender_data["id"]
        tender_data["doc_type"] = "Tender"
        request = MagicMock()
        request.registry.db = MagicMock()

        # Test with extract_tender_adapter raise HTTP 404
        request.registry.mongodb.tenders.get.return_value = None
        with self.assertRaises(Exception):
            extract_tender_doc(request)
        self.assertEqual(request.errors.status, 404)
        request.errors.add.assert_has_calls([call("url", "tender_id", "Not Found")])

        # Test with extract_tender_adapter return Tender object
        request.registry.mongodb.tenders.get.return_value = tender_data
        doc = extract_tender_doc(request)
        self.assertEqual(doc, tender_data)


class TestCalculateTenderBusinessDate(TestUtilsBase):
    def test_working_days(self):
        date_obj = parse_date("2020-11-07T12:00:00+02:00")
        delta_obj = timedelta(days=7)

        business_date = calculate_tender_business_date(date_obj, delta_obj, tender={}, working_days=True)
        self.assertEqual(business_date.isoformat(), "2020-11-18T00:00:00+02:00")

    def test_working_days_backwards(self):
        date_obj = parse_date("2020-11-19T12:00:00+02:00")
        delta_obj = -timedelta(days=7)

        business_date = calculate_tender_business_date(date_obj, delta_obj, tender={}, working_days=True)
        self.assertEqual(business_date.isoformat(), "2020-11-10T00:00:00+02:00")

    def test_calendar_days(self):
        date_obj = parse_date("2020-11-07T12:00:00+02:00")
        delta_obj = timedelta(days=7)

        business_date = calculate_tender_business_date(date_obj, delta_obj, tender={}, working_days=False)
        self.assertEqual(business_date.isoformat(), "2020-11-15T00:00:00+02:00")

    def test_calendar_days_backwards(self):
        date_obj = parse_date("2020-11-15T12:00:00+02:00")
        delta_obj = -timedelta(days=7)

        business_date = calculate_tender_business_date(date_obj, delta_obj, tender={}, working_days=False)
        self.assertEqual(business_date.isoformat(), "2020-11-08T00:00:00+02:00")

    def test_working_days_dst_transition(self):
        date_obj = parse_date("2021-03-10T12:00:00+02:00")
        delta_obj = timedelta(days=30)

        business_date = calculate_tender_business_date(date_obj, delta_obj, tender={}, working_days=True)
        self.assertEqual(business_date.isoformat(), "2021-04-22T00:00:00+03:00")

    def test_working_days_dst_transition_backwards(self):
        date_obj = parse_date("2021-04-21T12:00:00+03:00")
        delta_obj = -timedelta(days=30)

        business_date = calculate_tender_business_date(date_obj, delta_obj, tender={}, working_days=True)
        self.assertEqual(business_date.isoformat(), "2021-03-10T00:00:00+02:00")

    def test_calendar_dst_transition(self):
        date_obj = parse_date("2021-03-10T12:00:00+02:00")
        delta_obj = timedelta(days=30)

        business_date = calculate_tender_business_date(date_obj, delta_obj, tender={}, working_days=False)
        self.assertEqual(business_date.isoformat(), "2021-04-10T00:00:00+03:00")

    def test_calendar_dst_transition_backwards(self):
        date_obj = parse_date("2021-04-10T12:00:00+03:00")
        delta_obj = -timedelta(days=30)

        business_date = calculate_tender_business_date(date_obj, delta_obj, tender={}, working_days=False)
        self.assertEqual(business_date.isoformat(), "2021-03-11T00:00:00+02:00")

    def test_calendar_dst_transition_backwards_from_midnight(self):
        date_obj = parse_date("2021-04-10T00:00:00+03:00")
        delta_obj = -timedelta(days=30)

        business_date = calculate_tender_business_date(date_obj, delta_obj, tender={}, working_days=False)
        self.assertEqual(business_date.isoformat(), "2021-03-11T00:00:00+02:00")

    def test_with_accelerator(self):
        date_obj = datetime(2021, 10, 7)
        delta_obj = timedelta(days=7)

        # Test with accelerator = 1440
        context = {"procurementMethodDetails": "quick, accelerator=1440", "procurementMethodType": "negotiation"}
        business_date = calculate_tender_business_date(date_obj, delta_obj, tender=context, working_days=True)
        self.assertEqual(business_date, datetime(2021, 10, 7, 0, 7))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")


@contextmanager
def change_auth(app, auth):
    authorization = app.authorization
    app.authorization = auth
    yield app
    app.authorization = authorization
