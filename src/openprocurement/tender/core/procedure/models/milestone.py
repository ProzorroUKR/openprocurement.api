from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.core.procedure.models.qualification_milestone import QualificationMilestoneCode


class QualificationMilestone(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    code: QualificationMilestoneCode
    dueDate: IsoDateTime | None = None
    description: str | None = None
    date: IsoDateTime = Field(default_factory=get_request_now)


class QualificationMilestoneListMixin(Model):
    milestones: list[QualificationMilestone] | None = None

    @field_validator("milestones")
    @classmethod
    def validate_milestones(cls, milestones):
        """
        This validation on the model, not on the view
        because there is a way to post milestone to different zones (couchdb masters)
        and concord will merge them, that shouldn't be the case
        """
        if milestones and len([m for m in milestones if m.code == QualificationMilestoneCode.CODE_24_HOURS]) > 1:
            raise ValidationError("There can be only one '24h' milestone")
        return milestones


def validate_milestones_lot(tender, milestones):
    lot_ids = {lot.id for lot in getattr(tender, "lots", None) or []}  # not a field of all the tenders
    for milestone in milestones or "":
        if milestone.relatedLot is not None and milestone.relatedLot not in lot_ids:
            raise ValidationError("relatedLot should be one of the lots.")
