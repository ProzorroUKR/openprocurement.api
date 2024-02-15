from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.views.complaint_document import (
    TenderComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.complaint_document import (
    OpenComplaintDocumentState,
)


@resource(
    name="{}:Tender Complaint Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue stage2 EU complaint documents",
)
class CD2EUComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = OpenComplaintDocumentState


@resource(
    name="{}:Tender Complaint Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue stage2 UA complaint documents",
)
class CD2UAComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = OpenComplaintDocumentState
