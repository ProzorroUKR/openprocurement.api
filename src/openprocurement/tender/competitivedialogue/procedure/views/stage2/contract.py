from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.core.procedure.views.contract import TenderContractResource

LOGGER = getLogger(__name__)


@resource(
    name="{}:Tender Contracts".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU contracts",
)
class CDStage2EUTenderContractResource(TenderContractResource):
    pass


@resource(
    name="{}:Tender Contracts".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA contracts",
)
class CDStage2UATenderContractResource(TenderContractResource):
    pass
