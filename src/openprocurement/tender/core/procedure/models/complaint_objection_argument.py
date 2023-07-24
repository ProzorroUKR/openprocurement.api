from enum import Enum
from uuid import uuid4

from schematics.types import StringType, MD5Type
from schematics.types.compound import ListType, ModelType
from schematics.types.serializable import serializable

from openprocurement.api.models import Model
from openprocurement.tender.core.procedure.models.document import PostDocument


class EvidenceType(Enum):
    external = "external"
    internal = "internal"


class Evidence(Model):
    @serializable
    def id(self):
        return uuid4().hex

    type = StringType(choices=[choice.value for choice in EvidenceType], required=True)
    title = StringType(required=True)
    description = StringType(required=True)
    documents = ListType(ModelType(PostDocument), min_size=1, required=True)


class Argument(Model):
    @serializable
    def id(self):
        return uuid4().hex

    description = StringType(required=True)
    relatedJustification = StringType(required=True)
    evidences = ListType(ModelType(Evidence))
