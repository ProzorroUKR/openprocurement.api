# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import (
    validate_patch_contract_data,
    validate_contract_operation_not_in_allowed_status,
    validate_update_contract_only_for_active_lots,
    validate_contract_signing,
    validate_update_contract_value_with_award,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
)
from openprocurement.tender.esco.validation import validate_update_contract_value_esco
from openprocurement.tender.openeu.views.contract import TenderAwardContractResource as TenderEUContractResource
from openprocurement.tender.openua.validation import validate_contract_update_with_accepted_complaint


@optendersresource(
    name="esco:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType="esco",
    description="Tender ESCO contracts",
)
class TenderESCOContractResource(TenderEUContractResource):
    """
    Tender ESCO Contract Resource
    """

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_patch_contract_data,
            validate_contract_operation_not_in_allowed_status,
            validate_update_contract_only_for_active_lots,
            validate_contract_update_with_accepted_complaint,
            validate_update_contract_value_esco,
            validate_contract_signing,
            validate_update_contract_value_net_required,
            validate_update_contract_value_with_award,
            validate_update_contract_value_amount,
        ),
    )
    def patch(self):
        """
        Update of contract
        """
        return super(TenderESCOContractResource, self).patch()
