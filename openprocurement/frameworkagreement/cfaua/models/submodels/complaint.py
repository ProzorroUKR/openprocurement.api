from openprocurement.api.models import ListType
from openprocurement.frameworkagreement.cfaua.models.submodels.documents import EUDocument
from openprocurement.tender.core.models import ComplaintModelType as BaseComplaintModelType, view_bid_role, get_tender
from openprocurement.tender.openua.models import Complaint as BaseComplaint
from schematics.types.compound import ModelType


class ComplaintModelType(BaseComplaintModelType):
    view_claim_statuses = ['active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction']


class Complaint(BaseComplaint):
    class Options:
        roles = {
            'active.pre-qualification': view_bid_role,
            'active.pre-qualification.stand-still': view_bid_role,
        }
    documents = ListType(ModelType(EUDocument), default=list())

    def serialize(self, role=None, context=None):
        if role == 'view' and self.type == 'claim' and get_tender(self).status in ['active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction']:
            role = 'view_claim'
        return super(Complaint, self).serialize(role=role, context=context)