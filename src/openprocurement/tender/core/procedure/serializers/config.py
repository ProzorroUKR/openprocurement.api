from openprocurement.api.context import get_request
from openprocurement.tender.core.migrations.add_config_has_auction_field import has_auction_populator
from openprocurement.tender.core.procedure.serializers.base import BaseSerializer


def has_auction_serializer(obj, value):
    # TODO: remove serializer after migration
    if value is None:
        tender = get_request().validated.get("tender")
        data = get_request().validated.get("data")
        return has_auction_populator(tender or data)
    return value


class TenderConfigSerializer(BaseSerializer):
    def __init__(self, data: dict):
        super().__init__(data)
        for field_name in self.serializers.keys():
            if field_name not in self._data:
                self._data[field_name] = None

    serializers = {
        "hasAuction": has_auction_serializer,
    }
