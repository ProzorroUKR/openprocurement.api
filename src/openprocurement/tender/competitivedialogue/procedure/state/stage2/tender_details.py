from openprocurement.api.auth import AccreditationLevel, AccreditationPermission
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_WORKING_DAYS_CONFIG,
    STAGE_2_UA_WORKING_DAYS_CONFIG,
)
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

    @staticmethod
    def watch_value_meta_changes(tender):
        pass

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

    @staticmethod
    def watch_value_meta_changes(tender):
        pass
