from openprocurement.api.auth import AccreditationLevel, AccreditationPermission
from openprocurement.api.constants_env import (
    REQUIRED_DELIVERY_AND_FINANCING_MILESTONES_VALIDATION_FROM,
)
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.competitivedialogue.constants import (
    FEATURES_MAX_SUM,
    STAGE_2_EU_DEFAULT_CONFIG,
    STAGE_2_EU_WORKING_DAYS_CONFIG,
    STAGE_2_UA_DEFAULT_CONFIG,
    STAGE_2_UA_WORKING_DAYS_CONFIG,
)
from openprocurement.tender.competitivedialogue.procedure.models.tender import (
    CDStage2EUPatchTender,
    CDStage2EUPostTender,
    CDStage2EUTender,
    CDStage2UAPatchTender,
    CDStage2UAPostTender,
    CDStage2UATender,
)
from openprocurement.tender.core.constants import EU_REQUIRED_MULTILINGUAL_FIELDS
from openprocurement.tender.core.procedure.models.auction import DecimalAuctionLotResults, DecimalAuctionResults
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.openua.constants import TENDERING_EXTRA_PERIOD


class CDEUStage2TenderDetailsState(TenderDetailsMixing, TenderState):
    auction_results_model = DecimalAuctionResults
    auction_lot_results_model = DecimalAuctionLotResults
    award_class = Award
    post_data_model = CDStage2EUPostTender
    patch_data_model = CDStage2EUPatchTender
    data_model = CDStage2EUTender

    tender_create_accreditation_check = False
    tender_create_accreditations = (AccreditationPermission.ACCR_COMPETITIVE,)
    tender_central_accreditations = (AccreditationPermission.ACCR_COMPETITIVE, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)
    tender_transfer_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)

    patch_status_choices = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
    items_classification_prefix_change_check = True
    required_multilingual_fields = EU_REQUIRED_MULTILINGUAL_FIELDS
    procuring_entity_available_language_default = "uk"
    tender_period_extra = TENDERING_EXTRA_PERIOD
    should_validate_vat_not_included = True
    items_delivery_required = True
    tender_period_start_date_required = True
    active_bid_statuses = ("active", "pending")
    tender_config_default = STAGE_2_EU_DEFAULT_CONFIG
    tender_patch_owner_check_exempt_roles = ("Administrator", "admins")
    tender_patch_allowed_statuses = (
        "draft.stage2",
        "active.tendering",
        "active.pre-qualification",  # state class only allows status change (pre-qualification.stand-still)
        "active.pre-qualification.stand-still",
    )
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
    should_validate_notice_doc_required = False
    should_validate_related_lot_in_items = False
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft",)
    working_days_config = STAGE_2_EU_WORKING_DAYS_CONFIG
    watch_value_meta_changes_enabled = False
    item_profile_category_check_on_post = False
    # the stage 2 tender is validated while the stage 1 tender (hasAuction=False) is the request context
    minimal_step_regardless_of_auction = True

    def validate_patch_request(self):
        role = self.request.authenticated_role
        if role not in self.tender_patch_owner_check_exempt_roles:
            self.validate_item_owner("tender")
        if role != "Administrator":
            self.validate_tender_patch_allowed()
        self.validate_patch_input_data(self.get_patch_data_model())
        if role != "Administrator":
            self.validate_patch_fields_allowed()
        self.validate_patch_data_simple(self.get_data_model(), "tender")

    def validate_patch_fields_allowed(self):
        changes = self.request.validated["data"]
        tender = self.request.validated["tender"]

        status = tender["status"]
        patchable_fields_by_status = {
            "draft.stage2": {"tenderPeriod", "complaintPeriod", "items", "mainProcurementCategory", "status"},
            "active.tendering": {"tenderPeriod", "complaintPeriod", "items"},
        }
        if tender_created_after(REQUIRED_DELIVERY_AND_FINANCING_MILESTONES_VALIDATION_FROM):
            patchable_fields_by_status["draft.stage2"].add("milestones")

        if status in patchable_fields_by_status:
            for f in changes:
                if f not in patchable_fields_by_status[status] and tender.get(f) != changes[f]:
                    raise_operation_error(
                        self.request,
                        "Field change's not allowed",
                        location="body",
                        name=f,
                        status=422,
                    )

            items = changes.get("items")
            if items:
                before_items = tender["items"]
                if len(items) != len(before_items):
                    raise_operation_error(
                        self.request,
                        "List size change's not allowed",
                        location="body",
                        name="items",
                    )

                item_public_fields = {"deliveryDate", "profile", "category"}
                for a, b in zip(items, before_items):
                    for f in a:
                        if f not in item_public_fields and a[f] != b.get(f):
                            raise_operation_error(
                                self.request,
                                "Field change's not allowed",
                                location="body",
                                name=f"items.{f}",
                                status=422,
                            )


class CDUAStage2TenderDetailsState(CDEUStage2TenderDetailsState):
    post_data_model = CDStage2UAPostTender
    patch_data_model = CDStage2UAPatchTender
    data_model = CDStage2UATender

    tender_create_accreditations = (AccreditationPermission.ACCR_COMPETITIVE,)
    tender_central_accreditations = (AccreditationPermission.ACCR_COMPETITIVE, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)
    tender_transfer_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)

    tender_config_default = STAGE_2_UA_DEFAULT_CONFIG
    required_multilingual_fields = {}
    procuring_entity_available_language_default = None
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft",)
    working_days_config = STAGE_2_UA_WORKING_DAYS_CONFIG
