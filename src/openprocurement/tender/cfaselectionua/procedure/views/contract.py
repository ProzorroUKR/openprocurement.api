from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.contract import TenderContractResource

LOGGER = getLogger(__name__)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender contracts",
)
class CFASelectionContractResource(TenderContractResource):
    pass
