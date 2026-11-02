from uuid import uuid4

from isodate import duration_isoformat
from schematics.exceptions import ValidationError
from schematics.types import BaseType, MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.validation import validate_uniq_code, validate_uniq_id
from openprocurement.tender.cfaua.constants import CFA_UA_MAX_AGREEMENT_PERIOD
from openprocurement.tender.cfaua.procedure.models.agreement_contract import CFAAgreementContract
from openprocurement.tender.cfaua.procedure.models.feature import CFAFeature
from openprocurement.tender.core.procedure.models.feature import validate_related_items
from openprocurement.tender.core.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.milestone import Milestone


class CFAPatchAgreement(Model):
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    status = StringType(choices=["pending", "active", "cancelled", "unsuccessful"])
    period = ModelType(Period)
    dateSigned = IsoDateTimeType()
    agreementNumber = StringType()


class CFAAgreement(Model):
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    agreementID = StringType()
    agreementNumber = StringType()
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    features = ListType(ModelType(CFAFeature, required=True), validators=[validate_uniq_code])
    items = ListType(ModelType(Item, required=True))
    period = ModelType(Period)
    status = StringType(choices=["pending", "active", "cancelled", "unsuccessful"], required=True)
    contracts = ListType(ModelType(CFAAgreementContract, required=True))
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])

    documents = BaseType()

    def validate_features(self, data, features):
        validate_related_items(data, features)

    def validate_period(self, data, value):
        if data.get("status") == "active":
            if not value:
                raise ValidationError("Period is required for agreement signing.")
            if not value.startDate or not value.endDate:
                raise ValidationError("startDate and endDate are required in agreement.period.")

            calculated_end_date = value.startDate + CFA_UA_MAX_AGREEMENT_PERIOD
            if value.endDate > calculated_end_date:
                raise ValidationError(
                    f"Agreement period can't be greater than {duration_isoformat(CFA_UA_MAX_AGREEMENT_PERIOD)}."
                )
