# -*- coding: utf-8 -*-
from contextlib import contextmanager

import unittest
from copy import deepcopy

from datetime import datetime, timedelta
from mock import patch, MagicMock, call
from schematics.transforms import wholelist
from schematics.types import StringType
from pyramid.exceptions import URLDecodeError
from openprocurement.tender.core.utils import (
    SubscribersPicker,
    isTender,
    generate_tender_id,
    tender_from_data,
    extract_tender_id,
    extract_tender_doc,
    extract_tender,
    register_tender_procurementMethodType,
    has_unanswered_complaints,
    has_unanswered_questions,
    calculate_tender_business_date,
    calculate_date_diff,
    submission_method_details_includes,
    QUICK,
    QUICK_NO_AUCTION,
    QUICK_FAST_FORWARD,
    QUICK_FAST_AUCTION,
)
from openprocurement.api.constants import TZ
from openprocurement.tender.core.models import Tender as BaseTender, Lot, Complaint, Item, Question


class Tender(BaseTender):
    class Options:
        roles = {"draft": wholelist()}

    procurementMethodType = StringType(
        choices=["esco.EU", "bellowThreshold", "aboveThresholdEU"], default="bellowThreshold"
    )


class TestUtilsBase(unittest.TestCase):
    def setUp(self):
        self.tender_data = {
            "id": "ae50ea25bb1349898600ab380ee74e57",
            "dateModified": "2016-04-18T11:26:10.320970+03:00",
            "status": "draft",
            "tenderID": "UA-2016-04-18-000003",
        }
        self.lots = [
            Lot(
                {
                    "id": "11111111111111111111111111111111",
                    "title": "Earth",
                    "value": {"amount": 500000},
                    "minimalStep": {"amount": 1000},
                }
            ),
            Lot(
                {
                    "id": "22222222222222222222222222222222",
                    "title": "Mars",
                    "value": {"amount": 600000},
                    "minimalStep": {"amount": 2000},
                }
            ),
        ]
        self.items = [Item({"description": "Some item", "relatedLot": "11111111111111111111111111111111"})]


