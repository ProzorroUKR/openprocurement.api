from copy import deepcopy

from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.constants import TENDER_CO_CONFIG_JSONSCHEMAS
from openprocurement.api.procedure.context import get_object
from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from openprocurement.api.procedure.state.base import ConfigMixin
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
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    should_validate_notice_doc_required = True
    agreement_allowed_types = [DPS_TYPE]
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.tendering")

    def on_patch(self, before, after):
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

        self.validate_items_classification_prefix_unchanged(before, after)

    @property
    def should_match_agreement_procuring_entity(self):
        if (
            get_object("tender")["procuringEntity"]["kind"] == ProcuringEntityKind.DEFENSE
            and get_object("agreement")["procuringEntity"]["kind"] == ProcuringEntityKind.DEFENSE
        ):
            # Defense procuring entity can use agreement with other defense procuring entity
            return False

        return True


class COTenderConfigMixin(ConfigMixin):
    co_config_schema_name = "competitiveOrdering"

    def validate_co_config(self, data):
        config_schema = TENDER_CO_CONFIG_JSONSCHEMAS.get(self.co_config_schema_name)
        config_schema = deepcopy(config_schema)
        config_schema.pop("required", None)
        self.validate_config_schema(data, config_schema)

    def validate_config(self, data):
        super().validate_config(data)
        self.validate_co_config(data)


class COShortTenderDetailsState(COTenderConfigMixin, COTenderDetailsState):
    co_config_schema_name = "competitiveOrdering.short"
    agreement_with_items_forbidden = False

    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = False

    working_days_config = SHORT_WORKING_DAYS_CONFIG


class COLongTenderDetailsState(COTenderConfigMixin, COTenderDetailsState):
    co_config_schema_name = "competitiveOrdering.long"
    agreement_with_items_forbidden = True

    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = False

    working_days_config = LONG_WORKING_DAYS_CONFIG
