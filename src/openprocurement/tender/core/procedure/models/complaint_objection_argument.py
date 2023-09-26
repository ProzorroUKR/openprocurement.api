from uuid import uuid4

from schematics.types import StringType, MD5Type
from schematics.types.serializable import serializable
from schematics.types.compound import ListType, ModelType

from openprocurement.api.models import Model
from openprocurement.tender.core.procedure.models.document import PostDocument


class EvidenceDocument(PostDocument):

    @serializable
    def dateModified(self):
        pass


class Evidence(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True)
    description = StringType(required=True)
    documents = ListType(ModelType(EvidenceDocument), min_size=1, required=True)


class Argument(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    description = StringType(required=True)
    evidences = ListType(ModelType(Evidence), serialize_when_none=True, default=list())
