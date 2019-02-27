# openprocurement.tender.belowthreshold/openprocurement/tender/belowthreshold/models.py:250
from openprocurement.api.adapters import Serializable

class SerializableTenderGuarantee(Serializable):
    serialized_name = "guarantee"
    serialize_when_none = False

    def __call__(self, obj, *args, **kwargs):
        if obj.lots:
            lots_amount = [i.guarantee.amount for i in obj.lots if i.guarantee]
            if not lots_amount:
                return obj.guarantee
            guarantee = {'amount': sum(lots_amount)}
            lots_currency = [i.guarantee.currency for i in obj.lots if i.guarantee]
            guarantee['currency'] = lots_currency[0] if lots_currency else None
            if obj.guarantee:
                guarantee['currency'] = obj.guarantee.currency
            guarantee_class = obj._fields['guarantee']
            return guarantee_class(guarantee)
        else:
            return obj.guarantee
