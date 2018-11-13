# src/openprocurement.tender.belowthreshold/openprocurement/tender/belowthreshold/models.py:267
from openprocurement.api.adapters import Serializable


class SerializableTenderMinimalStep(Serializable):
    serialized_name = "minimalStep"

    def __call__(self, obj, *args, **kwargs):
        if obj.minimalStep and all([i.minimalStep for i in obj.lots]):
            value_class = obj._fields['value']
            return value_class(
                dict(amount=min([i.minimalStep.amount for i in obj.lots]),
                     currency=obj.minimalStep.currency,
                     valueAddedTaxIncluded=obj.minimalStep.valueAddedTaxIncluded)) if obj.lots else obj.minimalStep
