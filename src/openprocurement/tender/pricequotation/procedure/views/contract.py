from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.contract import TenderContractResource
from openprocurement.tender.pricequotation.constants import PQ

LOGGER = getLogger(__name__)


@resource(
    name=f"{PQ}:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="priceQuotation",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class PQContractResource(TenderContractResource):
    pass
