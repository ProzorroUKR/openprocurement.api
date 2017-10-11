# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    context_unpack,
    json_view,
    set_ownership,
    get_now,
    raise_operation_error
)
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_award_complaint_add_only_for_active_lots,
    validate_update_complaint_not_in_allowed_complaint_status
)
from openprocurement.tender.core.utils import (
    apply_patch,
    save_tender
)
from openprocurement.tender.openeu.views.award_complaint import (
    TenderEUAwardComplaintResource
)
from openprocurement.tender.openua.views.award_complaint import get_bid_id
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.validation import (
    validate_add_complaint_not_in_pre_qualification,
    validate_update_complaint_not_in_pre_qualification,
    validate_add_complaint_not_in_qualification_period,
    validate_update_qualification_complaint_only_for_active_lots
)


@qualifications_resource(name='aboveThresholdEU:Tender Qualification Complaints',
                         collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints',
                         path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}',
                         procurementMethodType='aboveThresholdEU',
                         description="Tender EU qualification complaints")
class TenderEUQualificationComplaintResource(TenderEUAwardComplaintResource):

    def complaints_len(self, tender):
        return sum([len(i.complaints) for i in tender.awards], sum([len(i.complaints) for i in tender.qualifications], len(tender.complaints)))

    @json_view(content_type="application/json", permission='create_qualification_complaint', validators=(validate_complaint_data, validate_add_complaint_not_in_pre_qualification,
               validate_award_complaint_add_only_for_active_lots, validate_add_complaint_not_in_qualification_period))
    def collection_post(self):
        """Post a complaint
        """
        tender = self.request.validated['tender']
        complaint = self.request.validated['complaint']
        complaint.relatedLot = self.context.lotID
        complaint.date = get_now()
        complaint.bid_id = get_bid_id(self.request)
        if complaint.status == 'claim':
            complaint.dateSubmitted = get_now()
        elif complaint.status == 'pending':
            complaint.type = 'complaint'
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = 'draft'
        if self.context.status == 'unsuccessful' and complaint.status == 'claim' and self.context.bidID != complaint.bid_id:
            raise_operation_error(self.request, 'Can add claim only on unsuccessful qualification of your bid')
        complaint.complaintID = '{}.{}{}'.format(tender.tenderID, self.server_id, self.complaints_len(tender) + 1)
        set_ownership(complaint, self.request)
        self.context.complaints.append(complaint)
        if save_tender(self.request):
            self.LOGGER.info('Created tender qualification complaint {}'.format(complaint.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_qualification_complaint_create'}, {'complaint_id': complaint.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('{}:Tender Qualification Complaints'.format(tender.procurementMethodType), tender_id=tender.id, qualification_id=self.request.validated['qualification_id'], complaint_id=complaint['id'])
            return {
                'data': complaint.serialize("view"),
                'access': {
                    'token': complaint.owner_token
                }
            }

    @json_view(content_type="application/json", permission='edit_complaint', validators=(validate_patch_complaint_data, validate_update_complaint_not_in_pre_qualification,
               validate_update_qualification_complaint_only_for_active_lots, validate_update_complaint_not_in_allowed_complaint_status))
    def patch(self):
        """Patch the complaint
        """
        tender = self.request.validated['tender']
        data = self.request.validated['data']
        is_qualificationPeriod = tender.qualificationPeriod.startDate < get_now() and (not tender.qualificationPeriod.endDate or tender.qualificationPeriod.endDate > get_now())
        # complaint_owner
        if self.request.authenticated_role == 'complaint_owner' and self.context.status in ['draft', 'claim', 'answered'] and data.get('status', self.context.status) == 'cancelled':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status in ['pending', 'accepted'] and data.get('status', self.context.status) == 'stopping':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and is_qualificationPeriod and self.context.status == 'draft' and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and is_qualificationPeriod and self.context.status == 'draft' and data.get('status', self.context.status) == 'claim':
            if self.request.validated['qualification'].status == 'unsuccessful' and self.request.validated['qualification'].bidID != self.context.bid_id:
                raise_operation_error(self.request, 'Can add claim only on unsuccessful qualification of your bid')
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateSubmitted = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and is_qualificationPeriod and self.context.status == 'draft' and data.get('status', self.context.status) == 'pending':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.type = 'complaint'
            self.context.dateSubmitted = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status == 'answered' and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        # tender_owner
        elif self.request.authenticated_role == 'tender_owner' and self.context.status in ['pending', 'accepted']:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'tender_owner' and self.context.status in ['claim', 'satisfied'] and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'tender_owner' and self.context.status == 'claim' and data.get('resolution', self.context.resolution) and data.get('resolutionType', self.context.resolutionType) and data.get('status', self.context.status) == 'answered':
            if len(data.get('resolution', self.context.resolution)) < 20:
                raise_operation_error(self.request, 'Can\'t update complaint: resolution too short')
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateAnswered = get_now()
        elif self.request.authenticated_role == 'tender_owner' and self.context.status == 'satisfied' and data.get('tendererAction', self.context.tendererAction) and data.get('status', self.context.status) == 'resolved':
            apply_patch(self.request, save=False, src=self.context.serialize())
        # aboveThresholdReviewers
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status in ['pending', 'accepted', 'stopping'] and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status in ['pending', 'stopping'] and data.get('status', self.context.status) in ['invalid', 'mistaken']:
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            self.context.acceptance = False
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status == 'pending' and data.get('status', self.context.status) == 'accepted':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateAccepted = get_now()
            self.context.acceptance = True
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status in ['accepted', 'stopping'] and data.get('status', self.context.status) == 'declined':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status in ['accepted', 'stopping'] and data.get('status', self.context.status) == 'satisfied':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            tender.status = 'active.pre-qualification'
            if tender.qualificationPeriod.endDate:
                tender.qualificationPeriod.endDate = None
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status in ['pending', 'accepted', 'stopping'] and data.get('status', self.context.status) == 'stopped':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            self.context.dateCanceled = self.context.dateCanceled or get_now()
        else:
            raise_operation_error(self.request, 'Can\'t update complaint')
        if self.context.tendererAction and not self.context.tendererActionDate:
            self.context.tendererActionDate = get_now()
        if save_tender(self.request):
            self.LOGGER.info('Updated tender qualification complaint {}'.format(self.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_qualification_complaint_patch'}))
            return {'data': self.context.serialize("view")}
