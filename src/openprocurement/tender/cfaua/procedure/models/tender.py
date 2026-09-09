from schematics.types import IntType, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import IsoDurationType, ListType
from openprocurement.api.validation import validate_uniq_code, validate_uniq_id
from openprocurement.tender.cfaua.constants import CFA_UA
from openprocurement.tender.cfaua.constants import LOTS_MAX_SIZE as CFA_LOTS_MAX_SIZE
from openprocurement.tender.cfaua.constants import LOTS_MIN_SIZE as CFA_LOTS_MIN_SIZE
from openprocurement.tender.cfaua.procedure.models.feature import CFAFeature
from openprocurement.tender.core.procedure.models.lot import Lot, PatchTenderLot, PostTenderLot
from openprocurement.tender.core.procedure.models.tender import (
    PatchTender,
    PostTender,
    Tender,
    validate_cfa_features,
    validate_cfa_max_agreement_duration_period,
    validate_cfa_max_awards_number,
)


class CFAPostTender(PostTender):
    procurementMethodType = StringType(choices=[CFA_UA], default=CFA_UA)

    agreementDuration = IsoDurationType(required=True, validators=[validate_cfa_max_agreement_duration_period])
    maxAwardsCount = IntType(required=True, validators=[validate_cfa_max_awards_number])

    lots = ListType(
        ModelType(PostTenderLot, required=True),
        required=True,
        min_size=CFA_LOTS_MIN_SIZE,
        max_size=CFA_LOTS_MAX_SIZE,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFAFeature, required=True), validators=[validate_uniq_code])

    def validate_features(self, data, features):
        validate_cfa_features(data, features)


class CFAPatchTender(PatchTender):
    procurementMethodType = StringType(choices=[CFA_UA])
    agreementDuration = IsoDurationType(validators=[validate_cfa_max_agreement_duration_period])
    maxAwardsCount = IntType(validators=[validate_cfa_max_awards_number])

    lots = ListType(
        ModelType(PatchTenderLot, required=True),
        min_size=CFA_LOTS_MIN_SIZE,
        max_size=CFA_LOTS_MAX_SIZE,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFAFeature, required=True), validators=[validate_uniq_code])


class CFATender(Tender):
    procurementMethodType = StringType(choices=[CFA_UA], required=True)
    agreementDuration = IsoDurationType(required=True, validators=[validate_cfa_max_agreement_duration_period])
    maxAwardsCount = IntType(required=True, validators=[validate_cfa_max_awards_number])

    lots = ListType(
        ModelType(Lot, required=True),
        required=True,
        min_size=CFA_LOTS_MIN_SIZE,
        max_size=CFA_LOTS_MAX_SIZE,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFAFeature, required=True), validators=[validate_uniq_code])

    auctionPeriod = ModelType(Period)

    def validate_features(self, data, features):
        validate_cfa_features(data, features)
