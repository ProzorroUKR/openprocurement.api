from openprocurement.tender.core.procedure.state.award import AwardStateMixin
from openprocurement.tender.esco.procedure.models.award import ESCOAward, ESCOPostAward
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOAwardState(AwardStateMixin, ESCOTenderState):
    post_data_model = ESCOPostAward
    data_model = ESCOAward

    items_unit_required: bool = False
    items_quantity_required: bool = False
