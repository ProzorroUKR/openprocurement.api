# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.cancellation import TenderCancellationResource as TenderCancellationEUResource
from openprocurement.tender.openua.views.cancellation import TenderUaCancellationResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@opresource(name='Competitive Dialogue stage2 EU Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue stage2 UE cancellations")
class CompetitiveDialogueEUCancellationResource(TenderCancellationEUResource):
    """ TenderEU Cancellations """
    pass


@opresource(name='Competitive Dialogue stage2 UA Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue stage2 UA cancellations")
class CompetitiveDialogueUACancellationResource(TenderUaCancellationResource):
    """ TenderUA Cancellations """
    pass
