from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_1_EU_WORKING_DAYS_CONFIG,
    STAGE_1_UA_WORKING_DAYS_CONFIG,
    STAGE_2_EU_DEFAULT_CONFIG,
    STAGE_2_UA_DEFAULT_CONFIG,
)
from openprocurement.tender.competitivedialogue.procedure.models.stage2.tender import (
    PostEUTender,
    PostUATender,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDEUStage2TenderDetailsState,
    CDUAStage2TenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.utils import (
    prepare_stage2_tender_data,
)
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

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        if after == "active.stage2.waiting":
            # prepare stage2 tender
            new_tender = prepare_stage2_tender_data(data)
            new_tender = self.stage_2_tender_model(new_tender).serialize()
            new_tender["config"] = self.stage_2_config
            self.stage_2_tender_state(self.request).on_post(new_tender)
            # create stage2 tender
            self.request.validated["stage_2_tender"] = new_tender

            # update stage1 tender
            data["stage2TenderID"] = new_tender["_id"]
            self.set_object_status(data, "complete")

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
    stage_2_tender_state = CDEUStage2TenderDetailsState
    stage_2_tender_model = PostEUTender
    stage_2_config = STAGE_2_EU_DEFAULT_CONFIG


class CDUAStage1TenderDetailsState(CDStage1TenderDetailsStateMixin):
    working_days_config = STAGE_1_UA_WORKING_DAYS_CONFIG
    stage_2_tender_state = CDUAStage2TenderDetailsState
    stage_2_tender_model = PostUATender
    stage_2_config = STAGE_2_UA_DEFAULT_CONFIG
