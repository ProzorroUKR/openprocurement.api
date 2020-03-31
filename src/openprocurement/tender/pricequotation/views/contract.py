# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.contract\
    import TenderAwardContractResource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Contracts".format(PMT),
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType=PMT,
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class PQTenderAwardContractResource(TenderAwardContractResource):
    """"""
