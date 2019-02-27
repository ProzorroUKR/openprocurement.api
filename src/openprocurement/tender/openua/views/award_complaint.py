# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.views.award_complaint import TenderAwardComplaintResource

from openprocurement.api.utils import (
    get_now,
    context_unpack,
    json_view,
    set_ownership,
    raise_operation_error
)
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_add_complaint_not_in_complaint_period,
    validate_award_complaint_add_only_for_active_lots,
    validate_award_complaint_update_only_for_active_lots,
    validate_award_complaint_operation_not_in_allowed_status,
    validate_update_complaint_not_in_allowed_complaint_status
)

from openprocurement.tender.belowthreshold.utils import (
    check_tender_status,
)

from openprocurement.tender.core.utils import (
    save_tender, apply_patch,
    optendersresource
)

def get_bid_id(request):
    if request.authenticated_role != 'bid_owner':
        return
    tender = request.validated['tender']
    bids = {'{}_{}'.format(i.owner, i.owner_token): i.id for i in tender.bids}
    common = set(request.effective_principals).intersection(set(bids))
    if common:
        return bids[common.pop()]


@optendersresource(name='aboveThresholdUA:Tender Award Complaints',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}',
                   procurementMethodType='aboveThresholdUA',
                   description="Tender award complaints")
class TenderUaAwardComplaintResource(TenderAwardComplaintResource):

    def complaints_len(self, tender):
        return sum([len(i.complaints) for i in tender.awards], len(tender.complaints))

    @json_view(content_type="application/json", permission='create_award_complaint', validators=(validate_complaint_data, validate_award_complaint_operation_not_in_allowed_status,
               validate_award_complaint_add_only_for_active_lots, validate_add_complaint_not_in_complaint_period))
    def collection_post(self):
        """Post a complaint for award
        """
        tender = self.request.validated['tender']
        complaint = self.request.validated['complaint']
        complaint.date = get_now()
        complaint.relatedLot = self.context.lotID
        complaint.bid_id = get_bid_id(self.request)
        if complaint.status == 'claim':
            complaint.dateSubmitted = get_now()
        elif complaint.status == 'pending':
            if not any([i.status == 'active' for i in tender.awards if i.lotID == self.request.validated['award'].lotID]):
                raise_operation_error(self.request, 'Complaint submission is allowed only after award activation.')
            complaint.type = 'complaint'
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = 'draft'
        if self.context.status == 'unsuccessful' and complaint.status == 'claim' and self.context.bid_id != complaint.bid_id:
            raise_operation_error(self.request, 'Can add claim only on unsuccessful award of your bid')
        complaint.complaintID = '{}.{}{}'.format(tender.tenderID, self.server_id, self.complaints_len(tender) + 1)
        set_ownership(complaint, self.request)
        self.context.complaints.append(complaint)
        if save_tender(self.request):
            self.LOGGER.info('Created tender award complaint {}'.format(complaint.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_complaint_create'}, {'complaint_id': complaint.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('{}:Tender Award Complaints'.format(tender.procurementMethodType), tender_id=tender.id, award_id=self.request.validated['award_id'], complaint_id=complaint['id'])
            return {
                'data': complaint.serialize("view"),
                'access': {
                    'token': complaint.owner_token
                }
            }

    @json_view(content_type="application/json", permission='edit_complaint', validators=(validate_patch_complaint_data, validate_award_complaint_operation_not_in_allowed_status,
               validate_award_complaint_update_only_for_active_lots, validate_update_complaint_not_in_allowed_complaint_status))
    def patch(self):
        """Post a complaint resolution for award
        """
        tender = self.request.validated['tender']
        data = self.request.validated['data']
        complaintPeriod = self.request.validated['award'].complaintPeriod
        is_complaintPeriod = complaintPeriod.startDate < get_now() and complaintPeriod.endDate > get_now() if complaintPeriod.endDate else complaintPeriod.startDate < get_now()
        # complaint_owner
        if self.request.authenticated_role == 'complaint_owner' and self.context.status in ['draft', 'claim', 'answered'] and data.get('status', self.context.status) == 'cancelled':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status in ['pending', 'accepted'] and data.get('status', self.context.status) == 'stopping':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and is_complaintPeriod and self.context.status == 'draft' and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and is_complaintPeriod and self.context.status == 'draft' and data.get('status', self.context.status) == 'claim':
            if self.request.validated['award'].status == 'unsuccessful' and self.request.validated['award'].bid_id != self.context.bid_id:
                raise_operation_error(self.request, 'Can add claim only on unsuccessful award of your bid')
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateSubmitted = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and is_complaintPeriod and self.context.status == 'draft' and data.get('status', self.context.status) == 'pending':
            if not any([i.status == 'active' for i in tender.awards if i.lotID == self.request.validated['award'].lotID]):
                raise_operation_error(self.request, 'Complaint submission is allowed only after award activation.')
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
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status in ['accepted', 'stopping'] and data.get('status', self.context.status) in ['declined', 'satisfied']:
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status in ['pending', 'accepted', 'stopping'] and data.get('status', self.context.status) == 'stopped':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            self.context.dateCanceled = self.context.dateCanceled or get_now()
        else:
            raise_operation_error(self.request, 'Can\'t update complaint')
        if self.context.tendererAction and not self.context.tendererActionDate:
            self.context.tendererActionDate = get_now()
        if self.context.status not in ['draft', 'claim', 'answered', 'pending', 'accepted', 'satisfied', 'stopping'] and tender.status in ['active.qualification', 'active.awarded']:
            check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender award complaint {}'.format(self.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_complaint_patch'}))
            return {'data': self.context.serialize("view")}
