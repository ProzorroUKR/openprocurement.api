from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.openua.constants import (
    ENQUIRY_PERIOD_TIME,
    TENDERING_EXTRA_PERIOD,
)
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsMixing,
)


class OpenEUTenderDetailsMixing(OpenUATenderDetailsMixing):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)
    tendering_period_extra = TENDERING_EXTRA_PERIOD
    enquiry_period_timedelta = -ENQUIRY_PERIOD_TIME
    tender_period_working_day = False
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.tendering")

    def on_patch(self, before, after):
        self.validate_items_classification_prefix_unchanged(before, after)

        super().on_patch(before, after)  # TenderDetailsMixing.on_patch


class OpenEUTenderDetailsState(OpenEUTenderDetailsMixing, BaseOpenEUTenderState):
    pass
