from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.constants import WORKING_DAYS_WITH_WORKING_WEEKENDS
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.tender.core.constants import CALENDAR_DAYS_CONFIG, EU_REQUIRED_MULTILINGUAL_FIELDS
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.models.tender import PatchActiveTender, PatchDraftTender
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixin,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_EU_TENDERING_EXTRA_PERIOD,
    ABOVE_THRESHOLD_TENDERING_EXTRA_PERIOD,
    ABOVE_THRESHOLD_UA_DEFENSE_TENDERING_EXTRA_PERIOD,
    ABOVE_THRESHOLD_UA_DEFENSE_WORKING_DAYS,
    ABOVE_THRESHOLD_UA_DEFENSE_WORKING_DAYS_CONFIG,
    ABOVE_THRESHOLD_UA_TENDERING_EXTRA_PERIOD,
    ABOVE_THRESHOLD_WORKING_DAYS_CONFIG,
    BELOW_THRESHOLD_TENDERING_EXTRA_PERIOD,
    BELOW_THRESHOLD_WORKING_DAYS_CONFIG,
    COMPETITIVE_ORDERING_SHORT_WORKING_DAYS_CONFIG,
    COMPETITIVE_ORDERING_TENDERING_EXTRA_PERIOD,
    REQUEST_FOR_PROPOSAL_TENDERING_EXTRA_PERIOD,
    REQUEST_FOR_PROPOSAL_WORKING_DAYS_CONFIG,
    SIMPLE_DEFENSE_TENDERING_EXTRA_PERIOD,
    SIMPLE_DEFENSE_WORKING_DAYS_CONFIG,
)
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    BelowThresholdTenderState,
    COTenderState,
    RFPTenderState,
)


class AboveThresholdTenderDetailsState(TenderDetailsMixin, AboveThresholdTenderState):
    tender_period_extra = ABOVE_THRESHOLD_TENDERING_EXTRA_PERIOD
    contract_template_required = True
    working_days_config = ABOVE_THRESHOLD_WORKING_DAYS_CONFIG


class AboveThresholdUATenderDetailsMixin(TenderDetailsMixin):
    pass


class AboveThresholdUATenderDetailsState(AboveThresholdUATenderDetailsMixin, AboveThresholdUATenderState):
    tender_period_extra = ABOVE_THRESHOLD_UA_TENDERING_EXTRA_PERIOD
    contract_template_required = True


# fields that used to be `required=True` on openeu Organization/Identifier/ContactPoint/Item models
class AboveThresholdEUTenderDetailsMixin(TenderDetailsMixin):
    required_multilingual_fields = EU_REQUIRED_MULTILINGUAL_FIELDS
    procuring_entity_available_language_default = "uk"
    tender_period_extra = ABOVE_THRESHOLD_EU_TENDERING_EXTRA_PERIOD
    contract_template_required = True
    patch_status_choices = None


class AboveThresholdEUTenderDetailsState(AboveThresholdEUTenderDetailsMixin, AboveThresholdEUTenderState):
    patch_status_choices = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )


class DefenseTenderDetailsState(TenderDetailsMixin, TenderState):
    award_class = Award

    items_zero_quantity_check = False
    procuring_entity_available_language_default = "uk"
    tender_period_extra = ABOVE_THRESHOLD_UA_DEFENSE_TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = True
    notice_doc_required_check = False
    vat_not_included_check = False
    working_days_config = ABOVE_THRESHOLD_UA_DEFENSE_WORKING_DAYS_CONFIG
    calendar = ABOVE_THRESHOLD_UA_DEFENSE_WORKING_DAYS
    tender_patch_allowed_statuses = ("draft", "active.tendering", "active.pre-qualification")
    guarantee_criterion_check = False
    related_lot_in_items_check = False


class SimpleDefenseTenderDetailsState(TenderDetailsMixin, TenderState):
    award_class = Award

    items_zero_quantity_check = False
    procuring_entity_available_language_default = "uk"
    tender_period_extra_working_days = True
    notice_doc_required_check = False
    vat_not_included_check = False
    calendar = WORKING_DAYS_WITH_WORKING_WEEKENDS
    tender_period_extra = SIMPLE_DEFENSE_TENDERING_EXTRA_PERIOD
    contract_template_required = True
    working_days_config = SIMPLE_DEFENSE_WORKING_DAYS_CONFIG


