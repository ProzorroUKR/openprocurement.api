from datetime import timedelta

from openprocurement.api.auth import AccreditationLevel, AccreditationPermission
from openprocurement.api.context import get_request, get_request_now
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_WORKING_DAYS_CONFIG,
    STAGE_2_UA_WORKING_DAYS_CONFIG,
)
from openprocurement.tender.competitivedialogue.procedure.models.stage2.tender import (
    BotPatchTender,
    PatchEUTender,
    PatchUATender,
)
from openprocurement.tender.core.utils import calculate_tender_full_date
from openprocurement.tender.openeu.procedure.state.tender_details import (
    OpenEUTenderDetailsState,
)


class CDEUStage2TenderDetailsState(OpenEUTenderDetailsState):
    tender_create_accreditations = (AccreditationPermission.ACCR_COMPETITIVE,)
    tender_central_accreditations = (AccreditationPermission.ACCR_COMPETITIVE, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)
    tender_transfer_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)

    should_validate_notice_doc_required = False
    should_validate_related_lot_in_items = False
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft",)

    working_days_config = STAGE_2_EU_WORKING_DAYS_CONFIG

    def get_patch_data_model(self):
        if get_request().authenticated_role == "competitive_dialogue":
            return BotPatchTender
        return PatchEUTender

    @staticmethod
    def watch_value_meta_changes(tender):
        pass

    def on_post(self, tender):
        tender["tenderPeriod"] = {
            "startDate": get_request_now().isoformat(),
            "endDate": calculate_tender_full_date(
                get_request_now(),
                timedelta(days=tender["config"]["minTenderingDuration"]),
                tender=tender,
            ).isoformat(),
        }

        super().on_post(tender)

    def validate_change_item_profile_or_category(self, after, before, force_validate: bool = False):
        if self.request.method != "POST":
            super().validate_change_item_profile_or_category(after, before, force_validate)


class CDUAStage2TenderDetailsState(CDEUStage2TenderDetailsState):
    tender_create_accreditations = (AccreditationPermission.ACCR_COMPETITIVE,)
    tender_central_accreditations = (AccreditationPermission.ACCR_COMPETITIVE, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)
    tender_transfer_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)

    contract_template_required = False
    contract_template_name_patch_statuses = ("draft",)

    working_days_config = STAGE_2_UA_WORKING_DAYS_CONFIG

    def get_patch_data_model(self):
        if get_request().authenticated_role == "competitive_dialogue":
            return BotPatchTender
        return PatchUATender

    @staticmethod
    def watch_value_meta_changes(tender):
        pass
