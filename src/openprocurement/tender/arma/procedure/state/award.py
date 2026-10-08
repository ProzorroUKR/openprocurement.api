from openprocurement.tender.arma.procedure.models.award import ARMAAward, ARMAPostAward
from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.award import AwardStateMixin


class ARMAAwardState(AwardStateMixin, ARMATenderState):
    post_data_model = ARMAPostAward
    data_model = ARMAAward
    award_class = ARMAAward

    items_delivery_required: bool = True
