# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import (
    validate_complaint_operation_not_in_active_tendering,
    validate_update_complaint_not_in_allowed_complaint_status,
    validate_update_complaint_not_in_allowed_claim_status,
    validate_complaint_update_with_cancellation_lot_pending,
    validate_add_complaint_with_tender_cancellation_in_pending,
    validate_add_complaint_with_lot_cancellation_in_pending,
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource, TenderEUClaimResource
from openprocurement.tender.openua.views.complaint import TenderUAComplaintResource, TenderUAClaimResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.validation import (
    validate_complaint_data_stage2,
    validate_patch_complaint_data_stage2,
)


@optendersresource(
    name="{}:Tender Complaints Get".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue stage2 EU complaints get",
)
class CompetitiveDialogueStage2EUComplaintGetResource(BaseComplaintGetResource):
    """ """


@optendersresource(
    name="{}:Tender Complaints".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue stage2 EU complaints",
)
class CompetitiveDialogueStage2EUComplaintResource(TenderEUComplaintResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_complaint_data_stage2,
            validate_complaint_operation_not_in_active_tendering,
            validate_add_complaint_with_tender_cancellation_in_pending,
            validate_add_complaint_with_lot_cancellation_in_pending("complaint")
        ),
        permission="create_complaint",
    )
    def collection_post(self):
        return super(CompetitiveDialogueStage2EUComplaintResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_complaint_data_stage2,
            validate_complaint_update_with_cancellation_lot_pending,
            validate_complaint_operation_not_in_active_tendering,
            validate_update_complaint_not_in_allowed_complaint_status,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        return super(CompetitiveDialogueStage2EUComplaintResource, self).patch()


@optendersresource(
    name="{}:Tender Claims".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue stage2 EU claims",
)
class CompetitiveDialogueStage2EUClaimResource(TenderEUClaimResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_complaint_data_stage2,
            validate_complaint_operation_not_in_active_tendering,
            validate_add_complaint_with_tender_cancellation_in_pending,
            validate_add_complaint_with_lot_cancellation_in_pending("complaint")
        ),
        permission="create_complaint",
    )
    def collection_post(self):
        return super(CompetitiveDialogueStage2EUClaimResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_complaint_data_stage2,
            validate_complaint_update_with_cancellation_lot_pending,
            validate_complaint_operation_not_in_active_tendering,
            validate_update_complaint_not_in_allowed_claim_status,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        return super(CompetitiveDialogueStage2EUClaimResource, self).patch()


@optendersresource(
    name="{}:Tender Complaints Get".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue stage2 UA complaints get",
)
class CompetitiveDialogueStage2UAComplaintGetResource(BaseComplaintGetResource):
    """ """


@optendersresource(
    name="{}:Tender Complaints".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue stage2 UA complaints",
)
class CompetitiveDialogueStage2UAComplaintResource(TenderUAComplaintResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_complaint_data_stage2,
            validate_complaint_operation_not_in_active_tendering,
            validate_add_complaint_with_tender_cancellation_in_pending,
            validate_add_complaint_with_lot_cancellation_in_pending("complaint")
        ),
        permission="create_complaint",
    )
    def collection_post(self):
        return super(CompetitiveDialogueStage2UAComplaintResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_complaint_data_stage2,
            validate_complaint_update_with_cancellation_lot_pending,
            validate_complaint_operation_not_in_active_tendering,
            validate_update_complaint_not_in_allowed_complaint_status,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        return super(CompetitiveDialogueStage2UAComplaintResource, self).patch()


@optendersresource(
    name="{}:Tender Claims".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue stage2 UA claims",
)
class CompetitiveDialogueStage2UAClaimResource(TenderUAClaimResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_complaint_data_stage2,
            validate_complaint_operation_not_in_active_tendering,
            validate_add_complaint_with_tender_cancellation_in_pending,
            validate_add_complaint_with_lot_cancellation_in_pending("complaint")
        ),
        permission="create_complaint",
    )
    def collection_post(self):
        return super(CompetitiveDialogueStage2UAClaimResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_complaint_data_stage2,
            validate_complaint_update_with_cancellation_lot_pending,
            validate_complaint_operation_not_in_active_tendering,
            validate_update_complaint_not_in_allowed_claim_status,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        return super(CompetitiveDialogueStage2UAClaimResource, self).patch()
