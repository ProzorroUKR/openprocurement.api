from openprocurement.api.procedure.context import get_object
from openprocurement.api.procedure.models.item import (
    CPVClassification as BaseCPVClassification,
)
from openprocurement.api.procedure.models.item import validate_scheme


class CPVClassification(BaseCPVClassification):
    def validate_scheme(self, data, scheme):
        validate_scheme(get_object("framework"), scheme)
