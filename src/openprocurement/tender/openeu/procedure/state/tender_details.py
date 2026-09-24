from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.constants import EU_REQUIRED_MULTILINGUAL_FIELDS
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.openeu.constants import WORKING_DAYS_CONFIG
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.openua.constants import TENDERING_EXTRA_PERIOD


# fields that used to be `required=True` on openeu Organization/Identifier/ContactPoint/Item models
class OpenEUTenderDetailsMixing(TenderDetailsMixing):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    should_validate_notice_doc_required = True
    should_validate_vat_not_included = True
    items_delivery_required = True
    tender_period_start_date_required = True
    items_classification_prefix_change_check = True
    required_multilingual_fields = EU_REQUIRED_MULTILINGUAL_FIELDS
    procuring_entity_available_language_default = "uk"
    tender_period_extra = TENDERING_EXTRA_PERIOD
    contract_template_name_patch_statuses = ("draft", "active.tendering")
    contract_template_required = True
    working_days_config = WORKING_DAYS_CONFIG


class OpenEUTenderDetailsState(OpenEUTenderDetailsMixing, BaseOpenEUTenderState):
    patch_status_choices = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