class TestUtils(TestUtilsBase):
    def setUp(self):
        self.tender_data = {
            "id": "ae50ea25bb1349898600ab380ee74e57",
            "dateModified": "2016-04-18T11:26:10.320970+03:00",
            "status": "draft",
            "tenderID": "UA-2016-04-18-000003",
        }
        self.lots = [
            Lot(
                {
                    "id": "11111111111111111111111111111111",
                    "title": "Earth",
                    "value": {"amount": 500000},
                    "minimalStep": {"amount": 1000},
                }
            ),
            Lot(
                {
                    "id": "22222222222222222222222222222222",
                    "title": "Mars",
                    "value": {"amount": 600000},
                    "minimalStep": {"amount": 2000},
                }
            ),
        ]
        self.items = [Item({"description": "Some item", "relatedLot": "11111111111111111111111111111111"})]

    def test_generate_tender_id(self):
        ctime = datetime.now(TZ)
        request = MagicMock()
        request.registry.mongodb.get_next_sequence_value.return_value = 99

        tender_id = generate_tender_id(request)
        tid = "UA-{:04}-{:02}-{:02}-{:06}-a".format(
            ctime.year, ctime.month, ctime.day, 99
        )
        self.assertEqual(tid, tender_id)

    def test_register_tender_procurementMethodType(self):
        config = MagicMock()
        config.registry.tender_procurementMethodTypes = {}

        self.assertEqual(config.registry.tender_procurementMethodTypes, {})
        register_tender_procurementMethodType(config, Tender)
        bellow_threshold = config.registry.tender_procurementMethodTypes.get("bellowThreshold")
        self.assertEqual(bellow_threshold, Tender)

    def test_calculate_tender_business_date(self):
        date_obj = datetime(2017, 10, 7)
        delta_obj = timedelta(days=7)

        # Test with accelerator = 1440
        context = {"procurementMethodDetails": "quick, accelerator=1440", "procurementMethodType": "negotiation"}
        business_date = calculate_tender_business_date(date_obj, delta_obj, tender=context, working_days=True)
        self.assertEqual(business_date, datetime(2017, 10, 7, 0, 7))

    def test_calculate_date_diff(self):
        dt1 = datetime(2020, 3, 17, 13)
        dt2 = dt1
        dt3 = datetime(2020, 3, 20)
        dt4 = datetime(2020, 3, 22)
        dt5 = datetime(2020, 3, 23, 15)

        self.assertEqual(calculate_date_diff(dt2, dt1), timedelta(days=0))
        self.assertEqual(calculate_date_diff(dt3, dt1), timedelta(days=2, hours=11))
        self.assertEqual(calculate_date_diff(dt4, dt1), timedelta(days=2, hours=11))
        self.assertEqual(calculate_date_diff(dt5, dt1), timedelta(days=4, hours=2))

        dt6 = datetime(2020, 4, 17, 17, 37)
        dt7 = datetime(2020, 4, 17, 17, 30)
        self.assertEqual(calculate_date_diff(dt6, dt7), timedelta(minutes=7))

    @patch("openprocurement.tender.core.utils.error_handler")
    def test_tender_from_data(self, mocked_handler):
        mocked_handler.return_value = Exception("Mocked!")
        request = MagicMock()
        request.registry.tender_procurementMethodTypes.get.side_effect = [None, None, Tender, Tender]

        with self.assertRaises(Exception) as e:
            tender_from_data(request, self.tender_data)
        self.assertEqual(str(e.exception), "Mocked!")
        self.assertEqual(request.errors.status, 415)
        request.errors.add.assert_called_once_with("body", "procurementMethodType", "Not implemented")

        model = tender_from_data(request, self.tender_data, raise_error=False)
        self.assertIs(model, None)

        model = tender_from_data(request, self.tender_data, create=False)
        self.assertIs(model, Tender)

        model = tender_from_data(request, self.tender_data)
        self.assertIsInstance(model, Tender)

    def test_tender_from_data_revisions(self):
        request = MagicMock()
        request.registry.tender_procurementMethodTypes = {"belowThreshold": Tender}

        data = dict(**self.tender_data)
        data["revisions"] = [dict(rev=str(i), author="me") for i in range(10)]

        for method in ("GET", "POST", "PATCH", "PUT", "DELETE", "HEAD"):
            request.environ = {"REQUEST_METHOD": method}
            model = tender_from_data(request, data)

            self.assertEqual(len(model.revisions), 10)
            self.assertEqual(model.revisions[0]["rev"], "0")

    @patch("openprocurement.tender.core.utils.decode_path_info")
    @patch("openprocurement.tender.core.utils.error_handler")
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

    @patch("openprocurement.tender.core.utils.extract_tender_id")
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

    def test_extract_tender(self):
        request = MagicMock()
        tender_data = deepcopy(self.tender_data)
        tender_data["doc_type"] = "Tender"

        request.tender_doc = tender_data
        request.registry.tender_procurementMethodTypes.get.return_value = Tender
        request.tender_from_data.return_value = tender_from_data(request, tender_data)

        # Test with extract_tender_adapter return Tender object
        request.registry.mongodb.tenders.get.return_value = tender_data
        tender = extract_tender(request)
        serialized_tender = tender.serialize("draft")
        self.assertIsInstance(tender, Tender)
        for k in tender_data:
            self.assertEqual(tender_data[k], serialized_tender[k])

    def test_has_unanswered_complaints(self):
        tender = Tender(self.tender_data)
        tender.block_tender_complaint_status = ["pending"]
        tender.lots = self.lots
        tender.complaints = [
            Complaint(
                {"status": "pending", "relatedLot": "11111111111111111111111111111111", "title": "Earth is mine!"}
            )
        ]
        self.assertEqual(True, has_unanswered_complaints(tender))

        tender.complaints[0].relatedLot = "33333333333333333333333333333333"
        self.assertEqual(False, has_unanswered_complaints(tender))

        self.assertEqual(True, has_unanswered_complaints(tender, False))

        tender.complaints[0].status = "resolved"
        self.assertEqual(False, has_unanswered_complaints(tender, False))

    def test_has_unanswered_questions(self):
        tender = Tender(self.tender_data)
        tender.lots = self.lots
        tender.items = self.items
        tender.questions = [
            Question(
                {
                    "questionOf": "lot",
                    "relatedItem": "11111111111111111111111111111111",
                    "title": "Do you have some Earth?",
                }
            )
        ]
        self.assertEqual(True, has_unanswered_questions(tender))
        self.assertEqual(True, has_unanswered_questions(tender, False))

        tender.questions[0].answer = "No"
        self.assertEqual(False, has_unanswered_questions(tender))
        self.assertEqual(False, has_unanswered_questions(tender, False))


