from openprocurement.api.models import ListType
from openprocurement.frameworkagreement.cfaua.models.submodels.documents import EUDocument
from openprocurement.frameworkagreement.cfaua.models.submodels.item import Item
from openprocurement.frameworkagreement.cfaua.models.submodels.complaint import Complaint
from openprocurement.tender.core.models import Award as BaseAward
from schematics.types import BooleanType
from schematics.types.compound import ModelType
from schematics.transforms import whitelist

class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """
    class Options:
        roles = {
            'edit': whitelist(
                'description',
                'description_en',
                'description_ru',
                'eligible',
                'qualified',
                'status',
                'title',
                'title_en',
                'title_ru'
            ),
        }

    complaints = ListType(ModelType(Complaint), default=list())
    items = ListType(ModelType(Item))
    documents = ListType(ModelType(EUDocument), default=list())
    qualified = BooleanType()
    eligible = BooleanType()
