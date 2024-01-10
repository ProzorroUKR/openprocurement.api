from openprocurement.api.procedure.models.item import (
    validate_scheme,
    CPVClassification as BaseCPVClassification,
)
from openprocurement.framework.core.procedure.context import get_object


class CPVClassification(BaseCPVClassification):
    def validate_scheme(self, data, scheme):
        validate_scheme(get_object("framework"), scheme)
