from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.models.value import EstimatedValue
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.api.validation import validate_uniq_id
from openprocurement.tender.core.procedure.models.document import PostDocument
from openprocurement.tender.core.procedure.models.item import TechFeatureItem as Item
from openprocurement.tender.core.procedure.models.item import validate_classification_id
from openprocurement.tender.core.procedure.models.lot import PatchTenderLot
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
from openprocurement.tender.core.procedure.models.tender_base import (
    MAIN_PROCUREMENT_CATEGORY_CHOICES,
)
from openprocurement.tender.core.procedure.models.value import BasicValue
from openprocurement.tender.requestforproposal.constants import REQUEST_FOR_PROPOSAL


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[REQUEST_FOR_PROPOSAL], default=REQUEST_FOR_PROPOSAL)
    enquiryPeriod = ModelType(StartedEnquiryPeriodEndRequired, required=True)

    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )


class PatchTender(BasePatchTender):
    enquiryPeriod = ModelType(EnquiryPeriodEndRequired)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )


class PatchActiveTender(Model):
    tenderPeriod = ModelType(PeriodEndRequired)
    guarantee = ModelType(BasicValue)
    value = ModelType(EstimatedValue)
    milestones = ListType(
        ModelType(Milestone, required=True),
        validators=[validate_uniq_id],
    )
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    documents = ListType(ModelType(PostDocument, required=True))
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    mainProcurementCategory = StringType(choices=MAIN_PROCUREMENT_CATEGORY_CHOICES)
    lots = ListType(ModelType(PatchTenderLot, required=True), validators=[validate_uniq_id])
    contractTemplateName = StringType()


class PatchDraftTender(PatchTender):
    inspector = ModelType(Organization)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[REQUEST_FOR_PROPOSAL], required=True)
    enquiryPeriod = ModelType(EnquiryPeriodEndRequired, required=True)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
