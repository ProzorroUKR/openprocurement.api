from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.serializers.stage1.tender import (
    CD1StageTenderSerializer,
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
            "tender": CD1StageTenderSerializer,
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
