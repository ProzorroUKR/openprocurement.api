from openprocurement.tender.core.procedure.state.award import AwardStateMixin
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUAAwardState(AwardStateMixin, OpenUATenderState):
    items_delivery_required: bool = True
