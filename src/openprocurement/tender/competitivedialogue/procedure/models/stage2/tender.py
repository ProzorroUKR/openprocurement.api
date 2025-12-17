from schematics.types import StringType
from schematics.types.compound import ListType, ModelType
from schematics.types.serializable import serializable

from openprocurement.api.validation import validate_uniq_code, validate_uniq_id
from openprocurement.tender.competitivedialogue.constants import (
    FEATURES_MAX_SUM,
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.models.feature import Feature
from openprocurement.tender.competitivedialogue.procedure.models.stage2.firms import (
    Firms,
    validate_shortlisted_firm_ids,
)
from openprocurement.tender.competitivedialogue.procedure.models.stage2.item import (
    EUItem,
    UAItem,
)
from openprocurement.tender.core.procedure.models.criterion import (
    Criterion,
    validate_criteria_requirement_uniq,
)
from openprocurement.tender.core.procedure.models.feature import validate_related_items
from openprocurement.tender.core.procedure.models.period import (
    PostPeriodStartEndRequired,
)
from openprocurement.tender.core.procedure.utils import validate_features_custom_weight
from openprocurement.tender.core.procedure.validation import validate_object_id_uniq
from openprocurement.tender.openeu.procedure.models.tender import (
    PatchTender as BasePatchTender,
)
from openprocurement.tender.openeu.procedure.models.tender import (
    PostTender as BasePostTender,
)
from openprocurement.tender.openeu.procedure.models.tender import Tender as BaseTender
from openprocurement.tender.openua.procedure.models.tender import (
    PatchTender as UABasePatchTender,
)
from openprocurement.tender.openua.procedure.models.tender import (
    PostTender as UABasePostTender,
)
from openprocurement.tender.openua.procedure.models.tender import Tender as UABaseTender


# === EU
class PostEUTender(BasePostTender):
    procurementMethodType = StringType(choices=[STAGE_2_EU_TYPE], default=STAGE_2_EU_TYPE)

    owner = StringType(required=True)
    tenderID = StringType()  # in tests it's not passed
    dialogue_token = StringType(required=True)
    dialogueID = StringType()
    shortlistedFirms = ListType(ModelType(Firms, required=True), min_size=3, required=True)

    items = ListType(
        ModelType(EUItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])
    tenderPeriod = ModelType(PostPeriodStartEndRequired)

    criteria = ListType(
        ModelType(Criterion, required=True),
        validators=[validate_object_id_uniq, validate_criteria_requirement_uniq],
    )

    @serializable(serialized_name="tenderID")
    def serialize_tender_id(self):
        return self.tenderID  # just return what have been passed

    def validate_awardCriteria(self, data, value):
        return  # to deactivate validation of awardCriteria from parent class

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, FEATURES_MAX_SUM)

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        pass

    def validate_shortlistedFirms(self, data, value):
        validate_shortlisted_firm_ids(data, value)


class PatchEUTender(BasePatchTender):
    procurementMethodType = StringType(choices=[STAGE_2_EU_TYPE])

    items = ListType(
        ModelType(EUItem, required=True),
        min_size=1,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
        ]
    )


class EUTender(BaseTender):
    procurementMethodType = StringType(choices=[STAGE_2_EU_TYPE], required=True)

    dialogue_token = StringType(required=True)
    dialogueID = StringType()

    items = ListType(
        ModelType(EUItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])
    shortlistedFirms = ListType(ModelType(Firms, required=True), min_size=3, required=True)
    status = StringType(
        choices=[
            "draft",
            "draft.stage2",
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

    def validate_awardCriteria(self, data, value):
        # for deactivate validation of awardCriteria from parent class
        return

    def validate_shortlistedFirms(self, data, value):
        validate_shortlisted_firm_ids(data, value)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, FEATURES_MAX_SUM)

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        pass


# === UA


class PostUATender(UABasePostTender):
    procurementMethodType = StringType(choices=[STAGE_2_UA_TYPE], default=STAGE_2_UA_TYPE)

    owner = StringType(required=True)
    tenderID = StringType()  # in tests it's not passed
    dialogue_token = StringType(required=True)
    dialogueID = StringType()
    shortlistedFirms = ListType(ModelType(Firms, required=True), min_size=3, required=True)

    items = ListType(
        ModelType(UAItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])
    tenderPeriod = ModelType(PostPeriodStartEndRequired)

    criteria = ListType(
        ModelType(Criterion, required=True),
        validators=[validate_object_id_uniq, validate_criteria_requirement_uniq],
    )

    @serializable(serialized_name="tenderID")
    def serialize_tender_id(self):
        return self.tenderID  # just return what have been passed

    def validate_awardCriteria(self, data, value):
        # for deactivate validation of awardCriteria from parent class
        return

    def validate_shortlistedFirms(self, data, value):
        validate_shortlisted_firm_ids(data, value)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, FEATURES_MAX_SUM)

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        pass


class PatchUATender(UABasePatchTender):
    procurementMethodType = StringType(choices=[STAGE_2_UA_TYPE])

    items = ListType(
        ModelType(UAItem, required=True),
        min_size=1,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
        ]
    )


class UATender(UABaseTender):
    procurementMethodType = StringType(choices=[STAGE_2_UA_TYPE], required=True)

    dialogue_token = StringType(required=True)
    dialogueID = StringType()
    shortlistedFirms = ListType(ModelType(Firms, required=True), min_size=3, required=True)

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
            "draft.stage2",
        ],
    )

    items = ListType(
        ModelType(UAItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])

    def validate_awardCriteria(self, data, value):
        # for deactivate validation of awardCriteria from parent class
        return

    def validate_shortlistedFirms(self, data, value):
        validate_shortlisted_firm_ids(data, value)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, FEATURES_MAX_SUM)

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        pass
