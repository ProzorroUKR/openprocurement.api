"""
Client of ProZorro Dictionaries API: the dictionaries that change without a release of `standards`.

A dictionary is fetched as a whole and kept in the memory of the process for DICTIONARIES_CACHE_TTL seconds.
There is no stale copy: when a dictionary has to be fetched and the API fails, the request fails with 502
(a failure isn't cached, the next request tries again).
"""

from logging import getLogger
from threading import Condition
from typing import Any, NoReturn

import requests
from cachetools import TTLCache, cached

from openprocurement.api.constants import DICTIONARIES_API_TIMEOUT, DICTIONARIES_CACHE_TTL, KPK_SCHEME
from openprocurement.api.constants_utils import split_classifier_by_year
from openprocurement.api.context import get_request
from openprocurement.api.utils import raise_operation_error

LOGGER = getLogger(__name__)

KPK_PATH = "kpk/all.json"

_session = requests.Session()


def _raise_unavailable(details: Any) -> NoReturn:
    LOGGER.warning(f"Error while getting data from ProZorro Dictionaries. Details: {details}")
    raise_operation_error(
        get_request(),
        "Error while getting data from ProZorro Dictionaries. Try again later",
        status=502,
    )
    raise AssertionError("unreachable")  # raise_operation_error always raises


def fetch_dictionary(path: str) -> Any:
    """The `data` of a dictionary, e.g. of "kpk/all.json"."""
    url = f"{get_request().registry.dictionaries_api_host}/api/1.0/{path}"
    try:
        response = _session.get(url, timeout=DICTIONARIES_API_TIMEOUT)
    except requests.exceptions.RequestException as e:
        _raise_unavailable(e)
    if response.status_code != 200:
        _raise_unavailable(f"{url}: {response.status_code} {response.text[:200]}")
    try:
        return response.json()["data"]
    except (ValueError, LookupError, TypeError) as e:
        _raise_unavailable(f"{url}: unexpected response: {e!r}")


# the condition makes the concurrent requests wait for the one that fetches the dictionary
@cached(TTLCache(maxsize=1, ttl=DICTIONARIES_CACHE_TTL), condition=Condition())
def get_kpk() -> dict[str, frozenset[str]]:
    """
    The codes of KPK (the classifier of the state budget programmes) by the scheme of a year:
    {"КПК-2025": {"0110000", ...}, "КПК-2026": {...}}
    """
    data = fetch_dictionary(KPK_PATH)
    try:
        return {scheme: frozenset(items) for scheme, items in split_classifier_by_year(data, KPK_SCHEME).items()}
    except (AttributeError, LookupError, TypeError) as e:
        _raise_unavailable(f"{KPK_PATH}: unexpected data: {e!r}")
