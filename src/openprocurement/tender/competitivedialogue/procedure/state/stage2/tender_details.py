from openprocurement.api.auth import AccreditationLevel, AccreditationPermission
from openprocurement.tender.competitivedialogue.constants import (
    FEATURES_MAX_SUM,
    STAGE_2_EU_WORKING_DAYS_CONFIG,
    STAGE_2_UA_WORKING_DAYS_CONFIG,
)
from openprocurement.tender.openeu.procedure.state.tender_details import (
    OpenEUTenderDetailsState,
)


class CDEUStage2TenderDetailsState(OpenEUTenderDetailsState):
    should_validate_items_zero_quantity = False
    guarantee_criterion_check_skipped_for_administrator = True
    features_max_weight = FEATURES_MAX_SUM
    items_unit_required = False
    items_quantity_required = False
    milestones_required = False
    milestones_delivery_financing_required_on_post = False
    items_classification_id_check = False
    main_procurement_category_required = False
    award_criteria_lcc_features_check = False
    tender_create_accreditations = (AccreditationPermission.ACCR_COMPETITIVE,)
    tender_central_accreditations = (AccreditationPermission.ACCR_COMPETITIVE, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)
    tender_transfer_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)

    should_validate_notice_doc_required = False
    should_validate_related_lot_in_items = False
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft",)

    working_days_config = STAGE_2_EU_WORKING_DAYS_CONFIG
    watch_value_meta_changes_enabled = False
    item_profile_category_check_on_post = False
    # the stage 2 tender is validated while the stage 1 tender (hasAuction=False) is the request context
    minimal_step_regardless_of_auction = True


class CDUAStage2TenderDetailsState(CDEUStage2TenderDetailsState):
    required_multilingual_fields = {}
    procuring_entity_available_language_default = None
    tender_create_accreditations = (AccreditationPermission.ACCR_COMPETITIVE,)
    tender_central_accreditations = (AccreditationPermission.ACCR_COMPETITIVE, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)
    tender_transfer_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)

    contract_template_required = False
    contract_template_name_patch_statuses = ("draft",)

    working_days_config = STAGE_2_UA_WORKING_DAYS_CONFIG
