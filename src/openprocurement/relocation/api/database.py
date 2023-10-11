from openprocurement.api.database import BaseCollection


class TransferCollection(BaseCollection):
    object_name = "transfer"

    def create_indexes(self):
        pass

    def save(self, data, insert=False):
        self.store.save_data_simple(self.collection, data, insert=insert)

    def save_deprecated(self, o, insert=False):
        data = o.to_primitive()
        updated = self.store.save_data_simple(self.collection, data, insert=insert)
        o.import_data(updated)
