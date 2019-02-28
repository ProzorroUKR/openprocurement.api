# /src/openprocurement.tender.openua/openprocurement/tender/openua/models.py:382
from openprocurement.api.adapters import Serializable


class SerializableTenderNumberOfBids(Serializable):
    serialized_name = "numberOfBids"

    def __call__(self, obj, *args, **kwargs):
        return len(obj.bids)
