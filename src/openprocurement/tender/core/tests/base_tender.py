import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import MagicMock, patch

from schematics.exceptions import ModelValidationError
from schematics.types.compound import ListType, ModelType

from openprocurement.api.context import set_now, set_request
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_data,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.utils import set_tender_lots
from openprocurement.tender.core.procedure.models.lot import Lot
from openprocurement.tender.core.procedure.models.milestone import TenderMilestoneTypes
from openprocurement.tender.core.procedure.models.tender import PostTender, Tender

test_tender_data = deepcopy(test_tender_below_data)
del test_tender_data["procurementMethodType"]
del test_tender_data["milestones"]
test_tender_data["awardCriteria"] = "lowestCost"
test_tender_data["procurementMethod"] = "open"

test_tender_data_with_lots = set_tender_lots(
    deepcopy(test_tender_data),
    test_tender_below_lots * 2,
)


def create_tender_instance(model, data):
    request = MagicMock()
    request.registry.mongodb.get_next_sequence_value.return_value = 1
    set_request(request)
    set_now(get_now())
    tender_data = PostTender(data).serialize()
    tender = model(tender_data)
    request.validated = {"tender": tender_data}
    return tender


class TestTenderMilestones(unittest.TestCase):
    initial_tender_data = test_tender_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_validate_without_milestones(self):
        with patch(
            "openprocurement.tender.core.procedure.models.tender.MILESTONES_VALIDATION_FROM",
            get_now() - timedelta(days=1),
        ):
            tender = create_tender_instance(Tender, self.initial_tender_data)
            data = tender.serialize()
            self.assertNotIn("milestones", data)
            with self.assertRaises(ModelValidationError) as e:
                tender.validate()
            self.assertEqual(e.exception.messages, {"milestones": ["Tender should contain at least one milestone"]})

    def test_regression_milestones(self):
        with patch(
            "openprocurement.tender.core.procedure.models.tender.MILESTONES_VALIDATION_FROM",
            get_now() + timedelta(days=1),
        ):
            tender = create_tender_instance(Tender, self.initial_tender_data)
            tender.validate()
            data = tender.serialize()
            self.assertNotIn("milestones", data)

    def test_validate_empty(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(milestones=[])
        tender = create_tender_instance(Tender, initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        self.assertEqual(e.exception.messages, {"milestones": ["Tender should contain at least one milestone"]})

    def test_validate_empty_object(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(milestones=[{}])
        tender = create_tender_instance(Tender, initial_data)

        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        self.assertEqual(
            e.exception.messages,
            {
                "milestones": [
                    {
                        "title": ["This field is required."],
                        "code": ["This field is required."],
                        "duration": ["This field is required."],
                        'percentage': ['This field is required.'],
                        "type": ["This field is required."],
                        "sequenceNumber": ["This field is required."],
                    }
                ]
            },
        )

    def test_validate_incorrect_required(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    "title": "Title",
                    "code": 1488,
                    "type": "M",
                    "duration": {"type": "type"},
                    "percentage": 0,
                    "sequenceNumber": -1,
                }
            ]
        )
        tender = create_tender_instance(Tender, initial_data)

        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        expected_types = [TenderMilestoneTypes.FINANCING.value, TenderMilestoneTypes.DELIVERY.value]
        self.maxDiff = None
        self.assertEqual(
            e.exception.messages,
            {
                "milestones": [
                    {
                        "type": ["Value must be one of {}.".format(expected_types)],
                        "duration": {
                            "type": ["Value must be one of ['working', 'banking', 'calendar']."],
                            "days": ["This field is required."],
                        },
                        "percentage": ["Float value should be greater than 0."],
                        "sequenceNumber": ["Int value should be greater than 0."],
                    }
                ]
            },
        )

    def test_title_other_description_required(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    "title": "anotherEvent",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "percentage": 100,
                    "sequenceNumber": 0,
                }
            ]
        )

        tender = create_tender_instance(Tender, initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(e.exception.messages, {"milestones": [{"description": ["This field is required."]}]})

    def test_title_other_description_empty_invalid(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    "title": "anotherEvent",
                    "description": "",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "percentage": 100,
                    "sequenceNumber": 1,
                }
            ]
        )

        tender = create_tender_instance(Tender, initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(e.exception.messages, {"milestones": [{"description": ["This field is required."]}]})

    def test_validate_percentage_too_big(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    "title": "deliveryOfGoods",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "percentage": 100.000001,
                    "sequenceNumber": 2,
                }
            ]
        )

        tender = create_tender_instance(Tender, initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(
            e.exception.messages, {"milestones": [{"percentage": ["Float value should be less than 100."]}]}
        )

    def test_validate_percentage_sum_float_point(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    "title": "deliveryOfGoods",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 2,
                    "percentage": 8.34,
                }
            ]
            * 4
            + [
                {
                    "title": "endDateOfTheReportingPeriod",
                    "code": "postpayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 2,
                    "percentage": 8.33,
                }
            ]
            * 8
        )

        tender = create_tender_instance(Tender, initial_data)
        tender.validate()


