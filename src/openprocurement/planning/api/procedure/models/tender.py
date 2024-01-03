from itertools import chain

from schematics.exceptions import ValidationError
from schematics.types import StringType

from openprocurement.api.constants import PLAN_ADDRESS_KIND_REQUIRED_FROM
from openprocurement.api.models import Model
from openprocurement.api.procedure.utils import is_obj_const_active
from openprocurement.api.procedure.models.base import ModelType
from openprocurement.api.procedure.models.period import Period
from openprocurement.planning.api.constants import PROCEDURES
from openprocurement.planning.api.procedure.context import get_plan


class Tender(Model):
    procurementMethod = StringType(choices=list(PROCEDURES.keys()), default="")
    procurementMethodType = StringType(choices=list(chain(*PROCEDURES.values())), default="")
    tenderPeriod = ModelType(Period, required=True)

    def validate_procurementMethodType(self, tender, procurement_method_type):
        plan = get_plan()
        method = tender.get("procurementMethod")
        if is_obj_const_active(plan, PLAN_ADDRESS_KIND_REQUIRED_FROM) and method == "":
            procurement_method_types = ("centralizedProcurement", )
        else :
            procurement_method_types = PROCEDURES[method]
        if procurement_method_type not in procurement_method_types:
            raise ValidationError(
                "Value must be one of {!r}.".format(procurement_method_types)
            )
