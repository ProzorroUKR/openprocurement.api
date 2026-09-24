from openprocurement.tender.core.procedure.state.award import AwardStateMixin
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenAwardState(AwardStateMixin, OpenTenderState):
    items_delivery_required: bool = True
