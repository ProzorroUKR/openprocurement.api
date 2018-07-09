# /src/openprocurement.tender.openua/openprocurement/tender/openua/models.py:382
from openprocurement.api.adapters import Serializable


class SerializableTenderNumberOfAwards(Serializable):
    serialized_name = "numberOfAwards"

    def __call__(self, obj, *args, **kwargs):
        return len([award for award in obj.awards if award.status in ("active", "pending",)])