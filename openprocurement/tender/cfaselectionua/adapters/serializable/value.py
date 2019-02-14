# src/openprocurement.tender.belowthreshold/openprocurement/tender/belowthreshold/models.py:246
from openprocurement.api.adapters import Serializable


class SerializableTenderMultilotValue(Serializable):
    serialized_name = "value"
    serialize_when_none = False

    def __call__(self, obj, *args, **kwargs):
        if all([i.value for i in obj.lots]):
            value_class = obj._fields['value']
            return value_class(dict(amount=sum([i.value.amount for i in obj.lots]),
                                    currency=obj.lots[0].value.currency,
                                    valueAddedTaxIncluded=obj.lots[0].value.valueAddedTaxIncluded)) if obj.lots else obj.value
