from openprocurement.tender.core.constants import EU_REQUIRED_MULTILINGUAL_FIELDS
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixin
from openprocurement.tender.openeu.constants import TENDERING_EXTRA_PERIOD
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


# fields that used to be `required=True` on openeu Organization/Identifier/ContactPoint/Item models
class OpenEUTenderDetailsMixin(TenderDetailsMixin):
    required_multilingual_fields = EU_REQUIRED_MULTILINGUAL_FIELDS
    procuring_entity_available_language_default = "uk"
    tender_period_extra = TENDERING_EXTRA_PERIOD
    contract_template_required = True
    patch_status_choices = None


class OpenEUTenderDetailsState(OpenEUTenderDetailsMixin, OpenEUTenderState):
    patch_status_choices = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
