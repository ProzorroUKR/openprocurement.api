from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.contract import TenderContractResource

LOGGER = getLogger(__name__)


@resource(
    name="reporting:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="reporting",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class ReportingContractResource(TenderContractResource):
    pass


@resource(
    name="negotiation:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="negotiation",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class NegotiationContractResource(ReportingContractResource):
    pass


@resource(
    name="negotiation.quick:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="negotiation.quick",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class NegotiationQuickContractResource(NegotiationContractResource):
    pass
