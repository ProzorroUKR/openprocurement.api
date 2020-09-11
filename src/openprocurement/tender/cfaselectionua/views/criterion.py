# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.criterion import TenderCriteriaResource


@optendersresource(
    name="closeFrameworkAgreementSelectionUA:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender criteria",
)
class TenderCriteriaResource(TenderCriteriaResource):
    pass

