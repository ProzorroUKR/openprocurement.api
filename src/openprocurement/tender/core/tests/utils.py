# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, time
from mock import patch, MagicMock, call
from schematics.transforms import wholelist
from schematics.types import StringType
from pyramid.exceptions import URLDecodeError
from openprocurement.tender.core.utils import (
    generate_tender_id, tender_serialize, tender_from_data,
    register_tender_procurementMethodType, calculate_business_date,
    isTender, SubscribersPicker, extract_tender, has_unanswered_complaints,
    has_unanswered_questions
)
from openprocurement.api.constants import TZ
from openprocurement.tender.core.models import (
    Tender as BaseTender, Lot, Complaint, Item, Question
)


class Tender(BaseTender):
    class Options:
        roles = {
            'draft': wholelist()
        }
    procurementMethodType = StringType(
        choices=['esco.EU', 'bellowThreshold', 'aboveThresholdEU'],
        default='bellowThreshold'
    )


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.tender_data = {
            'id': 'ae50ea25bb1349898600ab380ee74e57',
            'dateModified': '2016-04-18T11:26:10.320970+03:00',
            'status': 'draft',
            'tenderID': 'UA-2016-04-18-000003'
        }
        self.lots = [Lot({
            'id': '11111111111111111111111111111111',
            'title': 'Earth',
            'value': {'amount': 500000},
            'minimalStep': {'amount': 1000}
        }), Lot({
            'id': '22222222222222222222222222222222',
            'title': 'Mars',
            'value': {'amount': 600000},
            'minimalStep': {'amount': 2000}
        })]
        self.items = [Item({
            'description': 'Some item',
            'relatedLot': '11111111111111111111111111111111'
        })]

    def test_generate_tender_id(self):
        server_id = '7'
        ctime = datetime.now(TZ)
        db = MagicMock()

        def db_get(doc_id, default_value):
            return default_value

        db.get = db_get
        tender_id = generate_tender_id(ctime, db, server_id)
        tid = 'UA-{:04}-{:02}-{:02}-{:06}{}'.format(
            ctime.year, ctime.month, ctime.day, 1,
            server_id and '-' + server_id)
        self.assertEqual(tid, tender_id)

    def test_tender_serialize(self):
        request = MagicMock()
        request.tender_from_data.return_value = None
        request.context = None

        tender_data = {}
        fields = []
        tender = tender_serialize(request, tender_data, fields)
        self.assertEqual(
            tender, {'procurementMethodType': '', 'dateModified': '', 'id': ''}
        )

        request.context = self.tender_data
        request.tender_from_data.return_value = Tender(self.tender_data)
        fields = ['id', 'dateModified', 'status', 'tenderID']
        tender = tender_serialize(request, self.tender_data, fields)
        self.assertEqual(tender, self.tender_data)

    def test_register_tender_procurementMethodType(self):
        config = MagicMock()
        config.registry.tender_procurementMethodTypes = {}

        self.assertEqual(config.registry.tender_procurementMethodTypes, {})
        register_tender_procurementMethodType(config, Tender)
        bellow_threshold = config.registry.tender_procurementMethodTypes.get(
            'bellowThreshold'
        )
        self.assertEqual(bellow_threshold, Tender)

    def test_calculate_business_date(self):
        date_obj = datetime(2017,10,7)
        delta_obj = timedelta(days=7)

        # Test with accelerator = 1440
        context = {
            "procurementMethodDetails": "quick, accelerator=1440",
            "procurementMethodType": "negotiation"
        }
        business_date = calculate_business_date(
            date_obj, delta_obj, context=context, working_days=True)
        self.assertEqual(business_date, datetime(2017, 10, 7, 0, 7))

        # Test without context and working_days
        business_date = calculate_business_date(date_obj, delta_obj)
        self.assertEqual(business_date, datetime(2017, 10, 14))

        # Test with working_days and timedelta_obj > timedelta()
        business_date = calculate_business_date(
            date_obj, delta_obj, working_days=True)
        self.assertEqual(business_date, datetime(2017, 10, 19))

        # Test with working days and timedelta_obj < timedelta()
        business_date = calculate_business_date(
            date_obj, timedelta(0), working_days=True
        )
        self.assertEqual(business_date, datetime(2017, 10, 7))

        # Another test with working days and timedelta > timedelta()
        date_obj = datetime(2017, 10, 15)
        delta_obj = timedelta(1)
        business_date = calculate_business_date(
            date_obj, delta_obj, working_days=True
        )
        self.assertEqual(business_date, datetime(2017, 10, 18))

    @patch('openprocurement.tender.core.utils.error_handler')
    def test_tender_from_data(self, mocked_handler):
        mocked_handler.return_value = Exception('Mocked!')
        request = MagicMock()
        request.registry.tender_procurementMethodTypes.get.side_effect = [
            None, None, Tender, Tender
        ]

        with self.assertRaises(Exception) as e:
            tender_from_data(request, self.tender_data)
        self.assertEqual(e.exception.message, 'Mocked!')
        self.assertEqual(request.errors.status, 415)
        request.errors.add.assert_called_once_with(
            'data', 'procurementMethodType', 'Not implemented'
        )

        model = tender_from_data(request, self.tender_data, raise_error=False)
        self.assertIs(model, None)

        model = tender_from_data(request, self.tender_data, create=False)
        self.assertIs(model, Tender)

        model = tender_from_data(request, self.tender_data)
        self.assertIsInstance(model, Tender)

    @patch('openprocurement.tender.core.utils.decode_path_info')
    @patch('openprocurement.tender.core.utils.error_handler')
    def test_extract_tender(self, mocked_error_handler, mocked_decode_path):
        mocked_error_handler.return_value = Exception('Oops.')
        mocked_decode_path.side_effect = [
            KeyError('Missing \'PATH_INFO\''),
            UnicodeDecodeError('UTF-8', 'obj', 1, 10, 'Hm...'),
            '/', '/api/2.3/tenders/{}'.format(self.tender_data['id'])]
        tender_data = deepcopy(self.tender_data)
        tender_data['doc_type'] = 'Tender'
        request = MagicMock()
        request.environ = {'PATH_INFO': '/'}
        request.registry.tender_procurementMethodTypes.get.return_value = \
            Tender
        request.tender_from_data.return_value = \
            tender_from_data(request, tender_data)
        request.registry.db = MagicMock()

        # Test with KeyError
        self.assertIs(extract_tender(request), None)

        # Test with UnicodeDecodeError
        with self.assertRaises(URLDecodeError) as e:
            extract_tender(request)
        self.assertEqual(e.exception.encoding, 'UTF-8')
        self.assertEqual(e.exception.object, 'obj')
        self.assertEqual(e.exception.start, 1)
        self.assertEqual(e.exception.end, 10)
        self.assertEqual(e.exception.reason, 'Hm...')
        self.assertIsInstance(e.exception, URLDecodeError)

        # Test with path '/'
        self.assertIs(extract_tender(request), None)

        mocked_decode_path.side_effect = ['/api/2.3/tenders/{}'.format(
            self.tender_data['id'])] * 3

        # Test with extract_tender_adapter raise HTTP 410
        request.registry.db.get.return_value = {'doc_type': 'tender'}
        with self.assertRaises(Exception) as e:
            extract_tender(request)
        self.assertEqual(request.errors.status, 410)
        request.errors.add.assert_called_once_with(
            'url', 'tender_id', 'Archived')

        # Test with extract_tender_adapter raise HTTP 404
        request.registry.db.get.return_value = {'doc_type': 'notTender'}
        with self.assertRaises(Exception) as e:
            extract_tender(request)
        self.assertEqual(request.errors.status, 404)
        request.errors.add.assert_has_calls([
            call('url', 'tender_id', 'Not Found')])

        # Test with extract_tender_adapter return Tender object
        request.registry.db.get.return_value = tender_data
        tender = extract_tender(request)
        serialized_tender = tender.serialize('draft')
        self.assertIsInstance(tender, Tender)
        for k in tender_data:
            self.assertEqual(tender_data[k], serialized_tender[k])

    def test_has_unanswered_complaints(self):
        tender = Tender(self.tender_data)
        tender.block_tender_complaint_status = ['pending']
        tender.lots = self.lots
        tender.complaints = [Complaint({
            'status': 'pending',
            'relatedLot': '11111111111111111111111111111111',
            'title': 'Earth is mine!'
        })]
        self.assertEqual(True, has_unanswered_complaints(tender))

        tender.complaints[0].relatedLot = '33333333333333333333333333333333'
        self.assertEqual(False, has_unanswered_complaints(tender))

        self.assertEqual(True, has_unanswered_complaints(tender, False))

        tender.complaints[0].status = 'resolved'
        self.assertEqual(False, has_unanswered_complaints(tender, False))

    def test_has_unanswered_questions(self):
        tender = Tender(self.tender_data)
        tender.lots = self.lots
        tender.items = self.items
        tender.questions = [Question({
            'questionOf': 'lot',
            'relatedItem': '11111111111111111111111111111111',
            'title': 'Do you have some Earth?'
        })]
        self.assertEqual(True, has_unanswered_questions(tender))
        self.assertEqual(True, has_unanswered_questions(tender, False))

        tender.questions[0].answer = 'No'
        self.assertEqual(False, has_unanswered_questions(tender))
        self.assertEqual(False, has_unanswered_questions(tender, False))