class TestMultiLotTenderMilestones(unittest.TestCase):
    initial_tender_data = test_tender_data_with_lots

    class MultiLotTender(Tender):
        lots = ListType(ModelType(Lot, required=True))

    def test_validate_related_lot_not_required(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    "title": "deliveryOfGoods",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "percentage": 100,
                    "sequenceNumber": 0,
                }
            ]
        )

        tender = create_tender_instance(self.MultiLotTender, initial_data)
        tender.validate()

    def test_validate_related_lot_incorrect(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    "title": "deliveryOfGoods",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "percentage": 100,
                    "sequenceNumber": 0,
                    "relatedLot": "c" * 32,
                }
            ]
        )

        tender = create_tender_instance(self.MultiLotTender, initial_data)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()

        self.assertEqual(e.exception.messages, {"milestones": ["relatedLot should be one of the lots."]})

    def test_validate_lot_sum_success(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    "title": "deliveryOfGoods",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 0,
                    "percentage": 45.55,
                    "relatedLot": initial_data["lots"][0]["id"],
                },
                {
                    "title": "deliveryOfGoods",
                    "code": "postpayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 0,
                    "percentage": 54.45,
                    "relatedLot": initial_data["lots"][0]["id"],
                },
                {
                    "title": "deliveryOfGoods",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 0,
                    "percentage": 100.0,
                    "relatedLot": initial_data["lots"][1]["id"],
                },
            ]
        )

        tender = create_tender_instance(self.MultiLotTender, initial_data)
        tender.validate()

    def test_validate_lot_sum_third_success(self):
        initial_data = deepcopy(self.initial_tender_data)
        initial_data.update(
            milestones=[
                {
                    "title": "deliveryOfGoods",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 0,
                    "percentage": 33.333,
                    "relatedLot": initial_data["lots"][1]["id"],
                },
                {
                    "title": "deliveryOfGoods",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 0,
                    "percentage": 33.333,
                    "relatedLot": initial_data["lots"][1]["id"],
                },
                {
                    "title": "deliveryOfGoods",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 0,
                    "percentage": 33.334,
                    "relatedLot": initial_data["lots"][1]["id"],
                },
                {
                    "title": "deliveryOfGoods",
                    "code": "postpayment",
                    "type": "financing",
                    "duration": {"days": 15, "type": "banking"},
                    "sequenceNumber": 0,
                    "percentage": 100,
                    "relatedLot": initial_data["lots"][0]["id"],
                },
                {
                    "title": "deliveryOfGoods",
                    "code": "prepayment",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 0,
                    "percentage": 51,
                },
                {
                    "title": "deliveryOfGoods",
                    "code": "postpayment",
                    "type": "financing",
                    "duration": {"days": 15, "type": "banking"},
                    "sequenceNumber": 0,
                    "percentage": 49,
                },
            ]
        )

        tender = create_tender_instance(self.MultiLotTender, initial_data)
        tender.validate()
