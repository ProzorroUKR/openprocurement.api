from pydantic import field_validator

from openprocurement.api.procedure.models.base import validate_uniq_code
from openprocurement.tender.cfaselectionua.procedure.models.parameter import (
    CFASelectionParameter,
    CFASelectionPatchParameter,
)
from openprocurement.tender.core.procedure.models.bid import Bid, PatchBid, PatchQualificationBid, PostBid


class CFASelectionPatchBid(PatchBid):
    parameters: list[CFASelectionPatchParameter] | None = None

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value


class CFASelectionPatchQualificationBid(PatchQualificationBid):
    parameters: list[CFASelectionPatchParameter] | None = None

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value


class CFASelectionPostBid(PostBid):
    parameters: list[CFASelectionParameter] | None = None

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value


class CFASelectionBid(Bid):
    parameters: list[CFASelectionParameter] | None = None

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value
