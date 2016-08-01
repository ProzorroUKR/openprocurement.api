# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource
from openprocurement.tender.openua.views.complaint import TenderUaComplaintResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.validation import (validate_complaint_data_stage2,
                                                                   validate_patch_complaint_data_stage2)
from openprocurement.api.utils import (
    json_view,
    opresource,
)


@opresource(name='Competitive Dialogue stage2 EU Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue stage2 EU complaints")
class CompetitiveDialogueStage2EUComplaintResource(TenderEUComplaintResource):

    @json_view(content_type="application/json", validators=(validate_complaint_data_stage2,), permission='create_complaint')
    def collection_post(self):
        return super(CompetitiveDialogueStage2EUComplaintResource, self).collection_post()

    @json_view(content_type="application/json", validators=(validate_patch_complaint_data_stage2,), permission='edit_complaint')
    def patch(self):
        return super(CompetitiveDialogueStage2EUComplaintResource, self).patch()


@opresource(name='Competitive Dialogue stage2 UA Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue stage2 UA complaints")
class CompetitiveDialogueStage2UAComplaintResource(TenderUaComplaintResource):

    @json_view(content_type="application/json", validators=(validate_complaint_data_stage2,), permission='create_complaint')
    def collection_post(self):
        return super(CompetitiveDialogueStage2UAComplaintResource, self).collection_post()

    @json_view(content_type="application/json", validators=(validate_patch_complaint_data_stage2,), permission='edit_complaint')
    def patch(self):
        return super(CompetitiveDialogueStage2UAComplaintResource, self).patch()

