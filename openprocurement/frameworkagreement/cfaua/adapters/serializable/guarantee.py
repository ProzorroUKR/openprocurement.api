
# openprocurement.tender.belowthreshold/openprocurement/tender/belowthreshold/models.py:250
class SerializableTenderGuarantee(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, *args, **kwargs):
        if self.context.lots:
            lots_amount = [i.guarantee.amount for i in self.context.lots if i.guarantee]
            if not lots_amount:
                return self.context.guarantee
            guarantee = {'amount': sum(lots_amount)}
            lots_currency = [i.guarantee.currency for i in self.context.lots if i.guarantee]
            guarantee['currency'] = lots_currency[0] if lots_currency else None
            if self.context.guarantee:
                guarantee['currency'] = self.context.guarantee.currency
            guarantee_class = self.context._fields['guarantee']
            return guarantee_class(guarantee)
        else:
            return self.context.guarantee
