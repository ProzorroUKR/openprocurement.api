from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.utils import context_view
from openprocurement.tender.openeu.procedure.views.cancellation import (
    EUCancellationResource,
)


@resource(
    name="{}:Tender Cancellations".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue UE cancellations",
)
class CDEUCancellationResource(EUCancellationResource):
    @json_view(
        permission="view_tender",
    )
    @context_view(
        objs={
            "tender": (TenderBaseSerializer, TENDER_MASK_MAPPING),
        }
    )
    def get(self):
        return super().get()


@resource(
    name="{}:Tender Cancellations".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA cancellations",
)
class CDUACancellationResource(CDEUCancellationResource):
    pass
