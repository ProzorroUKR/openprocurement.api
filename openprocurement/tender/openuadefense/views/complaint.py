# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.tender.openua.views.complaint import TenderUaComplaintResource as TenderComplaintResource
from openprocurement.api.utils import (
    apply_patch,
    check_tender_status,
    context_unpack,
    json_view,
    opresource,
    save_tender,
    set_ownership,
)
from openprocurement.api.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
)
from openprocurement.tender.openuadefense.models import CLAIM_SUBMIT_TIME, COMPLAINT_SUBMIT_TIME
from openprocurement.tender.openuadefense.utils import calculate_business_date


@opresource(name='Tender UA.defense Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender complaints")
class TenderUaComplaintResource(TenderComplaintResource):

    @json_view(content_type="application/json", validators=(validate_complaint_data,), permission='create_complaint')
    def collection_post(self):
        """Post a complaint
        """
        tender = self.context
        if tender.status != 'active.tendering':
            self.request.errors.add('body', 'data', 'Can\'t add complaint in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        complaint = self.request.validated['complaint']
        if complaint.status == 'claim':
            if get_now() > calculate_business_date(tender.tenderPeriod.endDate, -CLAIM_SUBMIT_TIME, tender, True):
                self.request.errors.add('body', 'data', 'Can submit claim not later than {0.days} days before tenderPeriod end'.format(CLAIM_SUBMIT_TIME))
                self.request.errors.status = 403
                return
            complaint.dateSubmitted = get_now()
        elif complaint.status == 'pending':
            if get_now() > tender.complaintPeriod.endDate:
                self.request.errors.add('body', 'data', 'Can submit complaint not later than {0.days} days before tenderPeriod end'.format(COMPLAINT_SUBMIT_TIME))
                self.request.errors.status = 403
                return
            complaint.dateSubmitted = get_now()
            complaint.type = 'complaint'
        else:
            complaint.status = 'draft'
        complaint.complaintID = '{}.{}{}'.format(tender.tenderID, self.server_id, self.complaints_len(tender) + 1)
        set_ownership(complaint, self.request)
        tender.complaints.append(complaint)
        if save_tender(self.request):
            self.LOGGER.info('Created tender complaint {}'.format(complaint.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_complaint_create'}, {'complaint_id': complaint.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('Tender Complaints', tender_id=tender.id, complaint_id=complaint.id)
            return {
                'data': complaint.serialize(tender.status),
                'access': {
                    'token': complaint.owner_token
                }
            }

    @json_view(content_type="application/json", validators=(validate_patch_complaint_data,), permission='edit_complaint')
    def patch(self):
        """Post a complaint resolution
        """
        tender = self.request.validated['tender']
        if tender.status != 'active.tendering':
            self.request.errors.add('body', 'data', 'Can\'t update complaint in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        if self.context.status not in ['draft', 'claim', 'answered', 'pending', 'accepted', 'satisfied', 'stopping']:
            self.request.errors.add('body', 'data', 'Can\'t update complaint in current ({}) status'.format(self.context.status))
            self.request.errors.status = 403
            return
        data = self.request.validated['data']
        # complaint_owner
        if self.request.authenticated_role == 'complaint_owner' and self.context.status in ['draft', 'claim', 'answered'] and data.get('status', self.context.status) == 'cancelled':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status in ['pending', 'accepted'] and data.get('status', self.context.status) == 'stopping':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and tender.status == 'active.tendering' and self.context.status == 'draft' and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and tender.status == 'active.tendering' and self.context.status == 'draft' and data.get('status', self.context.status) == 'claim':
            if get_now() > calculate_business_date(tender.tenderPeriod.endDate, -CLAIM_SUBMIT_TIME, tender, True):
                self.request.errors.add('body', 'data', 'Can submit claim not later than {0.days} days before tenderPeriod end'.format(CLAIM_SUBMIT_TIME))
                self.request.errors.status = 403
                return
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateSubmitted = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and tender.status == 'active.tendering' and self.context.status in ['draft', 'claim'] and data.get('status', self.context.status) == 'pending':
            if get_now() > tender.complaintPeriod.endDate:
                self.request.errors.add('body', 'data', 'Can submit complaint not later than {0.days} days before tenderPeriod end'.format(COMPLAINT_SUBMIT_TIME))
                self.request.errors.status = 403
                return
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.type = 'complaint'
            self.context.dateSubmitted = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status == 'answered' and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status == 'answered' and data.get('satisfied', self.context.satisfied) is True and data.get('status', self.context.status) == 'resolved':
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status == 'answered' and data.get('satisfied', self.context.satisfied) is False and data.get('status', self.context.status) == 'pending':
            if get_now() > tender.complaintPeriod.endDate:
                self.request.errors.add('body', 'data', 'Can submit complaint not later than {0.days} days before tenderPeriod end'.format(COMPLAINT_SUBMIT_TIME))
                self.request.errors.status = 403
                return
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.type = 'complaint'
            self.context.dateEscalated = get_now()
        # tender_owner
        elif self.request.authenticated_role == 'tender_owner' and self.context.status == 'claim' and data.get('status', self.context.status) == self.context.status:
            now = get_now()
            if now > tender.enquiryPeriod.clarificationsUntil:
                self.request.errors.add('body', 'data', 'Can update claim only before enquiryPeriod.clarificationsUntil')
                self.request.errors.status = 403
                return
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'tender_owner' and self.context.status == 'satisfied' and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'tender_owner' and self.context.status == 'claim' and data.get('resolution', self.context.resolution) and data.get('resolutionType', self.context.resolutionType) and data.get('status', self.context.status) == 'answered':
            now = get_now()
            if now > tender.enquiryPeriod.clarificationsUntil:
                self.request.errors.add('body', 'data', 'Can update claim only before enquiryPeriod.clarificationsUntil')
                self.request.errors.status = 403
                return
            if len(data.get('resolution', self.context.resolution)) < 20:
                self.request.errors.add('body', 'data', 'Can\'t update complaint: resolution too short')
                self.request.errors.status = 403
                return
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateAnswered = get_now()
        elif self.request.authenticated_role == 'tender_owner' and self.context.status in ['pending', 'accepted']:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'tender_owner' and self.context.status == 'satisfied' and data.get('tendererAction', self.context.tendererAction) and data.get('status', self.context.status) == 'resolved':
            apply_patch(self.request, save=False, src=self.context.serialize())
        # aboveThresholdReviewers
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status in ['pending', 'accepted', 'stopping'] and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status in ['pending', 'stopping'] and data.get('status', self.context.status) == 'invalid':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            self.context.acceptance = False
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status == 'pending' and data.get('status', self.context.status) == 'accepted':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateAccepted = get_now()
            self.context.acceptance = True
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status == 'accepted' and data.get('status', self.context.status) in ['declined', 'satisfied']:
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status in ['accepted', 'stopping'] and data.get('status', self.context.status) == 'stopped':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            self.context.dateCanceled = self.context.dateCanceled or get_now()
        else:
            self.request.errors.add('body', 'data', 'Can\'t update complaint')
            self.request.errors.status = 403
            return
        if self.context.tendererAction and not self.context.tendererActionDate:
            self.context.tendererActionDate = get_now()
        if self.context.status not in ['draft', 'claim', 'answered', 'pending', 'accepted', 'stopping'] and tender.status in ['active.qualification', 'active.awarded']:
            check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender complaint {}'.format(self.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_complaint_patch'}))
            return {'data': self.context.serialize("view")}
