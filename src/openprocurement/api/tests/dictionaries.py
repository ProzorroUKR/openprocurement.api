from time import monotonic
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError

from openprocurement.api import dictionaries
from openprocurement.api.constants import DICTIONARIES_API_TIMEOUT, DICTIONARIES_CACHE_TTL
from openprocurement.api.dictionaries import fetch_dictionary, get_kpk
from openprocurement.api.tests.mock import MOCK_DICTIONARIES

KPK_URL = "http://dictionaries.test/api/1.0/kpk/all.json"


class OperationError(Exception):
    pass


@pytest.fixture(autouse=True)
def request_mock():
    request = Mock()
    request.registry.dictionaries_api_host = "http://dictionaries.test"
    with patch("openprocurement.api.dictionaries.get_request", return_value=request):
        yield request


@pytest.fixture(autouse=True)
def raise_operation_error_mock():
    with patch("openprocurement.api.dictionaries.raise_operation_error", side_effect=OperationError) as mock:
        yield mock


@pytest.fixture
def session_get():
    with patch.object(dictionaries._session, "get") as mock:
        mock.return_value = response_mock({"data": MOCK_DICTIONARIES["kpk/all.json"], "dateModified": "2026-11-26"})
        yield mock


def response_mock(json=None, status_code=200, text=""):
    response = Mock(status_code=status_code, text=text)
    if isinstance(json, Exception):
        response.json.side_effect = json
    else:
        response.json.return_value = json
    return response


def assert_unavailable(raise_operation_error_mock, request):
    raise_operation_error_mock.assert_called_once_with(
        request,
        "Error while getting data from ProZorro Dictionaries. Try again later",
        status=502,
    )


def test_fetch_dictionary(session_get):
    assert fetch_dictionary("kpk/all.json") == MOCK_DICTIONARIES["kpk/all.json"]
    session_get.assert_called_once_with(KPK_URL, timeout=DICTIONARIES_API_TIMEOUT)


def test_get_kpk_splits_codes_by_year(session_get):
    kpk = get_kpk()

    assert sorted(kpk) == [f"КПК-{year}" for year in range(2019, 2028)]
    assert kpk["КПК-2019"] == {"3500000"}
    assert kpk["КПК-2020"] == {"3500000", "3505000"}
    assert kpk["КПК-2023"] == {"0110000", "3500000", "3505000"}


def test_get_kpk_is_cached(session_get):
    assert get_kpk() is get_kpk()
    session_get.assert_called_once_with(KPK_URL, timeout=DICTIONARIES_API_TIMEOUT)


def test_get_kpk_is_fetched_again_after_ttl(session_get):
    get_kpk()
    get_kpk.cache.expire(monotonic() + DICTIONARIES_CACHE_TTL - 1)
    get_kpk()
    assert session_get.call_count == 1

    get_kpk.cache.expire(monotonic() + DICTIONARIES_CACHE_TTL + 1)
    get_kpk()
    assert session_get.call_count == 2


def test_connection_error(session_get, raise_operation_error_mock, request_mock):
    session_get.side_effect = ConnectionError("Connection refused")

    with pytest.raises(OperationError):
        get_kpk()
    assert_unavailable(raise_operation_error_mock, request_mock)


@pytest.mark.parametrize("status_code", [404, 500, 502])
def test_error_status(session_get, raise_operation_error_mock, request_mock, status_code):
    session_get.return_value = response_mock({"error": "KPK dictionary latest not found"}, status_code=status_code)

    with pytest.raises(OperationError):
        get_kpk()
    assert_unavailable(raise_operation_error_mock, request_mock)


@pytest.mark.parametrize(
    "json",
    [
        ValueError("Expecting value"),  # not a json
        {"errors": ["oops"]},  # no data
        ["0110000"],  # not an object
        {"data": {"0110000": "name"}},  # not a list of items
        {"data": [{"name": "an item without a code", "years": [2025]}]},
        {"data": [{"code": "0110000", "years": 2025}]},
    ],
)
def test_unexpected_response(session_get, raise_operation_error_mock, request_mock, json):
    session_get.return_value = response_mock(json)

    with pytest.raises(OperationError):
        get_kpk()
    assert_unavailable(raise_operation_error_mock, request_mock)


def test_failure_is_not_cached(session_get):
    response = session_get.return_value
    session_get.side_effect = ConnectionError("Connection refused")
    with pytest.raises(OperationError):
        get_kpk()

    session_get.side_effect = None
    session_get.return_value = response
    assert "КПК-2023" in get_kpk()
    assert session_get.call_count == 2
