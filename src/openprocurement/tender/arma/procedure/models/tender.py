from schematics.types import BaseType, StringType
from schematics.types.compound import ListType, ModelType

from openprocurement.api.validation import validate_uniq_id
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.models.item import Item
from openprocurement.tender.arma.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.constants import AWARD_CRITERIA_RATED_CRITERIA
from openprocurement.tender.core.procedure.models.item import validate_classification_id
from openprocurement.tender.core.procedure.models.milestone import (
    Milestone,
    validate_milestones_lot,
)
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriod,
    PeriodStartEndRequired,
    PostPeriodStartEndRequired,
)
from openprocurement.tender.core.procedure.models.tender import (
    PatchTender as BasePatchTender,
)
from openprocurement.tender.core.procedure.models.tender import (
    PostTender as BasePostTender,
)
from openprocurement.tender.core.procedure.models.tender import Tender as BaseTender


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[COMPLEX_ASSET_ARMA], default=COMPLEX_ASSET_ARMA)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=["draft"], default="draft")
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PostPeriodStartEndRequired, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    milestones = ListType(ModelType(Milestone, required=False), validators=[validate_uniq_id])
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA], default=AWARD_CRITERIA_RATED_CRITERIA)
    contractTemplateName = None
    features = None

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)


PostTender._fields.pop("contractTemplateName", None)
PostTender._fields.pop("features", None)


class PatchTender(BasePatchTender):
    procuringEntity = ModelType(ProcuringEntity)
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
        ],
    )
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodStartEndRequired)
    items = ListType(
        ModelType(Item, required=True),
        validators=[validate_uniq_id, validate_classification_id],
    )
    milestones = ListType(ModelType(Milestone, required=False), validators=[validate_uniq_id])
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA], default=AWARD_CRITERIA_RATED_CRITERIA)
    contractTemplateName = None
    features = None


PatchTender._fields.pop("contractTemplateName", None)
PatchTender._fields.pop("features", None)


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[COMPLEX_ASSET_ARMA], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
    )
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    milestones = ListType(ModelType(Milestone, required=False), validators=[validate_uniq_id])
    complaintPeriod = BaseType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA], default=AWARD_CRITERIA_RATED_CRITERIA)
    contractTemplateName = None
    features = None

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)


Tender._fields.pop("contractTemplateName", None)
Tender._fields.pop("features", None)
