from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.openua.procedure.views.contract import UAContractResource

LOGGER = getLogger(__name__)


@resource(
    name="simple.defense:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType="simple.defense",
    description="Tender contracts",
)
class SimpleDefenseContractResource(UAContractResource):
    pass
