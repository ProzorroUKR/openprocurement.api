# src/openprocurement.tender.belowthreshold/openprocurement/tender/belowthreshold/models.py:267
from openprocurement.api.adapters import Serializable

class SerializableTenderMinimalStep(Serializable):
    serialized_name = "minimalStep"

    def __call__(self, obj, *args, **kwargs):
        if obj.lots:
            minimalStep = obj._fields['minimalStep']
            return minimalStep(
                dict(amount=min([i.minimalStep.amount for i in obj.lots]),
                     currency=obj.minimalStep.currency,
                     valueAddedTaxIncluded=obj.minimalStep.valueAddedTaxIncluded
                )
            )
        else:
            return obj.minimalStep