from openprocurement.api.models import ListType
from openprocurement.frameworkagreement.cfaua.models.submodels.item import Item
from openprocurement.frameworkagreement.cfaua.models.submodels.documents import Document
from openprocurement.tender.core.models import Contract as BaseContract
from schematics.types.compound import ModelType


class Contract(BaseContract):
    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))