from itertools import chain

from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.organization import CommonOrganization
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import ModelType
from openprocurement.planning.api.constants import PROCEDURES


class PlanTender(Model):
    procurementMethod = StringType(choices=list(PROCEDURES.keys()), default="")
    procurementMethodType = StringType(choices=list(chain(*PROCEDURES.values())), default="")
    tenderPeriod = ModelType(Period, required=True)


class PreValidationTender(Model):
    """
    Only required fields for plan/tender validation with non strict mode
    Actual tender validation will be handled by dedicated tender models in tender view
    """

    procurementMethod = StringType()
    procurementMethodType = StringType()
    procuringEntity = ModelType(CommonOrganization, required=True, strict=False)
