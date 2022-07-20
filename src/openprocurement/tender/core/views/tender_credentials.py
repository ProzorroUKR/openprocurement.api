from hashlib import sha512
from openprocurement.api.views.base import BaseResource
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="Tender credentials",
    path="/tenders/{tender_id}/extract_credentials",
    description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info",
)
class TenderResource(BaseResource):
    @json_view(permission="extract_credentials")
    def get(self):
        self.LOGGER.info("Extract credentials for tender {}".format(self.context.id))
        tender = self.request.validated["tender"]
        data = tender.serialize("contracting")
        data["tender_token"] = sha512(tender.owner_token.encode("utf-8")).hexdigest()
        return {"data": data}
