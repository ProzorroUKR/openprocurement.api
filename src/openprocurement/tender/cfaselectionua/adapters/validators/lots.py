from schematics.exceptions import ValidationError


class TenderLotsValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, lots):
        if len(set([lot.guarantee.currency for lot in lots if lot.guarantee])) > 1:
            raise ValidationError(u"lot guarantee currency should be identical to tender guarantee currency")
