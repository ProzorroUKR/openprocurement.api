from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.contract import TenderContractResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD

LOGGER = getLogger(__name__)


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender contracts",
)
class UAContractResource(TenderContractResource):
    pass
