from openprocurement.tender.core.procedure.views.award_complaint import AwardComplaintGetResource
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer
from cornice.resource import resource


@resource(
    name="belowThreshold:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    request_method=["GET"],
    description="Tender award complaints get",
)
class BelowThresholdAwardComplaintGetResource(AwardComplaintGetResource):
    serializer_class = ComplaintSerializer
