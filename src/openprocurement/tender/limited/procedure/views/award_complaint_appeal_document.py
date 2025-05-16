from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_appeal_document import (
    BaseAwardComplaintAppealDocumentResource,
)


@resource(
    name="negotiation:Tender Award Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType="negotiation",
    description="Tender award complaint appeal documents",
)
class NegotiationAwardComplaintAppealDocumentResource(BaseAwardComplaintAppealDocumentResource):
    pass


@resource(
    name="negotiation.quick:Tender Award Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType="negotiation.quick",
    description="Tender award complaint appeal documents",
)
class NegotiationQuickAwardComplaintAppealDocumentResource(BaseAwardComplaintAppealDocumentResource):
    pass
