# -*- coding: utf-8 -*-
from schematics.types.compound import ModelType, ListType
from schematics.exceptions import ModelValidationError
from openprocurement.tender.core.models import Lot, BaseTender
import unittest


class TestTenderMilestones(unittest.TestCase):

    initial_tender_data = dict(
        title="Tal"
    )

    def test_validate_without_milestones(self):
        tender = BaseTender(self.initial_tender_data)
        tender.validate()
        data = tender.serialize("embedded")
        self.assertNotIn("milestones", data)

    def test_validate_empty(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(milestones=[])
        tender = BaseTender(initial_data)
        tender.validate()
        data = tender.serialize("embedded")
        self.assertNotIn("milestones", data)

    def test_validate_empty_object(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(milestones=[{}])
        tender = BaseTender(initial_data)

        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        self.assertEqual(
            e.exception.message,
            {'milestones': [
                {
                    'title': [u'This field is required.'],
                    'code': [u'This field is required.'],
                    'duration': [u'This field is required.'],
                    'percentage': [u'This field is required.'],
                    'type': [u'This field is required.'],
                    'sequenceNumber': [u'This field is required.']
                }
            ]}
        )

    def test_validate_incorrect_required(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(milestones=[{
            'title': "Title",
            'code': 1488,
            'type': 'M',
            'duration': {},
            'percentage': -1,
            'sequenceNumber': -1,
        }])
        tender = BaseTender(initial_data)

        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        expected_title_options = [
            "executionOfWorks", "deliveryOfGoods",
            "submittingServices", "signingTheContract",
            "submissionDateOfApplications", "dateOfInvoicing",
            "endDateOfTheReportingPeriod", "anotherEvent"
        ]
        expected_codes = ["prepayment", "postpayment"]
        expected_types = ['financing']
        self.assertEqual(
            e.exception.message,
            {'milestones': [
                {
                    'title': [u"Value must be one of {}.".format(expected_title_options)],
                    'code': [u"Value must be one of {}.".format(expected_codes)],
                    'type': [u"Value must be one of {}.".format(expected_types)],
                    'duration': {'type': [u'This field is required.'],
                                 'days': [u'This field is required.']},
                    'percentage': [u'Float value should be greater than 0.'],
                    'sequenceNumber': [u'Int value should be greater than 0.']
                }]}
        )

    def test_title_other_description_required(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(milestones=[{
            'title': 'anotherEvent',
            'code': 'prepayment',
            'type': 'financing',
            'duration': {'days': 2, 'type': 'banking'},
            'percentage': 100,
            'sequenceNumber': 0,
        }])

        tender = BaseTender(initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(
            e.exception.message,
            {'milestones': [{'description': [u'This field is required.']}]}
        )

    def test_title_other_description_empty_invalid(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(milestones=[{
            'title': 'anotherEvent',
            'description': u'',
            'code': 'prepayment',
            'type': 'financing',
            'duration': {'days': 2, 'type': 'banking'},
            'percentage': 100,
            'sequenceNumber': 1,
        }])

        tender = BaseTender(initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(
            e.exception.message,
            {'milestones': [{'description': [u'This field is required.']}]}
        )

    def test_validate_percentage_too_big(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(milestones=[{
            'title': "deliveryOfGoods",
            'code': 'prepayment',
            'type': 'financing',
            'duration': {'days': 2, 'type': 'banking'},
            'percentage': 100.000001,
            'sequenceNumber': 2,
        }])

        tender = BaseTender(initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(
            e.exception.message,
            {'milestones': [{'percentage': [u'Float value should be less than 100.']}]}
        )

    def test_validate_percentage_sum(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 2,
                    'percentage': 49.999,
                },
                {
                    'title': "endDateOfTheReportingPeriod",
                    'code': 'postpayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 2,
                    'percentage': 50.002,
                },
            ]
        )

        tender = BaseTender(initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(
            e.exception.message,
            {'milestones': [u'Sum of the financial milestone percentages 100.001 is not equal 100.']}
        )


class TestMultiLotTenderMilestones(unittest.TestCase):

    initial_tender_data = dict(
        title="Tal",
        lots=[
            {
                "id": "a" * 32,
                "title": "#1",
                "minimalStep": {"amount": 10},
                "value": {"amount": 100}
            },
            {
                "id": "b" * 32,
                "title": "#2",
                "minimalStep": {"amount": 5},
                "value": {"amount": 50.31}
            }
        ]
    )

    class MultiLotTender(BaseTender):
        lots = ListType(ModelType(Lot))

    def test_validate_related_lot_not_required(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(
            milestones=[{
                'title': "deliveryOfGoods",
                'code': 'prepayment',
                'type': 'financing',
                'duration': {'days': 2, 'type': 'banking'},
                'percentage': 100,
                'sequenceNumber': 0,
            }],
        )

        tender = self.MultiLotTender(initial_data)
        tender.validate()

    def test_validate_related_lot_incorrect(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(
            milestones=[{
                'title': "deliveryOfGoods",
                'code': 'prepayment',
                'type': 'financing',
                'duration': {'days': 2, 'type': 'banking'},
                'percentage': 50,
                'sequenceNumber': 0,
                'relatedLot': 'c' * 32,
            }],
        )

        tender = self.MultiLotTender(initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(
            e.exception.message,
            {'milestones': [{'relatedLot': [u'relatedLot should be one of the lots.']}]}
        )

    def test_validate_lot_sum_incorrect(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 50,
                    'relatedLot': 'a' * 32,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'postpayment',
                    'type': 'financing',
                    'duration': {'days': 15, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 100,
                    'relatedLot': 'b' * 32,
                }
            ],
        )

        tender = self.MultiLotTender(initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(
            e.exception.message,
            {'milestones': [
                u'Sum of the financial milestone percentages 50.0 is not equal 100 for lot {}.'.format("a" * 32)
            ]}
        )

    def test_validate_lot_sum_success(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 45.55,
                    'relatedLot': 'b' * 32,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'postpayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 54.45,
                    'relatedLot': 'b' * 32,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 100.,
                    'relatedLot': 'a' * 32,
                }
            ],
        )

        tender = self.MultiLotTender(initial_data)
        tender.validate()

    def test_validate_lot_sum_third(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 33.333,
                    'relatedLot': 'b' * 32,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'postpayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 33.333,
                    'relatedLot': 'b' * 32,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 33.333,
                    'relatedLot': 'b' * 32,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 15, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 100,
                    'relatedLot': 'a' * 32,
                }
            ],
        )

        tender = self.MultiLotTender(initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(
            e.exception.message,
            {'milestones': [
                u'Sum of the financial milestone percentages 99.999 is not equal 100 for lot {}.'.format(u'b' * 32)
            ]}
        )

    def test_validate_lot_sum_third_success(self):
        initial_data = dict(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 33.333,
                    'relatedLot': 'b' * 32,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 33.333,
                    'relatedLot': 'b' * 32,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 33.334,
                    'relatedLot': 'b' * 32,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'postpayment',
                    'type': 'financing',
                    'duration': {'days': 15, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 100,
                    'relatedLot': 'a' * 32,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'prepayment',
                    'type': 'financing',
                    'duration': {'days': 2, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 51,
                },
                {
                    'title': "deliveryOfGoods",
                    'code': 'postpayment',
                    'type': 'financing',
                    'duration': {'days': 15, 'type': 'banking'},
                    'sequenceNumber': 0,
                    'percentage': 49,
                }
            ],
        )

        tender = self.MultiLotTender(initial_data)
        tender.validate()

