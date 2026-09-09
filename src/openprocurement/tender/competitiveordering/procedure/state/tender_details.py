from openprocurement.api.auth import AccreditationLevel
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.tender.competitiveordering.constants import (
    LONG_WORKING_DAYS_CONFIG,
    SHORT_WORKING_DAYS_CONFIG,
    TENDERING_EXTRA_PERIOD,
)
from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)


class COTenderDetailsState(TenderDetailsMixing, COTenderState):
    items_classification_prefix_change_check = True
    agreement_procuring_entity_match_except_defense = True
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    should_validate_notice_doc_required = True
    should_validate_vat_not_included = True
    items_delivery_required = True
    tender_period_start_date_required = True
    patch_status_choices = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
    agreement_allowed_types = [DPS_TYPE]
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.tendering")


class COTenderConfigMixin:
    extra_config_schema_name = "competitiveOrdering"


class COShortTenderDetailsState(COTenderConfigMixin, COTenderDetailsState):
    extra_config_schema_name = "competitiveOrdering.short"
    agreement_with_items_forbidden = False

    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = False

    working_days_config = SHORT_WORKING_DAYS_CONFIG


class COLongTenderDetailsState(COTenderConfigMixin, COTenderDetailsState):
    extra_config_schema_name = "competitiveOrdering.long"
    agreement_with_items_forbidden = True

    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = False

    working_days_config = LONG_WORKING_DAYS_CONFIG
