from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.tender.core.procedure.models.criterion import LegislationItem
from openprocurement.tender.core.procedure.models.document import Document, PostDocument


class Proceeding(Model):
    dateProceedings = IsoDateTimeType(required=True)
    proceedingNumber = StringType(required=True)


class PostAppeal(Model):
    description = StringType(required=True)
    documents = ListType(ModelType(PostDocument, required=True))

    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def dateCreated(self):
        return get_request_now().isoformat()

    @serializable
    def datePublished(self):
        return get_request_now().isoformat()

    @serializable
    def legislation(self):
        legislation = {
            "version": "2020-04-19",
            "type": "NATIONAL_LEGISLATION",
            "article": "18.23",
            "identifier": {
                "id": "922-VIII",
                "legalName": 'Закон України "Про публічні закупівлі"',
                "uri": "https://zakon.rada.gov.ua/laws/show/922-19#n1284",
            },
        }
        return legislation


class PatchAppeal(Model):
    proceeding = ModelType(Proceeding)


class Appeal(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    description = StringType()
    documents = ListType(ModelType(Document, required=True))
    proceeding = ModelType(Proceeding)
    legislation = ModelType(LegislationItem)
    author = StringType()
    dateCreated = IsoDateTimeType()
    datePublished = IsoDateTimeType()
