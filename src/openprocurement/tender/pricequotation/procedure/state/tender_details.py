from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.context import get_request_now
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.pricequotation.constants import WORKING_DAYS_CONFIG
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class TenderDetailsState(TenderDetailsMixing, PriceQuotationTenderState):
    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    should_validate_pre_selection_agreement = True
    should_validate_cpv_prefix = False
    should_validate_notice_doc_required = True
    procurement_kinds_not_required_sign = ("other",)
    agreement_field = "agreement"
    should_validate_related_lot_in_items = False
    agreement_allowed_types = [ELECTRONIC_CATALOGUE_TYPE]
    agreement_without_items_forbidden = False
    agreement_min_active_contracts = 1
    should_match_agreement_procuring_entity = False
    should_validate_profiles_agreement_id = True
    items_profile_required = True

    contract_template_required = True
    contract_template_name_patch_statuses = ("draft",)

    working_days_config = WORKING_DAYS_CONFIG

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

        if before == "draft" and after == "active.tendering":
            data["tenderPeriod"]["startDate"] = get_request_now().isoformat()

        if after in self.unsuccessful_statuses:
            self.set_contracts_cancelled(after)

    def validate_tender_period_extension(self, tender):
        pass

    @staticmethod
    def set_bids_invalidation_date(tender):
        pass

    def invalidate_bids_data(self, tender):
        pass
