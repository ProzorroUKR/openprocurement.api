from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.state.award import AwardStateMixin


class COAwardState(AwardStateMixin, COTenderState):
    items_delivery_required: bool = True
    award_eligible_rules_by_creation_date = True
