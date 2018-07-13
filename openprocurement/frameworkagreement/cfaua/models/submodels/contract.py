from openprocurement.api.models import ListType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.frameworkagreement.cfaua.models.submodels.item import Item
from openprocurement.frameworkagreement.cfaua.models.submodels.documents import Document
from openprocurement.tender.core.models import Contract as BaseContract
from schematics.types.compound import ModelType


class Contract(BaseContract):
    class Options:
        roles = RolesFromCsv('Contract.csv', relative_to=__file__)
    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))
