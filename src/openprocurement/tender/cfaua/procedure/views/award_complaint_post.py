from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_complaint_post import (
    BaseAwardComplaintPostResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
    description="Tender award complaint posts",
)
class CFAUAAwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass
