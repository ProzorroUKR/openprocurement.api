# -*- coding: utf-8 -*-
from openprocurement.api.views.tender import TenderResource
from openprocurement.api.utils import (
    opresource,
)


@opresource(name='Competitive Dialogue for UA procedure',
            path='/tenders/{tender_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class CompetitiveDialogueUAResource(TenderResource):
    """ Resource handler for Competitive Dialogue UA"""


@opresource(name='Competitive Dialogue for EU procedure',
            path='/tenders/{tender_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class CompetitiveDialogueEUResource(TenderResource):
    """ Resource handler for Competitive Dialogue EU"""
