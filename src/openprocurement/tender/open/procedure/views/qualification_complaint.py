from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.qualification_claim import QualificationClaimResource
from openprocurement.tender.core.procedure.views.qualification_complaint import (
    QualificationComplaintGetResource,
    QualificationComplaintWriteResource,
)
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.qualification_claim import (
    AboveThresholdEUQualificationClaimState,
    OpenTenderingQualificationClaimState,
)
from openprocurement.tender.open.procedure.state.qualification_complaint import (
    AboveThresholdEUQualificationComplaintState,
    OpenTenderingQualificationComplaintState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Complaints Get",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    request_method=["GET"],
    description="Tender EU qualification complaints get",
    procurementMethodType=[ProcurementMethodType.ABOVE_THRESHOLD_EU, ProcurementMethodType.OPEN_TENDERING],
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
    procurementMethodType=[ProcurementMethodType.ABOVE_THRESHOLD_EU, ProcurementMethodType.OPEN_TENDERING],
)
class OpenQualificationClaimResource(QualificationClaimResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUQualificationClaimState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingQualificationClaimState,
    }


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Complaints",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU qualification complaints",
    procurementMethodType=[ProcurementMethodType.ABOVE_THRESHOLD_EU, ProcurementMethodType.OPEN_TENDERING],
)
class OpenQualificationComplaintWriteResource(QualificationComplaintWriteResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUQualificationComplaintState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingQualificationComplaintState,
    }
