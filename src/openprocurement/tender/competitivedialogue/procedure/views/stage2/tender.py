from cornice.resource import resource
from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDStage2EUTenderDetailsState,
    CDStage2UATenderDetailsState,
)
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource


def stage2_acl():
    acl = [
        (Allow, Everyone, "view_tender"),
        (Allow, "g:brokers", "edit_tender"),
        (Allow, "g:Administrator", "edit_tender"),
        (Allow, "g:admins", ALL_PERMISSIONS),  # some tests use this, idk why
    ]
    return acl


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2} tenders",
    accept="application/json",
)
class TenderStage2UEResource(TendersResource):
    serializer_class = TenderBaseSerializer
    state_class = CDStage2EUTenderDetailsState

    def __acl__(self):
        return stage2_acl()


# ============= UA


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2} tenders",
    accept="application/json",
)
class TenderStage2UAResource(TendersResource):
    serializer_class = TenderBaseSerializer
    state_class = CDStage2UATenderDetailsState

    def __acl__(self):
        return stage2_acl()
