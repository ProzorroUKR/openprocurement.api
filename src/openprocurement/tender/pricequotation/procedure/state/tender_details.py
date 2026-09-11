from openprocurement.api.auth import AccreditationLevel
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.tender.core.constants import AWARD_CRITERIA_LOWEST_COST
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.pricequotation.constants import WORKING_DAYS_CONFIG
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class TenderDetailsState(TenderDetailsMixing, PriceQuotationTenderState):
    tender_period_start_date_required = True
    items_related_lot_error = "Rogue field."
    milestones_required = False
    items_classification_id_check = False
    award_criteria_choices = (AWARD_CRITERIA_LOWEST_COST,)
    award_criteria_default = AWARD_CRITERIA_LOWEST_COST
    patch_status_choices = ("draft", "active.tendering")
    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    should_validate_pre_selection_agreement = True
    should_validate_cpv_prefix = False
    should_validate_notice_doc_required = True
    should_validate_vat_not_included = True
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
    tender_period_start_on_activation = True
    tender_period_extension_check = False
    bids_invalidation_enabled = False
