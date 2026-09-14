from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class AwardState(AwardStateMixing, PriceQuotationTenderState):
    procurement_kinds_not_required_sign = ("other",)  # in case when signing award will be required in the future
    award_unsuccessful_cancel_allowed = False
