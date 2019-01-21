# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.complaint import (
    TenderEUComplaintResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)


@optendersresource(name='{}:Tender Complaints'.format(CD_EU_TYPE),
                   collection_path='/tenders/{tender_id}/complaints',
                   path='/tenders/{tender_id}/complaints/{complaint_id}',
                   procurementMethodType=CD_EU_TYPE,
                   description="Competitive Dialogue EU complaints")
class CompetitiveDialogueEUComplaintResource(TenderEUComplaintResource):
    pass


@optendersresource(name='{}:Tender Complaints'.format(CD_UA_TYPE),
                   collection_path='/tenders/{tender_id}/complaints',
                   path='/tenders/{tender_id}/complaints/{complaint_id}',
                   procurementMethodType=CD_UA_TYPE,
                   description="Competitive Dialogue UA complaints")
class CompetitiveDialogueUAComplaintResource(TenderEUComplaintResource):
    pass
