from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.qualification_claim import (
    QualificationClaimState,
)
from openprocurement.tender.arma.procedure.state.qualification_complaint import (
    QualificationComplaintState,
)
from openprocurement.tender.core.procedure.views.qualification_claim import (
    QualificationClaimResource as BaseQualificationClaimResource,
)
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintGetResource,
)
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintWriteResource as BaseQualificationComplaintWriteResource,
)


@resource(
    name="complexAsset.arma:Tender Qualification Complaints Get",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    request_method=["GET"],
    description="Tender qualification complaints get",
)
class QualificationClaimAndComplaintGetResource(QualificationComplaintGetResource):
    pass


@resource(
    name="complexAsset.arma:Tender Qualification Claims",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender qualification claims",
)
class QualificationClaimResource(BaseQualificationClaimResource):
    state_class = QualificationClaimState


@resource(
    name="complexAsset.arma:Tender Qualification Complaints",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender qualification complaints",
)
class QualificationComplaintWriteResource(BaseQualificationComplaintWriteResource):
    state_class = QualificationComplaintState
