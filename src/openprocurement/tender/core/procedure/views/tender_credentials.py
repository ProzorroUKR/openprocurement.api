from cornice.resource import resource

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.serializers.tender_credentials import (
    TenderCredentialsSerializer,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource


@resource(
    name="Tender credentials",
    path="/tenders/{tender_id}/extract_credentials",
    description="Open Contracting compatible data exchange format",
)
class TenderResource(TenderBaseResource):
    @json_view(permission="extract_credentials")
    def get(self):
        tender = get_tender()
        self.LOGGER.info("Extract credentials for tender {}".format(tender["_id"]))
        return {"data": TenderCredentialsSerializer(tender).data}
