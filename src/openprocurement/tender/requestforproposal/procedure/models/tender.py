from datetime import timedelta

from schematics.types import StringType
from schematics.validate import ValidationError

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.context import get_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.procedure.models.document import PostDocument
from openprocurement.tender.core.procedure.models.guarantee import Guarantee
from openprocurement.tender.core.procedure.models.item import TechFeatureItem as Item
from openprocurement.tender.core.procedure.models.item import validate_classification_id
from openprocurement.tender.core.procedure.models.milestone import Milestone
from openprocurement.tender.core.procedure.models.organization import Organization
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriodEndRequired,
    StartedEnquiryPeriodEndRequired,
)
from openprocurement.tender.core.procedure.models.tender import (
    PatchTender as BasePatchTender,
)
from openprocurement.tender.core.procedure.models.tender import (
    PostTender as BasePostTender,
)
from openprocurement.tender.core.procedure.models.tender import Tender as BaseTender
from openprocurement.tender.core.procedure.validation import (
    validate_tender_period_duration,
)
from openprocurement.tender.core.utils import calculate_tender_full_date
from openprocurement.tender.requestforproposal.constants import (
    REQUEST_FOR_PROPOSAL,
    TENDERING_DURATION,
)


def validate_enquiry_period(data, period):
    if (
        get_first_revision_date(data, default=get_now()) > RELEASE_2020_04_19
        and period
        and period.startDate
        and period.endDate
        and period.endDate
        < calculate_tender_full_date(
            period.startDate,
            timedelta(days=3),
            tender=data,
        )
    ):
        raise ValidationError("the enquiryPeriod cannot end earlier than 3 calendar days after the start")


def validate_tender_period(data, period):
    if data.get("enquiryPeriod") and data.get("enquiryPeriod").endDate:
        if period.startDate:
            if period.startDate < data.get("enquiryPeriod").endDate:
                raise ValidationError("period should begin after enquiryPeriod")
        else:
            period.startDate = data.get("enquiryPeriod").endDate  # default tenderPeriod.startDate

    active_validation = get_first_revision_date(data, default=get_now()) > RELEASE_2020_04_19
    if active_validation and period and period.startDate and period.endDate:
        validate_tender_period_duration(data, period, TENDERING_DURATION)


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[REQUEST_FOR_PROPOSAL], default=REQUEST_FOR_PROPOSAL)
    enquiryPeriod = ModelType(StartedEnquiryPeriodEndRequired, required=True)

    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )

    def validate_enquiryPeriod(self, data, period):
        validate_enquiry_period(data, period)

    def validate_tenderPeriod(self, data, period):
        validate_tender_period(data, period)


class PatchTender(BasePatchTender):
    enquiryPeriod = ModelType(EnquiryPeriodEndRequired)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )


class PatchActiveTender(Model):
    tenderPeriod = ModelType(PeriodEndRequired)
    guarantee = ModelType(Guarantee)
    value = ModelType(Value)
    milestones = ListType(
        ModelType(Milestone, required=True),
        validators=[validate_items_uniq],
    )
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    documents = ListType(ModelType(PostDocument, required=True))
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    mainProcurementCategory = StringType(choices=["goods", "services", "works"])


class PatchDraftTender(PatchTender):
    inspector = ModelType(Organization)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[REQUEST_FOR_PROPOSAL], required=True)
    enquiryPeriod = ModelType(EnquiryPeriodEndRequired, required=True)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )

    def validate_enquiryPeriod(self, data, period):
        validate_enquiry_period(data, period)

    def validate_tenderPeriod(self, data, period):
        validate_tender_period(data, period)
