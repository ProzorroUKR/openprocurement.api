from openprocurement.api.auth import ACCR_1, ACCR_2, ACCR_5
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.requestforproposal.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)
from openprocurement.tender.requestforproposal.procedure.models.tender import (
    PatchActiveTender,
    PatchDraftTender,
    PatchTender,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalTenderDetailsMixing(TenderDetailsMixing):
    tender_create_accreditations = (ACCR_1, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_2,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = False
    should_validate_notice_doc_required = True
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft", "active.enquiries", "active.tendering")

    working_days_config = WORKING_DAYS_CONFIG

    def get_patch_data_model(self):
        tender = get_tender()
        if tender.get("status", "") == "active.tendering":
            return PatchActiveTender
        elif tender.get("status", "") in ("draft", "active.enquiries"):
            return PatchDraftTender
        return PatchTender


class RequestForProposalTenderDetailsState(RequestForProposalTenderDetailsMixing, RequestForProposalTenderState):
    pass
