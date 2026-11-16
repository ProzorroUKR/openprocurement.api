from logging import getLogger

from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.contract import TenderContractResource

LOGGER = getLogger(__name__)


@resource(
    name="{}:Tender Contracts".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue Stage 2 EU contracts",
)
class CDStage2EUTenderContractResource(TenderContractResource):
    pass


@resource(
    name="{}:Tender Contracts".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue Stage 2 UA contracts",
)
class CDStage2UATenderContractResource(TenderContractResource):
    pass
