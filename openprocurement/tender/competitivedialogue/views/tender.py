# -*- coding: utf-8 -*-
from openprocurement.api.views.tender import TenderResource
from openprocurement.tender.openeu.views.tender import TenderEUResource
from openprocurement.tender.openua.validation import validate_patch_tender_ua_data
from openprocurement.tender.competitivedialogue.utils import patch_eu
from openprocurement.api.utils import opresource, json_view


@opresource(name='Competitive Dialogue for UA procedure',
            path='/tenders/{tender_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="Open Contracting compatible data exchange format. See # for more info")
class CompetitiveDialogueUAResource(TenderResource):
    """ Resource handler for Competitive Dialogue UA"""

    @json_view(content_type="application/json", validators=(validate_patch_tender_ua_data,), permission='edit_tender')
    def patch(self):
        return patch_eu(self)


@opresource(name='Competitive Dialogue for EU procedure',
            path='/tenders/{tender_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Open Contracting compatible data exchange format. See  for more info")
class CompetitiveDialogueEUResource(TenderEUResource):
    """ Resource handler for Competitive Dialogue EU"""

    @json_view(content_type="application/json", validators=(validate_patch_tender_ua_data,), permission='edit_tender')
    def patch(self):
        return patch_eu(self)
