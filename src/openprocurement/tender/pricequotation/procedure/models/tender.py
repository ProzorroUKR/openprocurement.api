from schematics.types import StringType, MD5Type, BaseType
from schematics.types.compound import ListType
from schematics.validate import ValidationError
from openprocurement.tender.core.constants import AWARD_CRITERIA_LOWEST_COST
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.models.period import (
    StartedPeriodEndRequired,
    PeriodEndRequired,
    Period,
    PeriodStartEndRequired,
)
from openprocurement.tender.core.procedure.models.organization import BusinessOrganization
from openprocurement.tender.core.procedure.models.item import Classification
from openprocurement.tender.core.procedure.models.tender import (
    PostBaseTender,
    PatchBaseTender,
    BaseTender,
    validate_related_buyer_in_items,
)
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.pricequotation.procedure.models.criterion import Criterion, validate_criterion_related_items
from openprocurement.tender.pricequotation.procedure.models.requirement import validate_criteria_id_uniq
from openprocurement.tender.pricequotation.procedure.models.item import TenderItem
from openprocurement.tender.pricequotation.procedure.models.organization import ProcuringEntity
from openprocurement.tender.pricequotation.constants import PQ, TENDERING_DURATION
from openprocurement.tender.pricequotation.validation import validate_profile_pattern
from openprocurement.tender.openua.validation import _validate_tender_period_start_date
from openprocurement.api.models import ModelType, Model, IsoDateTimeType, Value
from openprocurement.api.validation import validate_items_uniq
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.constants import PQ_MULTI_PROFILE_FROM, WORKING_DAYS


class Agreement(Model):
    id = MD5Type(required=True)

    def validate_id(self, data, value):
        agreement = get_request().registry.mongodb.agreements.get(value)
        if not agreement:
            raise ValidationError("id must be one of exists agreement")


class ShortlistedFirm(BusinessOrganization):
    id = StringType()
    status = StringType()


def validate_agreement(data, value):
    multi_profile_released = get_first_revision_date(data, default=get_now()) > PQ_MULTI_PROFILE_FROM
    if multi_profile_released and not value:
        raise ValidationError(BaseType.MESSAGES["required"])


def validate_profile(data, value):
    multi_profile_released = get_first_revision_date(data, default=get_now()) > PQ_MULTI_PROFILE_FROM
    if multi_profile_released and value:
        raise ValidationError("Rogue field.")
    if value:
        validate_profile_pattern(value)


def validate_tender_period_duration(data, period):
    tender_period_end_date = calculate_tender_business_date(
        get_now(),
        TENDERING_DURATION,
        data,
        working_days=True,
        calendar=WORKING_DAYS
    )
    if tender_period_end_date > period.endDate:
        raise ValidationError(f"tenderPeriod must be at least {TENDERING_DURATION.days} full business days long")


class PostTender(PostBaseTender):
    procurementMethodType = StringType(choices=[PQ], default=PQ)
    procurementMethod = StringType(choices=["selective"], default="selective")
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], default=AWARD_CRITERIA_LOWEST_COST)
    status = StringType(choices=["draft"], default="draft")
    profile = StringType()
    agreement = ModelType(Agreement)
    classification = ModelType(Classification)

    value = ModelType(Value, required=True)
    tenderPeriod = ModelType(StartedPeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity, required=True)

    items = ListType(
        ModelType(TenderItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq],
    )
    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_criteria_id_uniq],
    )

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_criteria(self, data, value):
        validate_criterion_related_items(data, value)

    def validate_tenderPeriod(self, data, period):
        if period.startDate:
            _validate_tender_period_start_date(data, period)
        validate_tender_period_duration(data, period)

    def validate_awardPeriod(self, data, period):
        if (
            period
            and period.startDate
            and data.get("tenderPeriod")
            and data.get("tenderPeriod").endDate
            and period.startDate < data.get("tenderPeriod").endDate
        ):
            raise ValidationError("period should begin after tenderPeriod")

    def validate_agreement(self, data, value):
        return validate_agreement(data, value)

    def validate_profile(self, data, value):
        return validate_profile(data, value)


class PatchTender(PatchBaseTender):
    procurementMethod = StringType(choices=["selective"])
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST])
    enquiryPeriod = ModelType(PeriodEndRequired)
    status = StringType(
        choices=[
            "draft",
            "draft.publishing",
        ],
    )
    profile = StringType()
    agreement = ModelType(Agreement)

    value = ModelType(Value)
    tenderPeriod = ModelType(PeriodEndRequired)
    awardPeriod = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity)

    classification = ModelType(Classification)

    items = ListType(
        ModelType(TenderItem, required=True),
        min_size=1,
        validators=[validate_items_uniq],
    )
    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_criteria_id_uniq],
    )


class PatchPQBotTender(Model):
    shortlistedFirms = ListType(ModelType(ShortlistedFirm))
    status = StringType(choices=["active.tendering", "draft.unsuccessful"], required=True)
    items = ListType(
        ModelType(TenderItem, required=True),
        min_size=1,
        validators=[validate_items_uniq],
    )
    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_criteria_id_uniq],
    )
    value = ModelType(Value)
    unsuccessfulReason = ListType(StringType)


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[PQ], required=True)
    procurementMethod = StringType(choices=["selective"], required=True)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], required=True)
    status = StringType(
        choices=[
            "draft",
            "draft.publishing",
            "active.tendering",
            "draft.unsuccessful",
        ],
        required=True
    )
    profile = StringType()
    agreement = ModelType(Agreement)
    shortlistedFirms = ListType(ModelType(ShortlistedFirm))

    value = ModelType(Value, required=True)
    tenderPeriod = ModelType(PeriodStartEndRequired)
    awardPeriod = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity, required=True)

    classification = ModelType(Classification)
    noticePublicationDate = IsoDateTimeType()
    unsuccessfulReason = ListType(StringType)

    items = ListType(
        ModelType(TenderItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq],
    )
    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_criteria_id_uniq],
    )

    next_check = BaseType()

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_criteria(self, data, value):
        validate_criterion_related_items(data, value)

    def validate_tenderPeriod(self, data, period):
        validate_tender_period_duration(data, period)

    def validate_awardPeriod(self, data, period):
        if (
            period
            and period.startDate
            and data.get("tenderPeriod")
            and data.get("tenderPeriod").endDate
            and period.startDate < data.get("tenderPeriod").endDate
        ):
            raise ValidationError("period should begin after tenderPeriod")

    def validate_agreement(self, data, value):
        return validate_agreement(data, value)

    def validate_profile(self, data, value):
        return validate_profile(data, value)
