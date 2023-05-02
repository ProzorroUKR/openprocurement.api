# -*- coding: utf-8 -*-
from openprocurement.api.models import ListType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.cfaua.models.submodels.complaint import (
    ComplaintPolyModelType,
    Complaint,
    Claim,
)
from openprocurement.tender.openua.models import get_complaint_type_model
from openprocurement.tender.cfaua.models.submodels.item import Item
from openprocurement.tender.cfaua.models.submodels.value import Value
from openprocurement.tender.core.models import (
    Award as BaseAward,
    EUDocument,
    QualificationMilestoneListMixin,
    WeightedValueMixin,
)
from schematics.types import BooleanType
from schematics.types.compound import ModelType
from schematics.transforms import whitelist


class Award(BaseAward, QualificationMilestoneListMixin, WeightedValueMixin):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """
    class Options:
        _common = whitelist(
            "description", "description_ru", "description_en", "title", "title_ru", "title_en",
            "eligible", "qualified",
        )
        _all = _common + whitelist(
            "status", "lotID", "complaintPeriod", "bid_id", "subcontractingDetails", "date",
            "complaints", "id", "documents", "items", "suppliers", "value", "milestones", "requirementResponses",
            "weightedValue",
        )
        roles = {
            "Administrator": whitelist("complaintPeriod"),
            "embedded": _all,
            "default": _all,
            "create": whitelist("lotID", "bid_id", "subcontractingDetails", "items", "suppliers", "value") + _common,
            "edit": whitelist("status") + _common,
            "view": _all
        }

    complaints = ListType(
        ComplaintPolyModelType(
            [Complaint, Claim],
            claim_function=get_complaint_type_model,
            required=True,
        ),
        default=list(),
    )
    items = ListType(ModelType(Item, required=True))
    documents = ListType(ModelType(EUDocument, required=True), default=list())
    qualified = BooleanType()
    eligible = BooleanType()
    value = ModelType(Value)
