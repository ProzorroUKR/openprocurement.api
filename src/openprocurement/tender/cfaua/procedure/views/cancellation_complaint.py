from cornice.resource import resource
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class CFAUACancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class CFAUACancellationComplaintWriteResource(CancellationComplaintWriteResource):
    pass

