from schematics.types.serializable import serializable

from openprocurement.api.models import IsoDateTimeType, ValidationError
from openprocurement.tender.core.procedure.context import get_tender
from schematics.types import StringType, MD5Type, BooleanType, BaseType
from uuid import uuid4
from openprocurement.tender.core.procedure.models.base import (
    ModelType,
    ListType,
)
from openprocurement.tender.core.procedure.models.req_response import (
    PatchObjResponsesMixin,
    ObjResponseMixin,
)
from openprocurement.tender.core.procedure.models.document import Document
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
    documents = ListType(ModelType(Document, required=True))
    qualified = BooleanType()  # відсутність підстав для відмови в участі
    eligible = BooleanType()  # підтвердити відповідність кваліфікаційним критеріям (17 стаття)
    complaints = BaseType()

    @staticmethod
    def should_be_qualified():
        # TODO: find a way to determine, not based on procurementMethodType
        return get_tender()["procurementMethodType"] != "belowThreshold"

    @staticmethod
    def should_be_eligible():
        # TODO: find a way to determine, not based on procurementMethodType
        return get_tender()["procurementMethodType"] != "belowThreshold"

    @serializable(serialized_name="qualified", serialize_when_none=False)
    def default_qualified(self):
        if self.qualified is None and self.should_be_qualified():
            return False
        return self.qualified

    @serializable(serialized_name="eligible", serialize_when_none=False)
    def default_eligible(self):
        if self.eligible is None and self.should_be_eligible():
            return False
        return self.eligible

    def validate_qualified(self, data, qualified):
        if not self.should_be_qualified():
            return
        status = data.get("status")
        if status == "active" and qualified is not True:
            raise ValidationError("This field must be true.")

    def validate_eligible(self, data, eligible):
        if not self.should_be_eligible():
            return
        status = data.get("status")
        if status == "active" and eligible is not True:
            raise ValidationError("This field must be true.")

    def validate_lotID(self, data, value):
        lots = get_tender().get("lots")
        if lots:
            if not value:
                raise ValidationError("This field is required.")
            if value and value not in {lot["id"] for lot in lots if lot}:
                raise ValidationError("lotID should be one of lots")
