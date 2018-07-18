from schematics.exceptions import ValidationError


class LotsValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, lots):
        if len(lots) > 1:
            ValidationError(u"Can't add to tender more than one lot.")
        if len(set([lot.guarantee.currency for lot in lots if lot.guarantee])) > 1:
            raise ValidationError(u"lot guarantee currency should be identical to tender guarantee currency")