class COTenderDetailsState(TenderDetailsMixin, COTenderState):
    agreement_procuring_entity_match_except_defense = True
    agreement_allowed_types = [DPS_TYPE]
    contract_template_required = True
    working_days_config = CALENDAR_DAYS_CONFIG


class COTenderConfigMixin:
    extra_config_schema_name = "competitiveOrdering"


class COShortTenderDetailsState(COTenderConfigMixin, COTenderDetailsState):
    extra_config_schema_name = "competitiveOrdering.short"
    tender_period_extra = COMPETITIVE_ORDERING_TENDERING_EXTRA_PERIOD
    working_days_config = COMPETITIVE_ORDERING_SHORT_WORKING_DAYS_CONFIG


class COLongTenderDetailsState(COTenderConfigMixin, COTenderDetailsState):
    extra_config_schema_name = "competitiveOrdering.long"
    agreement_with_items_forbidden = True
    tender_period_extra = COMPETITIVE_ORDERING_TENDERING_EXTRA_PERIOD


class BelowThresholdTenderDetailsMixin(TenderDetailsMixin):
    tender_patch_models_by_status = {
        "active.tendering": PatchActiveTender,
        "draft": PatchDraftTender,
        "active.enquiries": PatchDraftTender,
    }

    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    tender_patch_allowed_statuses = (
        "draft",
        "active.enquiries",
        "active.pre-qualification",  # state class only allows status change (pre-qualification.stand-still)
        "active.pre-qualification.stand-still",
    )
    tender_patch_allowed_statuses_for_funder = ("active.tendering",)
    status_change_with_lot_cancellation_pending_check = False
    lot_operation_allowed_tender_statuses = ("active.enquiries", "draft")
    tender_period_extra = BELOW_THRESHOLD_TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = True
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.enquiries")
    working_days_config = BELOW_THRESHOLD_WORKING_DAYS_CONFIG
    enquiry_period_required = True
    patch_status_choices = (
        "draft",
        "active.enquiries",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
    vat_not_included_check = False
    items_classification_prefix_change_check = False
    items_delivery_required = False
    tender_period_start_date_required = False
    criterion_allowed_tender_statuses = ["draft", "active.enquiries"]
    criterion_patch_exclusion_check = False
    requirement_change_allowed_tender_statuses = ("draft",)
    requirement_change_legacy_status = "active.enquiries"
    requirement_put_allowed_tender_statuses = ["active.enquiries"]
    requirement_models_by_classification = False


class BelowThresholdTenderDetailsState(BelowThresholdTenderDetailsMixin, BelowThresholdTenderState):
    pass


class RFPTenderDetailsMixin(TenderDetailsMixin):
    tender_patch_models_by_status = {
        "active.tendering": PatchActiveTender,
        "draft": PatchDraftTender,
        "active.enquiries": PatchDraftTender,
    }

    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    tender_patch_allowed_statuses = (
        "draft",
        "active.enquiries",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.tendering",
    )
    status_change_with_lot_cancellation_pending_check = False
    lot_operation_allowed_tender_statuses = ("active.enquiries", "active.tendering", "draft")
    tender_period_extra = REQUEST_FOR_PROPOSAL_TENDERING_EXTRA_PERIOD
    notice_doc_required_check = False
    evaluation_reports_doc_required_check = False
    items_classifications_prefix_check = False
    contract_template_name_patch_statuses = ("draft", "active.enquiries", "active.tendering")
    working_days_config = REQUEST_FOR_PROPOSAL_WORKING_DAYS_CONFIG
    enquiry_period_required = True
    patch_status_choices = (
        "draft",
        "active.enquiries",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
    notice_publication_date_on_activation = True
    vat_not_included_check = False
    items_classification_prefix_change_check = False
    items_delivery_required = False
    tender_period_start_date_required = False
    criterion_allowed_tender_statuses = ["draft", "active.enquiries"]
    criterion_patch_exclusion_check = False
    requirement_change_allowed_tender_statuses = ("draft",)
    requirement_change_legacy_status = "active.enquiries"
    requirement_put_allowed_tender_statuses = ["active.enquiries"]
    requirement_models_by_classification = False


class RFPTenderDetailsState(RFPTenderDetailsMixin, RFPTenderState):
    pass
