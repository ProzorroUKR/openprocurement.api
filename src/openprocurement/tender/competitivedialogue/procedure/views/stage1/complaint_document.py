from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.complaint_document import (
    TenderComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.complaint_document import (
    OpenComplaintDocumentState,
)


@resource(
    name="{}:Tender Complaint Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue complaint documents",
)
class CDEUComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = OpenComplaintDocumentState


@resource(
    name="{}:Tender Complaint Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue complaint documents",
)
class CDUAComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = OpenComplaintDocumentState
