from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.requestforproposal.constants import TENDERING_EXTRA_PERIOD
from openprocurement.tender.requestforproposal.procedure.models.tender import (
    PatchActiveTender,
    PatchDraftTender,
    PatchTender,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalTenderDetailsMixing(TenderDetailsMixing):
    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    tendering_period_extra_working_days = False
    tendering_period_extra = TENDERING_EXTRA_PERIOD
    should_validate_notice_doc_required = False
    should_validate_evaluation_reports_doc_required = False
    enquiry_before_tendering = True
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft", "active.enquiries", "active.tendering")
    qualification_complain_duration_working_days = True
    clarification_period_working_day = False
    should_validate_items_classifications_prefix = False

    def get_patch_data_model(self):
        tender = get_tender()
        if tender.get("status", "") == "active.tendering":
            return PatchActiveTender
        elif tender.get("status", "") in ("draft", "active.enquiries"):
            return PatchDraftTender
        return PatchTender

    def on_patch(self, before, after):
        super().on_patch(before, after)
        if after["status"] != "draft" and before["status"] == "draft":
            # even without document `notice` it is required to set `noticePublicationDate` for RFP (CS-19667)
            after["noticePublicationDate"] = get_request_now().isoformat()


class RequestForProposalTenderDetailsState(RequestForProposalTenderDetailsMixing, RequestForProposalTenderState):
    pass
