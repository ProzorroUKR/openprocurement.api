# src/openprocurement.tender.belowthreshold/openprocurement/tender/belowthreshold/models.py:246
from openprocurement.api.adapters import Serializable


class SerializableTenderMultilotValue(Serializable):
    serialized_name = "value"

    def __call__(self, obj, *args, **kwargs):
        if obj.value:
            value_class = obj._fields['value']
            return value_class(dict(amount=sum([i.value.amount for i in obj.lots]),
                                    currency=obj.value.currency,
                                    valueAddedTaxIncluded=obj.value.valueAddedTaxIncluded)) if obj.lots else obj.value
