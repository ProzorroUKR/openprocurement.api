# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, json_view
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_award_complaint_add_only_for_active_lots,
    validate_award_complaint_update_only_for_active_lots,
    validate_update_complaint_not_in_allowed_complaint_status,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.award_complaint import BaseTenderAwardComplaintResource, get_bid_id

from openprocurement.tender.cfaua.utils import check_tender_status_on_active_qualification_stand_still
from openprocurement.tender.cfaua.validation import (
    validate_add_complaint_not_in_complaint_period,
    validate_update_complaint_not_in_qualification,
    validate_add_complaint_not_in_qualification_stand_still,
)


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU award complaints",
)
class TenderEUAwardComplaintResource(BaseTenderAwardComplaintResource):
    def complaints_len(self, tender):
        return sum(
            [len(i.complaints) for i in tender.awards],
            sum([len(i.complaints) for i in tender.qualifications], len(tender.complaints)),
        )

    def check_tender_status_method(self, request):
        return check_tender_status_on_active_qualification_stand_still(request)

    
    def pre_create(self):
        complaint = self.request.validated["complaint"]
        complaint.date = get_now()
        complaint.relatedLot = self.context.lotID
        complaint.bid_id = get_bid_id(self.request)

        if complaint.status == "claim":
            self.validate_posting_claim()
            complaint.dateSubmitted = get_now()
        elif complaint.status == "pending":
            complaint.type = "complaint"
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = "draft"
        
        return complaint

    @json_view(
        content_type="application/json",
        permission="create_award_complaint",
        validators=(
            validate_complaint_data,
            validate_add_complaint_not_in_qualification_stand_still,
            validate_award_complaint_add_only_for_active_lots,
            validate_add_complaint_not_in_complaint_period,
        ),
    )
    def collection_post(self):
        return super(TenderEUAwardComplaintResource, self).collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_complaint",
        validators=(
            validate_patch_complaint_data,
            validate_update_complaint_not_in_qualification,
            validate_award_complaint_update_only_for_active_lots,
            validate_update_complaint_not_in_allowed_complaint_status,
        ),
    )
    def patch(self):
        return super(TenderEUAwardComplaintResource, self).patch()

    def validate_posting_complaint(self):
        """
        we overwrite checking an active award
        as long as we have "validate_add_complaint_not_in_qualification_stand_still"
        in qualification.stand-still we always have an active award
        """

    def on_satisfy_complaint_by_reviewer(self):
        tender = self.request.validated["tender"]
        tender.status = "active.qualification"
        if tender.awardPeriod.endDate:
            tender.awardPeriod.endDate = None
