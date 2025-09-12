from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.validation import raise_operation_error
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_1_EU_WORKING_DAYS_CONFIG,
    STAGE_1_UA_WORKING_DAYS_CONFIG,
)
from openprocurement.tender.competitivedialogue.procedure.models.stage1.tender import (
    BotPatchTender,
    PatchEUTender,
    PatchUATender,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.utils import validate_field
from openprocurement.tender.openeu.procedure.state.tender_details import (
    OpenEUTenderDetailsMixing,
)


class CDStage1TenderDetailsStateMixin(OpenEUTenderDetailsMixing, CDStage1TenderState):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    should_validate_notice_doc_required = False
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft", "active.tendering")
    should_validate_required_market_criteria = False

    def on_patch(self, before, after):
        if get_request().authenticated_role != "competitive_dialogue":
            if before["status"] == "active.stage2.waiting":
                raise_operation_error(
                    get_request(),
                    "Can't update tender in (active.stage2.waiting) status",
                )

            if after["status"] == "complete":
                raise_operation_error(get_request(), "Can't update tender to (complete) status")

        super().on_patch(before, after)

    def validate_minimal_step(self, data, before=None):
        tender = get_tender()
        validate_field(
            data,
            "minimalStep",
            enabled=not tender.get("lots"),
        )

    def validate_lot_minimal_step(self, data, before=None):
        validate_field(data, "minimalStep")

    def validate_submission_method(self, data, before=None):
        validate_field(data, "submissionMethod", required=False)
        validate_field(data, "submissionMethodDetails", required=False)
        validate_field(data, "submissionMethodDetails_en", required=False)
        validate_field(data, "submissionMethodDetails_ru", required=False)


class CDEUStage1TenderDetailsState(CDStage1TenderDetailsStateMixin):
    working_days_config = STAGE_1_EU_WORKING_DAYS_CONFIG

    def get_patch_data_model(self):
        if get_request().authenticated_role == "competitive_dialogue":
            return BotPatchTender
        return PatchEUTender


class CDUAStage1TenderDetailsState(CDStage1TenderDetailsStateMixin):
    working_days_config = STAGE_1_UA_WORKING_DAYS_CONFIG

    def get_patch_data_model(self):
        if get_request().authenticated_role == "competitive_dialogue":
            return BotPatchTender
        return PatchUATender
