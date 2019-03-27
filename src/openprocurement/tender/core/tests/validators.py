# -*- coding: utf-8 -*-
import unittest
import mock

from openprocurement.tender.core.validation import (
    validate_update_contract_value_with_award,
    validate_update_contract_value, validate_update_contract_value_amount)
from pyramid.httpexceptions import HTTPError


class TestValidateUpdateContractValue(unittest.TestCase):

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_readonly_fields(self, error_handler_mock):
        request = mock.MagicMock()
        value = {'currency': 'test', 'valueAddedTaxIncluded': 'updated'}
        request.validated = {'data': {'value': value}}
        request.context.value.to_native.return_value.get.return_value = 'updated'
        error_handler_mock.return_value = HTTPError

        with self.assertRaises(HTTPError):
            validate_update_contract_value(request)

        request.errors.add.assert_called_once_with(
            'body', 'data', 'Can\'t update currency for contract value')


class TestValidateUpdateContractValueWithAward(unittest.TestCase):
    @mock.patch('openprocurement.api.utils.error_handler')
    def test_pass_tax_included_for_included_award(self, error_handler_mock):
        award = mock.MagicMock(id='test_id', value=mock.MagicMock(amount=100, valueAddedTaxIncluded=True))
        request = mock.MagicMock(validated={})
        request.validated['tender'] = mock.MagicMock(awards=[award])
        value = {'amount': 90, 'amountNet': 80, 'currency': 'USD', 'valueAddedTaxIncluded': True}
        request.validated['data'] = request.validated['json_data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        validate_update_contract_value_with_award(request)

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_fail_tax_included_for_included_award(self, error_handler_mock):
        award = mock.MagicMock(id='test_id', value=mock.MagicMock(amount=100, valueAddedTaxIncluded=True))
        request = mock.MagicMock(validated={})
        request.validated['tender'] = mock.MagicMock(awards=[award])
        value = {'amount': 105, 'amountNet': 95, 'currency': 'USD', 'valueAddedTaxIncluded': True}
        request.validated['data'] = request.validated['json_data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        with self.assertRaises(HTTPError):
            validate_update_contract_value_with_award(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Amount should be less or equal to awarded amount')

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_pass_tax_not_included_for_included_award(self, error_handler_mock):
        award = mock.MagicMock(id='test_id', value=mock.MagicMock(amount=100, valueAddedTaxIncluded=False))
        request = mock.MagicMock(validated={})
        request.validated['tender'] = mock.MagicMock(awards=[award])
        value = {'amount': 90, 'amountNet': 80, 'currency': 'USD', 'valueAddedTaxIncluded': True}
        request.validated['data'] = request.validated['json_data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        validate_update_contract_value_with_award(request)

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_fail_tax_not_included_for_included_award(self, error_handler_mock):
        award = mock.MagicMock(id='test_id', value=mock.MagicMock(amount=100, valueAddedTaxIncluded=True))
        request = mock.MagicMock(validated={})
        request.validated['tender'] = mock.MagicMock(awards=[award])
        value = {'amount': 105, 'amountNet': 95, 'currency': 'USD', 'valueAddedTaxIncluded': False}
        request.validated['data'] = request.validated['json_data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        with self.assertRaises(HTTPError):
            validate_update_contract_value_with_award(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Amount should be less or equal to awarded amount')

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_pass_tax_included_for_not_included_award(self, error_handler_mock):
        award = mock.MagicMock(id='test_id', value=mock.MagicMock(amount=100, valueAddedTaxIncluded=False))
        request = mock.MagicMock(validated={})
        request.validated['tender'] = mock.MagicMock(awards=[award])
        value = {'amount': 105, 'amountNet': 95, 'currency': 'USD', 'valueAddedTaxIncluded': True}
        request.validated['data'] = request.validated['json_data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        validate_update_contract_value_with_award(request)

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_fail_tax_included_for_not_included_award(self, error_handler_mock):
        award = mock.MagicMock(id='test_id', value=mock.MagicMock(amount=100, valueAddedTaxIncluded=False))
        request = mock.MagicMock(validated={})
        request.validated['tender'] = mock.MagicMock(awards=[award])
        value = {'amount': 110, 'amountNet': 105, 'currency': 'USD', 'valueAddedTaxIncluded': True}
        request.validated['data'] = request.validated['json_data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        with self.assertRaises(HTTPError):
            validate_update_contract_value_with_award(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'AmountNet should be less or equal to awarded amount')


class TestValidateUpdateContractValueAmount(unittest.TestCase):
    @mock.patch('openprocurement.api.utils.error_handler')
    def test_amount_net_greater_than_amount_error(self, error_handler_mock):
        request = mock.MagicMock(validated={})
        value = {'amount': 100, 'amountNet': 200, 'currency': 'USD', 'valueAddedTaxIncluded': True}
        request.validated['data'] = request.validated['json_data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        with self.assertRaises(HTTPError):
            validate_update_contract_value_amount(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Amount should be greater than amountNet and differ by no more than 20.0%')

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_amount_net_too_match_less_than_amount_error(self, error_handler_mock):
        request = mock.MagicMock(validated={})
        value = {'amount': 100, 'amountNet': 50, 'currency': 'USD', 'valueAddedTaxIncluded': True}
        request.validated['data'] = request.validated['json_data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        with self.assertRaises(HTTPError):
            validate_update_contract_value_amount(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Amount should be greater than amountNet and differ by no more than 20.0%')

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_amount_net_not_equal_to_amount_error(self, error_handler_mock):
        request = mock.MagicMock(validated={})
        value = {'amount': 100, 'amountNet': 50, 'currency': 'USD', 'valueAddedTaxIncluded': False}
        request.validated['data'] = request.validated['json_data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        with self.assertRaises(HTTPError):
            validate_update_contract_value_amount(request)

        request.errors.add.assert_called_once_with(
            'body', 'value', 'Amount and amountNet should be equal')
