from openprocurement.tender.core.validation import validate_minimalstep


class TenderMinimalStepValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, value):
        validate_minimalstep(data, value)
