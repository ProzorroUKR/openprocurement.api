from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.tender.competitiveordering.constants import (
    SHORT_WORKING_DAYS_CONFIG,
    TENDERING_EXTRA_PERIOD,
)
from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.constants import CALENDAR_DAYS_CONFIG
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixin,
)


class COTenderDetailsState(TenderDetailsMixin, COTenderState):
    agreement_procuring_entity_match_except_defense = True
    agreement_allowed_types = [DPS_TYPE]
    contract_template_required = True
    working_days_config = CALENDAR_DAYS_CONFIG


class COTenderConfigMixin:
    extra_config_schema_name = "competitiveOrdering"


class COShortTenderDetailsState(COTenderConfigMixin, COTenderDetailsState):
    extra_config_schema_name = "competitiveOrdering.short"
    tender_period_extra = TENDERING_EXTRA_PERIOD
    working_days_config = SHORT_WORKING_DAYS_CONFIG


class COLongTenderDetailsState(COTenderConfigMixin, COTenderDetailsState):
    extra_config_schema_name = "competitiveOrdering.long"
    agreement_with_items_forbidden = True
    tender_period_extra = TENDERING_EXTRA_PERIOD
