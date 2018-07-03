# src/openprocurement.tender.belowthreshold/openprocurement/tender/belowthreshold/models.py:267
class SerializableTenderMinimalStep(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, *args, **kwargs):
        if self.context.lots:
            minimalStep = self.context._fields['minimalStep']
            # minimalStep = type(self.context.minimalStep)
            return minimalStep(
                dict(amount=min([i.minimalStep.amount for i in self.context.lots]),
                     currency=self.context.minimalStep.currency,
                     valueAddedTaxIncluded=self.context.minimalStep.valueAddedTaxIncluded
                )
            )
        else:
            return self.context.minimalStep