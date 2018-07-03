# src/openprocurement.tender.belowthreshold/openprocurement/tender/belowthreshold/models.py:246
class TenderMultilotValue(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, *args, **kwargs):
        # Value = self.context.value.__class__
        value_class = self.context._fields['value']
        return value_class(dict(amount=sum([i.value.amount for i in self.context.lots]),
                                currency=self.context.value.currency,
                                valueAddedTaxIncluded=self.context.value.valueAddedTaxIncluded)) if self.context.lots else self.context.value