from uuid import uuid4
from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType, BaseType, BooleanType

from openprocurement.api.models import (
    IsoDateTimeType,
    Model,
    ModelType,
    ListType,
)
from openprocurement.api.utils import get_now
from openprocurement.framework.core.procedure.models.milestone import Milestone
from openprocurement.framework.core.procedure.models.organization import (
    ContractBusinessOrganization,
    PatchContractBusinessOrganization,
)


class PatchContract(Model):
    suppliers = ListType(ModelType(PatchContractBusinessOrganization, required=True), min_size=1)

    def validate_suppliers(self, data, suppliers):
        if len(suppliers) != 1:
            raise ValidationError("Contract must have only one supplier")


class Contract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    qualificationID = StringType()
    status = StringType(choices=["active", "suspended", "terminated"])
    submissionID = StringType()
    suppliers = ListType(ModelType(ContractBusinessOrganization, required=True), required=True, min_size=1)
    milestones = ListType(ModelType(Milestone, required=True), required=True, min_size=1, )
    date = IsoDateTimeType()

    def validate_suppliers(self, data, suppliers):
        if len(suppliers) != 1:
            raise ValidationError("Contract must have only one supplier")
