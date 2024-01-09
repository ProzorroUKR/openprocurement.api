from schematics.types import StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.api.procedure.models.item import Classification as BaseClassification

from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
    PostAgreement as BasePostAgreement,
)
from openprocurement.framework.core.procedure.models.framework import DKClassification
from openprocurement.framework.core.utils import generate_agreement_id
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.dps.procedure.models.organization import ProcuringEntity


class Agreement(BaseAgreement):
    agreementType = StringType(default=DPS_TYPE)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    frameworkID = StringType()
    classification = ModelType(DKClassification, required=True)
    additionalClassifications = ListType(ModelType(BaseClassification))
    frameworkDetails = StringType()

    @serializable(serialize_when_none=False)
    def next_check(self):
        checks = []
        if self.status == "active":
            milestone_dueDates = [
                milestone.dueDate
                for contract in self.contracts for milestone in contract.milestones
                if milestone.dueDate and milestone.status == "scheduled"
            ]
            if milestone_dueDates:
                checks.append(min(milestone_dueDates))
            checks.append(self.period.endDate)
        return min(checks).isoformat() if checks else None


class PostAgreement(BasePostAgreement):
    @serializable(serialized_name="agreementID")
    def agreement_id(self):
        return generate_agreement_id(get_request())

    agreementType = StringType(default=DPS_TYPE)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    frameworkID = StringType()
    classification = ModelType(DKClassification, required=True)
    additionalClassifications = ListType(ModelType(BaseClassification))
    frameworkDetails = StringType()
