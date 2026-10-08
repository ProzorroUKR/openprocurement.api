from openprocurement.tender.competitivedialogue.constants import (
    CD_FEATURES_MAX_SUM,
    CD_STAGE_2_EU_DEFAULT_CONFIG,
    CD_STAGE_2_UA_DEFAULT_CONFIG,
    CD_TENDERING_EXTRA_PERIOD,
)
from openprocurement.tender.competitivedialogue.procedure.models.tender import (
    CDStage1EUPatchTender,
    CDStage1EUPostTender,
    CDStage1EUTender,
    CDStage1UAPatchTender,
    CDStage1UAPostTender,
    CDStage1UATender,
    CDStage2EUPostTender,
    CDStage2UAPostTender,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDStage2EUTenderDetailsState,
    CDStage2UATenderDetailsState,
)
from openprocurement.tender.core.constants import EU_REQUIRED_MULTILINGUAL_FIELDS
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixin
from openprocurement.tender.core.procedure.utils import (
    prepare_stage2_tender_data,
)


class CDStage1TenderDetailsStateMixin(TenderDetailsMixin, CDStage1TenderState):
    required_multilingual_fields = EU_REQUIRED_MULTILINGUAL_FIELDS
    procuring_entity_available_language_default = "uk"
    tender_period_extra = CD_TENDERING_EXTRA_PERIOD
    tender_patch_owner_check_exempt_roles = ("Administrator", "admins")
    tender_patch_allowed_statuses = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.stage2.pending",
    )
    guarantee_criterion_check = False
    features_max_weight = CD_FEATURES_MAX_SUM
    main_procurement_category_choices = ("services", "works")
    milestones_required = False
    milestones_delivery_financing_required = False
    items_classification_id_check = False
    patch_status_choices = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.stage2.waiting",
    )
    notice_doc_required_check = False
    required_market_criteria_check = False
    # minimalStep is required although stage 1 has no auction; submission method is optional
    minimal_step_regardless_of_auction = True
    lot_minimal_step_check_before = False
    submission_method_required = False

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


class CDStage1EUTenderDetailsState(CDStage1TenderDetailsStateMixin):
    post_data_model = CDStage1EUPostTender
    patch_data_model = CDStage1EUPatchTender
    data_model = CDStage1EUTender
    stage_2_tender_model = CDStage2EUPostTender

    stage_2_tender_state = CDStage2EUTenderDetailsState
    stage_2_config = CD_STAGE_2_EU_DEFAULT_CONFIG


class CDStage1UATenderDetailsState(CDStage1TenderDetailsStateMixin):
    post_data_model = CDStage1UAPostTender
    patch_data_model = CDStage1UAPatchTender
    data_model = CDStage1UATender
    stage_2_tender_model = CDStage2UAPostTender

    required_multilingual_fields = {}
    procuring_entity_available_language_default = None
    stage_2_tender_state = CDStage2UATenderDetailsState
    stage_2_config = CD_STAGE_2_UA_DEFAULT_CONFIG
