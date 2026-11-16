from pymongo import IndexModel

from prozorro_cdb.api.database.store import BaseCollection


class ContractCollection(BaseCollection):
    object_name = "contract"

    def get_indexes(self) -> list[IndexModel]:
        return []  # indices already specified in sync collection
