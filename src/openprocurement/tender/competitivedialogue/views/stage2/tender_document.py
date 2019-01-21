# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now,
    raise_operation_error
)
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.validation import validate_tender_document_update_not_by_author_or_tender_owner
from openprocurement.tender.core.utils import (
    optendersresource, calculate_business_date
)
from openprocurement.tender.openeu.views.tender_document import (
    TenderEUDocumentResource
)
from openprocurement.tender.openua.views.tender_document import (
    TenderUaDocumentResource
)
from openprocurement.tender.openua.constants import TENDERING_EXTRA_PERIOD
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_UA_TYPE, STAGE_2_EU_TYPE, STAGE2_STATUS
)


@optendersresource(name='{}:Tender Documents'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Competitive Dialogue Stage 2 EU related binary files (PDFs, etc.)")
class CompetitiveDialogueStage2EUDocumentResource(TenderEUDocumentResource):

   def validate_update_tender(self):
        """ TODO move validators
        This class is inherited in openua package, but validate_update_tender function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if self.request.authenticated_role != 'auction' and self.request.validated['tender_status'] not in ['active.tendering', STAGE2_STATUS] or \
           self.request.authenticated_role == 'auction' and self.request.validated['tender_status'] not in ['active.auction', 'active.qualification']:
            raise_operation_error(self.request, 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(self.request.method), self.request.validated['tender_status']))
        if self.request.validated['tender_status'] == 'active.tendering' and calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, self.request.validated['tender']) > self.request.validated['tender'].tenderPeriod.endDate:
            raise_operation_error(self.request, 'tenderPeriod should be extended by {0.days} days'.format(TENDERING_EXTRA_PERIOD))
        if self.request.method in ['PUT', 'PATCH']:
            validate_tender_document_update_not_by_author_or_tender_owner(self.request)
        return True


@optendersresource(name='{}:Tender Documents'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue Stage 2 UA related binary files (PDFs, etc.)")
class CompetitiveDialogueStage2UADocumentResource(TenderUaDocumentResource):
    pass
