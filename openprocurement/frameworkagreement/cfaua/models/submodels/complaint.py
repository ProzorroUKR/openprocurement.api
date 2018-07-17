# -*- coding: utf-8 -*-
from openprocurement.api.models import ListType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.frameworkagreement.cfaua.models.submodels.documents import EUDocument
from openprocurement.tender.core.models import \
    ComplaintModelType as BaseComplaintModelType, \
    get_tender, Complaint as BaseComplaint
from schematics.types.compound import ModelType
from schematics.types import StringType, BooleanType
from schematics.exceptions import ValidationError
from openprocurement.api.models import IsoDateTimeType
from pyramid.security import Allow


class ComplaintModelType(BaseComplaintModelType):
    view_claim_statuses = ['active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction']


# openprocurement.tender.openua.models.Complaint + openprocurement.tender.openeu.models.Complaint
class Complaint(BaseComplaint):
    class Options:
        roles = RolesFromCsv('Complaint.csv', relative_to=__file__)
    documents = ListType(ModelType(EUDocument), default=list())
    status = StringType(choices=['draft', 'claim', 'answered', 'pending', 'accepted', 'invalid', 'resolved', 'declined', 'cancelled', 'satisfied', 'stopping', 'stopped', 'mistaken'], default='draft')
    acceptance = BooleanType()
    dateAccepted = IsoDateTimeType()
    rejectReason = StringType(choices=['lawNonСompliance', 'noPaymentReceived', 'buyerViolationsСorrected'])
    rejectReasonDescription = StringType()
    reviewDate = IsoDateTimeType()
    reviewPlace = StringType()
    bid_id = StringType()

    def __acl__(self):
        return [
            (Allow, 'g:aboveThresholdReviewers', 'edit_complaint'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_complaint_documents'),
        ]

    def get_role(self):
        root = self.__parent__
        while root.__parent__ is not None:
            root = root.__parent__
        request = root.request
        data = request.json_body['data']
        if request.authenticated_role == 'complaint_owner' and data.get('status', self.status) == 'cancelled':
            role = 'cancellation'
        elif request.authenticated_role == 'complaint_owner' and self.status in ['pending', 'accepted'] and data.get('status', self.status) == 'stopping':
            role = 'cancellation'
        elif request.authenticated_role == 'complaint_owner' and self.status == 'draft':
            role = 'draft'
        elif request.authenticated_role == 'complaint_owner' and self.status == 'claim':
            role = 'escalate'
        elif request.authenticated_role == 'tender_owner' and self.status == 'claim':
            role = 'answer'
        elif request.authenticated_role == 'tender_owner' and self.status in ['pending', 'accepted']:
            role = 'action'
        elif request.authenticated_role == 'tender_owner' and self.status == 'satisfied':
            role = 'resolve'
        elif request.authenticated_role == 'complaint_owner' and self.status == 'answered':
            role = 'satisfy'
        elif request.authenticated_role == 'aboveThresholdReviewers' and self.status == 'pending':
            role = 'pending'
        elif request.authenticated_role == 'aboveThresholdReviewers' and self.status in ['accepted', 'stopping']:
            role = 'review'
        else:
            role = 'invalid'
        return role

    def validate_cancellationReason(self, data, cancellationReason):
        if not cancellationReason and data.get('status') in ['cancelled', 'stopping']:
            raise ValidationError(u'This field is required.')

    def serialize(self, role=None, context=None):
        if role == 'view' and self.type == 'claim' and get_tender(self).status in ['active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction']:
            role = 'view_claim'
        return super(Complaint, self).serialize(role=role, context=context)
