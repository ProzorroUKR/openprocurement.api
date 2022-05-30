# -*- coding: utf-8 -*-
from pytz import utc, timezone

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_currency_rates, get_uah_amount_from_value, parse_date
from pyramid.testing import DummyRequest, testConfig
from requests.exceptions import ConnectionError
from datetime import datetime
from mock import Mock, patch
import unittest


class GetCurrencyRatesTestCase(unittest.TestCase):

    @patch("openprocurement.api.utils.get_now")
    @patch("openprocurement.api.utils.requests")
    def test_get_success(self, requests_mock, get_now_mock):
        get_now_mock.return_value = datetime(2007, 1, 2)

        request_obj = Mock()
        request_obj.registry.settings = {}
        result = get_currency_rates(request_obj)

        requests_mock.get.assert_called_once_with(
            'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date=20070102&json'
        )
        result_mock = requests_mock.get.return_value
        result_mock.json.assert_called_once_with()
        assert result is result_mock.json.return_value

    @patch("openprocurement.api.utils.get_now")
    @patch("openprocurement.api.utils.requests")
    def test_get_success_with_proxy(self, requests_mock, get_now_mock):
        get_now_mock.return_value = datetime(2021, 12, 31)

        request_obj = Mock()
        request_obj.registry.settings = {"proxy_address": "http://hide-my-ip.com"}
        get_currency_rates(request_obj)

        requests_mock.get.assert_called_once_with(
            'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date=20211231&json',
            proxies={
                'http': 'http://hide-my-ip.com',
                'https': 'http://hide-my-ip.com'
            }
        )


    @patch("openprocurement.api.utils.raise_operation_error")
    @patch("openprocurement.api.utils.get_now")
    @patch("openprocurement.api.utils.requests.get")
    def test_fail_connection(self, requests_get_mock, get_now_mock, raise_operation_error_mock):
        class MyExc(Exception):
            pass
        raise_operation_error_mock.return_value = MyExc()
        get_now_mock.return_value = datetime(2021, 12, 31)
        request_obj = Mock()
        request_obj.registry.settings = {}

        requests_get_mock.side_effect = ConnectionError("Windows update")

        with self.assertRaises(MyExc):
            get_currency_rates(request_obj)

        requests_get_mock.assert_called_once_with(
            "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date=20211231&json"
        )
        raise_operation_error_mock.assert_called_once_with(
            request_obj,
            "Error while getting data from bank.gov.ua: Windows update",
            status=409
        )

    @patch("openprocurement.api.utils.raise_operation_error")
    @patch("openprocurement.api.utils.get_now")
    @patch("openprocurement.api.utils.requests.get")
    def test_fail_connection(self, requests_get_mock, get_now_mock, raise_operation_error_mock):
        class MyExc(Exception):
            pass

        raise_operation_error_mock.return_value = MyExc()
        get_now_mock.return_value = datetime(2021, 12, 31)
        request_obj = Mock()
        request_obj.registry.settings = {}
        requests_get_mock.return_value.json.side_effect = ValueError("Invalid json")

        with self.assertRaises(MyExc):
            get_currency_rates(request_obj)

        requests_get_mock.assert_called_once_with(
            "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date=20211231&json"
        )
        raise_operation_error_mock.assert_called_once_with(
            request_obj,
            "Failure of decoding data from bank.gov.ua",
            status=409
        )


class GetUAHAmountFromValueTestCase(unittest.TestCase):

    def test_uah_amount(self):
        request = Mock()
        value = {"amount": 12.3, "currency": "UAH"}
        result = get_uah_amount_from_value(request, value, {})

        self.assertEqual(result, value["amount"])

    def test_usd_amount(self):
        usd_rate = 8.2
        request = Mock(
            currency_rates=[
                {
                    "cc": "USD",
                    "rate": usd_rate
                }
            ],
            logging_context={}
        )
        value = {"amount": 12.3, "currency": "USD"}
        result = get_uah_amount_from_value(request, value, {})

        self.assertEqual(result, value["amount"] * usd_rate)

    @patch("openprocurement.api.utils.raise_operation_error")
    def test_not_found_amount(self, raise_operation_error_mock):
        class MyExc(Exception):
            pass

        raise_operation_error_mock.return_value = MyExc()

        request = Mock(
            currency_rates=[
                {
                    "cc": "USD",
                    "rate": 8.2
                }
            ],
            logging_context={}
        )
        value = {"amount": 300, "currency": "рупии"}

        with self.assertRaises(MyExc):
            get_uah_amount_from_value(request, value, {})

        raise_operation_error_mock.assert_called_once_with(
            request,
            "Couldn't find currency {} on bank.gov.ua".format(value["currency"]),
            status=422
        )


class ParseDateTestCase(unittest.TestCase):
    def test_parse_date(self):
        dt_str = "2020-01-01T12:00:00+02:00"
        dt_result = parse_date(dt_str)
        dt_expected = timezone("Europe/Kiev").localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_parse_date_with_no_tz(self):
        dt_str = "2020-01-01T12:00:00"
        dt_result = parse_date(dt_str)
        dt_expected = utc.localize(datetime(2020, 1, 1, 12, 0, 0))
        self.assertEqual(dt_result, dt_expected)

    def test_parse_date_with_no_time_and_tz(self):
        dt_str = "2020-01-01"
        dt_result = parse_date(dt_str)
        dt_expected = utc.localize(datetime(2020, 1, 1))
        self.assertEqual(dt_result, dt_expected)

    def test_parse_date_invalid_format(self):
        dt_str = "test"
        with self.assertRaises(ValueError) as e:
            parse_date(dt_str)
