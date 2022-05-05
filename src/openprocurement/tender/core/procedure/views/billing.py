from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.serializers.billing import BillingTenderSerializer
from cornice.resource import resource
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS


@resource(
    name="BillingTender",
    path="/tenders/{tender_id}/billing",
    description="Tender info for billing",
    request_method=("GET",),
)
class TenderChronographResource(TenderBaseResource):
    serializer_class = BillingTenderSerializer

    @json_view(permission="billing")
    def get(self):
        data = self.serializer_class(self.request.validated["tender"]).data
        return {"data": data}

    def __acl__(self):
        acl = [
            (Allow, "g:Administrator", "billing"),
        ]
        return acl
