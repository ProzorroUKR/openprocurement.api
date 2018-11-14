# src/openprocurement.tender.belowthreshold/openprocurement/tender/belowthreshold/models.py:267
from openprocurement.api.adapters import Serializable


class SerializableTenderMinimalStep(Serializable):
    serialized_name = "minimalStep"
    serialize_when_none = False

    def __call__(self, obj, *args, **kwargs):
        if all([i.minimalStep for i in obj.lots]):
            value_class = obj._fields['minimalStep']
            return value_class(
                dict(amount=min([i.minimalStep.amount for i in obj.lots]),
                     currency=obj.lots[0].minimalStep.currency,
                     valueAddedTaxIncluded=obj.lots[0].minimalStep.valueAddedTaxIncluded)) if obj.lots else obj.minimalStep
