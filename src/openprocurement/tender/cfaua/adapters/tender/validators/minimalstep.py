from schematics.exceptions import ValidationError


class MinimalStepValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, value):
        if value and value.amount and data.get('value'):
            if data.get('value').amount < value.amount:
                raise ValidationError(u"value should be less than value of tender")
            if data.get('value').currency != value.currency:
                raise ValidationError(u"currency should be identical to currency of value of tender")
            if data.get('value').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                raise ValidationError(
                    u"valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of tender")