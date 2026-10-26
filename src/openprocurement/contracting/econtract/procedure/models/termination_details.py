from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.contracting.core.procedure.models.value import AmountPaid
from openprocurement.contracting.econtract.procedure.models.document import Document


class BaseTerminationDetails(Model):
    reasonType = StringType(choices=["completed", "disrupted"])
    reason = StringType()
    amountPaid = ModelType(AmountPaid)


class PostTerminationDetails(BaseTerminationDetails):
    pass


class TerminationDetails(BaseTerminationDetails):
    status = StringType(required=True, choices=["draft", "active"])
    dateCreated = IsoDateTimeType(required=True)
    datePublished = IsoDateTimeType()
    documents = ListType(ModelType(Document, required=True))


class PatchContractTerminationDetails(Model):
    terminationDetails = ModelType(PostTerminationDetails)
