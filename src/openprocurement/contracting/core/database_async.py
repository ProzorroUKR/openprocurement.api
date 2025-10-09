from typing import List

from pymongo import IndexModel

from openprocurement.api.database_async import BaseCollection


class ContractCollection(BaseCollection):
    object_name = "contract"

    def get_indexes(self) -> List[IndexModel]:
        return []  # indices already specified in sync collection
