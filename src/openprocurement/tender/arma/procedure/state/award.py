from openprocurement.tender.arma.procedure.models.award import ARMAAward, ARMAPostAward
from openprocurement.tender.arma.procedure.state.tender import (
    ComplexAssetTenderState,
    SimpleAssetTenderState,
)
from openprocurement.tender.core.procedure.state.award import AwardStateMixin


class ARMAAwardStateMixin(AwardStateMixin):
    award_post_data_model = ARMAPostAward
    award_data_model = ARMAAward
    award_class = ARMAAward

    items_delivery_required: bool = True


class ComplexAssetAwardState(ARMAAwardStateMixin, ComplexAssetTenderState):
    pass


class SimpleAssetAwardState(ARMAAwardStateMixin, SimpleAssetTenderState):
    pass
