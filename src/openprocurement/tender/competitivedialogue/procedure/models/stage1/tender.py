from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ListType, ModelType

from openprocurement.api.constants import MILESTONES_VALIDATION_FROM
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.validation import validate_features_uniq
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE,
    CD_UA_TYPE,
    FEATURES_MAX_SUM,
)
from openprocurement.tender.competitivedialogue.procedure.models.feature import Feature
from openprocurement.tender.core.procedure.models.feature import validate_related_items
from openprocurement.tender.core.procedure.models.item import validate_items_uniq
from openprocurement.tender.core.procedure.models.lot import (
    Lot,
    PatchTenderLot,
    PostTenderLot,
    validate_lots_uniq,
)
from openprocurement.tender.core.procedure.models.milestone import (
    TenderMilestoneTypes,
    validate_milestones_lot,
)
from openprocurement.tender.core.procedure.utils import (
    tender_created_after,
    validate_features_custom_weight,
)
from openprocurement.tender.openeu.procedure.models.item import Item
from openprocurement.tender.openeu.procedure.models.tender import (
    PatchTender as BasePatchTender,
)
from openprocurement.tender.openeu.procedure.models.tender import (
    PostTender as BasePostTender,
)
from openprocurement.tender.openeu.procedure.models.tender import Tender as BaseTender
from openprocurement.tender.openua.procedure.models.item import Item as UAItem
from openprocurement.tender.openua.procedure.models.organization import (
    ProcuringEntity as UAProcuringEntity,
)


class BotPatchTender(Model):  # "competitive_dialogue": whitelist("status", "stage2TenderID"),
    id = StringType()
    stage2TenderID = StringType()  # TODO: move to a distinct endpoint
    status = StringType(choices=["complete"])


# === EU


class PostEUTender(BasePostTender):
    procurementMethodType = StringType(choices=[CD_EU_TYPE], default=CD_EU_TYPE)
    mainProcurementCategory = StringType(choices=["services", "works"])
    status = StringType(choices=["draft"], default="draft")
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq],
    )
    lots = ListType(ModelType(PostTenderLot, required=True), validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, FEATURES_MAX_SUM)

    def validate_milestones(self, data, value):
        if tender_created_after(MILESTONES_VALIDATION_FROM):
            if value is None or len(value) < 1:
                raise ValidationError("Tender should contain at least one milestone")
        for milestone in value:
            if milestone.type == TenderMilestoneTypes.DELIVERY.value:
                raise ValidationError(f"Forbidden to add milestone with type {TenderMilestoneTypes.DELIVERY.value}")
        validate_milestones_lot(data, value)


class PatchEUTender(BasePatchTender):
    procurementMethodType = StringType(choices=[CD_EU_TYPE])
    mainProcurementCategory = StringType(choices=["services", "works"])
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification.stand-still",
            "active.stage2.waiting",
        ],
    )
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_items_uniq],
    )
    lots = ListType(ModelType(PatchTenderLot, required=True), validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])


class EUTender(BaseTender):
    procurementMethodType = StringType(choices=[CD_EU_TYPE], required=True)
    mainProcurementCategory = StringType(choices=["services", "works"])
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
            "active.stage2.pending",
            "active.stage2.waiting",
        ],
        required=True,
    )
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq],
    )
    lots = ListType(ModelType(Lot, required=True), validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])

    stage2TenderID = StringType()  # TODO: move to a distinct endpoint

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, FEATURES_MAX_SUM)

    def validate_milestones(self, data, value):
        if tender_created_after(MILESTONES_VALIDATION_FROM):
            if value is None or len(value) < 1:
                raise ValidationError("Tender should contain at least one milestone")
        for milestone in value:
            if milestone.type == TenderMilestoneTypes.DELIVERY.value:
                raise ValidationError(f"Forbidden to add milestone with type {TenderMilestoneTypes.DELIVERY.value}")
        validate_milestones_lot(data, value)


# === UA


class PostUATender(PostEUTender):
    procurementMethodType = StringType(choices=[CD_UA_TYPE], default=CD_UA_TYPE)
    procuringEntity = ModelType(UAProcuringEntity, required=True)
    items = ListType(
        ModelType(UAItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq],
    )


class PatchUATender(PatchEUTender):
    procurementMethodType = StringType(choices=[CD_UA_TYPE])
    procuringEntity = ModelType(UAProcuringEntity)
    items = ListType(
        ModelType(UAItem, required=True),
        min_size=1,
        validators=[validate_items_uniq],
    )


class UATender(EUTender):
    procurementMethodType = StringType(choices=[CD_UA_TYPE], required=True)
    procuringEntity = ModelType(UAProcuringEntity, required=True)
    items = ListType(
        ModelType(UAItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq],
    )
