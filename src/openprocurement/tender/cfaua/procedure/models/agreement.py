from schematics.types import MD5Type, StringType, BaseType
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError
from isodate import duration_isoformat
from uuid import uuid4
from openprocurement.api.context import get_now
from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
    Period,
)
from openprocurement.tender.core.models import validate_features_uniq
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.feature import Feature, validate_related_items
from openprocurement.tender.cfaua.procedure.models.agreement_contract import AgreementContract
from openprocurement.tender.cfaua.procedure.models.item import Item
from openprocurement.tender.cfaua.constants import MAX_AGREEMENT_PERIOD


class PatchAgreement(Model):
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

    def validate_period(self, data, value):
        if data.get("status") == "active":
            if not value:
                raise ValidationError("Period is required for agreement signing.")
            if not value.startDate or not value.endDate:
                raise ValidationError("startDate and endDate are required in agreement.period.")

            calculated_end_date = value.startDate + MAX_AGREEMENT_PERIOD
            if value.endDate > calculated_end_date:
                raise ValidationError(f"Agreement period can't be greater than {duration_isoformat(MAX_AGREEMENT_PERIOD)}.")


class Agreement(Model):
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
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    items = ListType(ModelType(Item, required=True))
    period = ModelType(Period)
    status = StringType(choices=["pending", "active", "cancelled", "unsuccessful"], required=True)
    contracts = ListType(ModelType(AgreementContract, required=True))

    documents = BaseType()

    def validate_features(self, data, features):
        validate_related_items(data, features)

    def validate_dateSigned(self, data, value):
        if value:
            award_ids = [c["awardID"] for c in data["contracts"]]
            award = next(i for i in get_tender().get("awards", [])
                         if i["id"] in award_ids)
            complaint_period = award.get("complaintPeriod")
            if (
                complaint_period
                and complaint_period.get("endDate")
                and value <= dt_from_iso(complaint_period['endDate'])
            ):
                raise ValidationError(
                    "Agreement signature date should be after "
                    f"award complaint period end date ({complaint_period['endDate']})"
                )
            if value > get_now():
                raise ValidationError("Agreement signature date can't be in the future")
