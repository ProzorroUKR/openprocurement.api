from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1EUTenderDetailsState,
    CDStage1UATenderDetailsState,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_EU} tenders",
    accept="application/json",
)
class CDEUTenderResource(TendersResource):
    state_class = CDStage1EUTenderDetailsState


# ============= UA


@resource(
    name=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description=f"{ProcurementMethodType.COMPETITIVE_DIALOGUE_UA} tenders",
    accept="application/json",
)
class CDUATenderResource(TendersResource):
    state_class = CDStage1UATenderDetailsState
