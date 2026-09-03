from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.openeu.constants import WORKING_DAYS_CONFIG
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.openua.constants import TENDERING_EXTRA_PERIOD
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsMixing,
)

# fields that used to be `required=True` on openeu Organization/Identifier/ContactPoint/Item models
EU_REQUIRED_MULTILINGUAL_FIELDS = {
    "procuringEntity": {
        "name_en": True,
        "identifier": {"legalName_en": True},
        "contactPoint": {"name_en": True},
        "additionalContactPoints": {"name_en": True},
    },
    "items": {"description_en": True},
}


class OpenEUTenderDetailsMixing(OpenUATenderDetailsMixing):
    required_multilingual_fields = EU_REQUIRED_MULTILINGUAL_FIELDS
    procuring_entity_available_language_default = "uk"
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    contract_template_name_patch_statuses = ("draft", "active.tendering")
    contract_template_required = True

    working_days_config = WORKING_DAYS_CONFIG

    def on_patch(self, before, after):
        self.validate_items_classification_prefix_unchanged(before, after)

        super().on_patch(before, after)  # TenderDetailsMixing.on_patch


class OpenEUTenderDetailsState(OpenEUTenderDetailsMixing, BaseOpenEUTenderState):
    patch_status_choices = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
