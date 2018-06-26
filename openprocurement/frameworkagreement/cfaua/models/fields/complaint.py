from openprocurement.tender.core.models import ComplaintModelType as BaseComplaintModelType


class ComplaintModelType(BaseComplaintModelType):
    view_claim_statuses = ['active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction']