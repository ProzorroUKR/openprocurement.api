from logging import getLogger

from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.contract import TenderContractResource

LOGGER = getLogger(__name__)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class PQContractResource(TenderContractResource):
    pass
