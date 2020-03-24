# -*- coding: utf-8 -*-
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import APIResourceListing, get_currency_rates, get_uah_amount_from_value
from pyramid.testing import DummyRequest, testConfig
from requests.exceptions import ConnectionError
from datetime import datetime
from mock import Mock, patch
import unittest


class ItemsListing(APIResourceListing):
    def __init__(self, request, context):
        super(ItemsListing, self).__init__(request, context)

        results = (
            Mock(
                key=k,
                value={
                    "status": "active",
                    "title": "title#%d" % k,
                    "description": "description#%d" % k,
                    "bids": [1, k],
                },
            )
            for k in range(5)
        )

        self.view_mock = Mock(return_value=results)
        self.test_view_mock = Mock(return_value=results)
        self.changes_view_mock = Mock(return_value=results)
        self.test_changes_view_mock = Mock(return_value=results)
        self.VIEW_MAP = {u"": self.view_mock, u"test": self.test_view_mock}
        self.CHANGES_VIEW_MAP = {u"": self.changes_view_mock, u"test": self.test_changes_view_mock}
        self.FEED = {u"dateModified": self.VIEW_MAP, u"changes": self.CHANGES_VIEW_MAP}
        self.FIELDS = ("id", "status", "title", "description")

        def item_serialize(_, data, fields):
            return {i: j for i, j in data.items() if i in fields}

        self.serialize_func = item_serialize
        self.object_name_for_listing = "health"
        self.log_message_id = "items_list_custom"


class ResourceListingTestCase(BaseWebTest):
    def setUp(self):
        self.request = DummyRequest()
        self.request.logging_context = {}
        self.request._registry = self.app.app.registry
        self.listing = ItemsListing(self.request, {})

    def get_listing(self):
        return self.listing.get()

    def test_get_listing(self):
        self.get_listing()
        self.listing.view_mock.assert_called_once_with(
            self.db, startkey="", stale="update_after", descending=False, limit=100
        )

    def test_get_test_listing(self):
        self.request.params = {"opt_fields": "id,status", "mode": "test"}
        self.get_listing()
        self.listing.test_view_mock.assert_called_once_with(
            self.db, startkey="", stale="update_after", descending=False, limit=100
        )

    def test_get_changes_listing(self):
        self.request.params = {"opt_fields": "id,status", "feed": "changes"}
        self.get_listing()
        self.listing.changes_view_mock.assert_called_once_with(
            self.db, startkey=0, stale="update_after", descending=False, limit=100
        )

    def test_get_test_changes_listing(self):
        self.request.params = {"opt_fields": "id,status", "feed": "changes", "mode": "test"}
        self.get_listing()
        self.listing.test_changes_view_mock.assert_called_once_with(
            self.db, startkey=0, stale="update_after", descending=False, limit=100
        )

    def test_get_listing_opt_fields_subset(self):
        self.request.params = {"opt_fields": "id,status"}
        self.get_listing()
        self.listing.view_mock.assert_called_once_with(
            self.db, startkey="", stale="update_after", descending=False, limit=100
        )

    def test_get_listing_opt_fields_not_subset(self):
        self.request.params = {"opt_fields": "id,status,title,description,bids"}
        data = self.get_listing()
        self.listing.view_mock.assert_called_once_with(
            self.db, startkey="", stale="update_after", descending=False, limit=100
        )
        self.assertEqual(len(data["data"]), 5)
        self.assertEqual(set(data["data"][0].keys()), {"id", "status", "title", "description", "dateModified"})


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
    def test_get_success_with_http_proxy(self, requests_mock, get_now_mock):
        get_now_mock.return_value = datetime(2021, 12, 31)

        request_obj = Mock()
        request_obj.registry.settings = {"proxy_address": "http://hide-my-ip.com"}
        get_currency_rates(request_obj)

        requests_mock.get.assert_called_once_with(
            'http://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date=20211231&json',
            proxies={'http': 'http://hide-my-ip.com'}
        )

    @patch("openprocurement.api.utils.get_now")
    @patch("openprocurement.api.utils.requests")
    def test_get_success_with_https_proxy(self, requests_mock, get_now_mock):
        get_now_mock.return_value = datetime(2021, 12, 31)

        request_obj = Mock()
        request_obj.registry.settings = {"proxy_address": "https://hide-my-ip.com"}
        get_currency_rates(request_obj)

        requests_mock.get.assert_called_once_with(
            'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date=20211231&json',
            proxies={'https': 'https://hide-my-ip.com'}
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
        value = {"amount": 300, "currency": u"рупии"}

        with self.assertRaises(MyExc):
            get_uah_amount_from_value(request, value, {})

        raise_operation_error_mock.assert_called_once_with(
            request,
            u"Couldn't find currency {} on bank.gov.ua".format(value["currency"]),
            status=422
        )
