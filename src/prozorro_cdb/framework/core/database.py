from pymongo import IndexModel

from prozorro_cdb.api.database.store import BaseCollection


class AgreementCollection(BaseCollection):
    object_name = "agreement"

    def get_indexes(self) -> list[IndexModel]:
        return []  # indices already specified in sync collection
