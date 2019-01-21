# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.cancellation import (
    TenderCancellationResource as TenderCancellationEUResource
)
from openprocurement.tender.openua.views.cancellation import (
    TenderUaCancellationResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
)


@optendersresource(name='{}:Tender Cancellations'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/cancellations',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Competitive Dialogue stage2 UE cancellations")
class CompetitiveDialogueEUCancellationResource(TenderCancellationEUResource):
    """ TenderEU Cancellations """
    pass


@optendersresource(name='{}:Tender Cancellations'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/cancellations',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue stage2 UA cancellations")
class CompetitiveDialogueUACancellationResource(TenderUaCancellationResource):
    """ TenderUA Cancellations """
    pass