class TestIsTender(TestUtils):

    def test_is_tender(self):
        tender = Tender(self.tender_data)
        is_tender = isTender('bellowThreshold', None)
        self.assertEqual(is_tender.phash(),
                         'procurementMethodType = bellowThreshold')
        request = MagicMock()
        request.tender = None

        self.assertEqual(False, is_tender(None, request))

        request.tender = tender
        self.assertEqual(True, is_tender(None, request))

        is_tender = isTender('esco.EU', None)
        self.assertEqual(is_tender.phash(), 'procurementMethodType = esco.EU')
        self.assertEqual(False, is_tender(None, request))
        self.assertEqual(tender.procurementMethodType, 'bellowThreshold')

    def test_subcribers_picker(self):
        picker = SubscribersPicker('bellowThreshold', None)
        tender = Tender(self.tender_data)
        event = MagicMock()
        event.tender = None
        self.assertEqual(picker.phash(),
                         'procurementMethodType = bellowThreshold')
        self.assertEqual(False, picker(event))

        event.tender = tender
        self.assertEqual(True, picker(event))

        picker = SubscribersPicker('esco.EU', None)
        self.assertEqual(picker.phash(), 'procurementMethodType = esco.EU')
        self.assertEqual(False, picker(event))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    suite.addTest(unittest.makeSuite(TestIsTender))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')