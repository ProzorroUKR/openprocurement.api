from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.open.constants import TENDERING_EXTRA_PERIOD
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenTenderDetailsState(TenderDetailsMixing, OpenTenderState):
    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)
    tender_period_extra = TENDERING_EXTRA_PERIOD
    should_validate_notice_doc_required = True
    contract_template_required = True

    contract_template_name_patch_statuses = ("draft", "active.tendering")

    tender_period_working_days = False
    enquiry_period_working_days = False
    clarification_period_working_days = False
    tender_period_extra_working_days = False

    def on_patch(self, before, after):
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

        self.validate_items_classification_prefix_unchanged(before, after)
