from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsState,
)
from openprocurement.tender.openuadefense.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS,
)


class DefenseTenderDetailsState(OpenUATenderDetailsState):
    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    should_validate_notice_doc_required = False
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft", "active.tendering")

    tender_period_working_days = True
    tender_period_extra_working_days = True
    enquiry_period_working_days = True
    tender_complain_regulation_working_days = True

    calendar = WORKING_DAYS

    def validate_required_criteria(self, before, after):
        pass


class AboveThresholdUADefenseTenderDetailsState(DefenseTenderDetailsState):
    should_validate_related_lot_in_items = False
