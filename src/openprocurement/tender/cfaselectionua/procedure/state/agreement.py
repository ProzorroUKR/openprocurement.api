from openprocurement.tender.core.procedure.context import get_now, get_request, get_tender
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS


class AgreementStateMixing:

    def validate_agreement_on_patch(self, *_):
        pass

    def agreement_on_patch(self, before, award):
        request = get_request()
        tender = get_tender()
        tender_status = tender["status"]
        if tender_status != "draft.pending":
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} agreement in current ({tender_status}) tender status"
            )


# example use
class AgreementState(AgreementStateMixing, TenderState):
    pass
