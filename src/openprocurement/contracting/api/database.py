from openprocurement.api.database import BaseCollection


class ContractCollection(BaseCollection):
    object_name = "contract"

    def save(self, data, insert=False, modified=True):
        self.store.save_data(self.collection, data, insert=insert, modified=modified)
