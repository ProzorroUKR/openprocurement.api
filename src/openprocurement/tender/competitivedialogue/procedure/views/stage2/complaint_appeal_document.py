from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseTenderComplaintAppealDocumentResource,
)


@resource(
    name="{}:Tender Complaint Appeal Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender complaint appeal documents",
)
class CD2EUComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    pass


@resource(
    name="{}:Tender Complaint Appeal Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender complaint appeal documents",
)
class CD2UAComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    pass
