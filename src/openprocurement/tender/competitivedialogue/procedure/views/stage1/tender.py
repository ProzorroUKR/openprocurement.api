from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1EUTenderDetailsState,
    CDStage1UATenderDetailsState,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource


@resource(
    name=f"{CD_EU_TYPE}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=CD_EU_TYPE,
    description=f"{CD_EU_TYPE} tenders",
    accept="application/json",
)
class CDEUTenderResource(TendersResource):
    state_class = CDStage1EUTenderDetailsState


# ============= UA


@resource(
    name=f"{CD_UA_TYPE}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=CD_UA_TYPE,
    description=f"{CD_UA_TYPE} tenders",
    accept="application/json",
)
class CDUATenderResource(TendersResource):
    state_class = CDStage1UATenderDetailsState
