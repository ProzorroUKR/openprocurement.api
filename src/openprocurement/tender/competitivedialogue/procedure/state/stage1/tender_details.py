from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.api.validation import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.utils import validate_field
from openprocurement.tender.openeu.procedure.state.tender_details import OpenEUTenderDetailsMixing
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import CDStage1TenderState


class CDStage1TenderDetailsState(OpenEUTenderDetailsMixing, CDStage1TenderState):
    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)

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
