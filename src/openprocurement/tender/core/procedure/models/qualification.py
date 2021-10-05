from openprocurement.api.models import IsoDateTimeType, ValidationError
from openprocurement.tender.core.procedure.models.milestone import QualificationMilestoneListMixin
from openprocurement.tender.core.procedure.context import get_tender
from schematics.types import StringType, MD5Type
from uuid import uuid4


class Qualification(QualificationMilestoneListMixin):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    bidID = StringType(required=True)
    lotID = MD5Type()
    status = StringType(choices=["pending", "active", "unsuccessful", "cancelled"], default="pending")
    date = IsoDateTimeType()

    def validate_lotID(self, data, value):
        lots = get_tender().get("lots")
        if lots:
            if not value:
                raise ValidationError("This field is required.")
            if value and value not in tuple(lot["id"] for lot in lots if lot):
                raise ValidationError("lotID should be one of lots")
