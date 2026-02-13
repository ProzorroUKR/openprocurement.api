from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.qualification_complaint_appeal import (
    QualificationComplaintAppealResource as BaseQualificationComplaintAppealResource,
)


@resource(
    name="complexAsset.arma:Tender Qualification Complaint Appeals",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender qualification complaint appeals",
)
class QualificationComplaintAppealResource(BaseQualificationComplaintAppealResource):
    pass
