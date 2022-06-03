# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.views.contract import (
    TenderAwardContractResource,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.openua.utils import check_tender_status
from openprocurement.tender.core.validation import (
    validate_contract_signing,
    validate_patch_contract_data,
    validate_update_contract_value,
    validate_update_contract_only_for_active_lots,
    validate_contract_operation_not_in_allowed_status,
    validate_update_contract_value_with_award,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
    validate_update_contract_status_by_supplier,
    validate_activate_contract,
    validate_update_contract_status,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.validation import (
    validate_contract_update_with_accepted_complaint,
)


# @optendersresource(
#     name="aboveThresholdUA:Tender Contracts",
#     collection_path="/tenders/{tender_id}/contracts",
#     path="/tenders/{tender_id}/contracts/{contract_id}",
#     procurementMethodType="aboveThresholdUA",
#     description="Tender contracts",
# )
class  TenderUaAwardContractResource(TenderAwardContractResource):
    @staticmethod
    def check_tender_status_method(request):
        return check_tender_status(request)

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_patch_contract_data,
            validate_contract_operation_not_in_allowed_status,
            validate_update_contract_status_by_supplier,
            validate_update_contract_status,
            validate_update_contract_only_for_active_lots,
            validate_contract_update_with_accepted_complaint,
            validate_update_contract_value,
            validate_contract_signing,
            validate_update_contract_value_net_required,
            validate_update_contract_value_with_award,
            validate_update_contract_value_amount,
        ),
    )
    def patch(self):
        return super(TenderUaAwardContractResource, self).patch()
