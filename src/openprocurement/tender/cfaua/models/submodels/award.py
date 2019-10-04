# -*- coding: utf-8 -*-
from openprocurement.api.models import ListType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.cfaua.models.submodels.complaint import Complaint
from openprocurement.tender.cfaua.models.submodels.documents import EUDocument
from openprocurement.tender.cfaua.models.submodels.item import Item
from openprocurement.tender.cfaua.models.submodels.value import Value
from openprocurement.tender.core.models import Award as BaseAward
from schematics.types import BooleanType
from schematics.types.compound import ModelType


class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """

    class Options:
        roles = RolesFromCsv("Award.csv", relative_to=__file__)

    complaints = ListType(ModelType(Complaint, required=True), default=list())
    items = ListType(ModelType(Item, required=True))
    documents = ListType(ModelType(EUDocument, required=True), default=list())
    qualified = BooleanType()
    eligible = BooleanType()
    value = ModelType(Value)
