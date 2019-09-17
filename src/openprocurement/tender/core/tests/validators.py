# -*- coding: utf-8 -*-
import copy
import mock
import unittest
from decimal import Decimal

from pyramid.httpexceptions import HTTPError
from schematics.exceptions import ModelValidationError

from openprocurement.tender.core.validation import (
    validate_update_contract_value_with_award,
    validate_update_contract_value,
    validate_update_contract_value_amount
)
from openprocurement.tender.belowthreshold.models import Tender
from openprocurement.tender.belowthreshold.tests.base import test_tender_data


def generate_contract_value_patch_request_mock(contract_value, award_value=None):
    request = mock.MagicMock(validated={})
    if award_value:
        award = mock.MagicMock(id='test_id', value=mock.Mock(**award_value))
        request.validated['tender'] = mock.MagicMock(awards=[award])
        request.context.awardID = 'test_id'
    request.validated['data'] = request.validated['json_data'] = {'value': contract_value}
    return request


@mock.patch('openprocurement.api.utils.error_handler', lambda *_:HTTPError)
class TestValidateUpdateContractValue(unittest.TestCase):

    def test_readonly_fields(self):
        request = generate_contract_value_patch_request_mock(
            contract_value={'currency': 'test', 'valueAddedTaxIncluded': 'updated'})
        request.context.value.to_native.return_value.get.return_value = 'updated'

        with self.assertRaises(HTTPError):
            validate_update_contract_value(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Can\'t update currency for contract value')


