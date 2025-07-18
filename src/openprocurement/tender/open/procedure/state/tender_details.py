from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.open.constants import (
    ENQUIRY_PERIOD_TIME,
    TENDERING_EXTRA_PERIOD,
)
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenTenderDetailsState(TenderDetailsMixing, OpenTenderState):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)
    tender_period_working_day = False
    clarification_period_working_day = False
    tendering_period_extra = TENDERING_EXTRA_PERIOD
    tendering_period_extra_working_days = False
    enquiry_period_timedelta = -ENQUIRY_PERIOD_TIME
    should_validate_notice_doc_required = True
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.tendering")

    def on_patch(self, before, after):
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

        self.validate_items_classification_prefix_unchanged(before, after)
