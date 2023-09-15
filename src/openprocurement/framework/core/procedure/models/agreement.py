from uuid import uuid4
from schematics.types import MD5Type, StringType, BaseType, BooleanType
from schematics.types.compound import DictType
from schematics.types.serializable import serializable

from openprocurement.api.models import (
    Model,
    ModelType,
    IsoDateTimeType,
    ListType,
    RootModel,
    PeriodEndRequired as BasePeriodEndRequired,
    Organization,
)
from openprocurement.framework.core.procedure.models.contract import Contract
from openprocurement.framework.dps.constants import DPS_TYPE


class PatchAgreement(Model):
    status = StringType(choices=["active", "terminated"])


class Agreement(RootModel):
    agreementID = StringType()
    agreementType = StringType(default=DPS_TYPE, required=True)
    status = StringType(choices=["active", "terminated"], required=True)
    period = ModelType(BasePeriodEndRequired)
    procuringEntity = ModelType(Organization, required=True)
    contracts = ListType(ModelType(Contract, required=True), default=list())

    _attachments = DictType(DictType(BaseType), default=dict())

    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    date = IsoDateTimeType()

    owner = StringType()
    owner_token = StringType()

    transfer_token = StringType()

    revisions = BaseType(default=list)
    config = BaseType()

    mode = StringType(choices=["test"])


class PostAgreement(Model):
    @serializable
    def doc_type(self):
        return "Agreement"

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    agreementID = StringType()
    agreementType = StringType(default=DPS_TYPE, required=True)
    status = StringType(choices=["active"], required=True)
    period = ModelType(BasePeriodEndRequired)
    procuringEntity = ModelType(Organization, required=True)
    contracts = ListType(ModelType(Contract, required=True), default=list())

    _attachments = DictType(DictType(BaseType), default=dict())

    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    date = IsoDateTimeType()

    owner = StringType()
    owner_token = StringType()

    transfer_token = StringType(default=lambda: uuid4().hex)

    revisions = BaseType(default=list)
    config = BaseType()

    mode = StringType(choices=["test"])


class AgreementConfig(Model):
    test = BooleanType()
    restricted = BooleanType()


class AgreementChronographData(Model):
    _id = MD5Type(deserialize_from=['id'])
    next_check = BaseType()
