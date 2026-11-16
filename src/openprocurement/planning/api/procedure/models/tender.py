from pydantic import ConfigDict

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.period import Period
from openprocurement.planning.api.constants import PlanProcurementMethod, PlanProcurementMethodType


class PlanTender(Model):
    procurementMethod: PlanProcurementMethod = ""
    procurementMethodType: PlanProcurementMethodType = ""
    tenderPeriod: Period


class CommonOrganization(Model):
    model_config = ConfigDict(extra="ignore")  # the tender view validates it against the tender models

    name: str
    name_en: str | None = None
    name_ru: str | None = None
    identifier: Identifier


class PreValidationTender(Model):
    """
    Only required fields for plan/tender validation, the other fields of the tender are ignored
    (only at the top level, nested models forbid unknown fields).
    Actual tender validation will be handled by dedicated tender models in tender view
    """

    model_config = ConfigDict(extra="ignore")

    procurementMethod: str | None = None
    procurementMethodType: str | None = None
    procuringEntity: CommonOrganization
