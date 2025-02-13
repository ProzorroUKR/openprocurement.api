from uuid import uuid4

from schematics.types import BaseType, MD5Type, StringType
from schematics.types.compound import DictType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model, RootModel
from openprocurement.api.procedure.models.organization import Organization
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.framework.core.procedure.models.contract import Contract
from openprocurement.framework.core.procedure.models.framework import (
    AdditionalClassification,
    DKClassification,
)
from openprocurement.framework.dps.constants import DPS_TYPE


class PatchAgreement(Model):
    status = StringType(choices=["active", "terminated"])


class CommonAgreement(RootModel):
    agreementID = StringType()
    agreementType = StringType(default=DPS_TYPE, required=True)
    status = StringType(choices=["active", "terminated"], required=True)
    period = ModelType(PeriodEndRequired)
    procuringEntity = ModelType(Organization, required=True)
    contracts = ListType(ModelType(Contract, required=True), default=[])

    _attachments = DictType(DictType(BaseType), default={})

    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    date = IsoDateTimeType()

    owner = StringType()
    owner_token = StringType()

    transfer_token = StringType()

    revisions = BaseType(default=list)
    config = BaseType()

    mode = StringType(choices=["test"])


class CommonPostAgreement(Model):
    @serializable
    def doc_type(self):
        return "Agreement"

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    agreementID = StringType()
    agreementType = StringType(default=DPS_TYPE, required=True)
    status = StringType(choices=["active"], required=True)
    period = ModelType(PeriodEndRequired)
    procuringEntity = ModelType(Organization, required=True)
    contracts = ListType(ModelType(Contract, required=True), default=[])

    _attachments = DictType(DictType(BaseType), default={})

    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    date = IsoDateTimeType()

    owner = StringType()
    owner_token = StringType()

    transfer_token = StringType(default=lambda: uuid4().hex)

    revisions = BaseType(default=list)
    config = BaseType()

    mode = StringType(choices=["test"])


class AgreementChronographData(Model):
    _id = MD5Type(deserialize_from=["id"])
    next_check = BaseType()


class Agreement(CommonAgreement):
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
