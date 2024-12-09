from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.tender.competitiveordering.constants import (
    ENQUIRY_PERIOD_TIME,
    TENDERING_EXTRA_PERIOD,
)
from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)


class OpenTenderDetailsState(TenderDetailsMixing, OpenTenderState):
    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)
    tender_period_working_day = False
    clarification_period_working_day = False

    required_criteria = {
        "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION",
        "CRITERION.EXCLUSION.CONVICTIONS.FRAUD",
        "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION",
        "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING",
        "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY",
        "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION",
        "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION",
        "CRITERION.EXCLUSION.NATIONAL.OTHER",
        "CRITERION.OTHER.BID.LANGUAGE",
    }

    tendering_period_extra = TENDERING_EXTRA_PERIOD
    tendering_period_extra_working_days = False
    enquiry_period_timedelta = -ENQUIRY_PERIOD_TIME
    should_validate_notice_doc_required = True
    article_16_criteria_required = False
    agreement_allowed_types = [DPS_TYPE]
    agreement_with_items_forbidden = True

    @classmethod
    def get_items_classification_prefix_length(cls, tender):
        return 3

    def on_patch(self, before, after):
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

        self.validate_items_classification_prefix_unchanged(before, after)
