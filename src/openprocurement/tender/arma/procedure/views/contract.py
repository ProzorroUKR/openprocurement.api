from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.contract import TenderContractResource

LOGGER = getLogger(__name__)


@resource(
    name="complexAsset.arma:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender contracts",
)
class ContractResource(TenderContractResource):
    pass
