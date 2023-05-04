from schematics.types import MD5Type, StringType, IntType, FloatType
from openprocurement.api.context import get_now
from openprocurement.api.models import IsoDateTimeType, Model
from openprocurement.api.utils import get_first_revision_date
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.utils import calculate_tender_date, calculate_complaint_business_date
from openprocurement.tender.core.validation import is_positive_float
from schematics.exceptions import ValidationError
from schematics.types.serializable import serializable
from openprocurement.tender.core.procedure.models.base import ModelType, ListType
from openprocurement.api.constants import MILESTONES_VALIDATION_FROM
from datetime import timedelta
from uuid import uuid4


class QualificationMilestone(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    CODE_24_HOURS = "24h"
    CODE_LOW_PRICE = "alp"
    code = StringType(required=True, choices=[CODE_24_HOURS, CODE_LOW_PRICE])
    dueDate = IsoDateTimeType()
    description = StringType()
    date = IsoDateTimeType(default=get_now)

    @serializable(serialized_name="dueDate")
    def set_due_date(self):
        if not self.dueDate:
            if self.code == self.CODE_24_HOURS:
                self.dueDate = calculate_tender_date(
                    self.date, timedelta(hours=24), get_tender()
                )
            elif self.code == self.CODE_LOW_PRICE:
                self.dueDate = calculate_complaint_business_date(
                    self.date, timedelta(days=1), get_tender(), working_days=True
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
        if milestones and len(list([m for m in milestones if m.code == QualificationMilestone.CODE_24_HOURS])) > 1:
            raise ValidationError("There can be only one '24h' milestone")


class Duration(Model):
    days = IntType(required=True, min_value=1)
    type = StringType(required=True, choices=["working", "banking", "calendar"])

    def validate_days(self, data, value):
        tender = get_tender()
        if get_first_revision_date(tender, default=get_now()) > MILESTONES_VALIDATION_FROM and value > 1000:
            raise ValidationError("days shouldn't be more than 1000")


class Milestone(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(
        required=True,
        choices=[
            "executionOfWorks",
            "deliveryOfGoods",
            "submittingServices",
            "signingTheContract",
            "submissionDateOfApplications",
            "dateOfInvoicing",
            "endDateOfTheReportingPeriod",
            "anotherEvent",
        ],
    )
    description = StringType()
    type = StringType(required=True, choices=["financing"])
    code = StringType(required=True, choices=["prepayment", "postpayment"])
    percentage = FloatType(required=True, max_value=100, validators=[is_positive_float])

    duration = ModelType(Duration, required=True)
    sequenceNumber = IntType(required=True, min_value=0)
    relatedLot = MD5Type()

    def validate_description(self, data, value):
        if data.get("title", "") == "anotherEvent" and not value:
            raise ValidationError("This field is required.")

        should_validate = get_first_revision_date(get_tender(), default=get_now()) > MILESTONES_VALIDATION_FROM
        if should_validate and value and len(value) > 2000:
            raise ValidationError("description should contain at most 2000 characters")


def validate_milestones_lot(data, milestones):
    lot_ids = {l.get("id") for l in data.get("lots") or ""}
    for milestone in milestones or "":
        if milestone.relatedLot is not None and  milestone.relatedLot not in lot_ids:
            raise ValidationError("relatedLot should be one of the lots.")