@mock.patch('openprocurement.api.utils.error_handler', lambda *_:HTTPError)
class TestValidateUpdateContractValueWithAward(unittest.TestCase):
    def test_pass_tax_included_for_included_award(self):
        request = generate_contract_value_patch_request_mock(
            contract_value={'amount': 90, 'amountNet': 80, 'currency': 'USD', 'valueAddedTaxIncluded': True},
            award_value={'amount': 100, 'valueAddedTaxIncluded': True})

        try:
            validate_update_contract_value_with_award(request)
        except HTTPError:
            self.fail("validate_update_contract_value_with_award() raised HTTPError unexpectedly")

    def test_fail_tax_included_for_included_award(self):
        request = generate_contract_value_patch_request_mock(
            contract_value={'amount': 105, 'amountNet': 95, 'currency': 'USD', 'valueAddedTaxIncluded': True},
            award_value={'amount': 100, 'valueAddedTaxIncluded': True})

        with self.assertRaises(HTTPError):
            validate_update_contract_value_with_award(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Amount should be less or equal to awarded amount')

    def test_pass_tax_not_included_for_included_award(self):
        request = generate_contract_value_patch_request_mock(
            contract_value={'amount': 90, 'amountNet': 80, 'currency': 'USD', 'valueAddedTaxIncluded': True},
            award_value={'amount': 100, 'valueAddedTaxIncluded': False})

        try:
            validate_update_contract_value_with_award(request)
        except HTTPError:
            self.fail("validate_update_contract_value_with_award() raised HTTPError unexpectedly")

    def test_fail_tax_not_included_for_included_award(self):
        request = generate_contract_value_patch_request_mock(
            contract_value={'amount': 105, 'amountNet': 95, 'currency': 'USD', 'valueAddedTaxIncluded': False},
            award_value={'amount': 100, 'valueAddedTaxIncluded': True})

        with self.assertRaises(HTTPError):
            validate_update_contract_value_with_award(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Amount should be less or equal to awarded amount')

    def test_pass_tax_included_for_not_included_award(self):
        request = generate_contract_value_patch_request_mock(
            contract_value={'amount': 105, 'amountNet': 95, 'currency': 'USD', 'valueAddedTaxIncluded': True},
            award_value={'amount': 100, 'valueAddedTaxIncluded': False})

        try:
            validate_update_contract_value_with_award(request)
        except HTTPError:
            self.fail("validate_update_contract_value_with_award() raised HTTPError unexpectedly")

    def test_fail_tax_included_for_not_included_award(self):
        request = generate_contract_value_patch_request_mock(
            contract_value={'amount': 110, 'amountNet': 105, 'currency': 'USD', 'valueAddedTaxIncluded': True},
            award_value={'amount': 100, 'valueAddedTaxIncluded': False})

        with self.assertRaises(HTTPError):
            validate_update_contract_value_with_award(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'AmountNet should be less or equal to awarded amount')


@mock.patch('openprocurement.api.utils.error_handler', lambda *_:HTTPError)
class TestValidateUpdateContractValueAmount(unittest.TestCase):
    def test_amount_net_greater_than_amount_error(self):
        request = generate_contract_value_patch_request_mock(
            contract_value={'amount': 100, 'amountNet': 200, 'currency': 'USD', 'valueAddedTaxIncluded': True})

        with self.assertRaises(HTTPError):
            validate_update_contract_value_amount(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Amount should be greater than amountNet and differ by no more than 20.0%')

    def test_amount_net_too_match_less_than_amount_error(self):
        request = generate_contract_value_patch_request_mock(
            contract_value={'amount': 100, 'amountNet': 50, 'currency': 'USD', 'valueAddedTaxIncluded': True})

        with self.assertRaises(HTTPError):
            validate_update_contract_value_amount(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Amount should be greater than amountNet and differ by no more than 20.0%')

    def test_amount_net_not_equal_to_amount_error(self):
        request = generate_contract_value_patch_request_mock(
            contract_value={'amount': 100, 'amountNet': 50, 'currency': 'USD', 'valueAddedTaxIncluded': False})

        with self.assertRaises(HTTPError):
            validate_update_contract_value_amount(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Amount and amountNet should be equal')

    def test_from_float(self):
        amount = 1478.4
        amount_net = 1232.0
        coef = 1.2

        #  the problem
        assert amount_net * coef == 1478.3999999999999

        request = generate_contract_value_patch_request_mock(
            contract_value={
                'amount': amount,
                'amountNet': amount_net,
                'currency': 'USD',
                'valueAddedTaxIncluded': True})

        try:
            validate_update_contract_value_amount(request)
        except HTTPError:
            self.fail("validate_update_contract_value_amount() raised HTTPError unexpectedly")


    def test_from_decimal(self):
        amount = Decimal('1478.4')
        amount_net = Decimal('1232.0')
        coef = Decimal('1.2')

        request = generate_contract_value_patch_request_mock(
            contract_value={
                'amount': amount,
                'amountNet': amount_net,
                'currency': 'USD',
                'valueAddedTaxIncluded': True})

        try:
            validate_update_contract_value_amount(request)
        except HTTPError:
            self.fail("validate_update_contract_value_amount() raised HTTPError unexpectedly")

    def test_round_up_from_float(self):
        amount = 120.14
        amount_net = 100.11
        coef = 1.2

        request = generate_contract_value_patch_request_mock(
            contract_value={
                'amount': amount,
                'amountNet': amount_net,
                'currency': 'USD',
                'valueAddedTaxIncluded': True})

        try:
            validate_update_contract_value_amount(request)
        except HTTPError:
            self.fail("validate_update_contract_value_amount() raised HTTPError unexpectedly")


    def test_round_up_from_decimal(self):
        amount = Decimal('120.14')
        amount_net = Decimal('100.11')
        coef = Decimal('1.2')

        request = generate_contract_value_patch_request_mock(
            contract_value={
                'amount': amount,
                'amountNet': amount_net,
                'currency': 'USD',
                'valueAddedTaxIncluded': True})

        try:
            validate_update_contract_value_amount(request)
        except HTTPError:
            self.fail("validate_update_contract_value_amount() raised HTTPError unexpectedly")


class TestTenderAdditionalClassificationUAROAD(unittest.TestCase):

    valid_ua_road = {
        u"scheme": u"UA-ROAD",
        u"id": u"M-06",
        u"description": u"Київ - Чоп (на м. Будапешт через мм. Львів, Мукачево і Ужгород)",
    }

    def setUp(self):
        self.test_tender = copy.deepcopy(test_tender_data)

    def test_with_invalid_cpv(self):
        self.test_tender["items"][0]["additionalClassifications"].append(self.valid_ua_road)
        tender = Tender(self.test_tender)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        error_message = e.exception.message['items'][0]['additionalClassifications'][0]
        self.assertIn(
            u"Item shouldn't have additionalClassification with scheme UA-ROAD for cpv not starts with",
            error_message
        )

    def test_valid(self):
        self.test_tender["items"][0]["classification"]["id"] = "71322200-3"
        self.test_tender["items"][0]["additionalClassifications"].append(self.valid_ua_road)
        tender = Tender(self.test_tender)
        tender.validate()

    def test_invalid_id(self):
        self.test_tender["items"][0]["classification"]["id"] = "71322200-3"
        self.test_tender["items"][0]["additionalClassifications"].append({
            u"scheme": u"UA-ROAD",
            u"id": u"some invalid id",
            u"description": u"Київ - Чоп (на м. Будапешт через мм. Львів, Мукачево і Ужгород)",
        })
        tender = Tender(self.test_tender)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        error_message = e.exception.message['items'][0]['additionalClassifications'][0]['id'][0]
        self.assertEqual(error_message, 'UA-ROAD id not found in standards')

    def test_invalid_description(self):
        self.test_tender["items"][0]["classification"]["id"] = "71322200-3"
        self.test_tender["items"][0]["additionalClassifications"].append({
            u"scheme": u"UA-ROAD",
            u"id": u"М-06",
            u"description": u"Some invalid description",
        })
        tender = Tender(self.test_tender)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        error_message = e.exception.message['items'][0]['additionalClassifications'][0]['description'][0]
        self.assertEqual(u"UA-ROAD description invalid", error_message)

    def test_more_than_one_ua_road(self):
        self.test_tender["items"][0]["classification"]["id"] = "71322200-3"
        self.test_tender["items"][0]["additionalClassifications"] = [self.valid_ua_road, self.valid_ua_road]
        tender = Tender(self.test_tender)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        error_message = e.exception.message['items'][0]['additionalClassifications'][0]
        self.assertIn("Item shouldn't have more than 1 additionalClassification", error_message)

    def test_required_id_description(self):
        self.test_tender["items"][0]["classification"]["id"] = "71322200-3"
        self.test_tender["items"][0]["additionalClassifications"] = [{'scheme': 'UA-ROAD'}]
        tender = Tender(self.test_tender)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        error_messages = e.exception.message['items'][0]['additionalClassifications'][0]
        self.assertEqual(error_messages, {'id': [u'This field is required.'], 'description': [u'This field is required.']})


class TestTenderAdditionalClassificationGMDN(unittest.TestCase):

    valid_gmdn = {
        u"scheme": u"GMDN",
        u"id": u"10024",
        u"description": u"Адаптометр",
    }

    def setUp(self):
        self.test_tender = copy.deepcopy(test_tender_data)

    def test_with_invalid_cpv(self):
        self.test_tender["items"][0]["additionalClassifications"] = [self.valid_gmdn]
        tender = Tender(self.test_tender)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        error_message = e.exception.message['items'][0]['additionalClassifications'][0]
        self.assertIn(
            u"Item shouldn't have additionalClassification with scheme GMDN for cpv not starts with",
            error_message
        )

    def test_valid(self):
        self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
        self.test_tender["items"][0]["additionalClassifications"] = [self.valid_gmdn]
        tender = Tender(self.test_tender)
        tender.validate()

    def test_invalid_id(self):
        self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
        self.test_tender["items"][0]["additionalClassifications"] = [{
            u"scheme": u"GMDN",
            u"id": u"some invalid id",
            u"description": u"Адаптометр",
        }]
        tender = Tender(self.test_tender)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        error_message = e.exception.message['items'][0]['additionalClassifications'][0]['id'][0]
        self.assertEqual(error_message, 'GMDN id not found in standards')

    def test_invalid_description(self):
        self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
        self.test_tender["items"][0]["additionalClassifications"] = [{
            u"scheme": u"GMDN",
            u"id": u"10024",
            u"description": u"Адаптометр invalid",
        }]
        tender = Tender(self.test_tender)
        tender.validate()   # description isn't validated

    def test_more_than_one_gmdn(self):
        self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
        self.test_tender["items"][0]["additionalClassifications"] = [self.valid_gmdn, self.valid_gmdn]
        tender = Tender(self.test_tender)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        error_message = e.exception.message['items'][0]['additionalClassifications'][0]
        self.assertIn("Item shouldn't have more than 1 additionalClassification", error_message)

    def test_gmdn_with_inn_atc(self):
        self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
        for scheme in ['INN', 'ATC']:
            self.test_tender["items"][0]["additionalClassifications"] = [self.valid_gmdn, {
                u"scheme": scheme,
                u"id": u"id",
                u"description": u"description",
            }]
            tender = Tender(self.test_tender)
            with self.assertRaises(ModelValidationError) as e:
                tender.validate()
            error_message = e.exception.message['items'][0]['additionalClassifications'][0]
            self.assertIn(u"Item shouldn't have additionalClassifications with both schemes INN/ATC and GMDN", error_message)

    def test_required_id_description(self):
        self.test_tender["items"][0]["classification"]["id"] = "33928000-1"
        self.test_tender["items"][0]["additionalClassifications"] = [{'scheme': 'GMDN'}]
        tender = Tender(self.test_tender)
        with self.assertRaises(ModelValidationError) as e:
            tender.validate()
        error_messages = e.exception.message['items'][0]['additionalClassifications'][0]
        self.assertEqual(error_messages, {'id': [u'This field is required.'], 'description': [u'This field is required.']})
