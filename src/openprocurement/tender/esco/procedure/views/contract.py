from logging import getLogger

from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.contract import TenderContractResource
from openprocurement.tender.esco.procedure.serializers.contract import (
    ContractSerializer,
)

LOGGER = getLogger(__name__)


@resource(
    name="esco:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType=ProcurementMethodType.ESCO,
    description="Tender ESCO contracts",
)
class ESCOContractResource(TenderContractResource):
    serializer_class = ContractSerializer
