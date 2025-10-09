from typing import List

from pymongo import IndexModel

from openprocurement.api.database_async import BaseCollection


class AgreementCollection(BaseCollection):
    object_name = "agreement"

    def get_indexes(self) -> List[IndexModel]:
        return []  # indices already specified in sync collection
