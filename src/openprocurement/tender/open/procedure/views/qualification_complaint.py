from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_claim import QualificationClaimResource
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintGetResource,
    QualificationComplaintWriteResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_EU, OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.qualification_claim import AboveThresholdEUQualificationClaimState
from openprocurement.tender.open.procedure.state.qualification_complaint import (
    AboveThresholdEUQualificationComplaintState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Complaints Get",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    request_method=["GET"],
    description="Tender EU qualification complaints get",
    procurementMethodType=[ABOVE_THRESHOLD_EU],
)
class OpenQualificationComplaintGetResource(QualificationComplaintGetResource):
    pass


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Claims",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender EU qualification claims",
    procurementMethodType=[ABOVE_THRESHOLD_EU],
)
class OpenQualificationClaimResource(QualificationClaimResource):
    state_classes = {
        ABOVE_THRESHOLD_EU: AboveThresholdEUQualificationClaimState,
    }


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Complaints",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU qualification complaints",
    procurementMethodType=[ABOVE_THRESHOLD_EU],
)
class OpenQualificationComplaintWriteResource(QualificationComplaintWriteResource):
    state_classes = {
        ABOVE_THRESHOLD_EU: AboveThresholdEUQualificationComplaintState,
    }
