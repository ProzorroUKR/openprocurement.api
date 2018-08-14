# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import (
    validate_patch_contract_data,
    validate_contract_operation_not_in_allowed_status,
    validate_update_contract_only_for_active_lots,
    validate_contract_signing,
)
from openprocurement.tender.esco.validation import (
    validate_update_contract_value
)
from openprocurement.tender.openeu.views.contract import (
    TenderAwardContractResource as TenderEUContractResource
)
from openprocurement.tender.openua.validation import validate_contract_update_with_accepted_complaint


@optendersresource(name='esco:Tender Contracts',
                   collection_path='/tenders/{tender_id}/contracts',
                   path='/tenders/{tender_id}/contracts/{contract_id}',
                   procurementMethodType='esco',
                   description="Tender ESCO contracts")
class TenderESCOContractResource(TenderEUContractResource):
    """
    Tender ESCO Contract Resource
    """
    @json_view(content_type="application/json", permission='edit_tender', validators=(
            validate_patch_contract_data,
            validate_contract_operation_not_in_allowed_status,
            validate_update_contract_only_for_active_lots,
            validate_contract_update_with_accepted_complaint,
            validate_update_contract_value,
            validate_contract_signing))
    def patch(self):
        """
        Update of contract
        """
        return super(TenderESCOContractResource, self).patch()
