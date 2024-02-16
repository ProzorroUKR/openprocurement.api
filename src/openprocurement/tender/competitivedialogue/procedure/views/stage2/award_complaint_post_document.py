from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.views.award_complaint_post_document import (
    BaseAwardComplaintPostDocumentResource,
)


@resource(
    name="{}:Tender Award Complaint Post Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender award complaint post documents",
)
class CD2EUAwardComplaintPostDocumentResource(BaseAwardComplaintPostDocumentResource):
    pass


@resource(
    name="{}:Tender Award Complaint Post Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender award complaint post documents",
)
class CD2UAAwardComplaintPostDocumentResource(BaseAwardComplaintPostDocumentResource):
    pass
