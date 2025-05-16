from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseTenderComplaintAppealDocumentResource,
)


@resource(
    name="{}:Tender Complaint Appeal Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender complaint appeal documents",
)
class CDEUComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    pass


@resource(
    name="{}:Tender Complaint Appeal Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender complaint appeal documents",
)
class CDUAComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    pass
