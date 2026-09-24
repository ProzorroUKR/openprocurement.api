from cornice.resource import resource

from openprocurement.tender.core.procedure.views.contract import TenderContractResource
from openprocurement.tender.open.constants import OPEN_PROCUREMENT_METHOD_TYPES, OPEN_ROUTE_PREFIX


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenTenderContractResource(TenderContractResource):
    pass
