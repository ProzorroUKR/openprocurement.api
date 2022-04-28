from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState
from openprocurement.api.utils import raise_operation_error


class ReportingTenderDetailsState(TenderDetailsMixing, NegotiationTenderState):
    pass


class NegotiationTenderDetailsState(TenderDetailsMixing, NegotiationTenderState):
    def on_patch(self, before, after):
        if before.get("awards"):
            raise_operation_error(
                get_request(),
                "Can't update tender when there is at least one award.",
            )
        super().on_patch(before, after)
