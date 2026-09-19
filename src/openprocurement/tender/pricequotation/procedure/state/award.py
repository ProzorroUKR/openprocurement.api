from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class AwardState(AwardStateMixing, PriceQuotationTenderState):
    award_status_change_waits_for_milestone_due_date = False
    procurement_kinds_not_required_sign = ("other",)  # in case when signing award will be required in the future
