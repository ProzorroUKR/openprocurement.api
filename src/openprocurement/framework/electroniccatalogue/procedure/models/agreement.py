from schematics.types import StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
)
from openprocurement.framework.core.procedure.models.agreement import (
    PostAgreement as BasePostAgreement,
)
from openprocurement.framework.core.procedure.models.framework import (
    AdditionalClassification,
    DKClassification,
)
from openprocurement.framework.core.utils import generate_agreement_id
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.framework.electroniccatalogue.procedure.models.organization import (
    CentralProcuringEntity,
)


class Agreement(BaseAgreement):
    agreementType = StringType(default=ELECTRONIC_CATALOGUE_TYPE)
    procuringEntity = ModelType(CentralProcuringEntity, required=True)
    frameworkID = StringType()
    classification = ModelType(DKClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True))
    frameworkDetails = StringType()

    @serializable(serialize_when_none=False)
    def next_check(self):
        checks = []
        if self.status == "active":
            milestone_dueDates = [
                milestone.dueDate
                for contract in self.contracts
                for milestone in contract.milestones
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

    agreementType = StringType(default=ELECTRONIC_CATALOGUE_TYPE)
    procuringEntity = ModelType(CentralProcuringEntity, required=True)
    frameworkID = StringType()
    classification = ModelType(DKClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True))
    frameworkDetails = StringType()
