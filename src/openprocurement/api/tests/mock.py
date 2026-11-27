from copy import deepcopy
from functools import wraps
from unittest.mock import Mock, patch

# ProZorro Dictionaries API: `data` of the dictionaries by their paths (a few items of the real ones)
MOCK_DICTIONARIES = {
    "kpk/all.json": [
        {
            "code": "0110000",
            "name": "Управління справами Апарату Верховної Ради України",
            "level": 1,
            "parentCode": None,
            "isactive": 1,
            "datefrom": "2023-01-01",
            "dateto": None,
            "id": 1708,
            "years": [2023, 2024, 2025, 2026, 2027],
        },
        {
            "code": "3500000",
            "name": "Міністерство фінансів України",
            "level": 1,
            "parentCode": None,
            "isactive": 1,
            "datefrom": "2019-01-01",
            "dateto": None,
            "id": 1171,
            "years": [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027],
        },
        {
            "code": "3505000",
            "name": "Державна аудиторська служба України",
            "level": 2,
            "parentCode": "3500000",
            "isactive": 1,
            "datefrom": "2021-01-01",
            "dateto": None,
            "id": 1487,
            "years": [2021, 2022, 2023, 2024, 2025, 2026, 2027],
        },
        {
            "code": "3505000",
            "name": "Офіс фінансового контролю",
            "level": 2,
            "parentCode": "3500000",
            "isactive": 0,
            "datefrom": "2020-01-01",
            "dateto": "2020-12-31",
            "id": 1204,
            "years": [2020],
        },
    ],
}


def mock_dictionaries_api_get(url, **kwargs):
    """
    Replaces `get` of the session of `openprocurement.api.dictionaries`, so the tests don't request the API
    (the host isn't looked at: the ini files of the tests don't set it).
    """
    path = url.partition("/api/1.0/")[2]
    if path not in MOCK_DICTIONARIES:
        return Mock(status_code=404, text=f"{path} not found")
    data = {"data": deepcopy(MOCK_DICTIONARIES[path]), "dateModified": "2026-11-26T07:00:27.423"}
    return Mock(status_code=200, json=Mock(return_value=data))


class ContextDecorator:
    """A base class that can be used as both a context manager and a decorator."""

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        """Enter the context. Subclasses must override this method."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context. Subclasses must override this method."""

    def start(self):
        """Start the context."""
        self.__enter__()
        return self

    def stop(self):
        """Exit the context."""
        self.__exit__(None, None, None)


class patch_multiple(ContextDecorator):
    """Patch multiple targets with the same mock object."""

    def __init__(self, targets, value):
        self.targets = targets
        self.value = value
        self.patchers = None

    def __enter__(self):
        self.patchers = [patch(target, self.value) for target in self.targets]
        for patcher in self.patchers:
            patcher.start()
        return self

    def __exit__(self, *exc_info):
        if self.patchers:
            for patcher in self.patchers:
                patcher.stop()
            self.patchers = None
