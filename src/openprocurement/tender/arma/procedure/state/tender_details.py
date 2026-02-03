from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.arma.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)
from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsMixing,
)


class TenderDetailsMixing(OpenUATenderDetailsMixing):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    contract_template_name_patch_statuses = ("draft", "active.tendering")
    contract_template_required = False

    working_days_config = WORKING_DAYS_CONFIG

    def on_patch(self, before, after):
        self.validate_items_classification_prefix_unchanged(before, after)
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch


class TenderDetailsState(TenderDetailsMixing, TenderState):
    pass