class TestIsTender(TestUtilsBase):
    def test_is_tender(self):
        tender = Tender(self.tender_data)
        is_tender = isTender("bellowThreshold", None)
        self.assertEqual(is_tender.phash(), "procurementMethodType = bellowThreshold")
        request = MagicMock()
        request.tender_doc = None

        self.assertEqual(False, is_tender(None, request))

        request.tender_doc = {"procurementMethodType": "bellowThreshold"}
        self.assertEqual(True, is_tender(None, request))

        is_tender = isTender("esco.EU", None)
        self.assertEqual(is_tender.phash(), "procurementMethodType = esco.EU")
        self.assertEqual(False, is_tender(None, request))
        self.assertEqual(tender.procurementMethodType, "bellowThreshold")

    def test_subcribers_picker(self):
        picker = SubscribersPicker("bellowThreshold", None)
        tender = Tender(self.tender_data)
        event = MagicMock()
        event.tender = None
        self.assertEqual(picker.phash(), "procurementMethodType = bellowThreshold")
        self.assertEqual(False, picker(event))

        event.tender = tender
        self.assertEqual(True, picker(event))

        picker = SubscribersPicker("esco.EU", None)
        self.assertEqual(picker.phash(), "procurementMethodType = esco.EU")
        self.assertEqual(False, picker(event))


class TestSubmissionMethodDetailsSearch(TestUtilsBase):

    def test_search_quick(self):
        tender = Tender(self.tender_data)
        tender.submissionMethodDetails = "some;quick"

        self.assertTrue(submission_method_details_includes(QUICK, tender))

    def test_search_quick_fast_forward(self):
        tender = Tender(self.tender_data)
        tender.submissionMethodDetails = "some;quick(mode:fast-forward)"

        self.assertTrue(submission_method_details_includes(QUICK_FAST_FORWARD, tender))

    def test_search_quick_fast_auction(self):
        tender = Tender(self.tender_data)
        tender.submissionMethodDetails = "some;quick(mode:fast-auction)"

        self.assertTrue(submission_method_details_includes(QUICK_FAST_AUCTION, tender))

    def test_search_quick_no_auction(self):
        tender = Tender(self.tender_data)
        tender.submissionMethodDetails = "some;quick(mode:no-auction)"

        self.assertTrue(submission_method_details_includes(QUICK_NO_AUCTION, tender))

    def test_search_tuple(self):
        tender = Tender(self.tender_data)
        tender.submissionMethodDetails = "some;quick(mode:fast-forward)"

        self.assertTrue(submission_method_details_includes((QUICK_FAST_FORWARD, "another"), tender))

    def test_search_list(self):
        tender = Tender(self.tender_data)
        tender.submissionMethodDetails = "some;quick(mode:fast-forward)"

        self.assertTrue(submission_method_details_includes([QUICK_FAST_FORWARD, "another"], tender))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    suite.addTest(unittest.makeSuite(TestIsTender))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")


@contextmanager
def change_auth(app, auth):
    authorization = app.authorization
    app.authorization = auth
    yield app
    app.authorization = authorization
