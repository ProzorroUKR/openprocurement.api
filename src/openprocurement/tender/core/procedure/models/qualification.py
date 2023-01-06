from openprocurement.api.models import IsoDateTimeType, ValidationError
from openprocurement.tender.core.procedure.context import get_tender
from schematics.types import StringType, MD5Type, BooleanType, BaseType
from uuid import uuid4
from openprocurement.tender.core.procedure.models.base import (
    ModelType,
    ListType,
    BaseQualification,
)
from openprocurement.tender.core.procedure.models.req_response import (
    PatchObjResponsesMixin,
    ObjResponseMixin,
)
from openprocurement.tender.core.procedure.models.document import EUDocument
from openprocurement.tender.core.procedure.models.milestone import QualificationMilestoneListMixin


class PatchQualification(PatchObjResponsesMixin):
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    status = StringType(choices=["pending", "active", "unsuccessful", "cancelled"])
    qualified = BooleanType()
    eligible = BooleanType()


class Qualification(ObjResponseMixin, PatchQualification, QualificationMilestoneListMixin):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    bidID = StringType(required=True)
    lotID = MD5Type()
    status = StringType(choices=["pending", "active", "unsuccessful", "cancelled"], default="pending")
    date = IsoDateTimeType()
    documents = ListType(ModelType(EUDocument, required=True))
    qualified = BooleanType(default=False)
    eligible = BooleanType(default=False)
    complaints = BaseType()

    def validate_qualified(self, data, qualified):
        tender_status = data.get("status")
        if tender_status == "active" and not qualified:
            raise ValidationError("This field is required.")

    def validate_eligible(self, data, eligible):
        tender_status = data.get("status")
        if tender_status == "active" and not eligible:
            raise ValidationError("This field is required.")

    def validate_lotID(self, data, value):
        lots = get_tender().get("lots")
        if lots:
            if not value:
                raise ValidationError("This field is required.")
            if value and value not in {lot["id"] for lot in lots if lot}:
                raise ValidationError("lotID should be one of lots")



