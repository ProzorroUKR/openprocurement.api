from openprocurement.api.auth import AccreditationLevel
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.tender.core.constants import AWARD_CRITERIA_LOWEST_COST
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixin,
)
from openprocurement.tender.pricequotation.constants import PQ_WORKING_DAYS_CONFIG
from openprocurement.tender.pricequotation.procedure.models.tender import PQPatchTender, PQPostTender, PQTender
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PQTenderState,
)


class PQTenderDetailsState(TenderDetailsMixin, PQTenderState):
    post_data_model = PQPostTender
    patch_data_model = PQPatchTender
    data_model = PQTender

    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    tender_patch_allowed_statuses = ("draft",)
    status_change_with_lot_cancellation_pending_check = False
    items_related_lot_error = "Rogue field."
    milestones_required = False
    items_classification_id_check = False
    award_criteria_choices = (AWARD_CRITERIA_LOWEST_COST,)
    patch_status_choices = ("draft", "active.tendering")
    cpv_prefix_check = False
    procurement_kinds_not_required_sign = ("other",)
    agreement_field = "agreement"
    related_lot_in_items_check = False
    agreement_allowed_types = [ELECTRONIC_CATALOGUE_TYPE]
    agreement_min_active_contracts = 1
    agreement_procuring_entity_match_check = False
    profiles_agreement_id_check = True
    items_profile_required = True
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft",)
    working_days_config = PQ_WORKING_DAYS_CONFIG
    tender_period_start_on_activation = True
    tender_period_extension_check = False
    bids_invalidation_enabled = False
    items_classification_prefix_change_check = False
    items_delivery_required = False
