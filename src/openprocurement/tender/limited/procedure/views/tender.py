from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.limited.procedure.serializers.tender import (
    LimitedTenderBaseSerializer,
)
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationQuickTenderDetailsState,
    NegotiationTenderDetailsState,
    ReportingTenderDetailsState,
)


@resource(
    name="reporting:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="reporting",
    description="reporting tenders",
    accept="application/json",
)
class ReportingTenderResource(TendersResource):
    state_class = ReportingTenderDetailsState
    serializer_class = LimitedTenderBaseSerializer


@resource(
    name="negotiation:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="negotiation",
    description="negotiation tenders",
    accept="application/json",
)
class NegotiationTenderResource(TendersResource):
    state_class = NegotiationTenderDetailsState
    serializer_class = LimitedTenderBaseSerializer


@resource(
    name="negotiation.quick:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="negotiation.quick",
    description="negotiation tenders",
    accept="application/json",
)
class NegotiationQuickTenderResource(TendersResource):
    state_class = NegotiationQuickTenderDetailsState
    serializer_class = LimitedTenderBaseSerializer
