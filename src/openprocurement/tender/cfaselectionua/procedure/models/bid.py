from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.api.validation import validate_uniq_code
from openprocurement.tender.cfaselectionua.procedure.models.parameter import (
    CFASelectionParameter,
    CFASelectionPatchParameter,
)
from openprocurement.tender.core.procedure.models.bid import Bid, PatchBid, PatchQualificationBid, PostBid


class CFASelectionPatchBid(PatchBid):
    parameters = ListType(ModelType(CFASelectionPatchParameter, required=True), validators=[validate_uniq_code])


class CFASelectionPatchQualificationBid(PatchQualificationBid):
    parameters = ListType(ModelType(CFASelectionPatchParameter, required=True), validators=[validate_uniq_code])


class CFASelectionPostBid(PostBid):
    parameters = ListType(ModelType(CFASelectionParameter, required=True), validators=[validate_uniq_code])


class CFASelectionBid(Bid):
    parameters = ListType(ModelType(CFASelectionParameter, required=True), validators=[validate_uniq_code])
