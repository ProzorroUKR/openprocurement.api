from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.open.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenTenderDetailsState(TenderDetailsMixing, OpenTenderState):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = False
    should_validate_notice_doc_required = True
    contract_template_required = True

    contract_template_name_patch_statuses = ("draft", "active.tendering")

    working_days_config = WORKING_DAYS_CONFIG

    def on_patch(self, before, after):
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

        self.validate_items_classification_prefix_unchanged(before, after)
