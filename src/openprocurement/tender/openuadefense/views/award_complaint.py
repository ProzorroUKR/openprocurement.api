# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.api.utils import json_view
from openprocurement.tender.core.views.award_complaint import (
    BaseTenderAwardComplaintResource,
    BaseTenderAwardClaimResource,
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_add_complaint_not_in_complaint_period,
    validate_award_complaint_add_only_for_active_lots,
    validate_award_complaint_operation_not_in_allowed_status,
    validate_add_complaint_with_tender_cancellation_in_pending,
    validate_add_complaint_with_lot_cancellation_in_pending
)
from openprocurement.tender.openuadefense.validation import validate_only_complaint_allowed


@optendersresource(
    name="aboveThresholdUA.defense:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["GET"],
    description="Tender award complaints get",
)
class TenderUaAwardComplaintGetResource(BaseComplaintGetResource):
    """"""


@optendersresource(
    name="aboveThresholdUA.defense:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class TenderUaAwardComplaintResource(BaseTenderAwardComplaintResource):
    """"""


@optendersresource(
    name="aboveThresholdUA.defense:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class TenderUaAwardClaimResource(BaseTenderAwardClaimResource):

    @json_view(
        content_type="application/json",
        permission="create_award_complaint",
        validators=(
                validate_complaint_data,
                validate_only_complaint_allowed,
                validate_award_complaint_operation_not_in_allowed_status,
                validate_award_complaint_add_only_for_active_lots,
                validate_add_complaint_not_in_complaint_period,
                validate_add_complaint_with_tender_cancellation_in_pending,
                validate_add_complaint_with_lot_cancellation_in_pending("award"),
        ),
    )
    def collection_post(self):
        """Post a claim for award
        """
        return super(TenderUaAwardClaimResource, self).collection_post()

