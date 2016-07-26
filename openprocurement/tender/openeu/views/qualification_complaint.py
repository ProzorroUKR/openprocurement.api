# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.award_complaint import TenderEUAwardComplaintResource
from openprocurement.api.utils import (
    apply_patch,
    context_unpack,
    json_view,
    save_tender,
    set_ownership,
)
from openprocurement.api.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
)


@qualifications_resource(
    name='Tender EU Qualification Complaints',
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}',
    procurementMethodType='aboveThresholdEU',
    description="Tender EU qualification complaints")
class TenderEUQualificationComplaintResource(TenderEUAwardComplaintResource):

    def complaints_len(self, tender):
        return sum([len(i.complaints) for i in tender.awards], sum([len(i.complaints) for i in tender.qualifications], len(tender.complaints)))

    @json_view(content_type="application/json", permission='create_qualification_complaint', validators=(validate_complaint_data,))
    def collection_post(self):
        """Post a complaint
        """
        tender = self.request.validated['tender']
        if tender.status not in ['active.pre-qualification.stand-still']:
            self.request.errors.add('body', 'data', 'Can\'t add complaint in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in tender.lots if i.id == self.context.lotID]):
            self.request.errors.add('body', 'data', 'Can add complaint only in active lot status')
            self.request.errors.status = 403
            return
        if tender.qualificationPeriod and \
           (tender.qualificationPeriod.startDate and tender.qualificationPeriod.startDate > get_now() or
                tender.qualificationPeriod.endDate and tender.qualificationPeriod.endDate < get_now()):
            self.request.errors.add('body', 'data', 'Can add complaint only in qualificationPeriod')
            self.request.errors.status = 403
            return
        complaint = self.request.validated['complaint']
        complaint.relatedLot = self.context.lotID
        complaint.type = 'complaint'
        complaint.date = get_now()
        if complaint.status == 'pending':
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = 'draft'
        complaint.complaintID = '{}.{}{}'.format(tender.tenderID, self.server_id, self.complaints_len(tender) + 1)
        set_ownership(complaint, self.request)
        self.context.complaints.append(complaint)
        if save_tender(self.request):
            self.LOGGER.info('Created tender qualification complaint {}'.format(complaint.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_qualification_complaint_create'}, {'complaint_id': complaint.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('Tender EU Qualification Complaints', tender_id=tender.id, qualification_id=self.request.validated['qualification_id'], complaint_id=complaint['id'])
            return {
                'data': complaint.serialize("view"),
                'access': {
                    'token': complaint.owner_token
                }
            }

    @json_view(content_type="application/json", permission='edit_complaint', validators=(validate_patch_complaint_data,))
    def patch(self):
        """Patch the complaint
        """
        tender = self.request.validated['tender']
        if tender.status not in ['active.pre-qualification', 'active.pre-qualification.stand-still']:
            self.request.errors.add('body', 'data', 'Can\'t update complaint in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in tender.lots if i.id == self.request.validated['qualification'].lotID]):
            self.request.errors.add('body', 'data', 'Can update complaint only in active lot status')
            self.request.errors.status = 403
            return
        if self.context.status not in ['draft', 'claim', 'answered', 'pending', 'accepted', 'satisfied', 'stopping']:
            self.request.errors.add('body', 'data', 'Can\'t update complaint in current ({}) status'.format(self.context.status))
            self.request.errors.status = 403
            return
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
        elif self.request.authenticated_role == 'complaint_owner' and is_qualificationPeriod and self.context.status == 'draft' and data.get('status', self.context.status) == 'pending':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.type = 'complaint'
            self.context.dateSubmitted = get_now()
        elif self.request.authenticated_role == 'tender_owner' and self.context.status in ['pending', 'accepted']:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'tender_owner' and self.context.status == 'satisfied' and data.get('status', self.context.status) == self.context.status:
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
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status == 'accepted' and data.get('status', self.context.status) == 'declined':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
        elif self.request.authenticated_role == 'aboveThresholdReviewers' and self.context.status == 'accepted' and data.get('status', self.context.status) == 'satisfied':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            tender.status = 'active.pre-qualification'
            if tender.qualificationPeriod.endDate:
                tender.qualificationPeriod.endDate = None
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
        if save_tender(self.request):
            self.LOGGER.info('Updated tender qualification complaint {}'.format(self.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_qualification_complaint_patch'}))
            return {'data': self.context.serialize("view")}
