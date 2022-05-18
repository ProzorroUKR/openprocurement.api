# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.contract import TenderUaAwardContractResource as TenderAwardContractResource


# @optendersresource(
#     name="simple.defense:Tender Contracts",
#     collection_path="/tenders/{tender_id}/contracts",
#     path="/tenders/{tender_id}/contracts/{contract_id}",
#     procurementMethodType="simple.defense",
#     description="Tender contracts",
# )
class TenderSimpleDefAwardContractResource(TenderAwardContractResource):
    pass
