# -*- coding: utf-8 -*-
import unittest
import mock

from openprocurement.tender.core.validation import validate_update_contract_value
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

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_old_amount_validation(self, error_handler_mock):
        award = mock.MagicMock(id='test_id', value=mock.MagicMock(amount=100))
        request = mock.MagicMock(validated={})
        request.validated['tender'] = mock.MagicMock(awards=[award])
        value = {'amount': 200, 'currency': 'USD', 'valueAddedTaxIncluded': True}
        request.validated['data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        with self.assertRaises(HTTPError):
            validate_update_contract_value(request)

        request.errors.add.assert_called_once_with(
            'body', 'data', 'Value amount should be less or equal to awarded amount (100)')

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_amount_net_greater_than_amount(self, error_handler_mock):
        award = mock.MagicMock(id='test_id', value=mock.MagicMock(amount=100))
        request = mock.MagicMock(validated={})
        request.validated['tender'] = mock.MagicMock(awards=[award])
        value = {'amount': 100, 'amountNet': 200, 'currency': 'USD', 'valueAddedTaxIncluded': True}
        request.validated['data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        with self.assertRaises(HTTPError):
            validate_update_contract_value(request)

        request.errors.add.assert_called_once_with(
            'body', 'data', 'Value amountNet should be less or equal to amount (100)')

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_pass_tax_included(self, error_handler_mock):
        award = mock.MagicMock(id='test_id', value=mock.MagicMock(amount=100))
        request = mock.MagicMock(validated={})
        request.validated['tender'] = mock.MagicMock(awards=[award])
        value = {'amount': 90, 'amountNet': 80, 'currency': 'USD', 'valueAddedTaxIncluded': True}
        request.validated['data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        validate_update_contract_value(request)

    @mock.patch('openprocurement.api.utils.error_handler')
    def test_pass_tax_notincluded(self, error_handler_mock):
        award = mock.MagicMock(id='test_id', value=mock.MagicMock(amount=100))
        request = mock.MagicMock(validated={})
        request.validated['tender'] = mock.MagicMock(awards=[award])
        value = { 'amount': 105, 'amountNet': 95, 'currency': 'USD', 'valueAddedTaxIncluded': False}
        request.validated['data'] = {'value': value}
        request.context.value.to_native.return_value.get = lambda x: value[x]
        request.context.awardID = 'test_id'
        error_handler_mock.return_value = HTTPError

        validate_update_contract_value(request)
