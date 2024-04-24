from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.api.validation import raise_operation_error
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.utils import validate_field
from openprocurement.tender.openeu.procedure.state.tender_details import (
    OpenEUTenderDetailsMixing,
)


class CDStage1TenderDetailsState(OpenEUTenderDetailsMixing, CDStage1TenderState):
    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)

    required_criteria = {
        "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION",
        "CRITERION.EXCLUSION.CONVICTIONS.FRAUD",
        "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION",
        "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING",
        "CRITERION.EXCLUSION.CONTRIBUTIONS.PAYMENT_OF_TAXES",
        "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY",
        "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION",
        "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION",
        "CRITERION.EXCLUSION.NATIONAL.OTHER",
        "CRITERION.OTHER.BID.LANGUAGE",
    }

    def on_patch(self, before, after):
        if get_request().authenticated_role != "competitive_dialogue":
            if before["status"] == "active.stage2.waiting":
                raise_operation_error(get_request(), "Can't update tender in (active.stage2.waiting) status")

            if after["status"] == "complete":
                raise_operation_error(get_request(), "Can't update tender to (complete) status")

        super().on_patch(before, after)

    def validate_minimal_step(self, data, before=None):
        validate_field(data, "minimalStep", required=True)

    def validate_submission_method(self, data, before=None):
        validate_field(data, "submissionMethod", required=False)
        validate_field(data, "submissionMethodDetails", required=False)
        validate_field(data, "submissionMethodDetails_en", required=False)
        validate_field(data, "submissionMethodDetails_ru", required=False)
