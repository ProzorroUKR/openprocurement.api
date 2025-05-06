from datetime import timedelta
from enum import StrEnum
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import FloatType, IntType, MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.constants import MILESTONE_CODES, MILESTONE_TITLES
from openprocurement.api.constants_env import MILESTONES_VALIDATION_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.api.utils import get_first_revision_date
from openprocurement.tender.core.procedure.models.qualification_milestone import (
    QualificationMilestoneCode,
)
from openprocurement.tender.core.procedure.validation import is_positive_float
from openprocurement.tender.core.utils import (
    calculate_tender_date,
    calculate_tender_full_date,
)


class QualificationMilestone(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    code = StringType(
        required=True,
        choices=[
            QualificationMilestoneCode.CODE_24_HOURS.value,
            QualificationMilestoneCode.CODE_LOW_PRICE.value,
        ],
    )
    dueDate = IsoDateTimeType()
    description = StringType()
    date = IsoDateTimeType(default=get_request_now)

    @serializable(serialized_name="dueDate")
    def set_due_date(self):
        if not self.dueDate:
            if self.code == QualificationMilestoneCode.CODE_24_HOURS.value:
                self.dueDate = calculate_tender_date(
                    self.date,
                    timedelta(hours=24),
                    tender=get_tender(),
                )
            elif self.code == QualificationMilestoneCode.CODE_LOW_PRICE.value:
                self.dueDate = calculate_tender_full_date(
                    self.date,
                    timedelta(days=1),
                    tender=get_tender(),
                    working_days=True,
                )
        return self.dueDate and self.dueDate.isoformat()


class QualificationMilestoneListMixin(Model):
    milestones = ListType(ModelType(QualificationMilestone, required=True))

    def validate_milestones(self, data, milestones):
        """
        This validation on the model, not on the view
        because there is a way to post milestone to different zones (couchdb masters)
        and concord will merge them, that shouldn't be the case
        """
        if milestones and len([m for m in milestones if m.code == QualificationMilestoneCode.CODE_24_HOURS]) > 1:
            raise ValidationError("There can be only one '24h' milestone")


class Duration(Model):
    days = IntType(required=True, min_value=1)
    type = StringType(required=True, choices=["working", "banking", "calendar"])


class TenderMilestoneType(StrEnum):
    FINANCING = "financing"
    DELIVERY = "delivery"


class Milestone(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True)
    description = StringType()
    type = StringType(
        required=True,
        choices=[
            TenderMilestoneType.FINANCING.value,
            TenderMilestoneType.DELIVERY.value,
        ],
    )
    code = StringType(required=True)
    percentage = FloatType(required=True, max_value=100, validators=[is_positive_float])

    duration = ModelType(Duration, required=True)
    sequenceNumber = IntType(required=True, min_value=0)
    relatedLot = MD5Type()

    def validate_description(self, data, value):
        if data.get("title", "") == "anotherEvent" and not value:
            raise ValidationError("This field is required.")

        should_validate = get_first_revision_date(get_tender(), default=get_request_now()) > MILESTONES_VALIDATION_FROM
        if should_validate and value and len(value) > 2000:
            raise ValidationError("description should contain at most 2000 characters")

    def validate_code(self, data, value):
        milestone_type = data.get("type")
        if value not in MILESTONE_CODES[milestone_type]:
            raise ValidationError(f"Value must be one of {MILESTONE_CODES[milestone_type]}")

    def validate_title(self, data, value):
        milestone_type = data.get("type")
        if value not in MILESTONE_TITLES[milestone_type]:
            raise ValidationError(f"Value must be one of {MILESTONE_TITLES[milestone_type]}")


def validate_milestones_lot(data, milestones):
    lot_ids = {lot.get("id") for lot in data.get("lots") or ""}
    for milestone in milestones or "":
        if milestone.relatedLot is not None and milestone.relatedLot not in lot_ids:
            raise ValidationError("relatedLot should be one of the lots.")
